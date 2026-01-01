import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM | Admin", layout="wide", initial_sidebar_state="expanded")

# 2. %100 BEYAZ TEMA & PREMIUM DATATABLE CSS
st.markdown("""
    <style>
    /* Global Temizlik */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
    }
    
    /* Font ve Yazı Rengi Zorlaması */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; color: #000000 !important; }
    h1, h2, h3, h4, p, label, span { color: #000000 !important; font-weight: 500 !important; }

    /* Premium Sidebar (Emoji Yok, Minimalist Linkler) */
    section[data-testid="stSidebar"] { border-right: 1px solid #E5E7EB !important; }
    .nav-section { font-size: 11px; font-weight: 700; color: #9CA3AF; margin-top: 20px; margin-left: 15px; text-transform: uppercase; }
    
    /* Sidebar Buton Tasarımı */
    div[data-testid="stSidebarNav"] { display: none; } /* Varsayılan nav'ı gizle */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #374151 !important;
        border: 1px solid #E5E7EB !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
    }
    .stButton > button:hover { background-color: #F9FAFB !important; border-color: #2563EB !important; color: #2563EB !important; }

    /* Form ve Kayıt Butonları (Mavi Accent) */
    .main-btn > div > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    /* DataTable Görünümü (st.data_editor için) */
    [data-testid="stDataEditor"] { border: 1px solid #E5E7EB !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 4. Sayfa Yönetimi
if 'current_page' not in st.session_state: st.session_state.current_page = "Dashboard"

# 5. Sidebar (Minimalist & Premium İkonlar Yerine Metinler)
with st.sidebar:
    st.markdown("<h3 style='color:#2563EB; padding-left:15px;'>İM-FEXİM</h3>", unsafe_allow_html=True)
    
    st.markdown("<div class='nav-section'>Genel</div>", unsafe_allow_html=True)
    if st.button("Dashboard"): st.session_state.current_page = "Dashboard"
    
    st.markdown("<div class='nav-section'>Organizasyon</div>", unsafe_allow_html=True)
    if st.button("Departmanlar"): st.session_state.current_page = "Departmanlar"
    if st.button("Pozisyonlar"): st.session_state.current_page = "Pozisyonlar"
    
    st.markdown("<div class='nav-section'>İnsan Kaynakları</div>", unsafe_allow_html=True)
    if st.button("Aday Havuzu"): st.session_state.current_page = "Adaylar"
    if st.button("Çalışan Listesi"): st.session_state.current_page = "Personeller"

# --- EKRANLAR ---

def render_table(df):
    """DataTable etkisini yaratan profesyonel tablo görünümü"""
    st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={"id": None}, # ID sütununu gizle
        disabled=True # Düzenlemeyi kapat, sadece görüntüle
    )

if st.session_state.current_page == "Dashboard":
    st.title("Dashboard")
    st.markdown("Sistemdeki güncel verilerin genel görünümü.")
    # Metrikler...

elif st.session_state.current_page == "Adaylar":
    st.title("Aday Takip Sistemi")
    t1, t2 = st.tabs(["Aday Ekle", "DataTable Havuz"])
    
    with t1:
        with st.form("new_candidate"):
            c1, c2 = st.columns(2)
            ad = c1.text_input("Ad Soyad")
            tc = c2.text_input("Kimlik No")
            st.markdown('<div class="main-btn">', unsafe_allow_html=True)
            submit = st.form_submit_button("Adayı Sisteme Tanımla")
            st.markdown('</div>', unsafe_allow_html=True)
            if submit:
                supabase.table("adaylar").insert({"ad_soyad": ad, "kimlik_no": tc}).execute()
                st.rerun()

    with t2:
        # Supabase'den verileri çekiyoruz
        res = supabase.table("adaylar").select("ad_soyad, kimlik_no, olusturma_tarihi").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            # Sütun isimlerini güzelleştir
            df.columns = ["Ad Soyad", "TC Kimlik No", "Kayıt Tarihi"]
            render_table(df)
        else:
            st.info("Havuzda kayıtlı aday bulunamadı.")

elif st.session_state.current_page == "Departmanlar":
    st.title("Departmanlar")
    res = supabase.table("departmanlar").select("departman_adi").execute()
    if res.data:
        render_table(pd.DataFrame(res.data).rename(columns={"departman_adi": "Departman Adı"}))

elif st.session_state.current_page == "Personeller":
    st.title("Personel Listesi")
    res = supabase.table("personeller").select("ad_soyad, kimlik_no").execute()
    if res.data:
        render_table(pd.DataFrame(res.data).rename(columns={"ad_soyad": "Çalışan", "kimlik_no": "TC No"}))
