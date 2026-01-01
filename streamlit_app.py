import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Bağlantı Ayarları
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

st.set_page_config(page_title="İM-FEXİM İK Paneli", layout="wide")
st.title("👥 Personel Yönetim ve Versiyon Takip")

# 2. Verileri Çekme
def load_data():
    try:
        res = supabase.table("Personel").select("*").execute()
        data = pd.DataFrame(res.data)
        if not data.empty and 'islem_tarihi' in data.columns:
            # HATAYI ÖNLEYEN KRİTİK SATIR: Hatalı tarihleri NaT (boş) yapar
            data['islem_tarihi'] = pd.to_datetime(data['islem_tarihi'], errors='coerce', utc=True)
        return data
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 3. Özet Bilgiler (Hata veren kısım revize edildi)
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Kayıt", len(df))
    c2.metric("Benzersiz Personel", df['personel_id'].nunique() if 'personel_id' in df.columns else 0)
    
    # Güvenli son işlem tarihi hesaplama
    try:
        last_action_val = df['islem_tarihi'].max()
        if pd.notnull(last_action_val):
            last_action_str = last_action_val.strftime('%Y-%m-%d %H:%M')
        else:
            last_action_str = "Tarih Yok"
    except:
        last_action_str = "Hatalı Format"
    
    c3.metric("Son İşlem", last_action_str)

    # 4. Güncel Liste
    st.subheader("📋 Güncel Durum")
    # Tarihe göre sıralayıp en günceli alıyoruz
    latest_df = df.sort_values('islem_tarihi', ascending=False).drop_duplicates('personel_id')
    
    # Tablo görünümü için tarihi metne çevir
    display_df = latest_df.copy()
    if 'islem_tarihi' in display_df.columns:
        display_df['islem_tarihi'] = display_df['islem_tarihi'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Mevcut sütunlara göre tabloyu bas
    cols_to_show = [c for c in ['ad_soyad', 'personel_id', 'tc_no', 'versiyon', 'islem_tarihi'] if c in display_df.columns]
    st.dataframe(display_df[cols_to_show], use_container_width=True, hide_index=True)

    # 5. Timeline Bölümü
    st.divider()
    st.subheader("📜 Personel Geçmişi (Timeline)")
    
    if 'personel_id' in df.columns:
        p_ids = df['personel_id'].unique()
        selected_id = st.selectbox("Geçmiş için Personel ID seçin:", p_ids)
        
        if selected_id:
            history = df[df['personel_id'] == selected_id].sort_values('islem_tarihi', ascending=False)
            for _, row in history.iterrows():
                tarih = row['islem_tarihi'].strftime('%Y-%m-%d %H:%M') if pd.notnull(row['islem_tarihi']) else "Bilinmiyor"
                with st.expander(f"{row.get('versiyon', 'V?')} — {tarih}"):
                    st.write(f"**Ad Soyad:** {row.get('ad_soyad', 'Belirtilmemiş')}")
                    st.write(f"**TC:** {row.get('tc_no', '-')}")
                    st.caption(f"ID: {row.get('id', '-')}")

# 6. Kayıt Formu
st.divider()
st.subheader("➕ Yeni Kayıt Ekle")
with st.form("kayit_formu", clear_on_submit=True):
    f_ad = st.text_input("Ad Soyad")
    f_id = st.text_input("Personel ID")
    f_tc = st.text_input("TC Kimlik No")
    f_ver = st.text_input("Versiyon (Örn: V1)")
    
    if st.form_submit_button("Sisteme İşle"):
        if f_ad and f_id:
            yeni_satir = {"ad_soyad": f_ad, "personel_id": f_id, "tc_no": f_tc, "versiyon": f_ver}
            try:
                supabase.table("Personel").insert(yeni_satir).execute()
                st.success("Başarıyla eklendi!")
                st.rerun()
            except Exception as e:
                st.error(f"Kayıt Hatası: {e}")
