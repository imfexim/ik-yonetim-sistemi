import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Konfigürasyon ve Yüksek Kontrastlı Stil
st.set_page_config(page_title="İM-FEXİM Kurumsal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    * { color: #000000 !important; }
    
    /* Input ve Dropbox (Zemin Beyaz, Yazı Siyah) */
    div[data-baseweb="select"] > div, input, select, textarea, .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    
    /* Okunmayan Gri/Disabled Alanlar İçin Siyah Yazı Zorlaması */
    input:disabled {
        -webkit-text-fill-color: #000000 !important;
        color: #000000 !important;
        background-color: #F0F0F0 !important;
    }
    
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #000000 !important; }
    .stButton>button { background-color: #FFFFFF !important; border: 1px solid #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- VERİ ÇEKME FONKSİYONLARI ---
def fetch(table, order_col="id"): return supabase.table(table).select("*").order(order_col).execute().data
def fetch_filtered(table, col, val): return supabase.table(table).select("*").eq(col, val).execute().data

# 3. Sol Menü
with st.sidebar:
    st.markdown("### 🏢 İM-FEXİM")
    main_nav = st.radio("ANA MENÜ", ["Organizasyon", "İşe Alım"])
    st.markdown("---")
    if main_nav == "Organizasyon":
        sub_nav = st.radio("ALT MENÜ", ["Departmanlar", "Pozisyonlar", "Seviyeler"])
    else:
        sub_nav = st.radio("ALT MENÜ", ["Adaylar"])

# --- MODÜL: DEPARTMANLAR ---
if sub_nav == "Departmanlar":
    st.header("🏢 Departman Yönetimi")
    t1, t2 = st.tabs(["➕ Ekle", "📋 Liste"])
    with t1:
        with st.form("dep_f", clear_on_submit=True):
            d_ad = st.text_input("Departman Adı")
            if st.form_submit_button("Kaydet"):
                if d_ad: supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute(); st.rerun()
    with t2:
        res = fetch("departmanlar", "departman_adi")
        if res: st.table(pd.DataFrame(res)[["departman_adi"]])

# --- MODÜL: POZİSYONLAR ---
elif sub_nav == "Pozisyonlar":
    st.header("👔 Pozisyon Yönetimi")
    t1, t2 = st.tabs(["➕ Ekle", "📋 Liste"])
    deps = fetch("departmanlar", "departman_adi")
    with t1:
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
    with t2:
        res = supabase.table("pozisyonlar").select("pozisyon_adi, departmanlar(departman_adi)").execute()
        if res.data: st.table(pd.DataFrame([{"Pozisyon": r['pozisyon_adi'], "Departman": r['departmanlar']['departman_adi']} for r in res.data]))

# --- MODÜL: SEVİYELER ---
elif sub_nav == "Seviyeler":
    st.header("📊 Seviye Listesi")
    res = supabase.table("seviyeler").select("seviye_adi, pozisyonlar(pozisyon_adi)").execute()
    if res.data: st.table(pd.DataFrame([{"Seviye": r['seviye_adi'], "Pozisyon": r['pozisyonlar']['pozisyon_adi']} for r in res.data]))

# --- MODÜL: ADAYLAR ---
elif sub_nav == "Adaylar":
    st.header("👤 Aday Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Aday Ekle", "📋 Liste ve Güncelle"])
    
    # 1. YENİ ADAY EKLEME (Zincirleme Dropbox)
    with t1:
        st.subheader("Yeni Aday Kaydı")
        n_ad = st.text_input("Ad Soyad *", key="n_ad")
        n_tc = st.text_input("Kimlik No *", key="n_tc")
        n_tel = st.text_input("Telefon", key="n_tel")
        
        deps = fetch("departmanlar", "departman_adi")
        d_map = {d['departman_adi']: d['id'] for d in deps}
        s_d = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()), key="n_d")
        
        n_p_id, n_s_id = None, None
        if s_d != "Seçiniz...":
            pozs = fetch_filtered("pozisyonlar", "departman_id", d_map[s_d])
            p_map = {p['pozisyon_adi']: p['id'] for p in pozs}
            s_p = st.selectbox("Pozisyon", ["Seçiniz..."] + list(p_map.keys()), key="n_p")
            
            if s_p != "Seçiniz...":
                n_p_id = p_map[s_p]
                sevs = fetch_filtered("seviyeler", "pozisyon_id", n_p_id)
                sv_map = {sv['seviye_adi']: sv['id'] for sv in sevs}
                s_s = st.selectbox("Seviye", ["Seçiniz..."] + list(sv_map.keys()), key="n_s")
                if s_s != "Seçiniz...": n_s_id = sv_map[s_s]

        if st.button("🚀 Adayı Kaydet"):
            if n_ad and n_tc:
                a_res = supabase.table("adaylar").insert({"ad_soyad": n_ad, "kimlik_no": n_tc}).execute()
                a_id = a_res.data[0]['id']
                v_res = supabase.table("aday_versiyonlar").insert({
                    "aday_id": a_id, "ad_soyad": n_ad, "kimlik_no": n_tc, "telefon": n_tel,
                    "departman_id": d_map.get(s_d), "pozisyon_id": n_p_id, "seviye_id": n_s_id,
                    "islemi_yapan": "Sistemsel", "baslangic_tarihi": datetime.now().isoformat()
                }).execute()
                supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                st.success("Kaydedildi"); st.rerun()

    # 2. ADAY LİSTESİ VE GÜNCELLEME
    with t2:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi), seviyeler(seviye_adi))").execute()
        for aday in res.data:
            v = aday['aday_versiyonlar']
            with st.expander(f"📝 {aday['ad_soyad']} | TC: {aday['kimlik_no']}"):
                # Siyah Yazı Zorlamalı Kimlik Bilgileri
                st.text_input("Ad Soyad", value=aday['ad_soyad'], disabled=True, key=f"d_ad_{aday['id']}")
                st.text_input("Kimlik No", value=aday['kimlik_no'], disabled=True, key=f"d_tc_{aday['id']}")
                u_tel = st.text_input("Telefon", value=v['telefon'] if v else "", key=f"u_tel_{aday['id']}")
                
                # Güncelleme Zincirleme Dropbox
                deps = fetch("departmanlar", "departman_adi")
                d_map = {d['departman_adi']: d['id'] for d in deps}
                u_d = st.selectbox("Yeni Departman", ["Seçiniz..."] + list(d_map.keys()), key=f"u_d_{aday['id']}")
                
                u_p_id, u_s_id = None, None
                if u_d != "Seçiniz...":
                    pozs = fetch_filtered("pozisyonlar", "departman_id", d_map[u_d])
                    p_map = {p['pozisyon_adi']: p['id'] for p in pozs}
                    u_p = st.selectbox("Yeni Pozisyon", ["Seçiniz..."] + list(p_map.keys()), key=f"u_p_{aday['id']}")
                    
                    if u_p != "Seçiniz...":
                        u_p_id = p_map[u_p]
                        sevs = fetch_filtered("seviyeler", "pozisyon_id", u_p_id)
                        sv_map = {sv['seviye_adi']: sv['id'] for sv in sevs}
                        u_s = st.selectbox("Yeni Seviye", ["Seçiniz..."] + list(sv_map.keys()), key=f"u_s_{aday['id']}")
                        if u_s != "Seçiniz...": u_s_id = sv_map[u_s]

                if st.button("🔄 Bilgileri Güncelle (Yeni Versiyon)", key=f"btn_{aday['id']}"):
                    simdi = datetime.now().isoformat()
                    # 1. Eski versiyonu kapat
                    if v: supabase.table("aday_versiyonlar").update({"bitis_tarihi": simdi}).eq("id", v['id']).execute()
                    # 2. Yeni versiyonu aç
                    nv = supabase.table("aday_versiyonlar").insert({
                        "aday_id": aday['id'], "ad_soyad": aday['ad_soyad'], "kimlik_no": aday['kimlik_no'], 
                        "telefon": u_tel, "departman_id": d_map.get(u_d), "pozisyon_id": u_p_id, "seviye_id": u_s_id,
                        "islemi_yapan": "Kullanıcı", "baslangic_tarihi": simdi
                    }).execute()
                    # 3. Ana tabloyu güncelle
                    supabase.table("adaylar").update({"guncel_versiyon_id": nv.data[0]['id']}).eq("id", aday['id']).execute()
                    st.success("Versiyon Güncellendi"); st.rerun()
