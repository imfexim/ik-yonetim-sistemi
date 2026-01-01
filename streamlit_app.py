import streamlit as st
from supabase import create_client
import pandas as pd

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(
    page_title="İM-FEXİM Kurumsal İK",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. KURUMSAL TASARIM (CSS) - Beyaz Arka Plan ve Antrasit Metin
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp { background-color: #FFFFFF; }
    
    /* Yazı Renkleri ve Fontlar */
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #344767 !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Üst Panel (Header) */
    .top-bar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding: 10px 20px;
        background-color: #FFFFFF;
        border-bottom: 1px solid #E9ECEF;
        margin-bottom: 20px;
    }
    
    /* Sidebar Tasarımı */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
        border-right: 1px solid #E9ECEF !important;
    }
    
    /* Buton ve Girdi Alanları */
    .stButton>button {
        background-color: #344767;
        color: white;
        border-radius: 5px;
    }
    
    /* Dataframe Konteynırı */
    .stDataFrame {
        border: 1px solid #E9ECEF;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SUPABASE BAĞLANTISI
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- ÜST PANEL (PROFIL / AYARLAR / BILDIRIM) ---
# Streamlit'te üst bar simülasyonu
top_col1, top_col2 = st.columns([8, 2])
with top_col2:
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 14px; color: #67748E;">
            <span>Bildirimler</span>
            <span>|</span>
            <span>Ayarlar</span>
            <span>|</span>
            <span style="font-weight: bold; color: #344767;">Profil</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- SOL NAVİGASYON (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='color: #344767;'>İM-FEXİM</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px; color: #8392AB;'>KURUMSAL İK SİSTEMİ</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.radio(
        "ANA MENÜ",
        ["Organizasyon Yapısı", "Personel Yönetimi", "Tanımlamalar", "Raporlama"]
    )

# --- ANA ÇALIŞMA ALANI (CRUD) ---
if menu == "Organizasyon Yapısı":
    st.subheader("Organizasyon Birimleri")
    
    # Alt Menü / Tab Görünümü
    tab1, tab2, tab3 = st.tabs(["Birim Listesi", "Yeni Birim Ekle", "Hiyerarşi Şeması"])
    
    with tab1:
        # CRUD: Listeleme ve Filtreleme
        # Örnek veri çekme (Tablo adını senaryona göre değiştireceğiz)
        try:
            res = supabase.table("Personel").select("*").execute()
            df = pd.DataFrame(res.data)
            
            # Filtreleme Alanı
            search = st.text_input("Birim veya Personel Ara...", placeholder="Aramak istediğiniz anahtar kelimeyi yazın")
            
            if not df.empty:
                if search:
                    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Görüntülenecek veri bulunamadı.")
        except:
            st.warning("Henüz Organizasyon tablosu tanımlanmadı.")

    with tab2:
        # CRUD: Ekleme İşlemi
        st.markdown("#### Yeni Organizasyon Birimi Tanımla")
        with st.form("org_ekle_form"):
            birim_ad = st.text_input("Birim Adı")
            ust_birim = st.selectbox("Bağlı Olduğu Üst Birim", ["Genel Müdürlük", "İK Direktörlüğü", "Operasyon"])
            birim_kod = st.text_input("Birim Kodu")
            
            if st.form_submit_button("Kaydet"):
                # Buraya kayıt mantığı gelecek
                st.success("Birim sisteme başarıyla eklendi.")

# --- DİĞER MENÜLER İÇİN İSKELET ---
elif menu == "Personel Yönetimi":
    st.subheader("Personel Veri Bankası")
    st.info("Personel listesi ve detaylı filtreleme alanı.")
