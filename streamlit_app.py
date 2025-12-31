import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Bağlantı Ayarları (Secrets'tan çekiyoruz)
try:
    URL = st.secrets["SUPABASE_URL"].strip().replace('"', '')
    KEY = st.secrets["SUPABASE_KEY"].strip().replace('"', '')
except Exception:
    st.error("Lütfen Streamlit Secrets ayarlarına SUPABASE_URL ve SUPABASE_KEY ekleyin.")
    st.stop()

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

st.set_page_config(page_title="İK Personel Paneli", layout="wide")
st.title("👥 Personel Yönetim ve Versiyon Takip")

# 2. Verileri Çekme
def load_data():
    try:
        # Tablo adın görselde 'Personel' (Büyük P)
        res = supabase.table("Personel").select("*").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 3. Özet Bilgiler
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Kayıt", len(df))
    c2.metric("Benzersiz Personel", df['personel_id'].nunique())
    # islem_tarihi sütununu kullanarak son işlem zamanını gösteriyoruz
    last_action = pd.to_datetime(df['islem_tarihi']).max().strftime('%Y-%m-%d %H:%M')
    c3.metric("Son İşlem", last_action)

    # 4. Güncel Liste (Her personelin sadece en yüksek versiyonu)
    st.subheader("📋 Güncel Durum")
    # Versiyona göre sıralayıp sadece en yeniyi alıyoruz
    latest_df = df.sort_values('versiyon', ascending=False).drop_duplicates('personel_id')
    st.dataframe(latest_df[['personel_id', 'tc_no', 'versiyon', 'islem_tarihi']], 
                 use_container_width=True, hide_index=True)

    # 5. Timeline (Geçmiş) Bölümü
    st.divider()
    st.subheader("📜 Personel Geçmişi (Timeline)")
    
    selected_per = st.selectbox("Geçmişini incelemek için bir ID seçin:", df['personel_id'].unique())
    
    if selected_per:
        # Seçilen personelin tüm kayıtlarını eskiden yeniye döküyoruz
        history = df[df['personel_id'] == selected_per].sort_values('versiyon', ascending=False)
        for _, row in history.iterrows():
            with st.expander(f"{row['versiyon']} — Kayıt Tarihi: {row['islem_tarihi'][:16]}"):
                st.write(f"**Personel ID:** {row['personel_id']}")
                st.write(f"**TC Kimlik:** {row['tc_no']}")
                st.caption(f"Sistem Kayıt Numarası: {row['id']}")

# 6. Yeni Kayıt Ekleme Formu
st.divider()
st.subheader("➕ Yeni Kayıt veya Güncelleme Ekle")
with st.form("kayit_formu"):
    f_id = st.text_input("Personel ID (Görseldeki gibi PER-170...)")
    f_tc = st.text_input("TC Kimlik No")
    f_ver = st.text_input("Versiyon (Görseldeki gibi V1-... veya V2-...)")
    
    submit = st.form_submit_button("Sisteme İşle")
    
    if submit:
        if f_id and f_tc:
            # SÜTUN İSİMLERİ GÖRSELİNE GÖRE EŞLENDİ
            yeni_satir = {
                "personel_id": f_id, 
                "tc_no": f_tc, 
                "versiyon": f_ver
            }
            try:
                supabase.table("Personel").insert(yeni_satir).execute()
                st.success(f"{f_id} başarıyla sisteme işlendi!")
                st.rerun() # Sayfayı yenileyerek listeyi güncelle
            except Exception as e:
                st.error(f"Kayıt Hatası: {e}")
        else:
            st.warning("Lütfen Personel ID ve TC alanlarını doldurun.")
