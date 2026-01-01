import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM | Admin", layout="wide", initial_sidebar_state="expanded")

# 2. Premium SaaS & Minimalist CSS Tasarımı
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Reset */
    .stApp { background-color: #F9FAFB !important; color: #111827 !important; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Styling - Premium Minimalist */
    [data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        border-right: 1px solid #E5E7EB !important; 
        padding: 1rem 0 !important;
    }
    
    /* Sidebar Navigation Links */
    .nav-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #9CA3AF;
        margin: 1.5rem 0 0.5rem 1.25rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* CMS Cards (Görseldeki gibi gölgeli ve temiz) */
    .cms-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }

    /* Input Alanları */
    input, select, textarea, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
        color: #111827 !important;
        font-size: 0.9rem !important;
    }

    /* Premium Button (Mavi Accent) */
    .stButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: background-color 0.2s;
    }
    .stButton > button:hover { background-color: #1D4ED8 !important; }

    /* Lucide Ikon Simülasyonu için Sidebar CSS */
    .stRadio [data-testid="stWidgetLabel"] { display: none; }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #E5E7EB; }
    .stTabs [data-baseweb="tab"] { color: #6B7280; font-weight: 500; font-size: 0.875rem; }
    .stTabs [aria-selected="true"] { color: #2563EB !important; }

    </style>
    """, unsafe_allow_html=True)

# 3. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- YARDIMCI FONKSİYONLAR ---
def fetch_all(table): return supabase.table(table).select("*").execute().data
def fetch_filter(table, col, val): return supabase.table(table).select("*").eq(col, val).execute().data

# 4. Yan Menü (Minimalist & Premium İkon İsimleri)
with st.sidebar:
    st.markdown("<h2 style='color:#111827; font-weight:700; padding-left:1.25rem;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280; font-size:0.8rem; padding-left:1.25rem; margin-top:-10px;'>Kurumsal Portal</p>", unsafe_allow_html=True)
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='nav-label'>Genel Bakış</div>", unsafe_allow_html=True)
    main_nav = st.radio("MAIN", ["Dashboard", "Organizasyon", "İşe Alım", "Çalışanlar"], label_visibility="collapsed")
    
    sub_nav = ""
    if main_nav == "Organizasyon":
        st.markdown("<div class='nav-label'>Kaynak Yönetimi</div>", unsafe_allow_html=True)
        sub_nav = st.radio("ORG", ["Departmanlar", "Pozisyonlar", "Seviyeler"], label_visibility="collapsed")
    elif main_nav == "İşe Alım":
        st.markdown("<div class='nav-label'>Süreçler</div>", unsafe_allow_html=True)
        sub_nav = st.radio("REC", ["Adaylar"], label_visibility="collapsed")
    elif main_nav == "Çalışanlar":
        st.markdown("<div class='nav-label'>Kadrolar</div>", unsafe_allow_html=True)
        sub_nav = "Personel Listesi"
    else:
        sub_nav = "Dashboard"

# --- EKRANLAR ---

if sub_nav == "Dashboard":
    st.markdown("### Dashboard")
    c1, c2, c3 = st.columns(3)
    c1.markdown("<div class='cms-card'><span style='color:#6B7280; font-size:0.8rem;'>Adaylar</span><h2 style='margin:0;'>24</h2></div>", unsafe_allow_html=True)
    c2.markdown("<div class='cms-card'><span style='color:#6B7280; font-size:0.8rem;'>Personeller</span><h2 style='margin:0;'>112</h2></div>", unsafe_allow_html=True)
    c3.markdown("<div class='cms-card'><span style='color:#6B7280; font-size:0.8rem;'>Açık Pozisyonlar</span><h2 style='margin:0;'>8</h2></div>", unsafe_allow_html=True)

# --- 🏢 DEPARTMANLAR ---
elif sub_nav == "Departmanlar":
    st.markdown("### Departman Yönetimi")
    t1, t2 = st.tabs(["Ekle", "Liste"])
    with t1:
        st.markdown("<div class='cms-card'>", unsafe_allow_html=True)
        with st.form("f_dep", clear_on_submit=True):
            d_name = st.text_input("Departman Adı")
            if st.form_submit_button("Departmanı Kaydet"):
                if d_name: supabase.table("departmanlar").insert({"departman_adi": d_name}).execute(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with t2:
        deps = fetch_all("departmanlar")
        if deps: st.table(pd.DataFrame(deps)[["departman_adi"]])

# --- 👔 POZİSYONLAR ---
elif sub_nav == "Pozisyonlar":
    st.markdown("### Pozisyon Yönetimi")
    t1, t2 = st.tabs(["Yeni Pozisyon", "Mevcut Pozisyonlar"])
    deps = fetch_all("departmanlar")
    with t1:
        st.markdown("<div class='cms-card'>", unsafe_allow_html=True)
        with st.form("f_poz", clear_on_submit=True):
            d_map = {d['departman_adi']: d['id'] for d in deps}
            s_dep = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()))
            p_name = st.text_input("Pozisyon Unvanı")
            if st.form_submit_button("Pozisyon Tanımla"):
                if s_dep != "Seçiniz..." and p_name:
                    p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_name}).execute()
                    p_id = p_res.data[0]['id']
                    # Kariyer Seviyeleri (J1-S)
                    codes = ["J1", "J2", "M1", "M2", "M3", "S"]
                    supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_name} {c}", "seviye_kodu": c} for c in codes]).execute()
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with t2:
        res = supabase.table("pozisyonlar").select("pozisyon_adi, departmanlar(departman_adi)").execute()
        if res.data: st.table(pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res.data]))

# --- 👤 ADAYLAR ---
elif sub_nav == "Adaylar":
    st.markdown("### Aday Takip (ATS)")
    t1, t2 = st.tabs(["Aday Ekle", "Havuzu Görüntüle"])
    
    with t1:
        st.markdown("<div class='cms-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        n_ad = c1.text_input("Ad Soyad")
        n_tc = c2.text_input("TC Kimlik No")
        n_tel = st.text_input("İletişim")
        
        # Bağımlı Dropboxlar
        deps = fetch_all("departmanlar"); d_map = {d['departman_adi']: d['id'] for d in deps}
        s_d = st.selectbox("İlgili Departman", ["Seçiniz..."] + list(d_map.keys()))
        
        n_p_id, n_s_id = None, None
        if s_d != "Seçiniz...":
            pozs = fetch_filter("pozisyonlar", "departman_id", d_map[s_d])
            p_map = {p['pozisyon_adi']: p['id'] for p in pozs}
            s_p = st.selectbox("Pozisyon", ["Seçiniz..."] + list(p_map.keys()))
            if s_p != "Seçiniz...":
                n_p_id = p_map[s_p]
                sevs = fetch_filter("seviyeler", "pozisyon_id", n_p_id)
                sv_map = {sv['seviye_adi']: sv['id'] for sv in sevs}
                s_s = st.selectbox("Seviye", ["Seçiniz..."] + list(sv_map.keys()))
                if s_s != "Seçiniz...": n_s_id = sv_map[s_s]

        if st.button("Adayı Arşive Kaydet"):
            if n_ad and n_tc:
                a_res = supabase.table("adaylar").insert({"ad_soyad": n_ad, "kimlik_no": n_tc}).execute()
                a_id = a_res.data[0]['id']
                # Versiyonlama SCD Type 2
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": n_ad, "kimlik_no": n_tc, "telefon": n_tel,
                    "departman_id": d_map.get(s_d), "pozisyon_id": n_p_id, "seviye_id": n_s_id,
                    "ise_alim_sureci": "aday havuzu", "baslangic_tarihi": datetime.now().isoformat()
                }).execute()
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.success("Aday oluşturuldu."); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))").execute()
        aktif_adaylar = [r for r in res.data if r['aday_versiyonlar'] and r['aday_versiyonlar']['ise_alim_sureci'] not in ["işe alındı", "olumsuz"]]
        if aktif_adaylar:
            st.table(pd.DataFrame([{"Aday": r['ad_soyad'], "Aşama": r['aday_versiyonlar']['ise_alim_sureci']} for r in aktif_adaylar]))
        else: st.info("Süreçte aday yok.")

# --- 👥 PERSONELLER ---
elif sub_nav == "Personel Listesi":
    st.markdown("### Çalışan Kayıtları")
    res = supabase.table("personeller").select("*, personel_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))").execute()
    if res.data:
        p_list = []
        for r in res.data:
            v = r['personel_versiyonlar']
            p_list.append({
                "Ad Soyad": r['ad_soyad'],
                "Departman": v['departmanlar']['departman_adi'] if v and v['departmanlar'] else "-",
                "Pozisyon": v['pozisyonlar']['pozisyon_adi'] if v and v['pozisyonlar'] else "-"
            })
        st.table(pd.DataFrame(p_list))
    else: st.info("Aktif personel kaydı bulunamadı.")
