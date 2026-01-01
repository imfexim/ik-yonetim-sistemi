import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İMFEXİM Admin", layout="wide", initial_sidebar_state="expanded")

# 2. Üst Düzey Minimalist CSS (Preline UI Standartları)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Reset */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sol Sidebar - Ultra Minimalist */
    [data-testid="stSidebar"] { border-right: 1px solid #F2F4F7 !important; width: 240px !important; }
    
    /* Sol Menü Butonları */
    .stButton > button {
        background-color: transparent !important;
        color: #475467 !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        font-weight: 500 !important;
        padding: 10px 15px !important;
    }
    .stButton > button:hover { background-color: #F9FAFB !important; color: #101828 !important; }
    
    /* Aktif Menü Vurgusu */
    .active-menu > div > button { background-color: #F2F4F7 !important; color: #101828 !important; font-weight: 600 !important; }

    /* Üst Sekme (Alt Menü) Tasarımı */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #FFFFFF !important;
        border-bottom: 1px solid #EAECF0 !important;
        gap: 30px !important;
        padding-top: 10px !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500 !important;
        color: #667085 !important;
        padding-bottom: 12px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #101828 !important;
        border-bottom: 2px solid #101828 !important;
    }

    /* Input & Form Alanları - Bembeyaz & Keskin */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D0D5DD !important;
        border-radius: 8px !important;
    }
    input { color: #101828 !important; }
    
    /* İşlem Butonları - Siyah Minimalist */
    .main-action-btn > div > button {
        background-color: #101828 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        padding: 8px 24px !important;
    }

    /* DataTable Görünümü */
    [data-testid="stDataEditor"] { border: 1px solid #EAECF0 !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Bağlantı (Supabase)
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 4. State Yönetimi
if 'main_page' not in st.session_state: st.session_state.main_page = "Dashboard"

# 5. SOL MENÜ (Sabit)
with st.sidebar:
    st.markdown("<div style='padding: 20px 10px;'><h3 style='color:#101828; margin:0;'>İM-FEXİM</h3></div>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:11px; font-weight:700; color:#98A2B3; margin:20px 10px 10px;'>YÖNETİM</p>", unsafe_allow_html=True)
    
    if st.button("Dashboard", use_container_width=True): st.session_state.main_page = "Dashboard"
    if st.button("Organizasyon", use_container_width=True): st.session_state.main_page = "Organizasyon"
    if st.button("İşe Alım", use_container_width=True): st.session_state.main_page = "İşe Alım"
    if st.button("Çalışanlar", use_container_width=True): st.session_state.main_page = "Çalışanlar"

# --- SAĞ TARAF (ANA İÇERİK) ---

# A. DASHBOARD
if st.session_state.main_page == "Dashboard":
    st.title("Dashboard")
    st.markdown("Sistem genelindeki güncel durum ve metrikler.")
    # (Metrik kartları buraya gelecek)

# B. ORGANİZASYON (Alt Menüler Üstte Sekme Olarak)
elif st.session_state.main_page == "Organizasyon":
    st.title("Organizasyon Yapısı")
    tab_dep, tab_poz, tab_sev = st.tabs(["Departmanlar", "Pozisyonlar", "Seviyeler"])
    
    with tab_dep:
        st.markdown("### Departman Listesi")
        # (Departman Ekleme/Listeleme Fonksiyonları)

# C. İŞE ALIM (Alt Menüler Üstte Sekme Olarak)
elif st.session_state.main_page == "İşe Alım":
    st.title("İşe Alım Süreçleri")
    tab_aday_ekle, tab_havuz = st.tabs(["Aday Ekle", "Aday Havuzu"])
    
    with tab_aday_ekle:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container():
            c1, c2 = st.columns(2)
            ad = c1.text_input("Ad Soyad", placeholder="Zorunlu alan")
            tc = c2.text_input("Kimlik No", placeholder="11 haneli")
            st.markdown('<div class="main-action-btn">', unsafe_allow_html=True)
            if st.button("Kaydet ve Havuza At"):
                st.success("Kayıt Başarılı")
            st.markdown('</div>', unsafe_allow_html=True)

# D. ÇALIŞANLAR
elif st.session_state.main_page == "Çalışanlar":
    st.title("Çalışan Portalı")
    # (Personel listesi buraya gelecek)
