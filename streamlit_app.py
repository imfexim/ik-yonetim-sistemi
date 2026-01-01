import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="IMFEXIM Admin", layout="wide")

# 2. ULTRA DARK PREMIUM CSS (Tamamen Siyah & Beyaz Kontrast)
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    /* Global Karanlık Arka Plan */
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    /* Tüm Yazıları Beyaza Zorla */
    h1, h2, h3, h4, p, span, label, div {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sol Menü Butonları (Dark & Minimal) */
    section[data-testid="stSidebar"] button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 12px !important;
        border-radius: 4px !important;
        margin-bottom: 5px !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #111111 !important;
        border-color: #FFFFFF !important;
    }

    /* Input Alanları (Siyah Zemin - Beyaz Border) */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #000000 !important;
        border: 1px solid #333333 !important;
        color: #FFFFFF !important;
    }
    input { color: #FFFFFF !important; }

    /* Ana Aksiyon Butonları */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    /* Tablolar (Karanlık Mod Uyumu) */
    div[data-testid="stTable"] table { background-color: #000000 !important; color: #FFFFFF !important; }
    th { background-color: #111111 !important; color: #FFFFFF !important; border-bottom: 2px solid #333333 !important; }
    td { border-bottom: 1px solid #222222 !important; }

    /* Üst Sekmeler (Tabs) */
    .stTabs [data-baseweb="tab-list"] { background-color: #000000 !important; }
    .stTabs [data-baseweb="tab"] { color: #888888 !important; }
    .stTabs [aria-selected="true"] { color: #FFFFFF !important; border-bottom: 2px solid #FFFFFF !important; }
    
    .nav-header { font-size: 10px; font-weight: 800; color: #555555; margin: 20px 0 10px 15px; text-transform: uppercase; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# --- SOL MENÜ (İkonlu) ---
with st.sidebar:
    st.markdown("<h2 style='padding-left:15px; font-weight:900; letter-spacing: -1px;'>IMFEXIM</h2>", unsafe_allow_html=True)
    st.markdown("<div class='nav-header'>CORE</div>", unsafe_allow_html=True)
    
    if st.button("  DASHBOARD", use_container_width=True): st.session_state.page = "Dashboard"
    if st.button("  ORGANİZASYON", use_container_width=True): st.session_state.page = "Organizasyon"
    
    st.markdown("<div class='nav-header'>RECRUITMENT</div>", unsafe_allow_html=True)
    if st.button("User-Tie  İŞE ALIM", use_container_width=True): st.session_state.page = "ATS"
    if st.button("  PERSONEL", use_container_width=True): st.session_state.page = "HRM"

# --- ANA İÇERİK ---

if st.session_state.page == "Dashboard":
    st.markdown("<h1>Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888888 !important;'>Gerçek zamanlı sistem analitiği.</p>", unsafe_allow_html=True)
    
    # Minimalist Metrik Kartları
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Aday", "3", delta_color="normal")
    c2.metric("Aktif Çalışan", "2")
    c3.metric("Departmanlar", "10")

elif st.session_state.page == "Organizasyon":
    st.markdown("<h1>Organizasyon</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["Departman", "Pozisyon", "Kariyer"])
    
    with t1:
        with st.form("d_form"):
            name = st.text_input("Departman Adı")
            if st.form_submit_button("EKLE"):
                supabase.table("departmanlar").insert({"departman_adi": name}).execute()
                st.rerun()

elif st.session_state.page == "ATS":
    st.markdown("<h1>Aday Takip ve Versiyonlama</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Yeni Kayıt", "Havuz"])
    
    with t1:
        with st.form("c_form"):
            ad = st.text_input("Ad Soyad")
            tc = st.text_input("Kimlik No")
            if st.form_submit_button("HAVUZA EKLE"):
                # Versiyonlama Kurgusu (SCD Type 2)
                res = supabase.table("adaylar").insert({"ad_soyad": ad, "kimlik_no": tc}).execute()
                a_id = res.data[0]['id']
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": ad, "kimlik_no": tc, "ise_alim_sureci": "aday havuzu",
                    "baslangic_tarihi": datetime.now().isoformat()
                }).execute()
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.rerun()

    with t2:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*)").execute()
        if res.data:
            df = pd.DataFrame([{"Aday": r['ad_soyad'], "Durum": r['aday_versiyonlar']['ise_alim_sureci']} for r in res.data if r['aday_versiyonlar']])
            st.table(df)
