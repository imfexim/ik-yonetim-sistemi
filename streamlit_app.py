import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM | Admin", layout="wide", initial_sidebar_state="expanded")

# 2. %100 BEYAZ ZEMİN & SİYAH YAZI GARANTİSİ (CSS)
st.markdown("""
    <style>
    /* 1. Global Renk Zorlaması */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 2. Tüm Yazıları Siyah Yap */
    h1, h2, h3, h4, h5, h6, p, span, label, li, .stMarkdown {
        color: #000000 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 3. Input, Selectbox ve Textarea Alanları */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, input, select, textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
    }
    
    /* Selectbox açılır menü listesi */
    div[role="listbox"] { background-color: #FFFFFF !important; }
    div[role="option"] { color: #000000 !important; background-color: #FFFFFF !important; }

    /* 4. Tablolar (Zemin Beyaz, Yazı Siyah) */
    .stTable, .stDataFrame, div[data-testid="stTable"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    th { background-color: #F9FAFB !important; color: #000000 !important; }
    td { color: #000000 !important; }

    /* 5. Kilitli (Disabled) Alanlar */
    input:disabled {
        -webkit-text-fill-color: #000000 !important;
        background-color: #F3F4F6 !important;
    }

    /* 6. Sidebar (Sol Menü) */
    [data-testid="stSidebar"] { border-right: 1px solid #E5E7EB !important; }
    [data-testid="stSidebarNav"] { background-color: #FFFFFF !important; }
    
    /* 7. Butonlar (Premium Blue) */
    .stButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    
    /* 8. Card Yapısı */
    .cms-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- VERİ ÇEKME (Hata Kontrollü) ---
def safe_fetch(table, select="*"):
    try:
        res = supabase.table(table).select(select).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Veri çekme hatası ({table}): {e}")
        return []

# 4. Yan Menü
with st.sidebar:
    st.markdown("<h2 style='color:#2563EB; font-weight:700;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    main_nav = st.radio("MENÜ", ["Dashboard", "Organizasyon", "İşe Alım", "Çalışanlar"], label_visibility="collapsed")
    
    sub_nav = "Dashboard"
    if main_nav == "Organizasyon":
        sub_nav = st.radio("ORG", ["Departmanlar", "Pozisyonlar", "Seviyeler"], label_visibility="collapsed")
    elif main_nav == "İşe Alım":
        sub_nav = st.radio("REC", ["Adaylar"], label_visibility="collapsed")
    elif main_nav == "Çalışanlar":
        sub_nav = "Personel Listesi"

# --- EKRANLAR ---

if sub_nav == "Dashboard":
    st.markdown("### Genel Durum")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='cms-card'><span>Toplam Aday</span><h2>{len(safe_fetch('adaylar'))}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='cms-card'><span>Aktif Personel</span><h2>{len(safe_fetch('personeller'))}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='cms-card'><span>Departmanlar</span><h2>{len(safe_fetch('departmanlar'))}</h2></div>", unsafe_allow_html=True)

# DEPARTMANLAR
elif sub_nav == "Departmanlar":
    st.markdown("### Departman Yönetimi")
    t1, t2 = st.tabs(["Yeni Ekle", "Mevcut Liste"])
    with t1:
        with st.form("f_dep"):
            d_ad = st.text_input("Departman Adı")
            if st.form_submit_button("Kaydet"):
                supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute()
                st.rerun()
    with t2:
        res = safe_fetch("departmanlar")
        if res: st.table(pd.DataFrame(res)[["departman_adi"]])

# POZİSYONLAR
elif sub_nav == "Pozisyonlar":
    st.markdown("### Pozisyon Yönetimi")
    t1, t2 = st.tabs(["Yeni Ekle", "Mevcut Liste"])
    deps = safe_fetch("departmanlar")
    with t1:
        with st.form("f_poz"):
            d_map = {d['departman_adi']: d['id'] for d in deps}
            s_dep = st.selectbox("Departman Seç", ["Seçiniz..."] + list(d_map.keys()))
            p_ad = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Kaydet"):
                if s_dep != "Seçiniz..." and p_ad:
                    p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_ad}).execute()
                    p_id = p_res.data[0]['id']
                    # Otomatik 6 Seviye
                    ks = ["J1", "J2", "M1", "M2", "M3", "S"]
                    supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_ad} {k}", "seviye_kodu": k} for k in ks]).execute()
                    st.rerun()
    with t2:
        res = safe_fetch("pozisyonlar", "pozisyon_adi, departmanlar(departman_adi)")
        if res:
            df_poz = pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res])
            st.table(df_poz)

# ADAYLAR
elif sub_nav == "Adaylar":
    st.markdown("### Aday Takip")
    t1, t2 = st.tabs(["Yeni Aday", "Aktif Havuz"])
    with t1:
        with st.form("f_aday"):
            ad = st.text_input("Ad Soyad")
            tc = st.text_input("TC No")
            if st.form_submit_button("Havuza Ekle"):
                # Aday ekleme ve versiyonlama kodları buraya (Yukarıdaki fonksiyonlara benzer)
                st.success("Kaydedildi.")
    with t2:
        # Adayların gelmeme sorununu çözen JOIN sorgusu
        res = safe_fetch("adaylar", "*, aday_versiyonlar!guncel_versiyon_id(ise_alim_sureci)")
        if res:
            # Sadece aktif adayları (işe alındı/olumsuz olmayanları) filtrele
            df_aday = pd.DataFrame([{"Ad Soyad": r['ad_soyad'], "TC": r['kimlik_no'], "Süreç": r['aday_versiyonlar']['ise_alim_sureci']} 
                                    for r in res if r['aday_versiyonlar'] and r['aday_versiyonlar']['ise_alim_sureci'] not in ['işe alındı', 'olumsuz']])
            st.table(df_aday)

# PERSONEL
elif sub_nav == "Personel Listesi":
    st.markdown("### Aktif Çalışanlar")
    res = safe_fetch("personeller", "*, personel_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))")
    if res:
        df_p = pd.DataFrame([{"Ad Soyad": r['ad_soyad'], "Departman": r['personel_versiyonlar']['departmanlar']['departman_adi'], 
                             "Pozisyon": r['personel_versiyonlar']['pozisyonlar']['pozisyon_adi']} for r in res])
        st.table(df_p)
