import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM Admin", layout="wide", initial_sidebar_state="expanded")

# 2. Preline CMS Stil Paketi (Monokrom & Profesyonel Beyaz)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Reset */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sol Sidebar - Minimalist CMS Navigasyonu */
    [data-testid="stSidebar"] {
        border-right: 1px solid #F2F4F7 !important;
        width: 260px !important;
    }
    .nav-label {
        font-size: 11px; font-weight: 700; color: #98A2B3;
        margin: 25px 0 10px 15px; text-transform: uppercase; letter-spacing: 1px;
    }
    
    /* Sol Menü Butonları */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #475467 !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        font-weight: 500 !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #F9FAFB !important;
        color: #101828 !important;
    }

    /* Sağ Üst Sekmeler (Alt Menü) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #FFFFFF !important;
        border-bottom: 1px solid #EAECF0 !important;
        gap: 30px !important;
        padding-top: 5px !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500 !important;
        color: #667085 !important;
        padding-bottom: 12px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #101828 !important;
        border-bottom: 2px solid #101828 !important;
    }

    /* Girdi Alanları - Preline Form Standartları */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D0D5DD !important;
        border-radius: 8px !important;
        color: #101828 !important;
    }
    input { color: #101828 !important; background-color: transparent !important; }
    
    /* Aksiyon Butonları (Siyah & Minimal) */
    .action-btn > div > button {
        background-color: #101828 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        border: none !important;
    }

    /* Preline DataTable Görünümü */
    [data-testid="stDataEditor"], div[data-testid="stTable"] {
        border: 1px solid #EAECF0 !important;
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Supabase ve Veri Çekme Motoru
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

def db_get(table, select="*"): return supabase.table(table).select(select).execute().data

# 4. Sayfa Kontrolü (Sol Menü)
if 'active_nav' not in st.session_state: st.session_state.active_nav = "Dashboard"

with st.sidebar:
    st.markdown("<div style='padding:15px;'><h3 style='color:#101828; margin:0;'>İM-FEXİM</h3></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='nav-label'>GENEL</div>", unsafe_allow_html=True)
    if st.button("📊 Dashboard"): st.session_state.active_nav = "Dashboard"
    
    st.markdown("<div class='nav-label'>KURUMSAL</div>", unsafe_allow_html=True)
    if st.button("🏢 Organizasyon"): st.session_state.active_nav = "Organizasyon"
    
    st.markdown("<div class='nav-label'>SÜREÇLER</div>", unsafe_allow_html=True)
    if st.button("👤 İşe Alım (ATS)"): st.session_state.active_nav = "ATS"
    if st.button("👥 Çalışanlar (HRM)"): st.session_state.active_nav = "HRM"

# --- SAYFA İÇERİKLERİ ---

# A. DASHBOARD
if st.session_state.active_nav == "Dashboard":
    st.title("Dashboard")
    st.info("Kurumsal Portal Yönetim Paneli")

# B. ORGANİZASYON (Üst Sekme Hiyerarşisi)
elif st.session_state.active_nav == "Organizasyon":
    st.title("Organizasyon Yapılandırması")
    tab_dep, tab_poz, tab_sev = st.tabs(["Departman Yönetimi", "Pozisyon Tanımlama", "Seviye Listesi"])
    
    with tab_dep:
        with st.form("f_dep", clear_on_submit=True):
            d_ad = st.text_input("Departman Adı")
            if st.form_submit_button("Departman Ekle"):
                supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute(); st.rerun()
        st.table(pd.DataFrame(db_get("departmanlar"))[["departman_adi"]])

    with tab_poz:
        deps = db_get("departmanlar")
        d_map = {d['departman_adi']: d['id'] for d in deps}
        with st.form("f_poz"):
            s_dep = st.selectbox("Departman Seç", list(d_map.keys()))
            p_ad = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Pozisyon ve 6 Seviyeyi Tanımla"):
                p_id = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_ad}).execute().data[0]['id']
                # 6 Seviye Üretimi
                ks = ["J1", "J2", "M1", "M2", "M3", "S"]
                supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_ad} {k}", "seviye_kodu": k} for k in ks]).execute()
                st.success("Pozisyon ve kariyer basamakları oluşturuldu."); st.rerun()
        # Listeleme
        res_p = supabase.table("pozisyonlar").select("pozisyon_adi, departmanlar(departman_adi)").execute()
        if res_p.data: st.table(pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res_p.data]))

    with tab_sev:
        res_s = supabase.table("seviyeler").select("seviye_adi, seviye_kodu, pozisyonlar(pozisyon_adi)").execute()
        if res_s.data:
            df_s = pd.DataFrame([{"Seviye": r['seviye_adi'], "Kod": r['seviye_kodu'], "Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res_s.data])
            st.data_editor(df_s, use_container_width=True, hide_index=True)

# C. ATS (Aday -> Versiyon -> Personel Geçişi)
elif st.session_state.active_nav == "ATS":
    st.title("Aday Takip & İşe Alım")
    tab_ekle, tab_havuz = st.tabs(["Aday Ekle", "Güncel Aday Havuzu"])
    
    with tab_ekle:
        with st.form("f_aday"):
            ad = st.text_input("Ad Soyad")
            tc = st.text_input("Kimlik No")
            if st.form_submit_button("Havuza Kaydet"):
                a_id = supabase.table("adaylar").insert({"ad_soyad": ad, "kimlik_no": tc}).execute().data[0]['id']
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": ad, "kimlik_no": tc, "ise_alim_sureci": "aday havuzu",
                    "baslangic_tarihi": datetime.now().isoformat()
                }).execute()
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.rerun()

    with tab_havuz:
        res_a = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*)").execute()
        if res_a.data:
            for r in res_a.data:
                v = r['aday_versiyonlar']
                if v['ise_alim_sureci'] not in ["işe alındı", "olumsuz"]:
                    with st.expander(f"{r['ad_soyad']} | Durum: {v['ise_alim_sureci'].upper()}"):
                        new_s = st.selectbox("Süreç Güncelle", ["aday havuzu", "mülakat", "iş teklifi", "işe alındı", "olumsuz"], key=f"sel_{r['id']}")
                        if st.button("Versiyonla ve Kaydet", key=f"btn_{r['id']}"):
                            # SCD Type 2 Versiyonlama
                            nv = supabase.table("aday_versiyonlar").insert({
                                "aday_id": r['id'], "ad_soyad": r['ad_soyad'], "kimlik_no": r['kimlik_no'],
                                "ise_alim_sureci": new_s, "baslangic_tarihi": datetime.now().isoformat()
                            }).execute()
                            supabase.table("adaylar").update({"guncel_versiyon_id": nv.data[0]['id']}).eq("id", r['id']).execute()
                            
                            # İŞE ALINDI -> PERSONEL TRANSFERİ
                            if new_s == "işe alındı":
                                p_res = supabase.table("personeller").insert({"ad_soyad": r['ad_soyad'], "kimlik_no": r['kimlik_no'], "aday_id": r['id']}).execute()
                                supabase.table("personel_versiyonlar").insert({
                                    "personel_id": p_res.data[0]['id'], "ad_soyad": r['ad_soyad'], "baslangic_tarihi": datetime.now().isoformat()
                                }).execute()
                                st.balloons()
                            st.rerun()

# D. HRM (Personel Listesi)
elif st.session_state.active_nav == "HRM":
    st.title("Personel Listesi")
    res_p = db_get("personeller")
    if res_p: st.data_editor(pd.DataFrame(res_p)[["ad_soyad", "kimlik_no"]], use_container_width=True, hide_index=True)
    else: st.info("Aktif personel bulunamadı.")
