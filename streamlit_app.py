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
   # Test: Tabloyu okumayı dene
try:
    # 'personel' olan yeri 'Personel' olarak değiştirdik
    res = supabase.table("Personel").select("*").execute()
    st.success("📊 Veriler başarıyla çekildi!")
    
    if res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(df)
    else:
        st.info("Tablo bulundu ama içinde hiç veri yok.")
except Exception as e:
    st.error(f"Veri çekme hatası: {e}")
else:
    st.warning("⚠️ Lütfen Streamlit Secrets ayarlarına SUPABASE_URL ve SUPABASE_KEY ekleyin.")
