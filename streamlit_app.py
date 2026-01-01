import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM | Admin", layout="wide")

# 2. KARANLIK TEMAYI VE VERİ GİZLEME SORUNUNU ÖLDÜREN NİHAİ CSS
st.markdown("""
    <style>
    /* 1. TÜM ARKA PLANI BEYAZA ZORLA */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
    }

    /* 2. TÜM METİNLERİ SİYAH YAP */
    h1, h2, h3, h4, h5, h6, p, span, label, div, li, .stMarkdown {
        color: #000000 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 3. BUTONLAR: LACİVERT ZEMİN ÜZERİNE BEYAZ YAZI */
    div.stButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        display: block !important;
    }
    div.stButton > button:hover {
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
    }

    /* 4. TABLOLAR: BEYAZ ZEMİN, SİYAH YAZI, GRİ ÇİZGİLER */
    div[data-testid="stTable"] {
        background-color: #FFFFFF !important;
    }
    div[data-testid="stTable"] table {
        color: #000000 !important;
        border-collapse: collapse !important;
        width: 100% !important;
    }
    div[data-testid="stTable"] th {
        background-color: #F3F4F6 !important;
        color: #000000 !important;
        text-align: left !important;
        padding: 12px !important;
    }
    div[data-testid="stTable"] td {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        padding: 12px !important;
        border-bottom: 1px solid #E5E7EB !important;
    }

    /* 5. GİRDİ ALANLARI (INPUT & DROPBOX) */
    input, select, textarea, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #D1D5DB !important;
    }
    
    /* 6. SIDEBAR SEÇENEKLERİ */
    section[data-testid="stSidebar"] {
        border-right: 1px solid #E5E7EB !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- GÜVENLİ VERİ ÇEKME FONKSİYONU ---
def get_safe_data(table, select_query="*"):
    try:
        res = supabase.table(table).select(select_query).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Hata: {table} tablosundan veri alınamadı. {e}")
        return []

# 4. Yan Menü Yapısı
with st.sidebar:
    st.markdown("<h2 style='color:#2563EB;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    main_menu = st.radio("NAVİGASYON", ["Dashboard", "Organizasyon", "İşe Alım", "Çalışanlar"], label_visibility="collapsed")
    
    # Alt Menü Mantığı
    current_page = main_menu
    if main_menu == "Organizasyon":
        current_page = st.radio("ALT", ["Departmanlar", "Pozisyonlar", "Seviyeler"])
    elif main_nav := "İşe Alım":
        if main_menu == "İşe Alım": current_page = "Adaylar"

# --- EKRANLAR ---

# --- DASHBOARD ---
if current_page == "Dashboard":
    st.header("Sistem Özeti")
    c1, c2, c3 = st.columns(3)
    
    aday_sayisi = len(get_safe_data("adaylar"))
    personel_sayisi = len(get_safe_data("personeller"))
    dep_sayisi = len(get_safe_data("departmanlar"))
    
    c1.metric("Toplam Aday", aday_sayisi)
    c2.metric("Aktif Çalışan", personel_sayisi)
    c3.metric("Departman Sayısı", dep_sayisi)

# --- ADAYLAR ---
elif current_page == "Adaylar":
    st.header("Aday Takip Havuzu")
    t1, t2 = st.tabs(["➕ Yeni Kayıt", "📋 Aktif Liste"])
    
    with t1:
        with st.form("new_aday_form", clear_on_submit=True):
            ad = st.text_input("Ad Soyad")
            tc = st.text_input("Kimlik Numarası")
            if st.form_submit_button("Adayı Havuza Kaydet"):
                if ad and tc:
                    supabase.table("adaylar").insert({"ad_soyad": ad, "kimlik_no": tc}).execute()
                    st.success("Aday eklendi.")
                    st.rerun()

    with t2:
        # Verileri JOIN yaparak ve düzleştirerek çekiyoruz
        query = "*, aday_versiyonlar!guncel_versiyon_id(ise_alim_sureci, telefon)"
        raw_adaylar = get_safe_data("adaylar", query)
        
        if raw_adaylar:
            final_list = []
            for r in raw_adaylar:
                v = r.get('aday_versiyonlar')
                surec = v.get('ise_alim_sureci', 'aday havuzu') if v else "aday havuzu"
                
                # Sadece süreci tamamlanmamışları göster
                if surec not in ["işe alındı", "olumsuz"]:
                    final_list.append({
                        "Ad Soyad": r.get('ad_soyad'),
                        "TC No": r.get('kimlik_no'),
                        "Durum": surec.upper(),
                        "Telefon": v.get('telefon', '-') if v else "-"
                    })
            
            if final_list:
                st.table(pd.DataFrame(final_list))
            else:
                st.info("Aktif süreçte aday bulunmuyor.")
        else:
            st.warning("Veritabanında kayıtlı aday verisi bulunamadı.")

# --- DEPARTMANLAR ---
elif current_page == "Departmanlar":
    st.header("Departman Yönetimi")
    t1, t2 = st.tabs(["Ekle", "Liste"])
    with t1:
        with st.form("d_form"):
            d_ad = st.text_input("Departman Adı")
            if st.form_submit_button("Kaydet"):
                supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute()
                st.rerun()
    with t2:
        deps = get_safe_data("departmanlar")
        if deps: st.table(pd.DataFrame(deps)[["departman_adi"]])

# --- ÇALIŞANLAR ---
elif current_page == "Çalışanlar":
    st.header("Aktif Personel Listesi")
    # Personel verilerini çek ve tablola...
    p_query = "*, personel_versiyonlar!guncel_versiyon_id(departman_id, pozisyon_id)"
    personeller = get_safe_data("personeller", p_query)
    if personeller:
        st.table(pd.DataFrame(personeller)[["ad_soyad", "kimlik_no"]])
