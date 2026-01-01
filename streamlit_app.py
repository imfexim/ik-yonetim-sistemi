import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu ve Zorunlu Beyaz Tema Ayarları
st.set_page_config(page_title="İM-FEXİM Kurumsal", layout="wide", initial_sidebar_state="expanded")

# CSS - SaaS estetiği ve Beyaz Tema Zorlaması
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    :root { --primary: #6366F1; --bg: #FFFFFF; --text: #1B1B1B; --border: #E9ECEF; }
    .stApp { background-color: var(--bg) !important; color: var(--text) !important; }
    section[data-testid="stSidebar"] { background-color: var(--bg) !important; border-right: 1px solid var(--border) !important; }
    h1, h2, h3, p, label, .stMarkdown { color: var(--text) !important; font-family: 'Inter', sans-serif; }
    .saas-card { background: #FFFFFF; padding: 24px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid var(--border); margin-bottom: 20px; }
    input, select, textarea, div[data-baseweb="select"] > div { background-color: #FFFFFF !important; color: #000000 !important; border: 1px solid #DDE1E6 !important; border-radius: 8px !important; }
    input:disabled { -webkit-text-fill-color: #000000 !important; background-color: #F8F9FA !important; }
    .stButton > button { background-color: var(--primary) !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: 500 !important; width: 100%; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- VERİ FONKSİYONLARI ---
def fetch_all(table): return supabase.table(table).select("*").execute().data
def fetch_filter(table, col, val): return supabase.table(table).select("*").eq(col, val).execute().data

SUREC_LISTESI = [
    "aday havuzu", "ön değerlendirme", "ön görüşme", "mülakat", 
    "teknik değerlendirme", "iş teklifi", "belge toplama", "olumsuz", "işe alındı"
]

# 3. Yan Menü
with st.sidebar:
    st.markdown("<h2 style='color:#6366F1;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    main_nav = st.radio("MENÜ", ["📊 Dashboard", "🏢 Organizasyon", "👤 İşe Alım"], label_visibility="collapsed")
    if main_nav == "🏢 Organizasyon":
        sub_nav = st.radio("ALT", ["Departmanlar", "Pozisyonlar", "Seviyeler"])
    elif main_nav == "👤 İşe Alım":
        sub_nav = st.radio("ALT", ["Adaylar"])
    else: sub_nav = "Dashboard"

# --- EKRANLAR (Organizasyon kısımları korunmuştur) ---

if sub_nav == "Dashboard":
    st.subheader("Sistem Özeti")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='saas-card'><p>Toplam Aday</p><h2>{len(fetch_all('adaylar'))}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='saas-card'><p>Pozisyonlar</p><h2>{len(fetch_all('pozisyonlar'))}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='saas-card'><p>Departmanlar</p><h2>{len(fetch_all('departmanlar'))}</h2></div>", unsafe_allow_html=True)

elif sub_nav == "Departmanlar":
    st.subheader("🏢 Departman Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Ekle", "📋 Liste"])
    with t1:
        with st.form("dep_add"):
            d_name = st.text_input("Departman Adı")
            if st.form_submit_button("Kaydet"):
                if d_name: supabase.table("departmanlar").insert({"departman_adi": d_name}).execute(); st.rerun()
    with t2:
        res = fetch_all("departmanlar")
        if res: st.table(pd.DataFrame(res)[["departman_adi"]])

elif sub_nav == "Pozisyonlar":
    st.subheader("👔 Pozisyon Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Ekle", "📋 Liste"])
    deps = fetch_all("departmanlar")
    with t1:
        with st.form("poz_add"):
            d_map = {d['departman_adi']: d['id'] for d in deps}
            s_dep = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()))
            p_name = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Kaydet"):
                if s_dep != "Seçiniz..." and p_name:
                    p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_name}).execute()
                    p_id = p_res.data[0]['id']
                    codes = ["J1", "J2", "M1", "M2", "M3", "S"]
                    supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_name} {c}", "seviye_kodu": c} for c in codes]).execute()
                    st.rerun()
    with t2:
        res = supabase.table("pozisyonlar").select("pozisyon_adi, departmanlar(departman_adi)").execute()
        if res.data: st.table(pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res.data]))

elif sub_nav == "Seviyeler":
    st.subheader("📊 Kariyer Seviyeleri")
    res = supabase.table("seviyeler").select("seviye_adi, pozisyonlar(pozisyon_adi)").execute()
    if res.data: st.table(pd.DataFrame([{"Seviye": r['seviye_adi'], "Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res.data]))

elif sub_nav == "Adaylar":
    st.subheader("👤 Aday Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Aday Kaydı", "📋 Liste ve Süreç Güncelleme"])
    
    with t1:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        n_ad = c1.text_input("Ad Soyad *")
        n_tc = c2.text_input("Kimlik No *")
        n_tel = st.text_input("Telefon")
        
        deps = fetch_all("departmanlar")
        d_map = {d['departman_adi']: d['id'] for d in deps}
        s_d = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()))
        
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

        n_cv = st.file_uploader("CV Yükle (PDF)", type=['pdf'])

        if st.button("🚀 Adayı Havuza Ekle"):
            if n_ad and n_tc:
                cv_url = None
                if n_cv:
                    f_name = f"cv_{n_tc}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
                    supabase.storage.from_("cv_bucket").upload(f_name, n_cv.read())
                    cv_url = supabase.storage.from_("cv_bucket").get_public_url(f_name)

                a_res = supabase.table("adaylar").insert({"ad_soyad": n_ad, "kimlik_no": n_tc}).execute()
                a_id = a_res.data[0]['id']
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": n_ad, "kimlik_no": n_tc, "telefon": n_tel, "cv_url": cv_url,
                    "departman_id": d_map.get(s_d), "pozisyon_id": n_p_id, "seviye_id": n_s_id,
                    "ise_alim_sureci": "aday havuzu", # DEFAULT DEĞER
                    "islemi_yapan": "Sistemsel", "baslangic_tarihi": datetime.now().isoformat()
                }).execute()
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.success("Aday başarıyla 'Aday Havuzu'na eklendi."); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi), seviyeler(seviye_adi))").execute()
        for aday in res.data:
            v = aday['aday_versiyonlar']
            # Liste satırında süreci görselleştirme
            label = f"👤 {aday['ad_soyad']} | 📍 {v['ise_alim_sureci'].upper() if v else 'ADAY HAVUZU'}"
            with st.expander(label):
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                
                # 1. Süreç Yönetimi (Sizin İstediğiniz Dropbox)
                current_process = v['ise_alim_sureci'] if v and v['ise_alim_sureci'] else "aday havuzu"
                new_process = st.selectbox(
                    "İşe Alım Süreci Güncelle", 
                    SUREC_LISTESI, 
                    index=SUREC_LISTESI.index(current_process) if current_process in SUREC_LISTESI else 0,
                    key=f"proc_{aday['id']}"
                )
                
                st.markdown("---")
                
                # 2. Diğer Bilgiler
                st.text_input("Ad Soyad (Sabit)", value=aday['ad_soyad'], disabled=True, key=f"f_ad_{aday['id']}")
                u_tel = st.text_input("Telefon", value=v['telefon'] if v else "", key=f"u_tel_{aday['id']}")
                
                u_d = st.selectbox("Yeni Departman", ["Seçiniz..."] + list(d_map.keys()), key=f"u_d_{aday['id']}")
                u_p_id, u_s_id = None, None
                if u_d != "Seçiniz...":
                    u_pozs = fetch_filter("pozisyonlar", "departman_id", d_map[u_d])
                    u_p_map = {p['pozisyon_adi']: p['id'] for p in u_pozs}
                    u_p = st.selectbox("Yeni Pozisyon", ["Seçiniz..."] + list(u_p_map.keys()), key=f"u_p_{aday['id']}")
                    if u_p != "Seçiniz...":
                        u_p_id = u_p_map[u_p]
                        u_sevs = fetch_filter("seviyeler", "pozisyon_id", u_p_id)
                        u_s_map = {sv['seviye_adi']: sv['id'] for sv in u_sevs}
                        u_s = st.selectbox("Yeni Seviye", ["Seçiniz..."] + list(u_s_map.keys()), key=f"u_s_{aday['id']}")
                        if u_s != "Seçiniz...": u_s_id = u_s_map[u_s]

                if st.button("🔄 Süreci ve Bilgileri Güncelle", key=f"btn_{aday['id']}"):
                    simdi = datetime.now().isoformat()
                    if v: supabase.table("aday_versiyonlar").update({"bitis_tarihi": simdi}).eq("id", v['id']).execute()
                    
                    nv = supabase.table("aday_versiyonlar").insert({
                        "aday_id": aday['id'], "ad_soyad": aday['ad_soyad'], "kimlik_no": aday['kimlik_no'], 
                        "telefon": u_tel, 
                        "ise_alim_sureci": new_process, # GÜNCELLENEN SÜREÇ
                        "departman_id": d_map.get(u_d) if u_d != "Seçiniz..." else v['departman_id'], 
                        "pozisyon_id": u_p_id if u_p_id else v['pozisyon_id'], 
                        "seviye_id": u_s_id if u_s_id else v['seviye_id'],
                        "islemi_yapan": "İK Paneli", "baslangic_tarihi": simdi
                    }).execute()
                    
                    supabase.table("adaylar").update({"guncel_versiyon_id": nv.data[0]['id']}).eq("id", aday['id']).execute()
                    st.success(f"Aday süreci '{new_process}' olarak güncellendi."); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
