import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM Admin", layout="wide")

# 2. RADİKAL BEYAZLATMA CSS (Her butonu ayrı ayrı hedefler)
st.markdown("""
    <style>
    /* Global Beyaz Zemin */
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
    }

    /* 1. SOL MENÜ BUTONLARI (Sidebar içindeki tüm butonları beyaz yapar) */
    section[data-testid="stSidebar"] button {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #E5E7EB !important;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #F9FAFB !important;
        border-color: #111827 !important;
    }

    /* 2. FORM İÇİNDEKİ BUTONLAR (Havuza Kaydet vb.) */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        border-color: #111827 !important;
        background-color: #F9FAFB !important;
    }

    /* 3. INPUT VE DROPBOX BEYAZLATMA (Siyah bantları yok eder) */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #D1D5DB !important;
    }
    input { color: #000000 !important; }

    /* 4. TÜM YAZILAR SİMSİYAH */
    h1, h2, h3, h4, p, span, label, div {
        color: #000000 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 5. TABLAR (Üstteki Sekmeler) */
    .stTabs [data-baseweb="tab-list"] { background-color: #FFFFFF !important; }
    .stTabs [data-baseweb="tab"] { color: #6B7280 !important; }
    .stTabs [aria-selected="true"] { color: #000000 !important; border-bottom: 2px solid #000000 !important; }

    /* Sidebar Hiyerarşisi */
    .nav-header { font-size: 11px; font-weight: 700; color: #9CA3AF; margin: 20px 0 10px 15px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 3. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 4. Sayfa Kontrolü
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# --- SOL MENÜ (Sidebar) ---
with st.sidebar:
    st.markdown("<h3 style='padding-left:15px; font-weight:700;'>İM-FEXİM</h3>", unsafe_allow_html=True)
    st.markdown("<div class='nav-header'>Yönetim</div>", unsafe_allow_html=True)
    if st.button("📊 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
    if st.button("🏢 Organizasyon", use_container_width=True): st.session_state.page = "Organizasyon"
    
    st.markdown("<div class='nav-header'>İK Süreçleri</div>", unsafe_allow_html=True)
    if st.button("👤 İşe Alım (ATS)", use_container_width=True): st.session_state.page = "ATS"
    if st.button("👥 Çalışanlar (HRM)", use_container_width=True): st.session_state.page = "HRM"

# --- SAĞ TARAF (Ana İçerik) ---

# A. DASHBOARD
if st.session_state.page == "Dashboard":
    st.title("Dashboard")
    st.write("Sistem özeti burada listelenecektir.")

# B. ORGANİZASYON (Departman -> Pozisyon -> 6 Seviye)
elif st.session_state.page == "Organizasyon":
    st.title("Organizasyon Yapılandırması")
    tab_dep, tab_poz, tab_sev = st.tabs(["Departmanlar", "Pozisyonlar", "Seviye Listesi"])
    
    with tab_dep:
        with st.form("d_form", clear_on_submit=True):
            d_name = st.text_input("Yeni Departman Adı")
            if st.form_submit_button("Departman Oluştur"):
                supabase.table("departmanlar").insert({"departman_adi": d_name}).execute()
                st.rerun()
        # Listeleme
        res = supabase.table("departmanlar").select("*").execute()
        if res.data: st.table(pd.DataFrame(res.data)[["departman_adi"]])

    with tab_poz:
        deps = supabase.table("departmanlar").select("*").execute().data
        dep_map = {d['departman_adi']: d['id'] for d in deps}
        with st.form("p_form"):
            s_dep = st.selectbox("Departman Seç", list(dep_map.keys()))
            p_name = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Pozisyonu ve Seviyeleri Tanımla"):
                p_id = supabase.table("pozisyonlar").insert({"departman_id": dep_map[s_dep], "pozisyon_adi": p_name}).execute().data[0]['id']
                # Otomatik 6 Seviye Üretimi
                codes = ["J1", "J2", "M1", "M2", "M3", "S"]
                supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_name} {c}", "seviye_kodu": c} for c in codes]).execute()
                st.rerun()

# C. ATS (Aday Versiyonlama ve İşe Alım)
elif st.session_state.page == "ATS":
    st.title("Aday Takip ve Versiyonlama")
    t1, t2 = st.tabs(["Yeni Aday Kaydı", "Aday Havuzu"])
    
    with t1:
        with st.form("c_form"):
            ad = st.text_input("Ad Soyad")
            tc = st.text_input("Kimlik No")
            if st.form_submit_button("Havuza Kaydet"):
                a_id = supabase.table("adaylar").insert({"ad_soyad": ad, "kimlik_no": tc}).execute().data[0]['id']
                # Versiyonlama (SCD Type 2 Başlangıcı)
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
