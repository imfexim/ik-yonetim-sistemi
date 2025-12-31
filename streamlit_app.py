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

df = load_data()

if not df.empty:
    # 3. Üst Bilgi Kartları
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Kayıt", len(df))
    col2.metric("Benzersiz Personel", df['ad_soyad'].nunique())
    col3.metric("Sistem Durumu", "Aktif", delta="Bağlı")

    # 4. Ana Tablo (En Güncel Versiyonlar)
    st.subheader("📋 Güncel Personel Listesi")
    # Her personelin sadece en yüksek versiyonunu göster
    latest_df = df.sort_values('versiyon', ascending=False).drop_duplicates('ad_soyad')
    st.dataframe(latest_df[['ad_soyad', 'tc_no', 'versiyon', 'created_at']], use_container_width=True, hide_index=True)

    # 5. Timeline / Geçmiş İnceleme Alanı
    st.divider()
    st.subheader("📜 Personel İşlem Geçmişi (Timeline)")
    
    selected_person = st.selectbox("Geçmişini görmek istediğiniz personeli seçin:", df['ad_soyad'].unique())
    
    if selected_person:
        # Seçilen personelin tüm kayıtlarını versiyona göre diz
        person_history = df[df['ad_soyad'] == selected_person].sort_values('versiyon', ascending=False)
        
        for _, row in person_history.iterrows():
            with st.expander(f"Versiyon {row['versiyon']} — {row['created_at'][:10]} Tarihli Kayıt"):
                c1, c2 = st.columns(2)
                c1.write(f"**Ad Soyad:** {row['ad_soyad']}")
                c1.write(f"**TC No:** {row['tc_no']}")
                c2.write(f"**Sistem Kayıt ID:** {row['id']}")
                c2.info(f"Bu kayıt personelin {row['versiyon']}. güncellenmiş halidir.")

else:
    st.info("💡 Veri tabanı şu an boş. Supabase üzerinden veri eklediğinizde burada görünecektir.")
