import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Konfigürasyon ve Stil (Yüksek Kontrastlı)
st.set_page_config(page_title="İM-FEXİM İşe Alım", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    * { color: #000000 !important; }
    input, select, textarea, div[data-baseweb="select"] > div { background-color: #FFFFFF !important; border: 1px solid #000000 !important; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #000000 !important; }
    .stButton>button { background-color: #FFFFFF !important; border: 1px solid #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Sol Menü Hiyerarşisi
with st.sidebar:
    st.markdown("## İM-FEXİM")
    with st.expander("🛠️ Organizasyon", expanded=False):
        org_menu = st.radio("", ["Departmanlar", "Pozisyonlar", "Seviyeler"])
    with st.expander("💼 İşe Alım", expanded=True):
        hr_menu = st.radio("", ["Adaylar"])

# --- ADAYLAR MODÜLÜ ---
if hr_menu == "Adaylar":
    st.header("👤 Aday Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Aday Ekle", "📋 Aday Listesi"])

    with t1:
        with st.form("aday_form", clear_on_submit=True):
            st.markdown("##### Zorunlu Bilgiler")
            c1, c2 = st.columns(2)
            ad_soyad = c1.text_input("Ad Soyad *")
            tc_no = c2.text_input("Kimlik Numarası *")
            
            st.markdown("##### Opsiyonel Bilgiler")
            c3, c4 = st.columns(2)
            tel = c3.text_input("Telefon Numarası")
            
            # Verileri Dropbox için Çekme
            deps = supabase.table("departmanlar").select("id, departman_adi").execute().data
            dep_opts = ["Departman Seçiniz..."] + [d['departman_adi'] for d in deps]
            secilen_dep = c4.selectbox("Departman", dep_opts)
            
            # Dinamik Pozisyon ve Seviye Seçimi (Sadeleştirilmiş gösterim)
            pozs = supabase.table("pozisyonlar").select("id, pozisyon_adi").execute().data
            poz_opts = ["Pozisyon Seçiniz..."] + [p['pozisyon_adi'] for p in pozs]
            secilen_poz = st.selectbox("Pozisyon", poz_opts)
            
            cv_dosya = st.file_uploader("CV Yükle (PDF/Docx)", type=['pdf', 'docx'])

            if st.form_submit_button("Adayı Kaydet"):
                if ad_soyad and tc_no:
                    try:
                        # 1. Önce Aday Ana Tabloya Ekle (veya ID al)
                        aday_check = supabase.table("adaylar").select("id").eq("kimlik_no", tc_no).execute()
                        
                        if not aday_check.data:
                            aday_res = supabase.table("adaylar").insert({"ad_soyad": ad_soyad, "kimlik_no": tc_no}).execute()
                            aday_id = aday_res.data[0]['id']
                        else:
                            st.error("Bu kimlik numarası ile kayıtlı bir aday zaten var.")
                            st.stop()

                        # 2. Versiyon Tablosuna İlk Kaydı At
                        v_data = {
                            "aday_id": aday_id,
                            "ad_soyad": ad_soyad,
                            "kimlik_no": tc_no,
                            "telefon": tel,
                            "islemi_yapan": "Sistemsel",
                            "baslangic_tarihi": datetime.now().isoformat()
                        }
                        
                        v_res = supabase.table("aday_versiyonlar").insert(v_data).execute()
                        v_id = v_res.data[0]['id']
                        
                        # 3. Ana Tablodaki güncel_versiyon_id'yi güncelle
                        supabase.table("adaylar").update({"guncel_versiyon_id": v_id}).eq("id", aday_id).execute()
                        
                        st.success(f"Aday {ad_soyad} başarıyla kaydedildi.")
                    except Exception as e:
                        st.error(f"Hata oluştu: {e}")
                else:
                    st.warning("Ad Soyad ve Kimlik No alanları mecburidir.")

    with t2:
        # Listeleme: Ana tablodaki en güncel versiyon bilgilerini getirir
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*)").execute()
        if res.data:
            list_data = []
            for r in res.data:
                v = r['aday_versiyonlar']
                list_data.append({
                    "Ad Soyad": r['ad_soyad'],
                    "Kimlik No": r['kimlik_no'],
                    "Telefon": v.get('telefon', '-'),
                    "Kayıt Tarihi": r['olusturma_tarihi'][:10]
                })
            st.table(pd.DataFrame(list_data))
        else:
            st.info("Kayıtlı aday bulunamadı.")

# --- DİĞER MENÜLERİN LİSTELENMESİ ---
if org_menu == "Departmanlar":
    st.header("🏢 Departman Listesi")
    res = supabase.table("departmanlar").select("*").execute()
    if res.data: st.table(pd.DataFrame(res.data)[["departman_adi"]])

elif org_menu == "Pozisyonlar":
    st.header("👔 Pozisyon Listesi")
    res = supabase.table("pozisyonlar").select("pozisyon_adi, departmanlar(departman_adi)").execute()
    if res.data:
        p_list = [{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res.data]
        st.table(pd.DataFrame(p_list))

elif org_menu == "Seviyeler":
    st.header("📊 Seviye Listesi")
    res = supabase.table("seviyeler").select("seviye_adi, seviye_kodu, pozisyonlar(pozisyon_adi)").execute()
    if res.data:
        s_list = [{"Seviye": r['seviye_adi'], "Kod": r['seviye_kodu'], "Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res.data]
        st.table(pd.DataFrame(s_list))
