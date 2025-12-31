import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Bağlantı Ayarları
try:
    URL = st.secrets["SUPABASE_URL"].strip().replace('"', '')
    KEY = st.secrets["SUPABASE_KEY"].strip().replace('"', '')
except Exception:
    st.error("Lütfen Secrets ayarlarına SUPABASE_URL ve SUPABASE_KEY ekleyin.")
    st.stop()

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

st.set_page_config(page_title="İM-FEXİM İK Platformu", layout="wide")
st.title("👥 Personel Yönetim Sistemi")

# 2. Veri Çekme
def load_data():
    try:
        # Tablo ismin 'Personel' (Büyük P)
        res = supabase.table("Personel").select("*").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 3. İstatistikler
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Kayıt", len(df))
    c2.metric("Benzersiz Personel", df['personel_id'].nunique())
    c3.metric("Son Güncelleme", df['islem_tarihi'].max()[:10])

    # 4. Ana Liste (En güncel versiyonları göster)
    st.subheader("📋 Güncel Personel Listesi")
    latest_df = df.sort_values('versiyon', ascending=False).drop_duplicates('personel_id')
    st.dataframe(latest_df[['personel_id', 'tc_no', 'versiyon', 'islem_tarihi']], 
                 use_container_width=True, hide_index=True)

    # 5. Timeline (Geçmiş) Bölümü
    st.divider()
    st.subheader("📜 Personel İşlem Geçmişi")
    
    selected_per = st.selectbox("İncelemek istediğiniz Personel ID'yi seçin:", df['personel_id'].unique())
    
    if selected_per:
        history = df[df['personel_id'] == selected_per].sort_values('versiyon', ascending=False)
        for _, row in history.iterrows():
            with st.expander(f"Versiyon: {row['versiyon']} | Tarih: {row['islem_tarihi'][:16]}"):
                st.write(f"**Personel ID:** {row['personel_id']}")
                st.write(f"**TC Kimlik:** {row['tc_no']}")
                st.caption(f"Veritabanı Kayıt No: {row['id']}")

# 6. Kayıt Ekleme Formu
st.divider()
st.subheader("➕ Yeni Kayıt / Güncelleme")
with st.form("kayit_formu"):
    f_id = st.text_input("Personel ID (Örn: PER-170...)")
    f_tc = st.text_input("TC Kimlik No")
    f_ver = st.text_input("Versiyon (Örn: V1-...)")
    
    if st.form_submit_button("Sisteme İşle"):
        if f_id and f_tc:
            yeni_satir = {"personel_id": f_id, "tc_no": f_tc, "versiyon": f_ver}
            try:
                supabase.table("Personel").insert(yeni_satir).execute()
                st.success("Kayıt başarıyla eklendi!")
                st.rerun()
            except Exception as e:
                st.error(f"Hata: {e}")
