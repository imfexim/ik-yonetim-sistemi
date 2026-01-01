import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Yapılandırması
st.set_page_config(
    page_title="İM-FEXİM İK Yönetim", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- OKUNABİLİR KURUMSAL TEMA (CSS) ---
st.markdown("""
    <style>
    /* Ana Arka Plan: Saf Beyaz */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Ana Metinler: Koyu Antrasit (Okunabilirliği artırır) */
    html, body, [class*="css"], .stMarkdown, p, span {
        color: #333333 !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Başlıklar: Daha net ve güçlü antrasit */
    h1, h2, h3 {
        color: #1A1A1A !important;
        font-weight: 700 !important;
    }

    /* Alt Başlıklar ve Açıklamalar: Orta-Koyu Gri */
    .stCaption, p {
        color: #555555 !important;
    }

    /* Yan Menü (Sidebar): Hafif Kontrastlı Gri */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #EDEDED;
    }

    /* Metrik Kartları: Belirgin Çerçeve */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #DDE1E6;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    /* Metrik Etiketleri: Koyu Gri */
    div[data-testid="stMetricLabel"] > div {
        color: #555555 !important;
        font-weight: 500 !important;
        font-size: 16px !important;
    }
    
    /* Metrik Değerleri: Siyah-Antrasit */
    div[data-testid="stMetricValue"] > div {
        color: #1A1A1A !important;
        font-size: 32px !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Başlık ve Açıklama
st.title("🏢 İM-FEXİM İK Yönetim Paneli")
st.markdown("Operasyonel Veri ve Personel Takip Sistemi")
st.divider()

# 4. Veri Çekme (Hata korumalı)
def load_data():
    try:
        res = supabase.table("Personel").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df = load_data()

# 5. Metrik Kartları (Net ve Okunabilir)
if not df.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Kayıt", len(df))
    m2.metric("Benzersiz Personel", df['personel_id'].nunique() if 'personel_id' in df.columns else 0)
    m3.metric("Sistem Durumu", "Aktif ✅")

st.success("Yazı tonları koyulaştırıldı. Artık her şey net okunuyor olmalı.")
