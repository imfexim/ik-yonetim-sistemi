import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="IMFEXIM Admin", layout="wide", initial_sidebar_state="expanded")

# 2. Kompakt Preline CSS (Tailwind v4 Değişkenli)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --default-font-family: 'Inter', ui-sans-serif, system-ui, sans-serif;
        --spacing: 0.25rem;
        --text-xs: 0.8125rem; /* Biraz daha küçük font */
        --font-weight-medium: 500;
        --color-gray-50: #F9FAFB;
        --color-gray-100: #F3F4F6;
        --color-gray-800: #1F2937;
    }

    /* Global Reset */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        font-family: var(--default-font-family) !important;
    }

    /* Sidebar Genişlik ve Border */
    [data-testid="stSidebar"] {
        border-right: 1px solid var(--color-gray-100) !important;
        width: 240px !important;
    }
    
    /* Sidebar Başlık Alanı */
    .sidebar-brand {
        padding: calc(var(--spacing) * 5) calc(var(--spacing) * 5) calc(var(--spacing) * 3);
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: -0.02em;
        color: var(--color-gray-800);
    }

    /* Kategori Etiketleri (Küçültüldü ve Sıkılaştırıldı) */
    .nav-section-label {
        font-size: 10px; 
        font-weight: 700; 
        color: #9CA3AF;
        margin: calc(var(--spacing) * 4) 0 calc(var(--spacing) * 1) calc(var(--spacing) * 5);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* KOMPAKT BUTONLAR (Yükseklik ve Font Ayarı) */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #4B5563 !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        font-weight: 500 !important;
        font-size: var(--text-xs) !important; /* Daha küçük font */
        padding: calc(var(--spacing) * 2) calc(var(--spacing) * 5) !important; /* Yükseklik azaltıldı */
        margin: 0 !important;
        border-radius: 0px !important;
        transition: background-color 0.2s ease;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: var(--color-gray-100) !important;
        color: var(--color-gray-800) !important;
    }

    /* Buton Aralarındaki Boşluğu Sıfırla */
    [data-testid="stVerticalBlock"] > div {
        gap: 0px !important;
    }

    /* Üst Sekmeler (Daha İnce) */
    .stTabs [data-baseweb="tab"] {
        font-size: var(--text-xs) !important;
        padding-top: 8px !important;
        padding-bottom: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 4. Sayfa Kontrolü
if 'current_page' not in st.session_state: st.session_state.current_page = "Dashboard"

# --- SIDEBAR (Kompakt Tasarım) ---
with st.sidebar:
    st.markdown("<div class='sidebar-brand'>IMFEXIM</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='nav-section-label'>Analiz</div>", unsafe_allow_html=True)
    if st.button("Dashboard", use_container_width=True): st.session_state.current_page = "Dashboard"
    
    st.markdown("<div class='nav-section-label'>Kurumsal</div>", unsafe_allow_html=True)
    if st.button("Organizasyon", use_container_width=True): st.session_state.current_page = "Organizasyon"
    if st.button("İşe Alım", use_container_width=True): st.session_state.current_page = "İşe Alım"
    if st.button("Çalışanlar", use_container_width=True): st.session_state.current_page = "Çalışanlar"

# --- ANA İÇERİK ---
st.title(st.session_state.current_page)

if st.session_state.current_page == "Organizasyon":
    t1, t2, t3 = st.tabs(["Departmanlar", "Pozisyonlar", "Seviyeler"])
    with t1:
        st.write("Kompakt liste görünümü...")
