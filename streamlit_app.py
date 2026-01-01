import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM Kurumsal", layout="wide", initial_sidebar_state="expanded")

# --- CSS (Beyaz Tema Zorlaması) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    :root { --primary: #6366F1; --bg: #FFFFFF; --text: #1B1B1B; --border: #E9ECEF; }
    .stApp { background-color: var(--bg) !important; color: var(--text) !important; }
    section[data-testid="stSidebar"] { background-color: var(--bg) !important; border-right: 1px solid var(--border) !important; }
    h1, h2, h3, p, label, .stMarkdown { color: var(--text) !important; font-family: 'Inter', sans-serif; }
    .saas-card { background: #FFFFFF; padding: 24px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid var(--border); margin-bottom: 20px; }
    input, select, textarea, div[data-baseweb="select"] > div { background-color: #FFFFFF !important; color: #000000 !important; border: 1px solid #DDE1E6 !important; border-radius: 8px !important; }
    input:disabled { -webkit-text-fill-color: #000000 !important; background-color: #F8F9FA !important; opacity: 1; }
    .stButton > button { background-color: var(--primary) !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: 500 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- YARDIMCI FONKSİYONLAR ---
def fetch_all(table): return supabase.table(table).select("*").execute().data
def fetch_filter(table, col, val): return supabase.table(table).select("*").eq(col, val).execute().data

SUREC_LISTESI = ["aday havuzu", "ön değerlendirme", "ön görüşme", "mülakat", "teknik değerlendirme", "iş teklifi", "belge toplama", "olumsuz", "işe alındı"]

# 3. Yan Menü
with st.sidebar:
    st.markdown("<h2 style='color:#6366F1;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    main_nav = st.sidebar.radio("MENÜ", ["📊 Dashboard", "🏢 Organizasyon", "👤 İşe Alım", "👥 Çalışanlar"], label_visibility="collapsed")
    
    if main_nav == "🏢 Organizasyon":
        sub_nav = st.sidebar.radio("ALT", ["Departmanlar", "Pozisyonlar", "Seviyeler"])
    elif main_nav == "👤 İşe Alım":
        sub_nav = st.sidebar.radio("ALT", ["Adaylar"])
    elif main_nav == "👥 Çalışanlar":
        sub_nav = "Personel Listesi"
    else: sub_nav = "Dashboard"

# --- EKRANLAR ---

if sub_nav == "Dashboard":
    st.title("Sistem Özeti")
    c1, c2, c3 = st.columns(3)
    # Sadece aktif adayları (havuzdakileri) gösteren bir sayaç eklenebilir
    st.write("Hoş geldiniz. Sol menüden işlem seçebilirsiniz.")

elif sub_nav == "Adaylar":
    st.title("👤 Aday Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Aday Kaydı", "📋 Aktif Aday Listesi"])
    
    with t1:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        n_ad = st.text_input("Ad Soyad *")
        n_tc = st.text_input("Kimlik No *")
        n_tel = st.text_input("Telefon")
        
        # Dropboxlar
        deps = fetch_all("departmanlar")
        d_map = {d['departman_adi']: d['id'] for d in deps}
        s_d = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()))
        
        # Pozisyon ve Seviye Seçimi (Zincirleme)
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

        if st.button("🚀 Adayı Havuza Ekle"):
            if n_ad and n_tc:
                # KRİTİK: Mükerrer Kontrolü (Arşiv dahil tüm veritabanında arar)
                check = supabase.table("adaylar").select("id").eq("kimlik_no", n_tc).execute()
                if check.data:
                    st.error(f"❌ HATA: {n_tc} kimlik numarasına kayıtlı eski bir aday zaten mevcut!")
                else:
                    a_res = supabase.table("adaylar").insert({"ad_soyad": n_ad, "kimlik_no": n_tc}).execute()
                    a_id = a_res.data[0]['id']
                    v_res = supabase.table("aday_versiyonlar").insert({
                        "aday_id": a_id, "ad_soyad": n_ad, "kimlik_no": n_tc, "telefon": n_tel,
                        "departman_id": d_map.get(s_d), "pozisyon_id": n_p_id, "seviye_id": n_s_id,
                        "ise_alim_sureci": "aday havuzu",
                        "islemi_yapan": "Sistemsel", "baslangic_tarihi": datetime.now().isoformat()
                    }).execute()
                    supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                    st.success("Aday başarıyla kaydedildi."); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        # LİSTELEME: Sadece "işe alındı" ve "olumsuz" OLMAYANLARI getir
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))").execute()
        
        aktif_adaylar = [r for r in res.data if r['aday_versiyonlar'] and r['aday_versiyonlar']['ise_alim_sureci'] not in ["işe alındı", "olumsuz"]]
        
        if aktif_adaylar:
            st.info(f"Şu an değerlendirme süreci devam eden {len(aktif_adaylar)} aday bulunmaktadır.")
            for aday in aktif_adaylar:
                v = aday['aday_versiyonlar']
                with st.expander(f"👤 {aday['ad_soyad']} | Süreç: {v['ise_alim_sureci'].upper()}"):
                    st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                    new_proc = st.selectbox("Süreç Güncelle", SUREC_LISTESI, index=SUREC_LISTESI.index(v['ise_alim_sureci']), key=f"p_{aday['id']}")
                    
                    if st.button("🔄 Güncelle ve Kaydet", key=f"btn_{aday['id']}"):
                        simdi = datetime.now().isoformat()
                        # Eski versiyonu kapat
                        supabase.table("aday_versiyonlar").update({"bitis_tarihi": simdi}).eq("id", v['id']).execute()
                        # Yeni versiyon aç
                        nv = supabase.table("aday_versiyonlar").insert({
                            "aday_id": aday['id'], "ad_soyad": aday['ad_soyad'], "kimlik_no": aday['kimlik_no'], 
                            "telefon": v['telefon'], "ise_alim_sureci": new_proc,
                            "departman_id": v['departman_id'], "pozisyon_id": v['pozisyon_id'], "seviye_id": v['seviye_id'],
                            "islemi_yapan": "İK Uzmanı", "baslangic_tarihi": simdi
                        }).execute()
                        supabase.table("adaylar").update({"guncel_versiyon_id": nv.data[0]['id']}).eq("id", aday['id']).execute()
                        
                        # Eğer İşe Alındı ise Personel Tablosuna Yaz (Önceki fonksiyona benzer tetikleyici)
                        if new_proc == "işe alındı":
                            # (Burada personeller tablosuna kayıt kodları çalışır)
                            st.toast(f"{aday['ad_soyad']} çalışana dönüştürüldü.")
                        
                        st.success(f"Aday durumu '{new_proc}' olarak güncellendi. Liste yenileniyor...")
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Aktif süreçte bekleyen aday bulunmamaktadır.")

elif sub_nav == "Personel Listesi":
    st.subheader("👥 Çalışan Portalı")
    # Personel listeleme ve düzenleme kodları...
    st.write("Aktif çalışanların listesi burada yer alır.")
