import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Bağlantı Ayarları (Supabase panelinden aldığın kodlar)
URL = "sb_publishable_1I_NNEeGfhPSk6Wbh9Yuig_gNeeXjv3"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpwZHhtaXBtdnF0eG5tYXV4eHdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcyMDk1MTIsImV4cCI6MjA4Mjc4NTUxMn0.Gb4t-r9lmWBzmHE9EdMfNUbtxm78nKXqM8LRB0IktG4"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# Sayfa Ayarları
st.set_page_config(page_title="İK Yönetim Paneli", layout="wide")

st.title("🚀 Personel Yönetim Sistemi")
st.markdown("---")

# 2. Verileri Çekme
def get_data():
    response = supabase.table('personel').select("*").execute()
    return response.data

data = get_data()

if data:
    df = pd.DataFrame(data)
    
    # Sütunları düzenle (Gereksiz id vb. gizlemek için)
    display_df = df[['personel_id', 'ad_soyad', 'tc_no', 'versiyon', 'islem_tarihi']]
    
    # 3. Şık Tablo ve Arama
    search = st.text_input("🔍 İsim veya ID ile ara...", "")
    if search:
        display_df = display_df[display_df['ad_soyad'].str.contains(search, case=False)]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # 4. Detay ve Timeline (Zaman Çizelgesi) Özelliği
    st.sidebar.header("Personel Detay")
    selected_id = st.sidebar.selectbox("Geçmişini incelemek için seçin:", display_df['personel_id'].unique())
    
    if selected_id:
        st.sidebar.markdown(f"### {selected_id} Geçmişi")
        # Seçilen personelin tüm versiyonlarını çek
        history = df[df['personel_id'] == selected_id].sort_values(by='versiyon', ascending=False)
        for _, row in history.iterrows():
            with st.sidebar.expander(f"Versiyon {row['versiyon']} - {row['islem_tarihi'][:10]}"):
                st.write(f"**TC:** {row['tc_no']}")
                st.write(f"**Güncelleme:** {row['islem_tarihi']}")

else:
    st.warning("Veri tabanında henüz kayıt bulunamadı.")
