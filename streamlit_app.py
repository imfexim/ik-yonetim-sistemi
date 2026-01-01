import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Yapılandırması (Geniş Mod)
st.set_page_config(page_title="İMFEXİM", layout="wide", initial_sidebar_state="expanded")

# 2. Üst Düzey Kurumsal CSS (Preline UI Standartları)
st.markdown("""
    <style>
    /* 1. Reset & Global Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 2. Sidebar (Sol Menü) Tasarımı */
    [data-testid="stSidebar"] {
        border-right: 1px solid #F3F4F6 !important;
        padding-top: 2rem !important;
    }
    .nav-label {
        font-size: 11px; font-weight: 700; color: #9CA3AF;
        margin: 20px 0 10px 10px; text-transform: uppercase; letter-spacing: 0.05em;
    }

    /* 3. Başlıklar ve Metinler */
    h1, h2, h3, h4, p, label, span {
        color: #1F2937 !important; /* Koyu Gri/Siyah */
        font-weight: 500 !important;
    }

    /* 4. Girdi Alanları (Siyah Kutuları Yok Etme) */
    div[data-baseweb="input"], div[data-baseweb="select"] > div, textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
        color: #1F2937 !important;
    }
    input { color: #1F2937 !important; background-color: #FFFFFF !important; }
    
    /* Focus durumu (Mavi Çizgi) */
    div[data-baseweb="input"]:focus-within {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }

    /* 5. Modern Kart Yapısı (Sistem Özeti İçin) */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); border-color: #2563EB; }

    /* 6. Premium Butonlar */
    .stButton > button {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #1D4ED8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
    }

    /* 7. Tablo ve Data Editor Görünümü */
    [data-testid="stDataEditor"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 10px !important;
        background-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Navigasyon)
with st.sidebar:
    st.markdown("<h2 style='color:#2563EB; font-weight:700; padding-left:10px;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<div class='nav-label'>Genel Bakış</div>", unsafe_allow_html=True)
    page = st.radio("Ana Menü", ["Dashboard", "Organizasyon", "İşe Alım", "Çalışanlar"], label_visibility="collapsed")
    
    if page == "Organizasyon":
        st.markdown("<div class='nav-label'>Kaynaklar</div>", unsafe_allow_html=True)
        sub_page = st.radio("Alt Menü", ["Departmanlar", "Pozisyonlar", "Seviyeler"], label_visibility="collapsed")
    elif page == "İşe Alım":
        st.markdown("<div class='nav-label'>Süreç</div>", unsafe_allow_html=True)
        sub_page = st.radio("Alt Menü", ["Adaylar"], label_visibility="collapsed")
    else:
        sub_page = page

# --- SAYFA İÇERİKLERİ ---

if sub_page == "Dashboard":
    st.markdown("## Sistem Özeti")
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class='metric-card'><p style='color:#6B7280; font-size:14px;'>Toplam Aday</p><h2 style='margin:0;'>3</h2></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class='metric-card'><p style='color:#6B7280; font-size:14px;'>Aktif Çalışan</p><h2 style='margin:0;'>2</h2></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class='metric-card'><p style='color:#6B7280; font-size:14px;'>Departman Sayısı</p><h2 style='margin:0;'>10</h2></div>""", unsafe_allow_html=True)

elif sub_page == "Adaylar":
    st.markdown("## Aday Takip Sistemi")
    t1, t2 = st.tabs(["➕ Yeni Aday Ekle", "📋 Güncel Aday Havuzu"])
    
    with t1:
        st.markdown("<br>", unsafe_allow_html=True)
        # Formu beyaz bir kartın içine alalım
        with st.container():
            st.text_input("Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
            st.text_input("Kimlik No", placeholder="11 haneli TC No")
            st.button("Havuza Ekle")

    with t2:
        # Örnek DataTable (Görünüm testi için)
        df = pd.DataFrame({"Aday": ["Ahmet Y.", "Mehmet K."], "Süreç": ["Mülakat", "Teknik Test"]})
        st.data_editor(df, use_container_width=True, hide_index=True)
