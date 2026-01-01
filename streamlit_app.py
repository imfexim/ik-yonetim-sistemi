import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Yapılandırması
st.set_page_config(
    page_title="İM-FEXİM İK Yönetim", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- TATLI GRİ VE BEYAZ TEMA (CSS) ---
st.markdown("""
    <style>
    /* Ana Arka Plan Beyaz */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Tüm metinleri tatlı bir gri yapar */
    html, body, [class*="css"], .stMarkdown, p, span {
        color: #4A4A4A !important;
        font-family: 'Inter', sans-serif;
    }

    /* Başlıkları bir tık daha belirgin ama yine gri tonda tutar */
    h1, h2, h3 {
        color: #2D2D2D !important;
        font-weight: 600 !important;
    }

    /* Yan Menü (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #FBFBFB;
        border-right: 1px solid #F0F0F0;
    }

    /* Metrik Kartları - Sade ve Gri Çerçeveli */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    /* Metrik etiketleri (Küçük yazılar) */
    div[data-testid="stMetricLabel"] > div {
        color: #8E8E8E !important;
        font-size: 14px !important;
    }
    
    /* Metrik değerleri (Büyük rakamlar) */
    div[data-testid="stMetricValue"] > div {
        color: #4A4A4A !important;
        font-size: 28px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı (Aynı kalıyor)
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. İçerik Alanı
st.title("İM-FEXİM İK Yönetim Paneli")
st.markdown("Personel verileri ve operasyonel süreç takip ekranı")
st.divider()

# 4. Veri Yükleme
def load_data():
    try:
        res = supabase.table("Personel").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df = load_data()

# 5. Görsel Metrikler
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Kayıtlı Personel", df['personel_id'].nunique())
    col2.metric("Toplam İşlem", len(df))
    col3.metric("Bekleyen Onay", "0")
    col4.metric("Sistem Durumu", "Aktif")

st.info("Yazı renkleri 'Tatlı Gri' olarak güncellendi ve metrik kartları sadeleştirildi.")
