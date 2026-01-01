import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM Kurumsal Yönetim", layout="wide")

# --- KURUMSAL STİL (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #344767 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 { color: #1B1B1B !important; font-weight: 700 !important; }
    section[data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı Kurulumu
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Yan Menü
with st.sidebar:
    st.markdown("### İM-FEXİM")
    st.markdown("<p style='font-size:11px; color:#ADB5BD; letter-spacing:1px; margin-top:-15px;'>ORGANİZASYONEL YÖNETİM</p>", unsafe_allow_html=True)
    menu = st.radio("SİSTEM MENÜSÜ", ["Şirket Tanımlama", "Lokasyon Yönetimi", "Birim Yönetimi", "Personel İşlemleri"])

# --- ŞİRKET TANIMLAMA MENÜSÜ ---
if menu == "Şirket Tanımlama":
    st.subheader("Kurumsal Şirket Profil Yönetimi")
    tab_create, tab_list = st.tabs(["Yeni Şirket Kaydı", "Kayıtlı Şirketler"])
    
    with tab_create:
        with st.form("sirket_formu", clear_on_submit=True):
            st.markdown("##### Kurumsal Bilgiler")
            col1, col2 = st.columns(2)
            s_ad = col1.text_input("Şirket Adı")
            s_tel = col2.text_input("Şirket Telefonu")
            s_adres = st.text_area("Şirket Adresi", height=80)
            col3, col4 = st.columns(2)
            s_mail = col3.text_input("Şirket Mail Adresi")
            s_konum = col4.text_input("Şirket Konumu (Şehir/Ülke)")
            
            st.markdown("<br>##### Yönetici Bilgileri", unsafe_allow_html=True)
            col5, col6, col7 = st.columns(3)
            y_ad = col5.text_input("Yönetici Adı Soyadı")
            y_tel = col6.text_input("Yönetici Telefonu")
            y_mail = col7.text_input("Yönetici Mail Adresi")
            
            if st.form_submit_button("Şirket Profilini Kaydet"):
                if s_ad:
                    data = {"sirket_adi": s_ad, "sirket_adresi": s_adres, "sirket_telefonu": s_tel, "sirket_mail": s_mail, "sirket_konumu": s_konum, "yonetici_adi": y_ad, "yonetici_telefon": y_tel, "yonetici_mail": y_mail}
                    try:
                        supabase.table("sirketler").insert(data).execute()
                        st.success(f"'{s_ad}' başarıyla kaydedildi.")
                    except Exception as e: st.error(f"Hata: {e}")
                else: st.warning("Şirket adı zorunludur.")

    with tab_list:
        try:
            res = supabase.table("sirketler").select("*").execute()
            df = pd.DataFrame(res.data)
            if not df.empty:
                df.columns = [c.replace('_', ' ').title() for c in df.columns]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else: st.info("Kayıt bulunamadı.")
        except Exception as e: st.error(f"Veri hatası: {e}")

# --- LOKASYON YÖNETİMİ MENÜSÜ ---
elif menu == "Lokasyon Yönetimi":
    st.subheader("Lokasyon ve Fiziksel Alan Yönetimi")
    try:
        query_res = supabase.table("sirketler").select("id, sirket_adi").execute()
        sirket_df = pd.DataFrame(query_res.data)
    except: sirket_df = pd.DataFrame()

    if not sirket_df.empty:
        selected_sirket_name = st.selectbox("İşlem Yapılacak Şirketi Seçin", sirket_df['sirket_adi'])
        selected_sirket_id = sirket_df[sirket_df['sirket_adi'] == selected_sirket_name]['id'].values[0]

        tab_add, tab_list = st.tabs(["Yeni Lokasyon Tanımla", "Mevcut Lokasyonlar"])

        with tab_add:
            with st.form("lokasyon_detay_form", clear_on_submit=True):
                st.markdown("##### Lokasyon Temel Bilgileri")
                c1, c2, c3 = st.columns(3)
                l_ad = c1.text_input("Lokasyon Adı (Örn: Gebze Depo)")
                l_tip = c2.selectbox("Lokasyon Tipi", ["Genel Merkez", "Bölge Müdürlüğü", "Şube", "Depo", "Bayi", "Fabrika"])
                l_mail = c3.text_input("Lokasyon Genel Mail")
                
                l_adres = st.text_area("Lokasyon Adresi")
                l_tel = st.text_input("Lokasyon Telefonu")

                st.markdown("##### Muhatap / Sorumlu Kişi Bilgileri")
                m1, m2, m3 = st.columns(3)
                m_ad = m1.text_input("Muhatap Ad Soyad")
                m_tel = m2.text_input("Muhatap Telefon")
                m_mail = m3.text_input("Muhatap Mail")

                if st.form_submit_button("Lokasyonu Kaydet"):
                    if l_ad:
                        new_loc = {
                            "sirket_id": str(selected_sirket_id), "lokasyon_adi": l_ad, "lokasyon_tipi": l_tip,
                            "lokasyon_mail": l_mail, "adres": l_adres, "telefon": l_tel,
                            "muhatap_ad": m_ad, "muhatap_tel": m_tel, "muhatap_mail": m_mail
                        }
                        try:
                            supabase.table("lokasyonlar").insert(new_loc).execute()
                            st.success(f"{l_ad} başarıyla kaydedildi.")
                        except Exception as e: st.error(f"Hata: {e}")
                    else: st.warning("Lokasyon adı gereklidir.")

        with tab_list:
            try:
                res_l = supabase.table("lokasyonlar").select("*").eq("sirket_id", selected_sirket_id).execute()
                l_data = pd.DataFrame(res_l.data)
                if not l_data.empty:
                    l_data.columns = [c.replace('_', ' ').title() for c in l_data.columns]
                    st.dataframe(l_data, use_container_width=True, hide_index=True)
                else: st.info("Tanımlı lokasyon yok.")
            except: st.error("Veri yüklenemedi.")
    else: st.warning("Önce bir şirket tanımlamalısınız.")
