import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Konfigürasyon ve Görsel Stil
st.set_page_config(page_title="İM-FEXİM Kurumsal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    * { color: #000000 !important; }
    
    /* Dropboxların içini beyaz, yazılarını siyah yapma zorlaması */
    div[data-baseweb="select"] > div {
        background-color: white !important;
        border: 1px solid black !important;
    }
    div[role="listbox"] {
        background-color: white !important;
    }
    div[role="option"] {
        color: black !important;
        background-color: white !important;
    }
    input { background-color: white !important; color: black !important; border: 1px solid black !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Menü Yapısı (Kırpılmadan korunmuş hali)
with st.sidebar:
    st.markdown("### 🏢 İM-FEXİM")
    main_nav = st.radio("ANA MENÜ", ["Organizasyon", "İşe Alım"])
    st.markdown("---")
    if main_nav == "Organizasyon":
        sub_nav = st.radio("ALT MENÜ", ["Departmanlar", "Pozisyonlar", "Seviyeler"])
    else:
        sub_nav = st.radio("ALT MENÜ", ["Adaylar"])

# --- MODÜLLER ---

if sub_nav == "Departmanlar":
    st.header("🏢 Departman Yönetimi")
    t1, t2 = st.tabs(["➕ Ekle", "📋 Liste"])
    with t1:
        with st.form("dep_f", clear_on_submit=True):
            d_ad = st.text_input("Departman Adı")
            if st.form_submit_button("Kaydet"):
                supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute()
                st.success("Eklendi"); st.rerun()
    with t2:
        res = supabase.table("departmanlar").select("*").execute()
        if res.data: st.table(pd.DataFrame(res.data)[["departman_adi"]])

elif sub_nav == "Pozisyonlar":
    st.header("👔 Pozisyon Yönetimi")
    t1, t2 = st.tabs(["➕ Ekle", "📋 Liste"])
    deps = supabase.table("departmanlar").select("id, departman_adi").execute().data
    with t1:
        with st.form("poz_f", clear_on_submit=True):
            d_map = {d['departman_adi']: d['id'] for d in deps}
            s_dep = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()))
            p_ad = st.text_input("Pozisyon Adı")
            if st.form_submit_button("Kaydet"):
                if s_dep != "Seçiniz..." and p_ad:
                    p_res = supabase.table("pozisyonlar").insert({"departman_id": d_map[s_dep], "pozisyon_adi": p_ad}).execute()
                    p_id = p_res.data[0]['id']
                    # 6 Seviye Üretimi
                    ks = ["J1", "J2", "M1", "M2", "M3", "S"]
                    supabase.table("seviyeler").insert([{"pozisyon_id": p_id, "seviye_adi": f"{p_ad} {k}", "seviye_kodu": k} for k in ks]).execute()
                    st.success("Pozisyon ve Seviyeler Oluşturuldu"); st.rerun()
    with t2:
        res = supabase.table("pozisyonlar").select("pozisyon_adi, departmanlar(departman_adi)").execute()
        if res.data: st.table(pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res.data]))

elif sub_nav == "Seviyeler":
    st.header("📊 Kariyer Seviyeleri")
    res = supabase.table("seviyeler").select("seviye_adi, pozisyonlar(pozisyon_adi)").execute()
    if res.data: st.table(pd.DataFrame([{"Seviye": r['seviye_adi'], "Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res.data]))

elif sub_nav == "Adaylar":
    st.header("👤 Aday Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Aday", "📋 Aday Listesi"])
    
    with t1:
        # Bağımlı Dropboxlar için Form Dışı Seçim Alanları
        ad_soyad = st.text_input("Ad Soyad *")
        tc_no = st.text_input("Kimlik No *")
        tel = st.text_input("Telefon")
        
        deps = supabase.table("departmanlar").select("id, departman_adi").execute().data
        d_map = {d['departman_adi']: d['id'] for d in deps}
        s_dep = st.selectbox("Departman Seçiniz", ["Seçiniz..."] + list(d_map.keys()))
        
        s_poz_id = None
        s_sev_id = None
        
        if s_dep != "Seçiniz...":
            pozs = supabase.table("pozisyonlar").select("id, pozisyon_adi").eq("departman_id", d_map[s_dep]).execute().data
            p_map = {p['pozisyon_adi']: p['id'] for p in pozs}
            s_poz = st.selectbox("Pozisyon Seçiniz", ["Seçiniz..."] + list(p_map.keys()))
            
            if s_poz != "Seçiniz...":
                s_poz_id = p_map[s_poz]
                sevs = supabase.table("seviyeler").select("id, seviye_adi").eq("pozisyon_id", s_poz_id).execute().data
                sv_map = {sv['seviye_adi']: sv['id'] for sv in sevs}
                s_sev = st.selectbox("Seviye Seçiniz", ["Seçiniz..."] + list(sv_map.keys()))
                if s_sev != "Seçiniz...": s_sev_id = sv_map[s_sev]

        if st.button("🚀 Adayı Kaydet ve Versiyonla"):
            if ad_soyad and tc_no:
                try:
                    # 1. Ana Tablo Kaydı
                    a_res = supabase.table("adaylar").insert({"ad_soyad": ad_soyad, "kimlik_no": tc_no}).execute()
                    a_id = a_res.data[0]['id']
                    
                    # 2. Versiyon Kaydı
                    v_res = supabase.table("aday_versiyonlar").insert({
                        "aday_id": a_id, "ad_soyad": ad_soyad, "kimlik_no": tc_no, "telefon": tel,
                        "departman_id": d_map.get(s_dep) if s_dep != "Seçiniz..." else None,
                        "pozisyon_id": s_poz_id, "seviye_id": s_sev_id,
                        "islemi_yapan": "Sistemsel", "baslangic_tarihi": datetime.now().isoformat()
                    }).execute()
                    
                    # 3. Linkleme
                    supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                    st.success("Aday ve Versiyon Başarıyla Oluşturuldu"); st.rerun()
                except Exception as e:
                    st.error(f"Veritabanı Hatası: {e}")
            else:
                st.warning("Ad Soyad ve Kimlik No mecburidir.")

    with t2:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))").execute()
        if res.data:
            out = []
            for r in res.data:
                v = r['aday_versiyonlar']
                out.append({
                    "Ad Soyad": r['ad_soyad'], "TC No": r['kimlik_no'],
                    "Dep": v['departmanlar']['departman_adi'] if v and v['departmanlar'] else "-",
                    "Poz": v['pozisyonlar']['pozisyon_adi'] if v and v['pozisyonlar'] else "-"
                })
            st.table(pd.DataFrame(out))
