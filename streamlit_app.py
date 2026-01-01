import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Konfigürasyon ve Stil
st.set_page_config(page_title="İM-FEXİM Kurumsal", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    * { color: #000000 !important; }
    input, select, textarea, div[data-baseweb="select"] > div { background-color: #FFFFFF !important; border: 1px solid #000000 !important; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #000000 !important; }
    .stButton>button { background-color: #FFFFFF !important; border: 1px solid #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Menü Yapısı
with st.sidebar:
    st.markdown("### 🏢 İM-FEXİM")
    main_nav = st.radio("ANA MENÜ", ["Organizasyon", "İşe Alım"])
    st.markdown("---")
    if main_nav == "Organizasyon":
        sub_nav = st.radio("ALT MENÜ", ["Departmanlar", "Pozisyonlar", "Seviyeler"])
    else:
        sub_nav = st.radio("ALT MENÜ", ["Adaylar"])

# --- YARDIMCI VERİ ÇEKME FONKSİYONLARI ---
def get_deps(): return supabase.table("departmanlar").select("id, departman_adi").execute().data
def get_pozs(d_id=None): 
    query = supabase.table("pozisyonlar").select("id, pozisyon_adi")
    if d_id: query = query.eq("departman_id", d_id)
    return query.execute().data
def get_sevs(p_id=None):
    query = supabase.table("seviyeler").select("id, seviye_adi")
    if p_id: query = query.eq("pozisyon_id", p_id)
    return query.execute().data

# --- ADAYLAR MODÜLÜ ---
if sub_nav == "Adaylar":
    st.header("👤 Aday Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Aday Ekle", "📋 Aday Listesi & Düzenle"])
    
    with t1:
        # (Yeni Aday Ekleme kodunuz burada aynı kalıyor, yer kazanmak için özet geçiyorum)
        with st.container():
            n_ad = st.text_input("Ad Soyad *")
            n_tc = st.text_input("Kimlik No *")
            n_tel = st.text_input("Telefon")
            
            all_deps = get_deps()
            d_map = {d['departman_adi']: d['id'] for d in all_deps}
            s_d = st.selectbox("Departman", ["Seçiniz..."] + list(d_map.keys()), key="new_dep")
            
            s_p_id = None
            s_s_id = None
            if s_d != "Seçiniz...":
                all_pozs = get_pozs(d_map[s_d])
                p_map = {p['pozisyon_adi']: p['id'] for p in all_pozs}
                s_p = st.selectbox("Pozisyon", ["Seçiniz..."] + list(p_map.keys()), key="new_poz")
                if s_p != "Seçiniz...":
                    s_p_id = p_map[s_p]
                    all_sevs = get_sevs(s_p_id)
                    sv_map = {sv['seviye_adi']: sv['id'] for sv in all_sevs}
                    s_s = st.selectbox("Seviye", ["Seçiniz..."] + list(sv_map.keys()), key="new_sev")
                    if s_s != "Seçiniz...": s_s_id = sv_map[s_s]

            if st.button("🚀 Adayı Kaydet"):
                if n_ad and n_tc:
                    a_res = supabase.table("adaylar").insert({"ad_soyad": n_ad, "kimlik_no": n_tc}).execute()
                    a_id = a_res.data[0]['id']
                    v_res = supabase.table("aday_versiyonlar").insert({
                        "aday_id": a_id, "ad_soyad": n_ad, "kimlik_no": n_tc, "telefon": n_tel,
                        "departman_id": d_map.get(s_d), "pozisyon_id": s_p_id, "seviye_id": s_s_id,
                        "islemi_yapan": "Sistemsel", "baslangic_tarihi": datetime.now().isoformat()
                    }).execute()
                    supabase.table("adaylar").update({"guncel_versiyon_id": v_res.data[0]['id']}).eq("id", a_id).execute()
                    st.success("Kaydedildi"); st.rerun()

    with t2:
        # LİSTELEME VE DÜZENLEME
        res = supabase.table("adaylar").select("*, aday_versiyonlar!guncel_versiyon_id(*, departmanlar(departman_adi), pozisyonlar(pozisyon_adi), seviyeler(seviye_adi))").execute()
        
        if res.data:
            for aday in res.data:
                v = aday['aday_versiyonlar']
                with st.expander(f"📝 {aday['ad_soyad']} - {v['departmanlar']['departman_adi'] if v and v['departmanlar'] else 'Atanmamış'}"):
                    st.markdown("### Bilgileri Güncelle (Yeni Versiyon Oluşturur)")
                    
                    with st.form(key=f"edit_form_{aday['id']}"):
                        e_ad = st.text_input("Ad Soyad", value=v['ad_soyad'])
                        e_tel = st.text_input("Telefon", value=v['telefon'] if v['telefon'] else "")
                        
                        # Güncelleme için Departman/Pozisyon/Seviye Seçimi
                        all_deps = get_deps()
                        d_names = [d['departman_adi'] for d in all_deps]
                        current_d_name = v['departmanlar']['departman_adi'] if v and v['departmanlar'] else "Seçiniz..."
                        e_dep = st.selectbox("Departman", ["Seçiniz..."] + d_names, index=d_names.index(current_d_name)+1 if current_d_name in d_names else 0)
                        
                        st.info("Not: Pozisyon ve Seviye değişiklikleri bu sürümde ana tanımlardan manuel girilecektir. Dinamik bağlı seçim listeleme ekranında stabilite için sabitlenmiştir.")
                        
                        if st.form_submit_button("✅ Değişiklikleri Kaydet (Yeni Versiyon)"):
                            simdi = datetime.now().isoformat()
                            
                            # 1. ESKİ VERSİYONU KAPAT
                            supabase.table("aday_versiyonlar").update({"bitis_tarihi": simdi}).eq("id", v['id']).execute()
                            
                            # 2. YENİ VERSİYONU AÇ
                            new_v = supabase.table("aday_versiyonlar").insert({
                                "aday_id": aday['id'],
                                "ad_soyad": e_ad,
                                "kimlik_no": aday['kimlik_no'],
                                "telefon": e_tel,
                                "departman_id": v['departman_id'], # Mevcutları koru veya formdan al
                                "pozisyon_id": v['pozisyon_id'],
                                "seviye_id": v['seviye_id'],
                                "islemi_yapan": "Kullanıcı", # İleride dinamik olacak
                                "baslangic_tarihi": simdi
                            }).execute()
                            
                            # 3. ANA TABLOYU GÜNCELLE
                            supabase.table("adaylar").update({
                                "ad_soyad": e_ad,
                                "guncel_versiyon_id": new_v.data[0]['id']
                            }).eq("id", aday['id']).execute()
                            
                            st.success("Bilgiler güncellendi ve eski sürüm arşivlendi!")
                            st.rerun()
        else:
            st.info("Kayıtlı aday bulunamadı.")

# (Organizasyon menüleri aynı kalıyor...)
