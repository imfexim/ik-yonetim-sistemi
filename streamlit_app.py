import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="IMFEXIM Admin", layout="wide", initial_sidebar_state="expanded")

# 2. Paylaştığınız Stillerle Güçlendirilmiş Preline CSS
st.markdown("""
    <style>
    /* Preline UI Core & Tailwind v4 Variables */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --default-font-family: 'Inter', ui-sans-serif, system-ui, sans-serif;
        --spacing: 0.25rem;
        --text-xs: 0.75rem;
        --text-xs--line-height: 1rem;
        --font-weight-medium: 500;
        
        /* Preline oklch Renk Paleti */
        --color-gray-50: oklch(.984 .003 247.858);
        --color-gray-100: oklch(.967 .003 264.542);
        --color-gray-800: oklch(.269 .018 262.07);
        --primary-blue: oklch(.585 .233 257.138); /* Preline Blue */
    }

    /* Reset & Base Styles */
    *, :after, :before {
        box-sizing: border-box;
        border: 0 solid;
        margin: 0;
        padding: 0;
    }

    .stApp, [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        font-family: var(--default-font-family) !important;
        line-height: 1.5;
    }

    /* Sidebar - .uppercase, .text-xs, .font-medium Uygulaması */
    [data-testid="stSidebar"] {
        border-right: 1px solid var(--color-gray-100) !important;
        width: 260px !important;
    }
    
    .nav-section-title {
        display: block;
        margin-bottom: calc(var(--spacing) * 2);
        padding-inline-start: calc(var(--spacing) * 5);
        font-size: var(--text-xs);
        line-height: var(--text-xs--line-height);
        font-weight: var(--font-weight-medium);
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Menü Butonları - .duration-300 ve Hover Etkisi */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: var(--color-gray-800) !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        font-weight: 500 !important;
        padding: calc(var(--spacing) * 3) calc(var(--spacing) * 5) !important;
        transition: all 0.3s ease; /* .duration-300 */
        border-radius: 0px !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: var(--color-gray-50) !important;
        color: var(--primary-blue) !important;
    }

    /* Form Elemanları & Tabs */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid var(--color-gray-100) !important;
    }
    
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid var(--color-gray-100) !important;
        border-radius: 8px !important;
    }

    /* Aksiyon Butonu - Preline Primary */
    .stButton > button[kind="primary"] {
        background-color: var(--color-gray-800) !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 4. Sayfa Kontrolü
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# --- SIDEBAR (Sizin Stil Değişkenlerinizle) ---
with st.sidebar:
    st.markdown("<div style='padding: 24px 20px;'><h3 style='font-weight:700; color:var(--color-gray-800);'>IMFEXIM</h3></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='nav-section-title'>Yönetim</div>", unsafe_allow_html=True)
    if st.button("Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
    
    st.markdown("<div class='nav-section-title'>Organizasyon</div>", unsafe_allow_html=True)
    if st.button("Departmanlar", use_container_width=True): st.session_state.page = "Departmanlar"
    if st.button("Pozisyonlar", use_container_width=True): st.session_state.page = "Pozisyonlar"
    
    st.markdown("<div class='nav-section-title'>İK Süreçleri</div>", unsafe_allow_html=True)
    if st.button("Aday Havuzu", use_container_width=True): st.session_state.page = "Adaylar"
    if st.button("Çalışan Listesi", use_container_width=True): st.session_state.page = "Personeller"

# --- ANA İÇERİK ---
if st.session_state.page == "Dashboard":
    st.title("Genel Durum")
    st.markdown("Sistem üzerindeki verilerin anlık özeti.")

elif st.session_state.page == "Adaylar":
    st.title("Aday Takip Sistemi")
    t1, t2 = st.tabs(["Aday Ekle", "Güncel Liste"])
    # (Buraya önceki fonksiyonel kodlar gelecek)
