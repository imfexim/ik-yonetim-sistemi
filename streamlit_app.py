import streamlit as st
from supabase import create_client
import pandas as pd

# Secrets'tan verileri çek ve görünmez boşlukları temizle
try:
    URL = st.secrets["SUPABASE_URL"].strip()
    KEY = st.secrets["SUPABASE_KEY"].strip()
except Exception as e:
    st.error("Secrets bulunamadı! Lütfen Streamlit ayarlarından SUPABASE_URL ve SUPABASE_KEY ekleyin.")
    st.stop()

# Bağlantı fonksiyonu
@st.cache_resource
def init_connection():
    try:
        # URL formatını kontrol et
        if not URL.startswith("https://"):
            st.error(f"Hatalı URL Formatı: {URL}. Başında https:// olmalı.")
            st.stop()
        return create_client(URL, KEY)
    except Exception as e:
        st.error(f"Bağlantı Kurulurken Hata Oluştu: {e}")
        return None

supabase = init_connection()

if supabase:
    st.success("✅ Supabase bağlantısı başarılı!")
    # ... verileri çekme kodların buraya gelecek ...
