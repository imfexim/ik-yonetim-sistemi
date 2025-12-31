import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Güvenli Bağlantı Ayarları
URL = st.secrets["SUPABASE_URL"].strip().replace('"', '')
KEY = st.secrets["SUPABASE_KEY"].strip().replace('"', '')

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# Sayfa Yapılandırması
st.set_page_config(page_title="İK Personel Takip", layout="wide")
st.title("👥 Personel Yönetimi ve Versiyon Geçmişi")

# 2. Veri Çekme Fonksiyonu
def load_data():
    try:
        # Tablo ismini 'Personel' (Büyük P) olarak güncelledik
        res = supabase.table("Personel").select("*").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Veri çekilirken hata oluştu: {e}")
        return pd.DataFrame()

st.divider()
st.subheader("➕ Yeni Kayıt / Güncelleme Ekle")

with st.form("personel_form"):
    # Senin listendeki sütunlara göre alanları oluşturuyoruz
    p_id = st.text_input("Personel ID / Ad Soyad") # personel_id sütunu için
    p_tc = st.text_input("TC Kimlik No")           # tc_no sütunu için
    p_ver = st.number_input("Versiyon", min_value=1, step=1) # versiyon sütunu için
    
    submit = st.form_submit_button("Sisteme Kaydet")
    
    if submit:
        if p_id and p_tc:
            # SUPABASE SÜTUN İSİMLERİYLE BİREBİR EŞLEŞME:
            yeni_veri = {
                "personel_id": p_id, 
                "tc_no": p_tc, 
                "versiyon": p_ver
                # 'id' ve 'islem_tarihi' Supabase tarafından otomatik doldurulur.
            }
            try:
                supabase.table("Personel").insert(yeni_veri).execute()
                st.success(f"✅ {p_id} başarıyla kaydedildi!")
                st.rerun() 
            except Exception as e:
                st.error(f"❌ Kayıt Hatası: {e}")
        else:
            st.warning("Lütfen zorunlu alanları doldurun.")
