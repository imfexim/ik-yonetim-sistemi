import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM Admin", layout="wide", initial_sidebar_state="expanded")

# 2. Squadbase / Ultra-Minimalist CSS (Mavi Renk Temizlendi)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Reset - Bembeyaz Zemin */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar - Ince Ayırıcı ve Temiz Yazılar */
    [data-testid="stSidebar"] {
        border-right: 1px solid #F2F4F7 !important;
    }
    .nav-section-title {
        font-size: 11px; font-weight: 700; color: #98A2B3;
        margin: 25px 0 10px 20px; text-transform: uppercase; letter-spacing: 1px;
    }

    /* Başlıklar - Keskin Siyah */
    h1, h2, h3 { color: #101828 !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
    p, label, span { color: #475467 !important; font-size: 14px !important; }

    /* Metrik Kartları - Ince Gri Çizgi */
    .stat-card {
        background: #FFFFFF;
        border: 1px solid #EAECF0;
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }
    .stat-value { font-size: 32px; font-weight: 700; color: #101828; margin-top: 5px; }

    /* Input Alanları - Siyahlığı Tamamen Yok Et (Beyaz Zemin, Ince Gri Border) */
    div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D0D5DD !important;
        border-radius: 6px !important;
        color: #101828 !important;
    }
    input { background-color: transparent !important; color: #101828 !important; }
    
    /* Butonlar - Siyah & Minimalist (Mavi Yerine Siyah) */
    .stButton > button {
        background-color: #101828 !important; /* Mavi yerine Koyu Siyah */
        color: #FFFFFF !important;
        border-radius: 6px !important;
        border: 1px solid #101828 !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #1D2939 !important;
        border-color: #1D2939 !important;
        box-shadow: 0 4px 12px rgba(16, 24, 40, 0.1);
    }

    /* Tablar (Aday Takip Sekmeleri) */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #EAECF0; }
    .stTabs [data-baseweb="tab"] { color: #667085; font-weight: 500; }
    .stTabs [aria-selected="true"] { color: #101828 !important; border-bottom-color: #101828 !important; }

    /* DataTable */
    [data-testid="stDataEditor"] { border: 1px solid #EAECF0 !important; border-radius: 8px !important; }
    
    /* Gizlenen Elementler */
    [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Siyah-Beyaz Navigasyon)
with st.sidebar:
    st.markdown("<div style='padding: 20px;'><h3 style='color:#101828; margin:0;'>İM-FEXİM</h3></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='nav-section-title'>Genel</div>", unsafe_allow_html=True)
    if st.button("Dashboard", key="nav_dash", use_container_width=True): st.session_state.active_page = "Dashboard"
    
    st.markdown("<div class='nav-section-title'>Organizasyon</div>", unsafe_allow_html=True)
    if st.button("Departmanlar", use_container_width=True): st.session_state.active_page = "Departmanlar"
    if st.button("Pozisyonlar", use_container_width=True): st.session_state.active_page = "Pozisyonlar"
    
    st.markdown("<div class='nav-section-title'>İnsan Kaynakları</div>", unsafe_allow_html=True)
    if st.button("Aday Havuzu", use_container_width=True): st.session_state.active_page = "Adaylar"
    if st.button("Çalışan Listesi", use_container_width=True): st.session_state.active_page = "Personeller"

# --- SAYFA İÇERİKLERİ ---
# (Önceki işlevsel kodunu buraya ekleyebilirsin, stil artık yukarıdaki CSS ile kontrol ediliyor)
