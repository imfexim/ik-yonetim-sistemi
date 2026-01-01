import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid

# 1. Sayfa Konfigürasyonu ve Premium Stil
st.set_page_config(page_title="İM-FEXİM Admin", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #FFFFFF !important; font-family: 'Inter', sans-serif !important; }
    
    /* Sol Menü Tasarımı */
    [data-testid="stSidebar"] { border-right: 1px solid #F2F4F7 !important; width: 240px !important; }
    .stButton > button {
        background-color: transparent !important; color: #475467 !important; border: none !important;
        text-align: left !important; justify-content: flex-start !important; width: 100% !important;
        font-weight: 500 !important; padding: 12px 15px !important; border-radius: 8px !important;
    }
    .stButton > button:hover { background-color: #F9FAFB !important; color: #101828 !important; }
    
    /* Üst Sekmeler (Alt Menü) */
    .stTabs [data-baseweb="tab-list"] { background-color: #FFFFFF !important; border-bottom: 1px solid #EAECF0 !important; gap: 30px !important; }
    .stTabs [data-baseweb="tab"] { font-weight: 500 !important; color: #667085 !important; padding-bottom: 12px !important; }
    .stTabs [aria-selected="true"] { color: #101828 !important; border-bottom: 2px solid #101828 !important; }

    /* Input & Button Styles */
    div[data-baseweb="input"] { background-color: #FFFFFF !important; border: 1px solid #D0D5DD !important; border-radius: 8px !important; }
    .main-btn > div > button { background-color: #101828 !important; color: white !important; border: none !important; padding: 10px 24px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Session State (Sayfa Kontrolü)
if 'main_nav' not in st.session_state: st.session_state.main_nav = "Dashboard"

# --- SOL MENÜ (ANA HİYERARŞİ) ---
with st.sidebar:
    st.markdown("<div style='padding:20px 10px;'><h3 style='color:#101828; margin:0;'>İM-FEXİM</h3></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:11px; font-weight:700; color:#98A2B3; margin-left:10px;'>SİSTEM YÖNETİMİ</p>", unsafe_allow_html=True)
    
    if st.button("📊 Dashboard"): st.session_state.main_nav = "Dashboard"
    if st.button("🏢 Organizasyon"): st.session_state.main_nav = "Organizasyon"
    if st.button("👤 İşe Alım (ATS)"): st.session_state.main_nav = "ATS"
    if st.button("👥 Çalışanlar (HRM)"): st.session_state.main_nav = "HRM"

# --- YARDIMCI FONKSİYONLAR ---
def fetch(table, select="*"):
    return supabase.table(table).select(select).execute().data

# --- ANA İÇERİK ALANI ---

# A. DASHBOARD
if st.session_state.main_nav == "Dashboard":
    st.title("Sistem Özeti")
    st.info("Genel veriler burada analiz edilecektir.")

# B. ORGANİZASYON (Departman -> Pozisyon -> Seviye Üretimi)
elif st.session_state.main_nav == "Organizasyon":
    st.title("Organizasyon Yapılandırması")
    t1, t2, t3 = st.tabs(["Departmanlar", "Pozisyonlar", "Seviye Listesi"])

    with t1: # DEPARTMAN EKLE & LİSTELE
        with st.form("dep_form", clear_on_submit=True):
            d_name = st.text_input("Yeni Departman Adı")
            if st.form_submit_button("Departman Oluştur"):
                supabase.table("departmanlar").insert({"departman_adi": d_name}).execute()
                st.rerun()
        st.table(pd.DataFrame(fetch("departmanlar"))[["departman_adi"]])

    with t2: # POZİSYON EKLE (Bağımlı) & 6 SEVİYE ÜRET
        deps = fetch("departmanlar")
        dep_map = {d['departman_adi']: d['id'] for d in deps}
        with st.form("poz_form"):
            s_dep = st.selectbox("Bağlı Departman", list(dep_map.keys()))
            p_name = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Pozisyon ve Seviyeleri Tanımla"):
                # 1. Pozisyonu Ekle
                p_res = supabase.table("pozisyonlar").insert({"departman_id": dep_map[s_dep], "pozisyon_adi": p_name}).execute()
                p_id = p_res.data[0]['id']
                # 2. Otomatik 6 Seviye Üret (J1-S)
                levels = ["J1", "J2", "M1", "M2", "M3", "S"]
                supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_name} {l}", "seviye_kodu": l} for l in levels]).execute()
                st.success(f"{p_name} ve 6 kariyer seviyesi oluşturuldu."); st.rerun()

    with t3: # TÜM SEVİYELERİ LİSTELE
        res = fetch("seviyeler", "seviye_adi, seviye_kodu, pozisyonlar(pozisyon_adi)")
        if res:
            df_s = pd.DataFrame([{"Seviye": r['seviye_adi'], "Kod": r['seviye_kodu'], "Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res])
            st.data_editor(df_s, use_container_width=True, hide_index=True)

# C. ATS (Aday Ekle -> Versiyonla -> İşe Al)
elif st.session_state.main_nav == "ATS":
    st.title("Aday Takip & Versiyonlama")
    t1, t2 = st.tabs(["Yeni Aday Kaydı", "Aday Havuzu & Güncelleme"])

    with t1:
        with st.form("candidate_add"):
            c1, c2 = st.columns(2)
            ad = c1.text_input("Ad Soyad")
            tc = c2.text_input("TC No")
            if st.form_submit_button("Adayı Sisteme Al"):
                # 1. Aday Master Kaydı
                a_res = supabase.table("adaylar").insert({"ad_soyad": ad, "kimlik_no": tc}).execute()
                a_id = a_res.data[0]['id']
                # 2. İlk Versiyon (SCD Type 2)
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": ad, "kimlik_no": tc, "ise_alim_sureci": "aday havuzu",
                    "baslangic_tarihi": datetime.now().isoformat(), "is_current": True
                }).execute()
                # 3. Master'da güncel versiyonu işaretle
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.success("Aday başarıyla versiyonlandı."); st.rerun()

    with t2:
        # GÜNCEL VERSİYONLARI LİSTELE
        adaylar = fetch("adaylar", "*, aday_versiyonlar!guncel_versiyon_id(*)")
        if adaylar:
            for a in adaylar:
                v = a['aday_versiyonlar']
                with st.expander(f"{v['ad_soyad']} - Mevcut Durum: {v['ise_alim_sureci'].upper()}"):
                    new_status = st.selectbox("Süreç Güncelle", ["aday havuzu", "mülakat", "teklif", "işe alındı", "olumsuz"], key=f"sel_{a['id']}")
                    if st.button("Versiyonu Güncelle", key=f"btn_{a['id']}"):
                        # SCD Type 2: Eski versiyonu kapat (opsiyonel mantık) ve yenisini ekle
                        v_new = supabase.table("aday_versiyonlar").insert({
                            "aday_id": a['id'], "ad_soyad": v['ad_soyad'], "kimlik_no": v['kimlik_no'],
                            "ise_alim_sureci": new_status, "baslangic_tarihi": datetime.now().isoformat()
                        }).execute()
                        supabase.table("adaylar").update({"guncel_versiyon_id": v_new.data[0]['id']}).eq("id", a['id']).execute()
                        
                        # EĞER İŞE ALINDI İSE: Personel Tablosuna Aktar
                        if new_status == "işe alındı":
                            p_res = supabase.table("personeller").insert({"ad_soyad": v['ad_soyad'], "kimlik_no": v['kimlik_no']}).execute()
                            # Personel için ilk versiyonu oluştur
                            supabase.table("personel_versiyonlar").insert({
                                "personel_id": p_res.data[0]['id'], "ad_soyad": v['ad_soyad'], "baslangic_tarihi": datetime.now().isoformat()
                            }).execute()
                            st.balloons()
                        st.rerun()

# D. HRM (Çalışan Listesi)
elif st.session_state.main_nav == "HRM":
    st.title("Aktif Personel Listesi")
    personeller = fetch("personeller")
    if personeller:
        st.data_editor(pd.DataFrame(personeller)[["ad_soyad", "kimlik_no"]], use_container_width=True, hide_index=True)
    else: st.info("Henüz çalışan personel bulunmuyor.")
