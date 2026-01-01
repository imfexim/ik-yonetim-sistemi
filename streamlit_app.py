import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Konfigürasyon ve Görsel Stil (Beyaz Zemin - Siyah Yazı)
st.set_page_config(page_title="İM-FEXİM Kurumsal", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    * { color: #000000 !important; }
    input, select, textarea, div[data-baseweb="select"] > div { background-color: #FFFFFF !important; border: 1px solid #000000 !important; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #000000 !important; }
    .stButton>button { background-color: #FFFFFF !important; border: 1px solid #000000 !important; }
    /* Menü Başlıkları */
    .menu-header { font-weight: bold; font-size: 18px; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Sol Menü (Tek Seçim Mantığı - Radio Buttonlar İzole Edildi)
with st.sidebar:
    st.markdown("## İM-FEXİM")
    st.markdown("---")
    
    st.markdown("<p class='menu-header'>🛠️ ORGANİZASYON</p>", unsafe_allow_html=True)
    org_menu = st.radio("Seçiniz:", ["Departmanlar", "Pozisyonlar", "Seviyeler"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("<p class='menu-header'>💼 İŞE ALIM</p>", unsafe_allow_html=True)
    hr_menu = st.radio("Seçiniz:", ["Adaylar"], label_visibility="collapsed")

# --- FONKSİYONLAR ---

def get_data(table):
    return supabase.table(table).select("*").execute().data

# --- MODÜL 1: DEPARTMANLAR ---
if org_menu == "Departmanlar" and hr_menu != "Adaylar":
    st.header("🏢 Departman Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Departman Ekle", "📋 Departman Listesi"])
    with t1:
        with st.form("dep_ekle", clear_on_submit=True):
            d_ad = st.text_input("Departman Adı")
            if st.form_submit_button("Kaydet"):
                if d_ad:
                    supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute()
                    st.success("Eklendi"); st.rerun()
    with t2:
        deps = get_data("departmanlar")
        if deps: st.table(pd.DataFrame(deps)[["departman_adi"]])

# --- MODÜL 2: POZİSYONLAR ---
elif org_menu == "Pozisyonlar" and hr_menu != "Adaylar":
    st.header("👔 Pozisyon Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Pozisyon Ekle", "📋 Pozisyon Listesi"])
    with t1:
        deps = get_data("departmanlar")
        with st.form("poz_ekle", clear_on_submit=True):
            dep_opts = ["Departman Seçiniz..."] + [d['departman_adi'] for d in deps]
            secilen_dep = st.selectbox("Bağlı Olduğu Departman", dep_opts)
            p_ad = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Pozisyon ve 6 Seviyeyi Oluştur"):
                if secilen_dep != "Departman Seçiniz..." and p_ad:
                    d_id = [d['id'] for d in deps if d['departman_adi'] == secilen_dep][0]
                    p_res = supabase.table("pozisyonlar").insert({"departman_id": d_id, "pozisyon_adi": p_ad}).execute()
                    p_id = p_res.data[0]['id']
                    kodlar = ["J1", "J2", "M1", "M2", "M3", "S"]
                    supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_ad} {k}", "seviye_kodu": k} for k in kodlar]).execute()
                    st.success("Kayıt Başarılı"); st.rerun()
    with t2:
        res = supabase.table("pozisyonlar").select("pozisyon_adi, departmanlar(departman_adi)").execute()
        if res.data:
            st.table(pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res.data]))

# --- MODÜL 3: SEVİYELER ---
elif org_menu == "Seviyeler" and hr_menu != "Adaylar":
    st.header("📊 Seviye Listesi")
    res = supabase.table("seviyeler").select("seviye_adi, seviye_kodu, pozisyonlar(pozisyon_adi)").execute()
    if res.data:
        st.table(pd.DataFrame([{"Seviye": r['seviye_adi'], "Kod": r['seviye_kodu'], "Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res.data]))

# --- MODÜL 4: ADAYLAR (İŞE ALIM) ---
if hr_menu == "Adaylar":
    st.header("👤 Aday Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Aday Ekle", "📋 Aday Listesi"])
    
    with t1:
        with st.form("aday_ekle_form", clear_on_submit=True):
            st.markdown("##### Zorunlu Bilgiler")
            c1, c2 = st.columns(2)
            ad_soyad = c1.text_input("Ad Soyad *")
            tc_no = c2.text_input("Kimlik No *")
            
            st.markdown("##### Opsiyonel Bilgiler")
            tel = st.text_input("Telefon")
            
            # İlişkisel Veriler
            deps = get_data("departmanlar")
            secilen_dep = st.selectbox("Departman", ["Departman Seçiniz..."] + [d['departman_adi'] for d in deps])
            
            # Pozisyon ve Seviye Seçimi (Aday eklerken versiyonlama için gerekli)
            pozs = get_data("pozisyonlar")
            secilen_poz = st.selectbox("Pozisyon", ["Pozisyon Seçiniz..."] + [p['pozisyon_adi'] for p in pozs])
            
            sevs = get_data("seviyeler")
            secilen_sev = st.selectbox("Seviye", ["Seviye Seçiniz..."] + [s['seviye_adi'] for s in sevs])
            
            cv_dosya = st.file_uploader("CV Yükle", type=['pdf', 'docx'])

            if st.form_submit_button("Adayı Versiyonla ve Kaydet"):
                if ad_soyad and tc_no:
                    # 1. Ana Tablo (İşlem SCD Type 2 Mantığı)
                    a_res = supabase.table("adaylar").insert({"ad_soyad": ad_soyad, "kimlik_no": tc_no}).execute()
                    a_id = a_res.data[0]['id']
                    
                    # 2. Versiyon Tablosu (Bitis Tarihi Boş, Islemi Yapan 'Sistemsel')
                    v_res = supabase.table("aday_versiyonlar").insert({
                        "aday_id": a_id, "ad_soyad": ad_soyad, "kimlik_no": tc_no, 
                        "telefon": tel, "islemi_yapan": "Sistemsel", "baslangic_tarihi": datetime.now().isoformat()
                    }).execute()
                    
                    # 3. Ana tabloyu yeni versiyon ID'sine bağla
                    supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                    st.success("Aday ilk versiyonuyla kaydedildi.")
                else:
                    st.error("Ad Soyad ve Kimlik No mecburidir.")

    with t2:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*)").execute()
        if res.data:
            list_disp = []
            for r in res.data:
                v = r['aday_versiyonlar']
                list_disp.append({
                    "Ad Soyad": r['ad_soyad'],
                    "Kimlik No": r['kimlik_no'],
                    "Telefon": v['telefon'] if v else "-",
                    "Versiyon ID": v['id'][:8] if v else "-"
                })
            st.table(pd.DataFrame(list_disp))
