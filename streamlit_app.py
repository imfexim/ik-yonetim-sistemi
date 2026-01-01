import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Yapılandırması ve Tema Sıfırlama
st.set_page_config(page_title="İM-FEXİM Admin", layout="wide", initial_sidebar_state="expanded")

# 2. STRICT LIGHT MODE CSS (Siyahlığı Kökten Siler)
st.markdown("""
    <style>
    /* 1. Global Arka Plan ve Metin Renkleri */
    :root {
        --primary-text: #111827;
        --secondary-text: #4B5563;
        --bg-white: #FFFFFF;
        --border-light: #E5E7EB;
    }

    /* Tüm Container'ları Beyaz Yap */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: var(--bg-white) !important;
        color: var(--primary-text) !important;
    }

    /* 2. Form Elemanları (Dropbox, Inbox) - Siyahlığı Burası Öldürür */
    input, select, textarea, div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: var(--bg-white) !important;
        color: var(--primary-text) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 6px !important;
    }
    
    /* Input odaklandığında */
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #111827 !important;
    }

    /* 3. Tablolar (Zemin Beyaz, Yazı Siyah) */
    div[data-testid="stTable"], div[data-testid="stTable"] table {
        background-color: var(--bg-white) !important;
        color: var(--primary-text) !important;
    }
    th { background-color: #F9FAFB !important; color: var(--primary-text) !important; }
    td { color: var(--primary-text) !important; border-bottom: 1px solid var(--border-light) !important; }

    /* 4. Butonlar (Siyah Minimalist - Mavi Değil) */
    div.stButton > button {
        background-color: #111827 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #374151 !important;
        color: #FFFFFF !important;
    }

    /* 5. Sidebar Navigasyon */
    [data-testid="stSidebar"] { border-right: 1px solid var(--border-light) !important; }
    .nav-title { font-size: 11px; font-weight: 700; color: #9CA3AF; margin: 20px 0 10px 15px; text-transform: uppercase; }

    /* 6. Tabs (Üst Alt Menü) */
    .stTabs [data-baseweb="tab-list"] { background-color: var(--bg-white) !important; border-bottom: 1px solid var(--border-light) !important; }
    .stTabs [data-baseweb="tab"] { color: var(--secondary-text) !important; font-weight: 500 !important; }
    .stTabs [aria-selected="true"] { color: var(--primary-text) !important; border-bottom: 2px solid var(--primary-text) !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 4. Sayfa Yönetimi (Session State)
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# --- SOL MENÜ (ANA HİYERARŞİ) ---
with st.sidebar:
    st.markdown("<h3 style='color:#111827; padding-left:15px; font-weight:700;'>İM-FEXİM</h3>", unsafe_allow_html=True)
    st.markdown("<div class='nav-title'>Genel Bakış</div>", unsafe_allow_html=True)
    if st.button("📊 Dashboard", key="n_dash", use_container_width=True): st.session_state.page = "Dashboard"
    
    st.markdown("<div class='nav-title'>Kurumsal Yapı</div>", unsafe_allow_html=True)
    if st.button("🏢 Organizasyon", key="n_org", use_container_width=True): st.session_state.page = "Organizasyon"
    
    st.markdown("<div class='nav-title'>İnsan Kaynakları</div>", unsafe_allow_html=True)
    if st.button("👤 Aday Takip (ATS)", key="n_ats", use_container_width=True): st.session_state.page = "ATS"
    if st.button("👥 Personel (HRM)", key="n_hrm", use_container_width=True): st.session_state.page = "HRM"

# --- YARDIMCI VERİ ÇEKME ---
def fetch_safe(table):
    res = supabase.table(table).select("*").execute()
    return res.data if res.data else []

# --- ANA İÇERİK ---

if st.session_state.page == "Dashboard":
    st.title("Sistem Özeti")
    st.markdown("Veritabanındaki güncel metrikler ve organizasyonel durum.")

elif st.session_state.page == "Organizasyon":
    st.title("Organizasyon Yönetimi")
    t1, t2, t3 = st.tabs(["Departmanlar", "Pozisyonlar", "Kariyer Seviyeleri"])
    
    with t1:
        with st.form("f_dep", clear_on_submit=True):
            d_ad = st.text_input("Departman Adı")
            if st.form_submit_button("Departmanı Kaydet"):
                supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute()
                st.rerun()
        df_d = pd.DataFrame(fetch_safe("departmanlar"))
        if not df_d.empty: st.table(df_d[["departman_adi"]])

    with t2:
        deps = fetch_safe("departmanlar")
        d_map = {d['departman_adi']: d['id'] for d in deps}
        with st.form("f_poz"):
            s_dep = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()))
            p_ad = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Pozisyon Tanımla"):
                p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_ad}).execute()
                p_id = p_res.data[0]['id']
                # 6 Seviye Üretimi (SCD Type 2 Hazırlığı)
                levels = ["J1", "J2", "M1", "M2", "M3", "S"]
                supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_ad} {l}", "seviye_kodu": l} for l in levels]).execute()
                st.rerun()
        res_p = supabase.table("pozisyonlar").select("pozisyon_adi, departmanlar(departman_adi)").execute()
        if res_p.data:
            st.table(pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res_p.data]))

elif st.session_state.page == "ATS":
    st.title("Aday Takip & İşe Alım")
    t1, t2 = st.tabs(["Yeni Aday", "Aday Havuzu"])
    
    with t1:
        with st.form("f_aday"):
            ad = st.text_input("Ad Soyad")
            tc = st.text_input("Kimlik No")
            if st.form_submit_button("Havuza Kaydet"):
                a_res = supabase.table("adaylar").insert({"ad_soyad": ad, "kimlik_no": tc}).execute()
                a_id = a_res.data[0]['id']
                # SCD Type 2 Versiyonlama Başlat
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": ad, "kimlik_no": tc, "ise_alim_sureci": "aday havuzu",
                    "baslangic_tarihi": datetime.now().isoformat()
                }).execute()
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.success("Kayıt oluşturuldu."); st.rerun()

    with t2:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*)").execute()
        if res.data:
            df_a = pd.DataFrame([{"Ad Soyad": r['ad_soyad'], "Süreç": r['aday_versiyonlar']['ise_alim_sureci']} for r in res.data if r['aday_versiyonlar']])
            st.table(df_a)

elif st.session_state.page == "HRM":
    st.title("Personel Yönetimi")
    res_pers = fetch_safe("personeller")
    if res_pers:
        st.table(pd.DataFrame(res_pers)[["ad_soyad", "kimlik_no"]])
    else: st.info("Henüz çalışan personel kaydı bulunmuyor.")
