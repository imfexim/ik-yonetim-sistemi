import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Ayarları (Beyaz Arka Plan Odaklı)
st.set_page_config(
    page_title="İM-FEXİM İK Yönetim", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- GÖRSEL DÜZENLEME (CSS) ---
st.markdown("""
    <style>
    /* Uygulamanın ana arka planını beyaz yapar */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Yan menüyü (sidebar) hafif gri yaparak ana ekrandan ayırır */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E9ECEF;
    }

    /* Kartların ve metriklerin beyaz zemin üzerinde şık durmasını sağlar */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #F0F0F0;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    # Streamlit Secrets'tan güvenli çekim
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Başlık Alanı
st.title("🏢 İM-FEXİM İK Yönetim Paneli")
st.markdown("<p style='color: #6c757d;'>Operasyonel Veri ve Personel Takip Sistemi</p>", unsafe_allow_html=True)
st.divider()

# 4. Veri Yükleme
def load_data():
    try:
        res = supabase.table("Personel").select("*").execute()
        data = pd.DataFrame(res.data)
        if not data.empty:
            data['islem_tarihi'] = pd.to_datetime(data['islem_tarihi'], errors='coerce', utc=True)
        return data
    except Exception as e:
        st.error(f"Veri yüklenemedi: {e}")
        return pd.DataFrame()

df = load_data()

# 5. Üst Bilgi (Metrikler)
if not df.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Kayıt", len(df))
    m2.metric("Benzersiz Personel", df['personel_id'].nunique())
    m3.metric("Sistem Durumu", "Aktif ✅")

st.info("İskelet hazır. Beyaz arka plan ve temiz yerleşim aktif.")
