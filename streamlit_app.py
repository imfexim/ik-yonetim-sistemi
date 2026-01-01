import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM Kurumsal", layout="wide")

# 2. Gelişmiş SaaS CSS Tasarımı
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8F9FA !important;
    }

    /* Sidebar - Temiz Beyaz SaaS Görünümü */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E9ECEF !important;
    }
    
    /* Kart (Card) Yapısı */
    .saas-card {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        border: 1px solid #EFF2F5;
        margin-bottom: 25px;
    }

    /* Input Alanları - Modern Sade */
    input, select, textarea, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #1B1B1B !important;
        border-radius: 8px !important;
        border: 1px solid #DDE1E6 !important;
    }
    
    /* Disabled (Sabit) Alanlar İçin Siyah Yazı */
    input:disabled {
        -webkit-text-fill-color: #000000 !important;
        font-weight: 500;
        background-color: #F8F9FA !important;
    }

    /* Butonlar - SaaS Moru */
    .stButton > button {
        border-radius: 8px !important;
        background-color: #6366F1 !important;
        color: white !important;
        border: none !important;
        width: 100%;
        font-weight: 500 !important;
    }
    .stButton > button:hover {
        background-color: #4F46E5 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }

    /* Tablo ve Metin */
    h1, h2, h3 { color: #1B1B1B !important; letter-spacing: -0.5px; }
    p, label { color: #64748B !important; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# 3. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- YARDIMCI FONKSİYONLAR ---
def fetch_data(table, order_col="id"): 
    return supabase.table(table).select("*").order(order_col).execute().data

def fetch_filtered(table, col, val): 
    return supabase.table(table).select("*").eq(col, val).execute().data

# 4. Yan Menü (SaaS Hiyerarşisi)
with st.sidebar:
    st.markdown("<h2 style='color:#6366F1;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<p style='font-size:12px; font-weight:bold;'>HOME</p>", unsafe_allow_html=True)
    main_nav = st.radio("MAIN", ["Dashboard", "Organizasyon", "İşe Alım"], label_visibility="collapsed")
    
    if main_nav == "Organizasyon":
        st.markdown("<p style='font-size:12px; font-weight:bold; margin-top:20px;'>PAGES</p>", unsafe_allow_html=True)
        sub_nav = st.radio("ORG", ["Departmanlar", "Pozisyonlar", "Seviyeler"], label_visibility="collapsed")
    elif main_nav == "İşe Alım":
        st.markdown("<p style='font-size:12px; font-weight:bold; margin-top:20px;'>RECRUITMENT</p>", unsafe_allow_html=True)
        sub_nav = st.radio("REC", ["Adaylar"], label_visibility="collapsed")
    else:
        sub_nav = "Dashboard"

# --- EKRANLAR ---

if sub_nav == "Dashboard":
    st.title("Sistem Özeti")
    c1, c2, c3 = st.columns(3)
    c1.markdown("<div class='saas-card'><p>Toplam Aday</p><h3>" + str(len(fetch_data("adaylar"))) + "</h3></div>", unsafe_allow_html=True)
    c2.markdown("<div class='saas-card'><p>Aktif Pozisyonlar</p><h3>" + str(len(fetch_data("pozisyonlar"))) + "</h3></div>", unsafe_allow_html=True)
    c3.markdown("<div class='saas-card'><p>Departman Sayısı</p><h3>" + str(len(fetch_data("departmanlar"))) + "</h3></div>", unsafe_allow_html=True)

# --- DEPARTMANLAR ---
elif sub_nav == "Departmanlar":
    st.title("Departman Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Ekle", "📋 Liste"])
    with t1:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        with st.form("dep_f", clear_on_submit=True):
            d_ad = st.text_input("Departman Adı")
            if st.form_submit_button("Kaydet"):
                if d_ad: supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with t2:
        res = fetch_data("departmanlar", "departman_adi")
        if res: st.table(pd.DataFrame(res)[["departman_adi"]])

# --- POZİSYONLAR ---
elif sub_nav == "Pozisyonlar":
    st.title("Pozisyon Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Ekle", "📋 Liste"])
    deps = fetch_data("departmanlar", "departman_adi")
    with t1:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        with st.form("poz_f", clear_on_submit=True):
            d_map = {d['departman_adi']: d['id'] for d in deps}
            s_dep = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()))
            p_ad = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Kaydet"):
                if s_dep != "Seçiniz..." and p_ad:
                    p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_ad}).execute()
                    p_id = p_res.data[0]['id']
                    ks = ["J1", "J2", "M1", "M2", "M3", "S"]
                    supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_ad} {k}", "seviye_kodu": k} for k in ks]).execute()
                    st.success("Pozisyon ve 6 Seviye Oluşturuldu"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with t2:
        res = supabase.table("pozisyonlar").select("pozisyon_adi, departmanlar(departman_adi)").execute()
        if res.data: st.table(pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res.data]))

# --- SEVİYELER ---
elif sub_nav == "Seviyeler":
    st.title("Kariyer Seviyeleri")
    res = supabase.table("seviyeler").select("seviye_adi, pozisyonlar(pozisyon_adi)").execute()
    if res.data: st.table(pd.DataFrame([{"Seviye": r['seviye_adi'], "Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res.data]))

# --- ADAYLAR ---
elif sub_nav == "Adaylar":
    st.title("Aday Havuzu")
    t1, t2 = st.tabs(["➕ Yeni Aday Kaydı", "📋 Liste ve Bilgi Güncelleme"])
    
    with t1:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        # Form dışı bağımlı seçimler
        n_ad = st.text_input("Ad Soyad *")
        n_tc = st.text_input("Kimlik No *")
        n_tel = st.text_input("Telefon")
        
        deps = fetch_data("departmanlar", "departman_adi")
        d_map = {d['departman_adi']: d['id'] for d in deps}
        s_d = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()))
        
        n_p_id, n_s_id = None, None
        if s_d != "Seçiniz...":
            pozs = fetch_filtered("pozisyonlar", "departman_id", d_map[s_d])
            p_map = {p['pozisyon_adi']: p['id'] for p in pozs}
            s_p = st.selectbox("Pozisyon", ["Seçiniz..."] + list(p_map.keys()))
            if s_p != "Seçiniz...":
                n_p_id = p_map[s_p]
                sevs = fetch_filtered("seviyeler", "pozisyon_id", n_p_id)
                sv_map = {sv['seviye_adi']: sv['id'] for sv in sevs}
                s_s = st.selectbox("Seviye", ["Seçiniz..."] + list(sv_map.keys()))
                if s_s != "Seçiniz...": n_s_id = sv_map[s_s]

        cv_file = st.file_uploader("CV Yükle (PDF)", type=['pdf'])

        if st.button("🚀 Adayı Sisteme Kaydet"):
            if n_ad and n_tc:
                # CV Upload İşlemi
                cv_url = None
                if cv_file:
                    file_path = f"cv_{n_tc}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
                    supabase.storage.from_("cv_bucket").upload(file_path, cv_file.read())
                    cv_url = supabase.storage.from_("cv_bucket").get_public_url(file_path)

                a_res = supabase.table("adaylar").insert({"ad_soyad": n_ad, "kimlik_no": n_tc}).execute()
                a_id = a_res.data[0]['id']
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": n_ad, "kimlik_no": n_tc, "telefon": n_tel, "cv_url": cv_url,
                    "departman_id": d_map.get(s_d), "pozisyon_id": n_p_id, "seviye_id": n_s_id,
                    "islemi_yapan": "Sistemsel", "baslangic_tarihi": datetime.now().isoformat()
                }).execute()
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.success("Aday başarıyla kaydedildi."); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))").execute()
        for aday in res.data:
            v = aday['aday_versiyonlar']
            with st.expander(f"👤 {aday['ad_soyad']} | TC: {aday['kimlik_no']}"):
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.text_input("Ad Soyad (Sabit)", value=aday['ad_soyad'], disabled=True, key=f"d_ad_{aday['id']}")
                u_tel = st.text_input("Telefon", value=v['telefon'] if v else "", key=f"u_tel_{aday['id']}")
                
                # Güncelleme Zincirleme
                u_d = st.selectbox("Yeni Departman", ["Seçiniz..."] + list(d_map.keys()), key=f"u_d_{aday['id']}")
                u_p_id, u_s_id = None, None
                if u_d != "Seçiniz...":
                    u_p_list = fetch_filtered("pozisyonlar", "departman_id", d_map[u_d])
                    u_p_map = {p['pozisyon_adi']: p['id'] for p in u_p_list}
                    u_p = st.selectbox("Yeni Pozisyon", ["Seçiniz..."] + list(u_p_map.keys()), key=f"u_p_{aday['id']}")
                    if u_p != "Seçiniz...":
                        u_p_id = u_p_map[u_p]
                        u_s_list = fetch_filtered("seviyeler", "pozisyon_id", u_p_id)
                        u_s_map = {sv['seviye_adi']: sv['id'] for sv in u_s_list}
                        u_s = st.selectbox("Yeni Seviye", ["Seçiniz..."] + list(u_s_map.keys()), key=f"u_s_{aday['id']}")
                        if u_s != "Seçiniz...": u_s_id = u_s_map[u_s]

                if st.button("🔄 Versiyon Güncelle", key=f"btn_{aday['id']}"):
                    simdi = datetime.now().isoformat()
                    if v: supabase.table("aday_versiyonlar").update({"bitis_tarihi": simdi}).eq("id", v['id']).execute()
                    nv = supabase.table("aday_versiyonlar").insert({
                        "aday_id": aday['id'], "ad_soyad": aday['ad_soyad'], "kimlik_no": aday['kimlik_no'], 
                        "telefon": u_tel, "departman_id": d_map.get(u_d), "pozisyon_id": u_p_id, "seviye_id": u_s_id,
                        "islemi_yapan": "Kullanıcı", "baslangic_tarihi": simdi
                    }).execute()
                    supabase.table("adaylar").update({"guncel_versiyon_id": nv.data[0]['id']}).eq("id", aday['id']).execute()
                    st.success("Yeni versiyon oluşturuldu."); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
