import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM | Yönetim", layout="wide")

# 2. %100 BEYAZ TEMA VE SİYAH YAZI ZORLAMASI (CSS)
st.markdown("""
    <style>
    /* Global Beyaz Zemin */
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
    }
    /* Tüm Yazılar Siyah */
    h1, h2, h3, h4, p, span, label, div, li, .stMarkdown {
        color: #000000 !important;
        font-family: 'Inter', sans-serif !important;
    }
    /* Butonlar: Lacivert Zemin / Beyaz Yazı */
    div.stButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    /* Tablolar: Beyaz Zemin / Siyah Yazı */
    div[data-testid="stTable"] table { background-color: white !important; color: black !important; }
    div[data-testid="stTable"] th { background-color: #F9FAFB !important; color: black !important; border-bottom: 2px solid #EEEEEE !important; }
    div[data-testid="stTable"] td { border-bottom: 1px solid #F0F0F0 !important; }

    /* Input Alanları */
    input, select, textarea, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #D1D5DB !important;
    }
    /* Kilitli Alanlar Siyah Yazı */
    input:disabled { -webkit-text-fill-color: #000000 !important; background-color: #F3F4F6 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- VERİ ÇEKME FONKSİYONLARI ---
def fetch_data(table, query="*"):
    try:
        res = supabase.table(table).select(query).execute()
        return res.data if res.data else []
    except Exception: return []

# 4. Yan Menü (Sayfa Geçiş Garantili)
with st.sidebar:
    st.markdown("<h2 style='color:#2563EB;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    # Menü seçimi
    menu = st.sidebar.selectbox("ANA MENÜ", ["📊 Dashboard", "🏢 Organizasyon", "👤 İşe Alım", "👥 Çalışanlar"])

# --- SAYFA YÖNLENDİRME MANTIĞI ---

# A. DASHBOARD
if menu == "📊 Dashboard":
    st.title("Sistem Özeti")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Aday", len(fetch_data("adaylar")))
    c2.metric("Aktif Çalışan", len(fetch_data("personeller")))
    c3.metric("Departman Sayısı", len(fetch_data("departmanlar")))

# B. ORGANİZASYON
elif menu == "🏢 Organizasyon":
    st.title("Organizasyon Yapılandırması")
    org_sub = st.radio("İşlem Seçin:", ["Departmanlar", "Pozisyonlar", "Seviyeler"], horizontal=True)
    
    if org_sub == "Departmanlar":
        t1, t2 = st.tabs(["➕ Ekle", "📋 Liste"])
        with t1:
            with st.form("d_form", clear_on_submit=True):
                d_ad = st.text_input("Departman Adı")
                if st.form_submit_button("Kaydet"):
                    supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute()
                    st.rerun()
        with t2:
            data = fetch_data("departmanlar")
            if data: st.table(pd.DataFrame(data)[["departman_adi"]])

    elif org_sub == "Pozisyonlar":
        t1, t2 = st.tabs(["➕ Ekle", "📋 Liste"])
        deps = fetch_data("departmanlar")
        with t1:
            with st.form("p_form", clear_on_submit=True):
                d_map = {d['departman_adi']: d['id'] for d in deps}
                s_dep = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()))
                p_ad = st.text_input("Pozisyon Adı")
                if st.form_submit_button("Pozisyon ve 6 Seviye Oluştur"):
                    if s_dep != "Seçiniz..." and p_ad:
                        p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_ad}).execute()
                        p_id = p_res.data[0]['id']
                        ks = ["J1", "J2", "M1", "M2", "M3", "S"]
                        supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_ad} {k}", "seviye_kodu": k} for k in ks]).execute()
                        st.success("Başarılı"); st.rerun()
        with t2:
            res = fetch_data("pozisyonlar", "pozisyon_adi, departmanlar(departman_adi)")
            if res: st.table(pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res]))

# C. İŞE ALIM (ADAYLAR)
elif menu == "👤 İşe Alım":
    st.title("Aday Takip Sistemi")
    t1, t2 = st.tabs(["➕ Yeni Aday", "📋 Aktif Havuz"])
    
    with t1:
        # Aday Ekleme Formu ve Bağımlı Dropboxlar
        ad = st.text_input("Ad Soyad *")
        tc = st.text_input("Kimlik No *")
        tel = st.text_input("Telefon")
        # Departman/Pozisyon seçimleri...
        if st.button("Havuza Kaydet"):
            if ad and tc:
                a_res = supabase.table("adaylar").insert({"ad_soyad": ad, "kimlik_no": tc}).execute()
                a_id = a_res.data[0]['id']
                # Versiyonlama Kaydı
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": ad, "kimlik_no": tc, "telefon": tel,
                    "ise_alim_sureci": "aday havuzu", "baslangic_tarihi": datetime.now().isoformat()
                }).execute()
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.success("Kaydedildi"); st.rerun()

    with t2:
        # Düzleştirilmiş Aday Listesi
        res = fetch_data("adaylar", "*, aday_versiyonlar!guncel_versiyon_id(*)")
        aktifler = [r for r in res if r['aday_versiyonlar'] and r['aday_versiyonlar']['ise_alim_sureci'] not in ["işe alındı", "olumsuz"]]
        if aktifler:
            df_a = pd.DataFrame([{"Ad Soyad": r['ad_soyad'], "Süreç": r['aday_versiyonlar']['ise_alim_sureci'].upper()} for r in aktifler])
            st.table(df_a)
        else: st.info("Aktif aday bulunmuyor.")

# D. ÇALIŞANLAR
elif menu == "👥 Çalışanlar":
    st.title("Personel Portalı")
    res = fetch_data("personeller", "*, personel_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))")
    if res:
        df_p = pd.DataFrame([{"Ad Soyad": r['ad_soyad'], "Departman": r['personel_versiyonlar']['departmanlar']['departman_adi']} for r in res])
        st.table(df_p)
    else: st.warning("Henüz çalışan kaydı yok.")
