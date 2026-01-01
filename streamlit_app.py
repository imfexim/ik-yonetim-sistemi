import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Konfigürasyon ve Stil (Zorunlu Beyaz & SaaS Tasarımı)
st.set_page_config(page_title="İM-FEXİM Kurumsal", layout="wide")
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

# 2. Bağlantı ve Veri Fonksiyonları
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

def fetch_all(table): return supabase.table(table).select("*").execute().data
def fetch_filter(table, col, val): return supabase.table(table).select("*").eq(col, val).execute().data

SUREC_LISTESI = ["aday havuzu", "ön değerlendirme", "ön görüşme", "mülakat", "teknik değerlendirme", "iş teklifi", "belge toplama", "olumsuz", "işe alındı"]

# 3. Yan Menü
with st.sidebar:
    st.markdown("<h2 style='color:#6366F1;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    main_nav = st.radio("MENÜ", ["📊 Dashboard", "🏢 Organizasyon", "👤 İşe Alım", "👥 Çalışanlar"], label_visibility="collapsed")
    
    if main_nav == "🏢 Organizasyon":
        sub_nav = st.radio("ALT", ["Departmanlar", "Pozisyonlar", "Seviyeler"])
    elif main_nav == "👤 İşe Alım":
        sub_nav = st.radio("ALT", ["Adaylar"])
    elif main_nav == "👥 Çalışanlar":
        sub_nav = "Personel Listesi"
    else: sub_nav = "Dashboard"

# --- MODÜL: ADAYDAN PERSONELE DÖNÜŞÜM MANTIĞI ---
def aday_ise_alim_tetikle(aday_obj, v_obj, yeni_tel, yeni_d_id, yeni_p_id, yeni_s_id):
    simdi = datetime.now().isoformat()
    # 1. Personel Ana Tabloya Ekle (Eğer yoksa)
    p_check = supabase.table("personeller").select("id").eq("kimlik_no", aday_obj['kimlik_no']).execute()
    if not p_check.data:
        p_res = supabase.table("personeller").insert({
            "ad_soyad": aday_obj['ad_soyad'], 
            "kimlik_no": aday_obj['kimlik_no'],
            "aday_id": aday_obj['id']
        }).execute()
        p_id = p_res.data[0]['id']
        
        # 2. Personel Versiyon Oluştur
        pv_res = supabase.table("personel_versiyonlar").insert({
            "personel_id": p_id,
            "ad_soyad": aday_obj['ad_soyad'],
            "kimlik_no": aday_obj['kimlik_no'],
            "telefon": yeni_tel,
            "departman_id": yeni_d_id,
            "pozisyon_id": yeni_p_id,
            "seviye_id": yeni_s_id,
            "ise_baslama_tarihi": simdi,
            "islemi_yapan": "Sistemsel (İşe Alım)"
        }).execute()
        
        # 3. Personel Ana Tabloyu Güncelle
        supabase.table("personeller").update({"guncel_versiyon_id": pv_res.data[0]['id']}).eq("id", p_id).execute()
        return True
    return False

# --- EKRANLAR ---

if sub_nav == "Dashboard":
    st.title("Sistem Özeti")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='saas-card'><p>Toplam Aday</p><h2>{len(fetch_all('adaylar'))}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='saas-card'><p>Aktif Çalışanlar</p><h2>{len(fetch_all('personeller'))}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='saas-card'><p>Departmanlar</p><h2>{len(fetch_all('departmanlar'))}</h2></div>", unsafe_allow_html=True)

elif sub_nav == "Adaylar":
    st.title("Aday Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Aday Kaydı", "📋 Liste ve Süreç"])
    # (Aday ekleme kısmı öncekiyle aynı...)
    
    with t2:
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi))").execute()
        for aday in res.data:
            v = aday['aday_versiyonlar']
            with st.expander(f"👤 {aday['ad_soyad']} | Durum: {v['ise_alim_sureci'].upper() if v else 'BELİRSİZ'}"):
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                new_proc = st.selectbox("Süreç Güncelle", SUREC_LISTESI, index=SUREC_LISTESI.index(v['ise_alim_sureci']) if v and v['ise_alim_sureci'] in SUREC_LISTESI else 0, key=f"p_{aday['id']}")
                
                # Dinamik Dropboxlar (Kariyer Bilgisi İçin)
                deps = fetch_all("departmanlar")
                d_map = {d['departman_adi']: d['id'] for d in deps}
                u_d = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()), key=f"ud_{aday['id']}")
                # ... (Pozisyon ve Seviye Seçimleri Buraya Gelecek - Yer kazanmak için akışı birleştiriyorum)

                if st.button("Kaydet ve Güncelle", key=f"btn_{aday['id']}"):
                    simdi = datetime.now().isoformat()
                    # Aday Versiyon Güncelle
                    supabase.table("aday_versiyonlar").update({"bitis_tarihi": simdi}).eq("id", v['id']).execute()
                    nv = supabase.table("aday_versiyonlar").insert({
                        "aday_id": aday['id'], "ad_soyad": aday['ad_soyad'], "kimlik_no": aday['kimlik_no'], 
                        "ise_alim_sureci": new_proc, "baslangic_tarihi": simdi
                    }).execute()
                    supabase.table("adaylar").update({"guncel_versiyon_id": nv.data[0]['id']}).eq("id", aday['id']).execute()
                    
                    # KRİTİK: İŞE ALINDIYSA PERSONEL YAP
                    if new_proc == "işe alındı":
                        basari = aday_ise_alim_tetikle(aday, v, v['telefon'], v['departman_id'], v['pozisyon_id'], v['seviye_id'])
                        if basari: st.balloons(); st.success("Aday personeller listesine taşındı!")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

elif sub_nav == "Personel Listesi":
    st.title("👥 Çalışan Portalı")
    res = supabase.table("personeller").select("*, personel_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi), seviyeler(seviye_adi))").execute()
    
    if res.data:
        for p in res.data:
            pv = p['personel_versiyonlar']
            with st.expander(f"💼 {p['ad_soyad']} | {pv['pozisyonlar']['pozisyon_adi'] if pv and pv['pozisyonlar'] else 'Belirsiz'}"):
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.text_input("Ad Soyad", value=p['ad_soyad'], disabled=True, key=f"p_ad_{p['id']}")
                c2.text_input("Kimlik No", value=p['kimlik_no'], disabled=True, key=f"p_tc_{p['id']}")
                st.text_input("İşe Giriş Tarihi", value=pv['ise_baslama_tarihi'][:10] if pv else "-", disabled=True)
                
                # Personel üzerinde değişiklik (Kariyer/Telefon vb.) yapıldığında personel_versiyon tablosuna yeni satır atılır.
                st.button("Özlük Bilgilerini Güncelle (Yakında)", key=f"p_upd_{p['id']}")
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Henüz aktif çalışan bulunmamaktadır.")
