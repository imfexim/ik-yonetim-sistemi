import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İMFEXİM | Admin", layout="wide")

# 2. KARANLIK TEMAYI VE OKUNURLUK SORUNUNU ÖLDÜREN CSS
st.markdown("""
    <style>
    /* Uygulama Arka Planı */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Tüm Yazılar Siyah */
    h1, h2, h3, h4, p, span, label, .stMarkdown { color: #000000 !important; }

    /* Buton Yazısı Beyaz, Zemin Lacivert */
    .stButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important; /* BUTON YAZISI BEYAZ */
        font-weight: 600 !important;
        border: none !important;
    }

    /* Tablo Hücreleri: Beyaz Zemin, Siyah Yazı */
    div[data-testid="stTable"] table { background-color: white !important; color: black !important; }
    div[data-testid="stTable"] th { background-color: #F3F4F6 !important; color: black !important; }
    div[data-testid="stTable"] td { color: black !important; border-bottom: 1px solid #E5E7EB !important; }

    /* Input ve Dropboxlar */
    input, select, textarea, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E5E7EB !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- VERİ ÇEKME VE DÜZLEŞTİRME ---
def fetch_candidates():
    try:
        # Adayları ve en güncel versiyonlarındaki süreç bilgisini çek
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(ise_alim_sureci, telefon)").execute()
        raw_data = res.data if res.data else []
        
        flattened = []
        for r in raw_data:
            # Sadece aktif adayları (işe alındı/olumsuz olmayanlar) listeye ekle
            v = r.get('aday_versiyonlar')
            surec = v.get('ise_alim_sureci', 'aday havuzu') if v else 'aday havuzu'
            
            if surec not in ['işe alındı', 'olumsuz']:
                flattened.append({
                    "Ad Soyad": r.get('ad_soyad', '-'),
                    "TC Kimlik": r.get('kimlik_no', '-'),
                    "Telefon": v.get('telefon', '-') if v else "-",
                    "Mevcut Süreç": surec.upper()
                })
        return flattened
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return []

# 4. Yan Menü
with st.sidebar:
    st.markdown("<h2 style='color:#2563EB;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    main_nav = st.radio("MENÜ", ["Dashboard", "Organizasyon", "İşe Alım", "Çalışanlar"], label_visibility="collapsed")
    
    sub_nav = "Adaylar" if main_nav == "İşe Alım" else main_nav
    if main_nav == "Organizasyon":
        sub_nav = st.radio("ORG", ["Departmanlar", "Pozisyonlar", "Seviyeler"])

# --- ADAYLAR EKRANI ---
if sub_nav == "Adaylar":
    st.markdown("## 👤 Aday Takip")
    t1, t2 = st.tabs(["➕ Yeni Aday", "📋 Aktif Havuz"])
    
    with t1:
        with st.form("new_candidate", clear_on_submit=True):
            f_ad = st.text_input("Ad Soyad")
            f_tc = st.text_input("TC No")
            if st.form_submit_button("Havuza Ekle"):
                if f_ad and f_tc:
                    # Kayıt Mantığı
                    res = supabase.table("adaylar").insert({"ad_soyad": f_ad, "kimlik_no": f_tc}).execute()
                    # (Versiyonlama kodları buraya gelecek)
                    st.success("Aday başarıyla eklendi.")
                    st.rerun()

    with t2:
        aday_listesi = fetch_candidates()
        if aday_listesi:
            st.table(pd.DataFrame(aday_listesi))
        else:
            st.info("Havuzda şu an aktif aday bulunmuyor veya veriler yüklenemedi.")

# --- DİĞER EKRANLAR (Basitleştirilmiş) ---
elif sub_nav == "Dashboard":
    st.markdown("## Dashboard")
    # Dashboard kartları...
