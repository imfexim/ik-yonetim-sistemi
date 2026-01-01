import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Bağlantı Ayarları (Secrets'tan güvenli çekim)
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

# 2. Verileri Çekme Fonksiyonu
def load_data():
    try:
        # Tablo adın: Personel
        res = supabase.table("Personel").select("*").execute()
        data = pd.DataFrame(res.data)
        if not data.empty:
            # Tarih sütununu güvenli bir şekilde dönüştür (hatalı formatları NaT yapar)
            data['islem_tarihi'] = pd.to_datetime(data['islem_tarihi'], errors='coerce')
        return data
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 3. Özet Bilgiler (Hata Alınan Kısım Düzeltildi)
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Kayıt", len(df))
    c2.metric("Benzersiz Personel", df['personel_id'].nunique())
    
    # En son işlem tarihini hatasız hesapla
    last_action_val = df['islem_tarihi'].max()
    if pd.notnull(last_action_val):
        last_action_str = last_action_val.strftime('%Y-%m-%d %H:%M')
    else:
        last_action_str = "Kayıt Yok"
    c3.metric("Son İşlem", last_action_str)

    # 4. Güncel Liste (Her personelin sadece en son versiyonu)
    st.subheader("📋 Güncel Durum")
    # Önce tarihe göre sıralayıp sonra en güncel personelleri ayırıyoruz
    latest_df = df.sort_values(['islem_tarihi'], ascending=False).drop_duplicates('personel_id')
    
    # Görselleştirme için tarih formatını düzenle
    display_df = latest_df.copy()
    display_df['islem_tarihi'] = display_df['islem_tarihi'].dt.strftime('%Y-%m-%d %H:%M')
    
    st.dataframe(
        display_df[['ad_soyad', 'personel_id', 'tc_no', 'versiyon', 'islem_tarihi']], 
        use_container_width=True, 
        hide_index=True
    )

    # 5. Timeline (Geçmiş) Bölümü
    st.divider()
    st.subheader("📜 Personel Geçmişi (Timeline)")
    
    # Listede personel_id yanında isimle seçim yapmak daha kolay olur
    person_options = df['personel_id'].unique()
    selected_per_id = st.selectbox("Geçmişini incelemek için bir Personel ID seçin:", person_options)
    
    if selected_per_id:
        # Seçilen personelin geçmişini en yeni versiyon üstte olacak şekilde filtrele
        history = df[df['personel_id'] == selected_per_id].sort_values('islem_tarihi', ascending=False)
        for _, row in history.iterrows():
            tarih_str = row['islem_tarihi'].strftime('%Y-%m-%d %H:%M') if pd.notnull(row['islem_tarihi']) else "Bilinmiyor"
            with st.expander(f"{row['versiyon']} — Kayıt Tarihi: {tarih_str}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Ad Soyad:** {row['ad_soyad']}")
                    st.write(f"**Personel ID:** {row['personel_id']}")
                with col_b:
                    st.write(f"**TC Kimlik:** {row['tc_no']}")
                    st.caption(f"Sistem Kayıt Numarası: {row['id']}")

# 6. Yeni Kayıt Ekleme Formu
st.divider()
st.subheader("➕ Yeni Kayıt veya Güncelleme Ekle")
with st.form("kayit_formu", clear_on_submit=True):
    f_ad = st.text_input("Ad Soyad")
    f_id = st.text_input("Personel ID")
    f_tc = st.text_input("TC Kimlik No")
    f_ver = st.text_input("Versiyon (Örn: V1)")
    
    submit = st.form_submit_button("Sisteme İşle")
    
    if submit:
        if f_ad and f_id and f_tc:
            yeni_satir = {
                "ad_soyad": f_ad, 
                "personel_id": f_id, 
                "tc_no": f_tc, 
                "versiyon": f_ver
            }
            try:
                supabase.table("Personel").insert(yeni_satir).execute()
                st.success(f"✅ {f_ad} başarıyla kaydedildi!")
                st.rerun()
            except Exception as e:
                st.error(f"Kayıt Hatası: {e}")
        else:
            st.warning("Lütfen Ad Soyad, Personel ID ve TC alanlarını doldurun.")
