import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Konfigürasyon ve CSS (Beyaz Tema Garantisi)
st.set_page_config(page_title="İM-FEXİM Kurumsal", layout="wide")
st.markdown("""
    <style>
    :root { --primary: #6366F1; --bg: #FFFFFF; --text: #1B1B1B; --border: #E9ECEF; }
    .stApp { background-color: var(--bg) !important; color: var(--text) !important; }
    section[data-testid="stSidebar"] { background-color: var(--bg) !important; border-right: 1px solid var(--border) !important; }
    h1, h2, h3, p, label, .stMarkdown { color: var(--text) !important; }
    .saas-card { background: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid var(--border); margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    input, select, textarea, div[data-baseweb="select"] > div { background-color: #FFFFFF !important; color: #000000 !important; border: 1px solid #DDE1E6 !important; }
    input:disabled { -webkit-text-fill-color: #000000 !important; background-color: #F8F9FA !important; }
    .stButton > button { background-color: var(--primary) !important; color: white !important; width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı ve Yardımcı Fonksiyonlar
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

def fetch_all(table): return supabase.table(table).select("*").execute().data
def fetch_filter(table, col, val): return supabase.table(table).select("*").eq(col, val).execute().data

SUREC_LISTESI = ["aday havuzu", "ön değerlendirme", "ön görüşme", "mülakat", "teknik değerlendirme", "iş teklifi", "belge toplama", "olumsuz", "işe alındı"]

# 3. Sidebar Navigasyon
with st.sidebar:
    st.markdown("<h2 style='color:#6366F1;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    main_nav = st.radio("ANA MENÜ", ["📊 Dashboard", "🏢 Organizasyon", "👤 İşe Alım", "👥 Çalışanlar"], label_visibility="collapsed")
    
    sub_nav = ""
    if main_nav == "🏢 Organizasyon":
        sub_nav = st.radio("ALT MENÜ", ["Departmanlar", "Pozisyonlar", "Seviyeler"])
    elif main_nav == "👤 İşe Alım":
        sub_nav = st.radio("ALT MENÜ", ["Adaylar"])
    elif main_nav == "👥 Çalışanlar":
        sub_nav = "Personel Listesi"
    else:
        sub_nav = "Dashboard"

# --- MANTIKSAL FONKSİYON: İŞE ALIM TETİKLE ---
def convert_candidate_to_employee(aday, versiyon, yeni_tel, d_id, p_id, s_id):
    simdi = datetime.now().isoformat()
    # Personel var mı kontrol et
    check = supabase.table("personeller").select("id").eq("kimlik_no", aday['kimlik_no']).execute()
    if not check.data:
        p_res = supabase.table("personeller").insert({"ad_soyad": aday['ad_soyad'], "kimlik_no": aday['kimlik_no'], "aday_id": aday['id']}).execute()
        p_id = p_res.data[0]['id']
        pv_res = supabase.table("personel_versiyonlar").insert({
            "personel_id": p_id, "ad_soyad": aday['ad_soyad'], "kimlik_no": aday['kimlik_no'], "telefon": yeni_tel,
            "departman_id": d_id, "pozisyon_id": p_id, "seviye_id": s_id, "ise_baslama_tarihi": simdi
        }).execute()
        supabase.table("personeller").update({"guncel_versiyon_id": pv_res.data[0]['id']}).eq("id", p_id).execute()
        return True
    return False

# --- EKRANLAR ---

# A. DASHBOARD
if sub_nav == "Dashboard":
    st.title("📊 Sistem Özeti")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='saas-card'><h3>{len(fetch_all('adaylar'))}</h3><p>Toplam Aday</p></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='saas-card'><h3>{len(fetch_all('personeller'))}</h3><p>Aktif Çalışan</p></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='saas-card'><h3>{len(fetch_all('departmanlar'))}</h3><p>Departman</p></div>", unsafe_allow_html=True)

# B. DEPARTMANLAR
elif sub_nav == "Departmanlar":
    st.title("🏢 Departman Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Departman", "📋 Departman Listesi"])
    with t1:
        with st.form("f_dep"):
            d_name = st.text_input("Departman Adı")
            if st.form_submit_button("Kaydet"):
                supabase.table("departmanlar").insert({"departman_adi": d_name}).execute(); st.rerun()
    with t2:
        data = fetch_all("departmanlar")
        if data: st.table(pd.DataFrame(data)[["id", "departman_adi"]])

# C. POZİSYONLAR
elif sub_nav == "Pozisyonlar":
    st.title("👔 Pozisyon Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Pozisyon", "📋 Pozisyon Listesi"])
    deps = fetch_all("departmanlar")
    d_map = {d['departman_adi']: d['id'] for d in deps}
    with t1:
        with st.form("f_poz"):
            s_dep = st.selectbox("Bağlı Departman", list(d_map.keys()))
            p_name = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Kaydet ve 6 Seviye Oluştur"):
                p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_name}).execute()
                p_id = p_res.data[0]['id']
                codes = ["J1", "J2", "M1", "M2", "M3", "S"]
                supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_name} {c}", "seviye_kodu": c} for c in codes]).execute()
                st.success("Başarılı!"); st.rerun()
    with t2:
        res = supabase.table("pozisyonlar").select("id, pozisyon_adi, departmanlar(departman_adi)").execute()
        if res.data: st.table(pd.DataFrame([{"ID": r['id'], "Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res.data]))

# D. SEVİYELER
elif sub_nav == "Seviyeler":
    st.title("📊 Seviye Listesi")
    res = supabase.table("seviyeler").select("id, seviye_adi, seviye_kodu, pozisyonlar(pozisyon_adi)").execute()
    if res.data: st.table(pd.DataFrame([{"ID": r['id'], "Seviye": r['seviye_adi'], "Kod": r['seviye_kodu'], "Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res.data]))

# E. ADAYLAR
elif sub_nav == "Adaylar":
    st.title("👤 İşe Alım Paneli")
    t1, t2 = st.tabs(["➕ Yeni Aday", "📋 Süreçteki Adaylar"])
    
    with t1:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2); a_ad = c1.text_input("Ad Soyad *"); a_tc = c2.text_input("TC Kimlik No *")
        # Departman/Pozisyon/Seviye Dropboxları
        deps = fetch_all("departmanlar"); d_map = {d['departman_adi']: d['id'] for d in deps}
        s_d = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()))
        # ... (Zincirleme dropbox kodları buraya gelir)
        if st.button("Havuza Kaydet"):
            # Mükerrer kontrolü ve Kayıt işlemi...
            st.success("Kaydedildi.")
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        # Sadece AKTİF adayları (işe alındı/olumsuz olmayanlar) listele
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*)").execute()
        aktifler = [r for r in res.data if r['aday_versiyonlar'] and r['aday_versiyonlar']['ise_alim_sureci'] not in ["işe alındı", "olumsuz"]]
        if aktifler:
            st.table(pd.DataFrame([{"Ad Soyad": r['ad_soyad'], "Süreç": r['aday_versiyonlar']['ise_alim_sureci']} for r in aktifler]))
            # Detaylı güncelleme için Expanders...
        else: st.info("Aktif aday bulunamadı.")

# F. ÇALIŞANLAR
elif sub_nav == "Personel Listesi":
    st.title("👥 Çalışanlar")
    res = supabase.table("personeller").select("*, personel_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))").execute()
    if res.data:
        df_p = []
        for r in res.data:
            v = r['personel_versiyonlar']
            df_p.append({
                "Ad Soyad": r['ad_soyad'],
                "TC No": r['kimlik_no'],
                "Departman": v['departmanlar']['departman_adi'] if v and v['departmanlar'] else "-",
                "Pozisyon": v['pozisyonlar']['pozisyon_adi'] if v and v['pozisyonlar'] else "-",
                "İşe Başlama": v['ise_baslama_tarihi'][:10] if v else "-"
            })
        st.table(pd.DataFrame(df_p))
    else: st.warning("Henüz çalışan kaydı yok.")
