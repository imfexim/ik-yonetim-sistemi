import streamlit as st
from supabase import create_client
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode # Gelişmiş tablo için

# 1. Ayarlar ve Bağlantı
st.set_page_config(page_title="İM-FEXİM HR Portal", layout="wide", page_icon="🏢")

# --- DATA TABLE TEMASI (CSS) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp { background-color: #f8f9fa; }
    
    /* Kart Yapıları */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    /* Başlık Stilize Etme */
    h1 { color: #1e293b; font-weight: 800; }
    
    /* Yan Menü (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    </style>
    """, unsafe_allow_html=True)

# Supabase Bağlantısı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- HEADER / METRİKLER ---
st.title("🏢 İM-FEXİM İK Yönetim Paneli")
st.caption("Veri Odaklı İnsan Kaynakları ve Operasyonel Takip Sistemi")

# Veri çekme (Hata korumalı)
res = supabase.table("Personel").select("*").execute()
df = pd.DataFrame(res.data)

if not df.empty:
    # Üst Bilgi Kartları
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Aktif Personel", df['personel_id'].nunique())
    with m2: st.metric("Toplam İşlem", len(df))
    with m3: st.metric("Bekleyen Onay", "0") # Senaryolarına göre güncelleriz
    with m4: st.metric("Sistem Statüsü", "Online")

    st.markdown("---")

    # --- ANA İSKELET: İK DATA TABLE ---
    st.subheader("📋 Personel Veri Bankası")
    
    # AgGrid Yapılandırması (DataTables benzeri interaktif tablo)
    gb = GridOptionsBuilder.from_dataframe(df[['ad_soyad', 'personel_id', 'tc_no', 'versiyon', 'islem_tarihi']])
    gb.configure_pagination(paginationAutoPageSize=True) # Sayfalandırma
    gb.configure_side_bar() # Filtreleme çubuğu
    gb.configure_selection('single', use_checkbox=True) # Seçim kutusu
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=False)
    
    gridOptions = gb.build()

    # Tabloyu basıyoruz
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT',
        update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=True,
        theme='balham', # 'alpine', 'balham', 'material' gibi temalar var
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        enable_enterprise_modules=False
    )

    # Seçilen personelin detaylarını yan panelde göstermek için iskelet
    selected = grid_response['selected_rows']
    if selected:
        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 Seçili Personel Detayı")
        st.sidebar.write(f"**İsim:** {selected[0]['ad_soyad']}")
        st.sidebar.write(f"**ID:** {selected[0]['personel_id']}")
        st.sidebar.info("Buraya senaryolarına göre 'Eğitim', 'Zimmet' veya 'Maaş' detayları gelecek.")

else:
    st.info("Henüz veri bulunmuyor.")

# --- YENİ KAYIT MODAL/FORM ALANI ---
with st.expander("➕ Yeni Personel Kaydı / Güncelleme"):
    with st.form("main_form"):
        col1, col2 = st.columns(2)
        with col1:
            f_ad = st.text_input("Ad Soyad")
            f_id = st.text_input("Personel ID")
        with col2:
            f_tc = st.text_input("TC No")
            f_ver = st.text_input("İşlem Tipi / Versiyon")
        
        if st.form_submit_button("Sisteme İşle"):
            supabase.table("Personel").insert({"ad_soyad": f_ad, "personel_id": f_id, "tc_no": f_tc, "versiyon": f_ver}).execute()
            st.success("Kayıt veritabanına işlendi.")
            st.rerun()
