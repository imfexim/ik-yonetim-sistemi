import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Ayarları Çek ve Bağlan
URL = st.secrets["SUPABASE_URL"].strip().replace('"', '')
KEY = st.secrets["SUPABASE_KEY"].strip().replace('"', '')

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

st.title("👥 Personel Yönetim ve Versiyon Takip")

# 2. Verileri Çek
try:
    # Tablo adını Personel (Büyük P) olarak güncelledik
    res = supabase.table("Personel").select("*").execute()
    all_data = pd.DataFrame(res.data)

    if not all_data.empty:
        # 3. Sol Menü - Personel Seçimi
        personel_listesi = all_data['ad_soyad'].unique()
        secilen_personel = st.sidebar.selectbox("Geçmişini incelemek için bir personel seçin:", personel_listesi)

        # 4. Ana Ekran - Genel Liste (Sadece en güncel versiyonlar)
        st.subheader("Güncel Personel Listesi")
        # Her personelin sadece en yüksek (en yeni) versiyonunu filtreleyelim
        guncel_liste = all_data.sort_values('versiyon', ascending=False).drop_duplicates('ad_soyad')
        st.dataframe(guncel_liste[['ad_soyad', 'tc_no', 'versiyon', 'created_at']], use_container_width=True)

        # 5. Timeline (Zaman Çizelgesi) - Seçilen Personelin Geçmişi
        st.divider()
        st.subheader(f"📜 {secilen_personel} - Versiyon Geçmişi")
        
        personel_gecmisi = all_data[all_data['ad_soyad'] == secilen_personel].sort_values('versiyon', ascending=False)

        for _, row in personel_gecmisi.iterrows():
            with st.expander(f"Versiyon {row['versiyon']} - Tarih: {row['created_at'][:10]}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Ad Soyad:** {row['ad_soyad']}")
                    st.write(f"**TC Kimlik:** {row['tc_no']}")
                with col2:
                    st.write(f"**İşlem Tarihi:** {row['created_at']}")
                    st.info(f"Bu kayıt personelin {row['versiyon']}. güncellemesidir.")
    else:
        st.warning("Veri tabanında kayıtlı personel bulunamadı.")

except Exception as e:
    st.error(f"Bir hata oluştu: {e}")
