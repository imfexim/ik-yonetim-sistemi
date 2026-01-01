import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import io

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM | Yönetim Paneli", layout="wide", initial_sidebar_state="expanded")

# 2. Preline UI / Modern SaaS Stil Paketi
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Temel Zemin */
    .stApp { background-color: #F9FAFB !important; color: #1F2937 !important; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Tasarımı */
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E5E7EB !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #4B5563 !important; font-weight: 600; font-size: 0.8rem; margin-bottom: -10px; }
    
    /* Kart Yapısı (Preline Tarzı) */
    .cms-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 1.25rem;
    }

    /* Girdi Alanları */
    input, select, textarea, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 0.5rem !important;
        color: #1F2937 !important;
    }
    input:focus { border-color: #2563EB !important; box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1) !important; }
    
    /* Okunabilir Disabled Alanlar */
    input:disabled { -webkit-text-fill-color: #111827 !important; background-color: #F3F4F6 !important; font-weight: 500; opacity: 1; }

    /* Butonlar (Preline Blue) */
    .stButton > button {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 0.5rem !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 500 !important;
        transition: all 0.2s;
    }
    .stButton > button:hover { background-color: #1D4ED8 !important; transform: translateY(-1px); }

    /* Tablar */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 2rem; border-bottom: 1px solid #E5E7EB; }
    .stTabs [data-baseweb="tab"] { font-weight: 500; color: #6B7280; }
    .stTabs [aria-selected="true"] { color: #2563EB !important; border-bottom-color: #2563EB !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Veritabanı Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- YARDIMCI FONKSİYONLAR ---
def fetch_all(table): return supabase.table(table).select("*").execute().data
def fetch_filter(table, col, val): return supabase.table(table).select("*").eq(col, val).execute().data

SUREC_LISTESI = ["aday havuzu", "ön değerlendirme", "ön görüşme", "mülakat", "teknik değerlendirme", "iş teklifi", "belge toplama", "olumsuz", "işe alındı"]

# 4. Yan Menü (CMS Hiyerarşisi)
with st.sidebar:
    st.markdown("<h2 style='color:#2563EB; font-weight:700;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("MAIN")
    main_nav = st.radio("MAIN", ["Dashboard", "Organizasyon", "İşe Alım", "Çalışanlar"], label_visibility="collapsed")
    
    sub_nav = ""
    if main_nav == "Organizasyon":
        st.markdown("RESOURCES")
        sub_nav = st.radio("ORG", ["Departmanlar", "Pozisyonlar", "Seviyeler"], label_visibility="collapsed")
    elif main_nav == "İşe Alım":
        st.markdown("CANDIDATES")
        sub_nav = st.radio("REC", ["Adaylar"], label_visibility="collapsed")
    elif main_nav == "Çalışanlar":
        st.markdown("MEMBERS")
        sub_nav = "Personel Listesi"
    else:
        sub_nav = "Dashboard"

# --- EKRANLAR ---

if sub_nav == "Dashboard":
    st.title("Dashboard")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='cms-card'><p style='color:#6B7280; font-size:0.875rem;'>Aktif Adaylar</p><h2 style='margin:0;'>{len(fetch_all('adaylar'))}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='cms-card'><p style='color:#6B7280; font-size:0.875rem;'>Toplam Çalışan</p><h2 style='margin:0;'>{len(fetch_all('personeller'))}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='cms-card'><p style='color:#6B7280; font-size:0.875rem;'>Departmanlar</p><h2 style='margin:0;'>{len(fetch_all('departmanlar'))}</h2></div>", unsafe_allow_html=True)

# --- 🏢 ORGANİZASYON: DEPARTMANLAR ---
elif sub_nav == "Departmanlar":
    st.title("Departman Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Departman", "📋 Departman Listesi"])
    with t1:
        st.markdown("<div class='cms-card'>", unsafe_allow_html=True)
        with st.form("f_dep", clear_on_submit=True):
            d_name = st.text_input("Departman Adı", placeholder="Örn: Bilgi Teknolojileri")
            if st.form_submit_button("Departmanı Kaydet"):
                if d_name: supabase.table("departmanlar").insert({"departman_adi": d_name}).execute(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with t2:
        deps = fetch_all("departmanlar")
        if deps: st.table(pd.DataFrame(deps)[["departman_adi"]])

# --- 👔 ORGANİZASYON: POZİSYONLAR ---
elif sub_nav == "Pozisyonlar":
    st.title("Pozisyon & Ünvan Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Pozisyon", "📋 Pozisyon Listesi"])
    deps = fetch_all("departmanlar")
    with t1:
        st.markdown("<div class='cms-card'>", unsafe_allow_html=True)
        with st.form("f_poz", clear_on_submit=True):
            d_map = {d['departman_adi']: d['id'] for d in deps}
            s_dep = st.selectbox("Bağlı Departman", ["Seçiniz..."] + list(d_map.keys()))
            p_name = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Pozisyonu ve Seviyeleri Oluştur"):
                if s_dep != "Seçiniz..." and p_name:
                    p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_name}).execute()
                    p_id = p_res.data[0]['id']
                    codes = ["J1", "J2", "M1", "M2", "M3", "S"]
                    supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_name} {c}", "seviye_kodu": c} for c in codes]).execute()
                    st.success("Kayıt Başarılı."); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with t2:
        res = supabase.table("pozisyonlar").select("pozisyon_adi, departmanlar(departman_adi)").execute()
        if res.data: st.table(pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res.data]))

# --- 📊 ORGANİZASYON: SEVİYELER ---
elif sub_nav == "Seviyeler":
    st.title("Kariyer Seviyeleri Listesi")
    res = supabase.table("seviyeler").select("seviye_adi, pozisyonlar(pozisyon_adi)").execute()
    if res.data: st.table(pd.DataFrame([{"Seviye": r['seviye_adi'], "Bağlı Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res.data]))

# --- 👤 İŞE ALIM: ADAYLAR ---
elif sub_nav == "Adaylar":
    st.title("Aday Takip Sistemi (ATS)")
    t1, t2 = st.tabs(["➕ Yeni Aday Kaydı", "📋 Aktif Aday Havuzu"])
    
    with t1:
        st.markdown("<div class='cms-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        n_ad = c1.text_input("Ad Soyad *")
        n_tc = c2.text_input("Kimlik No *")
        n_tel = st.text_input("Telefon")
        
        # Zincirleme Dropboxlar
        deps = fetch_all("departmanlar"); d_map = {d['departman_adi']: d['id'] for d in deps}
        s_d = st.selectbox("Departman Seçiniz", ["Seçiniz..."] + list(d_map.keys()))
        
        n_p_id, n_s_id = None, None
        if s_d != "Seçiniz...":
            pozs = fetch_filter("pozisyonlar", "departman_id", d_map[s_d])
            p_map = {p['pozisyon_adi']: p['id'] for p in pozs}
            s_p = st.selectbox("Pozisyon Seçiniz", ["Seçiniz..."] + list(p_map.keys()))
            if s_p != "Seçiniz...":
                n_p_id = p_map[s_p]
                sevs = fetch_filter("seviyeler", "pozisyon_id", n_p_id)
                sv_map = {sv['seviye_adi']: sv['id'] for sv in sevs}
                s_s = st.selectbox("Seviye Seçiniz", ["Seçiniz..."] + list(sv_map.keys()))
                if s_s != "Seçiniz...": n_s_id = sv_map[s_s]

        n_cv = st.file_uploader("CV Yükle (PDF)", type=['pdf'])

        if st.button("🚀 Adayı Kaydet"):
            if n_ad and n_tc:
                check = supabase.table("adaylar").select("id").eq("kimlik_no", n_tc).execute()
                if check.data: st.error("Bu kimlik numarasıyla daha önce kayıt açılmış.")
                else:
                    # CV Upload logic...
                    a_res = supabase.table("adaylar").insert({"ad_soyad": n_ad, "kimlik_no": n_tc}).execute()
                    a_id = a_res.data[0]['id']
                    v_res = supabase.table("aday_versiyonlar").insert({
                        "aday_id": a_id, "ad_soyad": n_ad, "kimlik_no": n_tc, "telefon": n_tel,
                        "departman_id": d_map.get(s_d), "pozisyon_id": n_p_id, "seviye_id": n_s_id,
                        "ise_alim_sureci": "aday havuzu", "baslangic_tarihi": datetime.now().isoformat()
                    }).execute()
                    supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                    st.success("Aday başarıyla havuza eklendi."); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        # AKTİF ADAY LİSTESİ (Tablo Görünümü + Detay)
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))").execute()
        aktif_adaylar = [r for r in res.data if r['aday_versiyonlar'] and r['aday_versiyonlar']['ise_alim_sureci'] not in ["işe alındı", "olumsuz"]]
        
        if aktif_adaylar:
            st.table(pd.DataFrame([{"Ad Soyad": r['ad_soyad'], "Süreç": r['aday_versiyonlar']['ise_alim_sureci'], "Pozisyon": r['aday_versiyonlar']['pozisyonlar']['pozisyon_adi']} for r in aktif_adaylar]))
            
            for aday in aktif_adaylar:
                v = aday['aday_versiyonlar']
                with st.expander(f"GÜNCELLE: {aday['ad_soyad']}"):
                    st.markdown("<div class='cms-card'>", unsafe_allow_html=True)
                    new_proc = st.selectbox("Süreç Değiştir", SUREC_LISTESI, index=SUREC_LISTESI.index(v['ise_alim_sureci']), key=f"up_{aday['id']}")
                    u_tel = st.text_input("Telefon", value=v['telefon'] if v else "", key=f"ut_{aday['id']}")
                    
                    if st.button("Kaydet ve Versiyonla", key=f"ub_{aday['id']}"):
                        simdi = datetime.now().isoformat()
                        supabase.table("aday_versiyonlar").update({"bitis_tarihi": simdi}).eq("id", v['id']).execute()
                        nv = supabase.table("aday_versiyonlar").insert({
                            "aday_id": aday['id'], "ad_soyad": aday['ad_soyad'], "kimlik_no": aday['kimlik_no'], 
                            "telefon": u_tel, "ise_alim_sureci": new_proc, "baslangic_tarihi": simdi,
                            "departman_id": v['departman_id'], "pozisyon_id": v['pozisyon_id'], "seviye_id": v['seviye_id']
                        }).execute()
                        supabase.table("adaylar").update({"guncel_versiyon_id": nv.data[0]['id']}).eq("id", aday['id']).execute()
                        
                        # İŞE ALINDI TETİKLEMESİ
                        if new_proc == "işe alındı":
                            p_res = supabase.table("personeller").insert({"ad_soyad": aday['ad_soyad'], "kimlik_no": aday['kimlik_no'], "aday_id": aday['id']}).execute()
                            pv_res = supabase.table("personel_versiyonlar").insert({
                                "personel_id": p_res.data[0]['id'], "ad_soyad": aday['ad_soyad'], "kimlik_no": aday['kimlik_no'],
                                "telefon": u_tel, "departman_id": v['departman_id'], "pozisyon_id": v['pozisyon_id'], 
                                "seviye_id": v['seviye_id'], "ise_baslama_tarihi": simdi
                            }).execute()
                            supabase.table("personeller").update({"guncel_versiyon_id": pv_res.data[0]['id']}).eq("id", p_res.data[0]['id']).execute()
                            st.balloons()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

# --- 👥 ÇALIŞANLAR: PERSONEL LİSTESİ ---
elif sub_nav == "Personel Listesi":
    st.title("Çalışan Portföyü")
    res = supabase.table("personeller").select("*, personel_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))").execute()
    if res.data:
        p_list = []
        for r in res.data:
            v = r['personel_versiyonlar']
            p_list.append({
                "Ad Soyad": r['ad_soyad'],
                "TC No": r['kimlik_no'],
                "Departman": v['departmanlar']['departman_adi'] if v and v['departmanlar'] else "-",
                "Pozisyon": v['pozisyonlar']['pozisyon_adi'] if v and v['pozisyonlar'] else "-",
                "Giriş Tarihi": v['ise_baslama_tarihi'][:10] if v else "-"
            })
        st.table(pd.DataFrame(p_list))
    else: st.info("Henüz aktif çalışan kaydı bulunmamaktadır.")
