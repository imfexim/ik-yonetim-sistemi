import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Ayarlar
st.set_page_config(page_title="İM-FEXİM Kurumsal Yönetim", layout="wide")

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Session State (Dinamik Listeler)
if 'gecici_varliklar' not in st.session_state: st.session_state.gecici_varliklar = []
if 'gecici_iliskiler' not in st.session_state: st.session_state.gecici_iliskiler = []

# 4. Menü
with st.sidebar:
    st.title("İM-FEXİM")
    menu = st.radio("MENÜ", ["Lokasyon Bankası", "Şirket ve İlişki Yönetimi", "Birim Yönetimi"])

# --- MODÜL 1: LOKASYON BANKASI (Ortak Havuz) ---
if menu == "Lokasyon Bankası":
    st.subheader("📍 Fiziksel Lokasyon Havuzu")
    st.info("Buraya eklenen lokasyonlar, tüm şirketler tarafından ortak kullanılabilir.")
    
    with st.form("yeni_lokasyon"):
        c1, c2 = st.columns(2)
        l_ad = c1.text_input("Lokasyon Adı", placeholder="Örn: Forum İstanbul AVM")
        l_tip = c2.selectbox("Tip", ["AVM", "Plaza", "Sanayi Bölgesi", "Serbest Bölge", "Depo Alanı"])
        l_adr = st.text_area("Açık Adres")
        lx, ly = st.columns(2)
        if st.form_submit_button("Lokasyonu Havuza Ekle"):
            supabase.table("lokasyonlar").insert({"lokasyon_adi": l_ad, "lokasyon_tipi": l_tip, "adres": l_adr, "koordinat_x": lx.text_input("X"), "koordinat_y": ly.text_input("Y")}).execute()
            st.success("Lokasyon başarıyla eklendi.")

# --- MODÜL 2: ŞİRKET VE İLİŞKİ YÖNETİMİ ---
elif menu == "Şirket ve İlişki Yönetimi":
    st.subheader("🏢 Şirket Tanımlama ve Varlık Yönetimi")
    t1, t2 = st.tabs(["Yeni Kayıt", "Yönetim Paneli"])

    with t1:
        # BÖLÜM 1: GENEL BİLGİLER
        st.markdown("##### 1. Şirket Bilgileri")
        s_ad = st.text_input("Şirket Adı")
        
        # BÖLÜM 2: LOKASYONDAKİ VARLIK VE MUHATAP (Örn: Media Markt @ Forum Istanbul)
        st.divider()
        st.markdown("##### 2. Lokasyon Mevcudiyeti ve Muhataplar")
        
        res_l = supabase.table("lokasyonlar").select("id, lokasyon_adi").execute()
        l_df = pd.DataFrame(res_l.data)
        
        if not l_df.empty:
            c_l1, c_l2 = st.columns([1, 2])
            secilen_l_ad = c_l1.selectbox("Lokasyon Seçin", l_df['lokasyon_adi'].tolist())
            secilen_l_id = l_df[l_df['lokasyon_adi'] == secilen_l_ad]['id'].values[0]
            
            st.markdown("###### Bu Lokasyondaki Şirket Muhatabı")
            m1, m2, m3 = st.columns(3)
            m_ad = m1.text_input("Muhatap Ad Soyad")
            m_tel = m2.text_input("Muhatap Telefon")
            m_mail = m3.text_input("Muhatap Mail")
            
            if st.button("➕ Bu Varlığı Listeye Ekle"):
                st.session_state.gecici_varliklar.append({
                    "lokasyon_id": secilen_l_id, "lokasyon_adi": secilen_l_ad,
                    "muhatap_ad_soyad": m_ad, "muhatap_telefon": m_tel, "muhatap_mail": m_mail
                })
            
            if st.session_state.gecici_varliklar:
                st.table(pd.DataFrame(st.session_state.gecici_varliklar)[['lokasyon_adi', 'muhatap_ad_soyad', 'muhatap_telefon']])
        
        # BÖLÜM 3: MUHATAPLIK (İLİŞKİ)
        st.divider()
        st.markdown("##### 3. Şirket İlişki Türü ve Muhatap Şirketler")
        s_turu = st.selectbox("Bu Şirketin Türü", ["Grup Şirketi", "Tedarikçi", "Satış Kanalı", "Hizmet Sağlayıcı"])
        
        res_s = supabase.table("sirketler").select("id, sirket_adi").execute()
        s_df = pd.DataFrame(res_s.data)
        
        if not s_df.empty:
            r1, r2 = st.columns(2)
            muhatap_s = r1.selectbox("Muhatap Olduğu Bizim Şirketimiz", s_df['sirket_adi'].tolist())
            iliski_notu = r2.text_input("İlişki Notu (Örn: Teknoloji Tedariği)")
            
            if st.button("🔗 İlişkiyi Ekle"):
                st.session_state.gecici_iliskiler.append({
                    "hedef_id": s_df[s_df['sirket_adi'] == muhatap_s]['id'].values[0],
                    "hedef_ad": muhatap_s, "not": iliski_notu
                })
            
            if st.session_state.gecici_iliskiler:
                st.table(pd.DataFrame(st.session_state.gecici_iliskiler)[['hedef_ad', 'not']])

        # ANA KAYIT
        if st.button("🚀 ŞİRKET KAYDINI TAMAMLA"):
            try:
                # 1. Şirket
                s_res = supabase.table("sirketler").insert({"sirket_adi": s_ad, "sirket_turu": s_turu}).execute()
                new_s_id = s_res.data[0]['id']
                
                # 2. Varlıklar (Lokasyon Muhatapları)
                for v in st.session_state.gecici_varliklar:
                    supabase.table("sirket_lokasyon_varliklari").insert({
                        "sirket_id": new_s_id, "lokasyon_id": v['lokasyon_id'],
                        "muhatap_ad_soyad": v['muhatap_ad_soyad'], "muhatap_telefon": v['muhatap_telefon'], "muhatap_mail": v['muhatap_mail']
                    }).execute()
                
                # 3. İlişkiler
                for r in st.session_state.gecici_iliskiler:
                    supabase.table("sirket_iliskileri").insert({"kaynak_sirket_id": new_s_id, "hedef_sirket_id": r['hedef_id'], "iliski_turu": r['not']}).execute()
                
                st.success("İşlem Başarılı.")
                st.session_state.gecici_varliklar = []; st.session_state.gecici_iliskiler = []
                st.rerun()
            except Exception as e: st.error(str(e))
