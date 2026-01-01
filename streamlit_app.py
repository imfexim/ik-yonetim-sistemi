import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM Admin", layout="wide")

# 2. ULTRA-BEYAZ VE MİNAMALİST BUTON CSS (Siyahlığı Kökten Siler)
st.markdown("""
    <style>
    /* Global Beyaz Zemin Zorlaması */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* BUTONLARI BEYAZLAT (Siyah Buton Sorunu Çözümü) */
    div.stButton > button {
        background-color: #FFFFFF !important; /* Arka plan beyaz */
        color: #111827 !important;           /* Yazı siyah */
        border: 1px solid #D1D5DB !important; /* İnce gri çerçeve */
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }
    
    /* Buton Hover (Üzerine Gelince Hafif Gri) */
    div.stButton > button:hover {
        background-color: #F9FAFB !important;
        border-color: #111827 !important;
        color: #111827 !important;
    }

    /* Form Giriş Alanları (Dropbox & Inbox) */
    input, select, textarea, div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #D1D5DB !important;
    }

    /* Tablolar */
    div[data-testid="stTable"] table { background-color: #FFFFFF !important; color: #000000 !important; }
    th { background-color: #F9FAFB !important; color: #000000 !important; }
    td { border-bottom: 1px solid #F3F4F6 !important; }

    /* Sidebar Hiyerarşisi */
    [data-testid="stSidebar"] { border-right: 1px solid #F3F4F6 !important; }
    .nav-header { font-size: 11px; font-weight: 700; color: #9CA3AF; margin: 20px 0 10px 15px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 3. Bağlantı (Supabase)
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 4. State Yönetimi
if 'main_page' not in st.session_state: st.session_state.main_page = "Dashboard"

# --- SOL MENÜ (ANA KATEGORİLER) ---
with st.sidebar:
    st.markdown("<h3 style='padding-left:15px; font-weight:700;'>İM-FEXİM</h3>", unsafe_allow_html=True)
    st.markdown("<div class='nav-header'>Yönetim Paneli</div>", unsafe_allow_html=True)
    if st.button("📊 Dashboard", use_container_width=True): st.session_state.main_page = "Dashboard"
    if st.button("🏢 Organizasyon", use_container_width=True): st.session_state.main_page = "Organizasyon"
    if st.button("👤 İşe Alım (ATS)", use_container_width=True): st.session_state.main_page = "ATS"
    if st.button("👥 Çalışanlar (HRM)", use_container_width=True): st.session_state.main_page = "HRM"

# --- YARDIMCI FONKSİYONLAR ---
def fetch_data(table, select="*"):
    res = supabase.table(table).select(select).execute()
    return res.data if res.data else []

# --- SAĞ TARAF (ÜST SEKME VE FONKSİYONLAR) ---

if st.session_state.main_page == "Dashboard":
    st.title("Sistem Özeti")
    st.write("Dashboard metrikleri burada yer alacak.")

elif st.session_state.main_page == "Organizasyon":
    st.title("Organizasyon Yapılandırması")
    tab1, tab2, tab3 = st.tabs(["Departmanlar", "Pozisyonlar", "Seviyeler"])
    
    with tab1: # DEPARTMAN İŞLEMLERİ
        with st.form("dep_add"):
            d_ad = st.text_input("Yeni Departman")
            if st.form_submit_button("Kaydet"):
                supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute()
                st.rerun()
        st.table(pd.DataFrame(fetch_data("departmanlar"))[["departman_adi"]])

    with tab2: # POZİSYON VE OTOMATİK 6 SEVİYE
        deps = fetch_data("departmanlar")
        d_map = {d['departman_adi']: d['id'] for d in deps}
        with st.form("poz_add"):
            s_dep = st.selectbox("Departman", list(d_map.keys()))
            p_ad = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Pozisyonu ve 6 Seviyeyi Oluştur"):
                p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_ad}).execute()
                p_id = p_res.data[0]['id']
                # Otomatik Seviye Üretimi
                codes = ["J1", "J2", "M1", "M2", "M3", "S"]
                supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_ad} {c}", "seviye_kodu": c} for c in codes]).execute()
                st.rerun()

    with tab3: # SEVİYE LİSTELEME
        res = supabase.table("seviyeler").select("seviye_adi, pozisyonlar(pozisyon_adi)").execute()
        if res.data:
            st.table(pd.DataFrame([{"Seviye": r['seviye_adi'], "Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res.data]))

elif st.session_state.main_page == "ATS":
    st.title("Aday Takip ve Versiyonlama")
    tab_ekle, tab_liste = st.tabs(["Yeni Aday", "Aday Havuzu"])
    
    with tab_ekle:
        with st.form("aday_form"):
            ad = st.text_input("Ad Soyad")
            tc = st.text_input("Kimlik No")
            if st.form_submit_button("Havuza Kaydet"):
                a_res = supabase.table("adaylar").insert({"ad_soyad": ad, "kimlik_no": tc}).execute()
                a_id = a_res.data[0]['id']
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": ad, "kimlik_no": tc, "ise_alim_sureci": "aday havuzu",
                    "baslangic_tarihi": datetime.now().isoformat()
                }).execute()
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.rerun()

    with tab_liste:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*)").execute()
        if res.data:
            st.table(pd.DataFrame([{"Aday": r['ad_soyad'], "Süreç": r['aday_versiyonlar']['ise_alim_sureci']} for r in res.data if r['aday_versiyonlar']]))

elif st.session_state.main_page == "HRM":
    st.title("Personel Yönetimi")
    # Personel listesi ve versiyon detayları...
    st.table(pd.DataFrame(fetch_data("personeller"))[["ad_soyad", "kimlik_no"]])
