import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu (Preline Standartları)
st.set_page_config(page_title="İM-FEXİM Admin", layout="wide", initial_sidebar_state="expanded")

# 2. Squadbase & Preline UI Stil Paketi (Zorunlu Beyaz ve Keskin Siyah)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Reset */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar - Ultra Minimalist */
    [data-testid="stSidebar"] {
        border-right: 1px solid #F2F4F7 !important;
        width: 260px !important;
    }
    .nav-section-title {
        font-size: 11px; font-weight: 700; color: #98A2B3;
        margin: 25px 0 10px 20px; text-transform: uppercase; letter-spacing: 1px;
    }

    /* Başlıklar */
    h1, h2, h3 { color: #101828 !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
    p, label, span { color: #475467 !important; font-size: 14px !important; }

    /* Squadbase Tarzı Metrik Kartları */
    .stat-card {
        background: #FFFFFF;
        border: 1px solid #EAECF0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
    }
    .stat-value { font-size: 28px; font-weight: 700; color: #101828; margin-top: 5px; }

    /* Input Alanları - Siyahlığı Yok Et, Sadece Alt Çizgi veya İnce Border */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D0D5DD !important;
        border-radius: 8px !important;
        color: #101828 !important;
        height: 42px !important;
    }
    input { background-color: transparent !important; color: #101828 !important; }
    
    /* Butonlar - Minimalist Blue */
    .stButton > button {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #2563EB !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        width: auto !important;
    }
    .stButton > button:hover { background-color: #1D4ED8 !important; border-color: #1D4ED8 !important; }

    /* DataTable (Squadbase Excel Görünümü) */
    [data-testid="stDataEditor"] {
        border: 1px solid #EAECF0 !important;
        border-radius: 12px !important;
    }
    
    /* Gizlenen Elementler */
    [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 3. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 4. Sayfa Yönetimi
if 'active_page' not in st.session_state: st.session_state.active_page = "Dashboard"

# 5. Sidebar Navigasyon (Squadbase Minimalist)
with st.sidebar:
    st.markdown("<div style='padding: 10px 20px;'><h3 style='color:#2563EB; margin:0;'>İM-FEXİM</h3></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='nav-section-title'>Genel</div>", unsafe_allow_html=True)
    if st.button("📊 Dashboard", key="btn_dash", use_container_width=True): st.session_state.active_page = "Dashboard"
    
    st.markdown("<div class='nav-section-title'>Organizasyon</div>", unsafe_allow_html=True)
    if st.button("🏢 Departmanlar", use_container_width=True): st.session_state.active_page = "Departmanlar"
    if st.button("👔 Pozisyonlar", use_container_width=True): st.session_state.active_page = "Pozisyonlar"
    
    st.markdown("<div class='nav-section-title'>İnsan Kaynakları</div>", unsafe_allow_html=True)
    if st.button("👤 Aday Havuzu", use_container_width=True): st.session_state.active_page = "Adaylar"
    if st.button("👥 Çalışan Listesi", use_container_width=True): st.session_state.active_page = "Personeller"

# --- SAYFA İÇERİKLERİ ---

if st.session_state.active_page == "Dashboard":
    st.markdown("## Dashboard")
    st.markdown("Sistem genelindeki güncel veriler.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='stat-card'><p style='margin:0;'>Toplam Aday</p><div class='stat-value'>3</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='stat-card'><p style='margin:0;'>Aktif Çalışan</p><div class='stat-value'>2</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='stat-card'><p style='margin:0;'>Departmanlar</p><div class='stat-value'>10</div></div>", unsafe_allow_html=True)

elif st.session_state.active_page == "Adaylar":
    st.markdown("## Aday Takip Sistemi")
    t1, t2 = st.tabs(["➕ Yeni Aday", "📋 Aday Havuzu (Excel Görünümü)"])
    
    with t1:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container():
            c1, c2 = st.columns(2)
            ad_soyad = c1.text_input("Ad Soyad", placeholder="Ahmet Yılmaz")
            tc_no = c2.text_input("Kimlik No", placeholder="11 haneli TC")
            st.button("Havuza Kaydet")

    with t2:
        st.markdown("<br>", unsafe_allow_html=True)
        # Squadbase Tarzı DataTable
        res = supabase.table("adaylar").select("ad_soyad, kimlik_no, olusturma_tarihi").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df.columns = ["Aday Adı", "Kimlik No", "Kayıt Tarihi"]
            st.data_editor(df, use_container_width=True, hide_index=True, disabled=True)
        else:
            st.info("Havuz boş.")

elif st.session_state.active_page == "Departmanlar":
    st.markdown("## Departmanlar")
    res = supabase.table("departmanlar").select("departman_adi").execute()
    if res.data:
        st.data_editor(pd.DataFrame(res.data), use_container_width=True, hide_index=True)
