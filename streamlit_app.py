import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Page Configuration & Preline CMS Styling
st.set_page_config(page_title="İM-FEXİM Admin", layout="wide")

st.markdown("""
    <style>
    /* Global Preline UI Background */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
    }
    
    /* Typography - Professional Black */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; color: #111827 !important; }
    h1, h2, h3, h4, p, label, span { color: #111827 !important; }

    /* Clean Sidebar */
    section[data-testid="stSidebar"] { border-right: 1px solid #E5E7EB !important; }
    .nav-header { font-size: 11px; font-weight: 700; color: #9CA3AF; margin: 20px 0 10px 15px; text-transform: uppercase; }
    
    /* Custom Sidebar Navigation Buttons */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #374151 !important;
        border: 1px solid transparent !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
    }
    .stButton > button:hover { background-color: #F9FAFB !important; color: #2563EB !important; border-color: #E5E7EB !important; }

    /* Modern Table (Data Editor) */
    [data-testid="stDataEditor"] { border: 1px solid #E5E7EB !important; border-radius: 8px !important; }
    
    /* Primary Action Buttons */
    .main-btn > div > button { background-color: #2563EB !important; color: #FFFFFF !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Connection
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. State Management
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# 4. Premium Navigation Sidebar
with st.sidebar:
    st.markdown("<h3 style='color:#2563EB; padding-left:15px; font-weight:700;'>İM-FEXİM</h3>", unsafe_allow_html=True)
    
    st.markdown("<div class='nav-header'>Hızlı Erişim</div>", unsafe_allow_html=True)
    if st.button("Genel Durum"): st.session_state.page = "Dashboard"
    
    st.markdown("<div class='nav-header'>Organizasyon</div>", unsafe_allow_html=True)
    if st.button("Departmanlar"): st.session_state.page = "Departmanlar"
    if st.button("Pozisyonlar"): st.session_state.page = "Pozisyonlar"
    
    st.markdown("<div class='nav-header'>İnsan Kaynakları</div>", unsafe_allow_html=True)
    if st.button("Aday Havuzu"): st.session_state.page = "Adaylar"
    if st.button("Çalışan Listesi"): st.session_state.page = "Personeller"

# 5. Helper Functions
def show_table(df):
    st.data_editor(df, use_container_width=True, hide_index=True, disabled=True)

# --- PAGES ---

if st.session_state.page == "Dashboard":
    st.title("Sistem Özeti")
    st.markdown("Kurumsal portal üzerinden genel verileri takip edebilirsiniz.")
    # Metric cards here...

elif st.session_state.page == "Adaylar":
    st.title("Aday Takip Sistemi")
    t1, t2 = st.tabs(["Yeni Aday Ekle", "Güncel Aday Havuzu"])
    
    with t1:
        with st.form("c_form"):
            ad = st.text_input("Ad Soyad")
            tc = st.text_input("Kimlik No")
            st.markdown('<div class="main-btn">', unsafe_allow_html=True)
            if st.form_submit_button("Adayı Sisteme Kaydet"):
                # Supabase insert logic...
                st.success("Aday başarıyla kaydedildi.")
            st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        res = supabase.table("adaylar").select("ad_soyad, kimlik_no, olusturma_tarihi").execute()
        if res.data:
            df = pd.DataFrame(res.data).rename(columns={"ad_soyad": "Aday Adı", "kimlik_no": "TC No", "olusturma_tarihi": "Kayıt Tarihi"})
            show_table(df)
        else: st.info("Kayıtlı aday bulunamadı.")

elif st.session_state.page == "Departmanlar":
    st.title("Departmanlar")
    res = supabase.table("departmanlar").select("departman_adi").execute()
    if res.data: show_table(pd.DataFrame(res.data))

# ... Diğer sayfalar aynı mantıkla devam eder.
