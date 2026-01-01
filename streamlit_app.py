import streamlit as st
from supabase import create_client
import pandas as pd

# 1. KURUMSAL SAYFA AYARLARI
st.set_page_config(page_title="İM-FEXİM Kurumsal Portal", layout="wide")

# --- PROFESYONEL STİL (CSS) ---
st.markdown("""
    <style>
    /* Beyaz Arka Plan ve Koyu Antrasit Yazı */
    .stApp { background-color: #FFFFFF; }
    
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #344767 !important;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Yan Menü (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
        border-right: 1px solid #E9ECEF !important;
    }
    
    /* Tablo ve Form Kartları */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre;
        font-weight: 600;
        font-size: 14px;
        color: #67748E;
    }
    .stTabs [aria-selected="true"] { color: #344767; border-bottom-color: #344767; }

    /* Üst İnce Bar */
    .top-header {
        display: flex;
        justify-content: flex-end;
        padding: 5px 0px;
        border-bottom: 1px solid #F0F2F5;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BAĞLANTI
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- ÜST PANEL (PROFIL / BİLDİRİM / AYARLAR) ---
st.markdown("""
    <div class="top-header">
        <div style="font-size: 13px; color: #8392AB;">
            Bildirimler &nbsp;&nbsp; | &nbsp;&nbsp; Ayarlar &nbsp;&nbsp; | &nbsp;&nbsp; 
            <span style="font-weight: 600; color: #344767;">Yönetici Paneli</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- SOL NAVİGASYON (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h3 style='margin-bottom:0;'>İM-FEXİM</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:11px; color:#ADB5BD; letter-spacing:1px;'>KURUMSAL İK SİSTEMİ</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    main_menu = st.radio(
        "SİSTEM NAVİGASYONU",
        ["Organizasyon Yapısı", "Personel Yönetimi", "Tanımlamalar", "Sistem Raporları"],
        label_visibility="collapsed"
    )

# --- SAĞ ÇALIŞMA ALANI ---
if main_menu == "Organizasyon Yapısı":
    st.subheader("Organizasyonel Birim Yönetimi")
    st.markdown("<p style='font-size:14px; color:#67748E;'>Şirket hiyerarşisini, departmanları ve bağlı birimleri bu alandan yönetebilirsiniz.</p>", unsafe_allow_html=True)
    
    # CRUD İŞLEMLERİ İÇİN TABLAR
    tab_list, tab_create, tab_history = st.tabs(["Birim Listesi", "Yeni Birim Tanımla", "İşlem Günlüğü"])
    
    with tab_list:
        # Arama ve Filtreleme
        col_search, col_filter = st.columns([3, 1])
        with col_search:
            search = st.text_input("Birim veya Kod ile Ara", placeholder="Örn: İnsan Kaynakları...", label_visibility="collapsed")
        
        # Mevcut veriyi göster (Görselde gördüğüm Personel tablosunu şablon olarak kullanıyorum)
        try:
            res = supabase.table("Personel").select("*").execute()
            df = pd.DataFrame(res.data)
            
            if not df.empty:
                # Kolon başlıklarını kurumsallaştıralım
                st.dataframe(
                    df[['personel_id', 'tc_no', 'versiyon', 'islem_tarihi']], 
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                st.info("Henüz tanımlanmış bir organizasyon birimi bulunmuyor.")
        except:
            st.error("Veritabanı bağlantısı kurulamadı.")

    with tab_create:
        st.markdown("#### Yeni Birim Kaydı")
        with st.form("org_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            unit_name = c1.text_input("Birim / Departman Adı")
            unit_code = c2.text_input("Birim Kodu (Örn: HR-01)")
            
            parent_unit = st.selectbox("Bağlı Olduğu Üst Birim", ["Yönetim Kurulu", "Genel Müdürlük", "Operasyon Direktörlüğü"])
            
            if st.form_submit_button("Birimi Sisteme Kaydet"):
                # Burada INSERT işlemi yapılacak
                st.success(f"{unit_name} başarıyla organizasyon şemasına eklendi.")

elif main_menu == "Personel Yönetimi":
    st.subheader("Personel Veri Bankası")
    st.info("Personel kartları ve özlük işlemleri bu alanda listelenecektir.")
