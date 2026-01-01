import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Konfigürasyon
st.set_page_config(page_title="İM-FEXİM Kurumsal Yönetim", layout="wide")

# Kurumsal Stil
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #344767 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    section[data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Menü
with st.sidebar:
    st.markdown("### İM-FEXİM")
    menu = st.radio("SİSTEM MENÜSÜ", ["Şirket ve Lokasyon Tanımlama", "Birim Yönetimi", "Personel İşlemleri"])

if menu == "Şirket ve Lokasyon Tanımlama":
    st.subheader("Kurumsal Şirket ve Şube/Bayi Kaydı")
    
    t1, t2 = st.tabs(["Yeni Kayıt Oluştur", "Mevcut Şirketler ve Lokasyonlar"])
    
    with t1:
        with st.form("main_form", clear_on_submit=True):
            st.markdown("##### 🏢 1. Şirket Genel Bilgileri")
            c1, c2 = st.columns(2)
            s_ad = c1.text_input("Şirket Adı")
            s_mail = c2.text_input("Şirket Kurumsal Mail")
            
            st.markdown("<br>##### 👤 2. Şirket Üst Yöneticisi", unsafe_allow_html=True)
            y1, y2, y3 = st.columns(3)
            y_ad = y1.text_input("Yönetici Ad Soyad")
            y_tel = y2.text_input("Yönetici Telefon")
            y_mail = y3.text_input("Yönetici Mail")

            st.markdown("<br>##### 📍 3. Birincil Lokasyon / Şube / Bayi Bilgileri", unsafe_allow_html=True)
            l1, l2, l3 = st.columns(3)
            l_ad = l1.text_input("Lokasyon Adı", value="Genel Merkez")
            l_tip = l2.selectbox("Lokasyon Tipi", ["Genel Merkez", "Bölge Müdürlüğü", "Şube", "Depo", "Bayi", "Fabrika"])
            l_tel = l3.text_input("Lokasyon Sabit Telefon")
            
            l_adr = st.text_area("Lokasyon Açık Adresi")
            lx, ly = st.columns(2)
            l_x = lx.text_input("Koordinat X (Enlem)")
            l_y = ly.text_input("Koordinat Y (Boylam)")

            st.markdown("<br>##### 📞 4. Lokasyon Sorumlusu (Muhatap Kişi)", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m_ad = m1.text_input("Sorumlu Ad Soyad")
            m_tel = m2.text_input("Sorumlu Telefon")
            m_mail = m3.text_input("Sorumlu Mail")

            if st.form_submit_button("Sisteme Kaydet"):
                if s_ad and l_ad:
                    try:
                        # Şirket Ekle
                        s_ins = supabase.table("sirketler").insert({
                            "sirket_adi": s_ad, "sirket_mail": s_mail,
                            "yonetici_adi": y_ad, "yonetici_telefon": y_tel, "yonetici_mail": y_mail
                        }).execute()
                        s_id = s_ins.data[0]['id']

                        # Lokasyon Ekle
                        supabase.table("lokasyonlar").insert({
                            "sirket_id": s_id, "lokasyon_adi": l_ad, "lokasyon_tipi": l_tip,
                            "telefon": l_tel, "adres": l_adr, "koordinat_x": l_x, "koordinat_y": l_y,
                            "sorumlu_ad_soyad": m_ad, "sorumlu_telefon": m_tel, "sorumlu_mail": m_mail
                        }).execute()
                        
                        st.success(f"'{s_ad}' ve '{l_ad}' başarıyla tanımlandı.")
                    except Exception as e: st.error(f"Hata: {e}")
                else: st.warning("Zorunlu alanları doldurunuz.")

    with t2:
        try:
            res = supabase.table("sirketler").select("*, lokasyonlar(*)").execute()
            for item in res.data:
                with st.expander(f"🏢 {item['sirket_adi']} (Yönetici: {item['yonetici_adi']})"):
                    st.write(f"**Mail:** {item['sirket_mail']}")
                    if item['lokasyonlar']:
                        ldf = pd.DataFrame(item['lokasyonlar'])
                        ldf.columns = [c.replace('_', ' ').title() for c in ldf.columns]
                        st.table(ldf[['Lokasyon Adi', 'Lokasyon Tipi', 'Sorumlu Ad Soyad', 'Sorumlu Telefon', 'Adres']])
        except Exception as e: st.error(f"Veri çekme hatası: {e}")
