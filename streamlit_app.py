import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Konfigürasyonu (Geniş mod ve Kurumsal Başlık)
st.set_page_config(page_title="İM-FEXİM Kurumsal İK", layout="wide")

# --- KURUMSAL ARAYÜZ TASARIMI (CSS) ---
st.markdown("""
    <style>
    /* Ana Arka Plan: Beyaz */
    .stApp { background-color: #FFFFFF; }

    /* Metin Renkleri: Koyu Antrasit (#344767 kurumsal standarttır) */
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #344767 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Üst Profil Barı (Header) */
    .stHeader {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E9ECEF;
    }

    /* Sol Navigasyon (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
        border-right: 1px solid #E9ECEF !important;
    }

    /* Profesyonel Tablo Stili */
    .stDataFrame {
        border: 1px solid #E9ECEF;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- ÜST PANEL (PROFIL / AYARLAR / BİLDİRİMLER) ---
# Sağ üst köşeye ince bir işlem alanı simülasyonu
header_col1, header_col2 = st.columns([8, 2])
with header_col2:
    st.markdown("""
        <div style="text-align: right; font-size: 13px; color: #6C757D; padding-top: 10px;">
            Bildirimler &nbsp; | &nbsp; Ayarlar &nbsp; | &nbsp; <span style="font-weight: bold; color: #344767;">Admin Profil</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- SOL NAVİGASYON (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h3 style='margin-bottom: 0;'>İM-FEXİM</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 11px; color: #ADB5BD; letter-spacing: 1px;'>KURUMSAL YÖNETİM</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Ana Menü Navigasyonu
    menu_selection = st.radio(
        "SİSTEM MENÜSÜ",
        ["Organizasyon Yapısı", "Personel Yönetimi", "Tanımlamalar", "Raporlar"],
        label_visibility="visible"
    )

# --- SAĞ ÇALIŞMA ALANI (ANA EKRAN) ---
if menu_selection == "Organizasyon Yapısı":
    st.subheader("Organizasyonel Birim Yönetimi")
    
    # Alt Menü Sekmeleri
    tab_list, tab_add, tab_hierarchy = st.tabs(["Birim Listesi", "Yeni Birim Tanımla", "Şema Görüntüle"])
    
    with tab_list:
        # Arama ve Filtreleme Şeridi
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_query = st.text_input("Birim veya kod ara...", placeholder="Arama kriterlerini giriniz...")
        
        # CRUD: Veri Listeleme (Personel tablonu şimdilik referans alıyoruz)
        try:
            res = supabase.table("Personel").select("*").execute()
            df = pd.DataFrame(res.data)
            
            if not df.empty:
                # Basit filtreleme mantığı
                if search_query:
                    df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Kayıtlı birim bulunamadı.")
        except Exception as e:
            st.error(f"Veri erişim hatası: {e}")

    with tab_add:
        st.markdown("##### Yeni Birim Giriş Formu")
        with st.form("new_unit_form"):
            col_a, col_b = st.columns(2)
            unit_name = col_a.text_input("Birim Adı")
            unit_code = col_b.text_input("Birim Kodu")
            parent_unit = st.selectbox("Üst Birim", ["Yönetim Kurulu", "Genel Müdürlük", "İnsan Kaynakları"])
            
            if st.form_submit_button("Birimi Kaydet"):
                st.success("Yeni organizasyon birimi başarıyla oluşturuldu.")

elif menu_selection == "Personel Yönetimi":
    st.subheader("Personel Veri Bankası")
    st.markdown("Bu alandan personel özlük dosyalarına ve CRUD işlemlerine erişebilirsiniz.")
