import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px # Grafik için

# 1. Bağlantı Ayarları
try:
    URL = st.secrets["SUPABASE_URL"].strip().replace('"', '')
    KEY = st.secrets["SUPABASE_KEY"].strip().replace('"', '')
except Exception:
    st.error("Secrets ayarları eksik!")
    st.stop()

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="İM-FEXİM İK PORTAL", layout="wide", page_icon="👥")

# --- CUSTOM CSS (Görsellik İçin) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 İM-FEXİM İK Yönetim Paneli")
st.markdown("---")

# 2. Veri Yükleme
def load_data():
    res = supabase.table("Personel").select("*").execute()
    data = pd.DataFrame(res.data)
    if not data.empty:
        data['islem_tarihi'] = pd.to_datetime(data['islem_tarihi'], errors='coerce', utc=True)
    return data

df = load_data()

# --- YAN MENÜ (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/912/912214.png", width=100) # Temsili İK Logosu
    st.header("⚙️ Veri Girişi")
    with st.form("kayit_formu", clear_on_submit=True):
        f_ad = st.text_input("Ad Soyad")
        f_id = st.text_input("Personel ID")
        f_tc = st.text_input("TC No")
        f_ver = st.selectbox("Versiyon Durumu", ["V1-Giriş", "V2-Güncelleme", "V3-Terfi", "V4-Çıkış"])
        
        if st.form_submit_button("Sisteme İşle"):
            if f_ad and f_id:
                yeni = {"ad_soyad": f_ad, "personel_id": f_id, "tc_no": f_tc, "versiyon": f_ver}
                supabase.table("Personel").insert(yeni).execute()
                st.success("Kayıt Eklendi!")
                st.rerun()

# --- ANA EKRAN ---
if not df.empty:
    # 3. Üst Bilgi Kartları (Görsel Kartlar)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Toplam Kayıt", len(df))
    m2.metric("👤 Personel Sayısı", df['personel_id'].nunique())
    
    last_date = df['islem_tarihi'].max()
    m3.metric("📅 Son İşlem", last_date.strftime('%d.%m.%Y') if pd.notnull(last_date) else "-")
    m4.metric("📈 Sistem Durumu", "Aktif", delta="Online")

    # 4. Grafik ve Tablo Yan Yana
    st.markdown("### 📊 Veri Analizi ve Güncel Liste")
    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Küçük bir işlem yoğunluğu grafiği
        df_counts = df.groupby(df['islem_tarihi'].dt.date).size().reset_index(name='Kayıt Sayısı')
        fig = px.line(df_counts, x='islem_tarihi', y='Kayıt Sayısı', title="Günlük İşlem Yoğunluğu")
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Renklendirilmiş Tablo
        latest_df = df.sort_values('islem_tarihi', ascending=False).drop_duplicates('personel_id')
        st.dataframe(latest_df[['ad_soyad', 'personel_id', 'tc_no', 'versiyon']], use_container_width=True, hide_index=True)

    # 5. Timeline (Görsel Akış)
    st.markdown("---")
    st.subheader("📜 Personel Tarihçesi")
    selected = st.selectbox("İncelemek için personel seçin:", df['ad_soyad'].unique())
    
    if selected:
        history = df[df['ad_soyad'] == selected].sort_values('islem_tarihi', ascending=False)
        for _, row in history.iterrows():
            t_str = row['islem_tarihi'].strftime('%d.%m.%Y %H:%M')
            st.info(f"**{row['versiyon']}** | {t_str} tarihinde işlem yapıldı. (TC: {row['tc_no']})")

else:
    st.info("Henüz veri bulunmuyor. Yan menüden ilk kaydı ekleyebilirsiniz.")
