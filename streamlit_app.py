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
    
    /* Form alanlarını belirginleştirme */
    .stTextInput input, .stTextArea textarea {
        border: 1px solid #DDE1E6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı Kurulumu
@st.cache_resource
def init_connection():
    # Secrets üzerinden güvenli bağlantı
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# Üst Bilgi Barı
st.markdown("<div style='text-align: right; font-size: 13px; color: #8392AB; border-bottom: 1px solid #F0F2F5; padding-bottom: 10px;'>Sistem Yönetimi &nbsp; | &nbsp; Ayarlar &nbsp; | &nbsp; <b>Yönetici</b></div>", unsafe_allow_html=True)

# 3. Yan Menü Navigasyonu
with st.sidebar:
    st.markdown("### İM-FEXİM")
    st.markdown("<p style='font-size:11px; color:#ADB5BD; letter-spacing:1px; margin-top:-15px;'>ORGANİZASYONEL YÖNETİM</p>", unsafe_allow_html=True)
    menu = st.radio("SİSTEM MENÜSÜ", ["Şirket Tanımlama", "Birim Yönetimi", "Personel İşlemleri"])

# 4. Şirket Tanımlama Alanı
if menu == "Şirket Tanımlama":
    st.subheader("Kurumsal Şirket Profil Yönetimi")
    
    tab_create, tab_list = st.tabs(["Yeni Şirket Kaydı", "Kayıtlı Şirketler"])
    
    with tab_create:
        with st.form("sirket_olusturma_formu", clear_on_submit=True):
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
            
            submit = st.form_submit_button("Şirket Profilini Kaydet")
            
            if submit:
                if s_ad:
                    # VERİ TABANI UYUMU: Tablo adını 'sirketler' (küçük harf) olarak belirledik
                    data = {
                        "sirket_adi": s_ad, "sirket_adresi": s_adres, "sirket_telefonu": s_tel,
                        "sirket_mail": s_mail, "sirket_konumu": s_konum, "yonetici_adi": y_ad,
                        "yonetici_telefon": y_tel, "yonetici_mail": y_mail
                    }
                    try:
                        # Tablo adını 'sirketler' yaparak hatayı gideriyoruz
                        supabase.table("sirketler").insert(data).execute()
                        st.success(f"'{s_ad}' şirket profili başarıyla oluşturuldu.")
                    except Exception as e:
                        st.error(f"Kayıt Hatası: {e}")
                else:
                    st.warning("Lütfen Şirket Adı alanını doldurunuz.")

    with tab_list:
        try:
            # Okuma işleminde de küçük harf kullanımı zorunludur
            res = supabase.table("sirketler").select("*").execute()
            df = pd.DataFrame(res.data)
            if not df.empty:
                # Sütun isimlerini kullanıcı dostu yapmak için alt çizgileri kaldırıp baş harfleri büyütüyoruz
                df.columns = [col.replace('_', ' ').title() for col in df.columns]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Sistemde henüz kayıtlı bir şirket bulunmamaktadır.")
        except Exception as e:
            st.error(f"Veri çekme hatası: {e}")
