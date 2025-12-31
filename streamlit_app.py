import streamlit as st
from supabase import create_client
import pandas as pd

# 1. TEMİZLİK VE DOĞRULAMA FONKSİYONU
def get_clean_secret(key_name):
    if key_name in st.secrets:
        # Değeri al, boşlukları sil, başındaki/sonundaki tırnakları at
        raw_value = st.secrets[key_name]
        return raw_value.strip().replace('"', '').replace("'", "")
    return None

# 2. AYARLARI ÇEK
URL = get_clean_secret("SUPABASE_URL")
KEY = get_clean_secret("SUPABASE_KEY")

# 3. BAĞLANTIYI BAŞLAT
@st.cache_resource
def init_connection():
    if not URL or not URL.startswith("https://"):
        st.error(f"❌ Hatalı URL Tespit Edildi: '{URL}'. URL mutlaka 'https://' ile başlamalıdır.")
        st.stop()
    
    try:
        # En temiz haliyle gönderiyoruz
        return create_client(URL, KEY)
    except Exception as e:
        st.error(f"❌ Supabase Bağlantı Hatası: {e}")
        st.stop()

# Uygulama akışı
if URL and KEY:
    supabase = init_connection()
    st.success("✅ Supabase bağlantısı başarıyla kuruldu!")
    
    # Test: Tabloyu okumayı dene
    try:
        res = supabase.table("Personel").select("*").limit(5).execute()
        st.write("📊 Personel verileri hazır:")
        st.dataframe(res.data)
    except Exception as e:
        st.warning(f"Bağlantı tamam ama veriler çekilemedi: {e}")
else:
    st.warning("⚠️ Lütfen Streamlit Secrets ayarlarına SUPABASE_URL ve SUPABASE_KEY ekleyin.")
