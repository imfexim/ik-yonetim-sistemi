import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Konfigürasyon ve Stil
st.set_page_config(page_title="İM-FEXİM İnsan Kaynakları", layout="wide")
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

# 3. Yardımcı Fonksiyonlar (Veri Çekme)
def get_all(table): return supabase.table(table).select("*").execute().data
def get_filtered(table, col, val): return supabase.table(table).select("*").eq(col, val).execute().data

# --- ANA MENÜ ---
with st.sidebar:
    st.markdown("### 🏢 İM-FEXİM")
    main_nav = st.radio("ANA MENÜ", ["Organizasyon", "İşe Alım"])
    st.markdown("---")
    if main_nav == "Organizasyon":
        sub_nav = st.radio("ALT MENÜ", ["Departmanlar", "Pozisyonlar", "Seviyeler"])
    else:
        sub_nav = st.radio("ALT MENÜ", ["Adaylar"])

# --- ADAYLAR MODÜLÜ (GÜNCELLEME ODAKLI) ---
if sub_nav == "Adaylar":
    st.header("👤 Aday Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Aday Kaydı", "📋 Liste ve Bilgi Güncelleme"])

    # --- TAB 1: YENİ KAYIT (Özet Geçildi) ---
    with t1:
        st.info("Yeni aday kaydı yaparken kimlik bilgilerini eksiksiz giriniz.")
        # ... (Önceki bölümlerdeki yeni kayıt formu burada yer alacak)

    # --- TAB 2: LİSTELEME VE DİNAMİK VERSİYONLAMA ---
    with t2:
        # Mevcut adayları en güncel versiyonlarıyla çek
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi), seviyeler(seviye_adi))").execute()
        
        if res.data:
            for aday in res.data:
                v = aday['aday_versiyonlar']
                exp_label = f"📝 {aday['ad_soyad']} | {v['departmanlar']['departman_adi'] if v and v['departmanlar'] else 'Atanmamış'}"
                
                with st.expander(exp_label):
                    st.warning("Kimlik bilgileri (Ad Soyad, TC No) sabittir. Kariyer ve iletişim bilgilerini aşağıdan güncelleyebilirsiniz.")
                    
                    # Düzenleme Formu
                    with st.form(key=f"v_update_{aday['id']}", clear_on_submit=False):
                        c1, c2 = st.columns(2)
                        c1.text_input("Ad Soyad", value=aday['ad_soyad'], disabled=True)
                        c2.text_input("Kimlik No", value=aday['kimlik_no'], disabled=True)
                        
                        u_tel = st.text_input("Telefon Numarası", value=v['telefon'] if v else "")
                        
                        # --- DİNAMİK KARİYER SEÇİMİ (Versiyonlanacak Alanlar) ---
                        deps = get_all("departmanlar")
                        d_map = {d['departman_adi']: d['id'] for d in deps}
                        
                        # Mevcut departman indexini bul
                        current_d = v['departmanlar']['departman_adi'] if v and v['departmanlar'] else "Seçiniz..."
                        d_list = ["Seçiniz..."] + list(d_map.keys())
                        u_dep_name = st.selectbox("Departman", d_list, index=d_list.index(current_d) if current_d in d_list else 0)
                        
                        u_poz_id = v['pozisyon_id'] if v else None
                        u_sev_id = v['seviye_id'] if v else None

                        st.caption("Not: Departman/Pozisyon değişikliği yaptıysanız, lütfen ilgili alt seçenekleri de yeniden seçiniz.")
                        
                        if u_dep_name != "Seçiniz...":
                            pozs = get_filtered("pozisyonlar", "departman_id", d_map[u_dep_name])
                            p_map = {p['pozisyon_adi']: p['id'] for p in pozs}
                            p_list = ["Seçiniz..."] + list(p_map.keys())
                            u_poz_name = st.selectbox("Pozisyon", p_list)
                            
                            if u_poz_name != "Seçiniz...":
                                u_poz_id = p_map[u_poz_name]
                                sevs = get_filtered("seviyeler", "pozisyon_id", u_poz_id)
                                s_map = {s['seviye_adi']: s['id'] for s in sevs}
                                s_list = ["Seçiniz..."] + list(s_map.keys())
                                u_sev_name = st.selectbox("Seviye", s_list)
                                if u_sev_name != "Seçiniz...":
                                    u_sev_id = s_map[u_sev_name]

                        if st.form_submit_button("Sürüm Güncelle ve Arşivle"):
                            simdi = datetime.now().isoformat()
                            
                            # 1. ESKİ SÜRÜMÜN BİTİŞ TARİHİNİ GÜNCELLE
                            if v:
                                supabase.table("aday_versiyonlar").update({"bitis_tarihi": simdi}).eq("id", v['id']).execute()
                            
                            # 2. YENİ SÜRÜMÜ OLUŞTUR
                            new_v_res = supabase.table("aday_versiyonlar").insert({
                                "aday_id": aday['id'],
                                "ad_soyad": aday['ad_soyad'],
                                "kimlik_no": aday['kimlik_no'],
                                "telefon": u_tel,
                                "departman_id": d_map.get(u_dep_name) if u_dep_name != "Seçiniz..." else v['departman_id'],
                                "pozisyon_id": u_poz_id,
                                "seviye_id": u_sev_id,
                                "islemi_yapan": "Sistemsel", # İleride aktif kullanıcı adı gelecek
                                "baslangic_tarihi": simdi
                            }).execute()
                            
                            # 3. ANA TABLO REFERANSINI GÜNCELLE
                            new_v_id = new_v_res.data[0]['id']
                            supabase.table("adaylar").update({"guncel_versiyon_id": new_v_id}).eq("id", aday['id']).execute()
                            
                            st.success("Adayın yeni sürümü oluşturuldu ve geçmiş kayıt arşivlendi.")
                            st.rerun()
        else:
            st.info("Listelenecek aday bulunamadı.")
