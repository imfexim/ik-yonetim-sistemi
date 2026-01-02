import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Yapılandırması
st.set_page_config(page_title="IMFEXIM Admin", layout="wide", initial_sidebar_state="expanded")

# 2. Preline UI & Monokrom Stil Paketi
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Reset */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sol Sidebar Tasarımı */
    [data-testid="stSidebar"] {
        border-right: 1px solid #F2F4F7 !important;
        width: 260px !important;
    }
    .nav-section-label {
        font-size: 11px; font-weight: 700; color: #9CA3AF;
        margin: 25px 0 10px 20px; text-transform: uppercase; letter-spacing: 0.05em;
    }
    
    /* Sidebar Butonları - Eşit Genişlik ve Hover */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #374151 !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        font-weight: 500 !important;
        padding: 12px 20px !important;
        border-radius: 0px !important;
        margin: 0 !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #F3F4F6 !important;
        color: #111827 !important;
    }

    /* Üst Sekmeler (Alt Menü) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #FFFFFF !important;
        border-bottom: 1px solid #EAECF0 !important;
        gap: 32px !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500 !important;
        color: #6B7280 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #111827 !important;
        border-bottom: 2px solid #111827 !important;
    }

    /* Form ve Tablo Düzenlemeleri */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
    }
    .stButton > button {
        background-color: #111827 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Veritabanı Bağlantısı ve Fonksiyonlar
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

def db_fetch(table, select="*"): 
    return supabase.table(table).select(select).execute().data

# 4. Navigasyon State Yönetimi
if 'main_nav' not in st.session_state: st.session_state.main_nav = "Dashboard"

# --- SOL MENÜ ---
with st.sidebar:
    st.markdown("<div style='padding:25px 20px;'><h2 style='color:#111827; margin:0; letter-spacing:-1px; font-weight:700;'>IMFEXIM</h2></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='nav-section-label'>Analiz</div>", unsafe_allow_html=True)
    if st.button("Dashboard", use_container_width=True): st.session_state.main_nav = "Dashboard"
    
    st.markdown("<div class='nav-section-label'>Yönetim Paneli</div>", unsafe_allow_html=True)
    if st.button("Organizasyon", use_container_width=True): st.session_state.main_nav = "Organizasyon"
    if st.button("İşe Alım", use_container_width=True): st.session_state.main_nav = "İşe Alım"
    if st.button("Çalışanlar", use_container_width=True): st.session_state.main_nav = "Çalışanlar"

# --- ANA İÇERİK ---

if st.session_state.main_nav == "Dashboard":
    st.title("Sistem Özeti")
    st.markdown("Organizasyonel verilerin genel görünümü.")

elif st.session_state.main_nav == "Organizasyon":
    st.title("Organizasyon Yapılandırması")
    t1, t2, t3 = st.tabs(["Departmanlar", "Pozisyonlar", "Kariyer Seviyeleri"])
    
    with t1:
        with st.form("dep_add", clear_on_submit=True):
            d_name = st.text_input("Departman Adı")
            if st.form_submit_button("Ekle"):
                supabase.table("departmanlar").insert({"departman_adi": d_name}).execute()
                st.rerun()
        deps = db_fetch("departmanlar")
        if deps: st.table(pd.DataFrame(deps)[["departman_adi"]])

    with t2:
        deps = db_fetch("departmanlar")
        d_map = {d['departman_adi']: d['id'] for d in deps}
        with st.form("poz_add"):
            s_dep = st.selectbox("Departman Seçin", list(d_map.keys()))
            p_name = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Pozisyon Tanımla"):
                p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_name}).execute()
                p_id = p_res.data[0]['id']
                # Otomatik 6 Seviye Üretimi (J1-S)
                lvls = ["J1", "J2", "M1", "M2", "M3", "S"]
                supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_name} {l}", "seviye_kodu": l} for l in lvls]).execute()
                st.rerun()

    with t3:
        res = supabase.table("seviyeler").select("seviye_adi, pozisyonlar(pozisyon_adi)").execute()
        if res.data:
            df = pd.DataFrame([{"Seviye": r['seviye_adi'], "Bağlı Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res.data])
            st.data_editor(df, use_container_width=True, hide_index=True)

elif st.session_state.main_nav == "İşe Alım":
    st.title("Aday Takip Süreci")
    t1, t2 = st.tabs(["Yeni Kayıt", "Aday Havuzu"])
    
    with t1:
        with st.form("aday_form"):
            c1, c2 = st.columns(2)
            ad = c1.text_input("Ad Soyad")
            tc = c2.text_input("Kimlik No")
            if st.form_submit_button("Havuza Kaydet"):
                # Aday ve SCD Type 2 Versiyonlama Başlatma
                a_res = supabase.table("adaylar").insert({"ad_soyad": ad, "kimlik_no": tc}).execute()
                a_id = a_res.data[0]['id']
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": ad, "kimlik_no": tc, "ise_alim_sureci": "aday havuzu",
                    "baslangic_tarihi": datetime.now().isoformat()
                }).execute()
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.rerun()

    with t2:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*)").execute()
        if res.data:
            df_a = pd.DataFrame([{"Aday": r['ad_soyad'], "Durum": r['aday_versiyonlar']['ise_alim_sureci'].upper()} for r in res.data if r['aday_versiyonlar']])
            st.table(df_a)

elif st.session_state.main_nav == "Çalışanlar":
    st.title("Personel Listesi")
    # Personel transfer ve versiyon listeleme mantığı...
    res = db_fetch("personeller")
    if res: st.table(pd.DataFrame(res)[["ad_soyad", "kimlik_no"]])
