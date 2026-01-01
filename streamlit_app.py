import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Ayarları
st.set_page_config(page_title="İM-FEXİM Organizasyon", layout="wide")

# Kurumsal Stil
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF !important; }
    h1, h2, h3 { color: #1B1B1B !important; font-weight: 700 !important; }
    /* Buton ve Girdi Alanları */
    .stButton>button { border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Sol Menü
with st.sidebar:
    st.title("İM-FEXİM")
    st.markdown("### 🛠️ Organizasyon")
    org_menu = st.radio("", ["🏢 Departmanlar", "👥 Personel"])

# --- DEPARTMANLAR YÖNETİM ALANI ---
if org_menu == "🏢 Departmanlar":
    st.header("Departman Yönetimi")
    
    t1, t2 = st.tabs(["➕ Yeni Departman Ekle", "📋 Departman Listesi"])

    # --- EKLEME ALANI ---
    with t1:
        with st.form("dep_ekle_form", clear_on_submit=True):
            d_ad = st.text_input("Departman Adı", placeholder="Örn: Muhasebe")
            
            if st.form_submit_button("Departmanı Kaydet"):
                if d_ad:
                    try:
                        supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute()
                        st.success(f"'{d_ad}' departmanı sisteme eklendi.")
                        st.rerun()
                    except Exception as e: st.error(f"Hata: {e}")
                else: st.warning("Lütfen bir departman adı giriniz.")

    # --- LİSTELEME VE CRUD ALANI ---
    with t2:
        try:
            res = supabase.table("departmanlar").select("*").order("departman_adi").execute()
            if res.data:
                df = pd.DataFrame(res.data)
                
                # Tablo Görünümü
                for index, row in df.iterrows():
                    with st.expander(f"📌 {row['departman_adi']}"):
                        col_edit, col_del = st.columns([4, 1])
                        
                        # Düzenleme
                        with col_edit:
                            with st.form(f"edit_{row['id']}"):
                                new_name = st.text_input("Departman Adını Güncelle", value=row['departman_adi'])
                                if st.form_submit_button("Güncelle"):
                                    supabase.table("departmanlar").update({"departman_adi": new_name}).eq("id", row['id']).execute()
                                    st.success("Başarıyla güncellendi.")
                                    st.rerun()
                        
                        # Silme
                        with col_del:
                            st.write("") # Boşluk
                            st.write("") # Boşluk
                            if st.button("🗑️ Sil", key=f"del_{row['id']}"):
                                supabase.table("departmanlar").delete().eq("id", row['id']).execute()
                                st.warning("Silindi.")
                                st.rerun()
            else:
                st.info("Henüz departman tanımlanmamış.")
        except Exception as e:
            st.error(f"Veri yüklenemedi: {e}")
