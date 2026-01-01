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
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Sol Menü Hiyerarşisi
with st.sidebar:
    st.title("İM-FEXİM")
    st.markdown("### 🛠️ Organizasyon")
    # Alt menü simülasyonu
    org_menu = st.radio("", ["🏢 Departmanlar", "👥 Personel (Yakında)"])

# --- DEPARTMANLAR YÖNETİM ALANI ---
if org_menu == "🏢 Departmanlar":
    st.header("Departman Yönetimi")
    
    t1, t2 = st.tabs(["➕ Yeni Departman Ekle", "📋 Departman Listesi & İşlemler"])

    # --- EKLEME ALANI ---
    with t1:
        with st.form("dep_ekle_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            d_ad = col1.text_input("Departman Adı", placeholder="Örn: İnsan Kaynakları")
            d_kod = col2.text_input("Departman Kodu", placeholder="Örn: IK-01")
            d_aciklama = st.text_area("Açıklama")
            
            if st.form_submit_button("Departmanı Kaydet"):
                if d_ad:
                    try:
                        supabase.table("departmanlar").insert({
                            "departman_adi": d_ad, "departman_kodu": d_kod, "aciklama": d_aciklama
                        }).execute()
                        st.success(f"'{d_ad}' departmanı başarıyla oluşturuldu.")
                        st.rerun()
                    except Exception as e: st.error(f"Hata: {e}")
                else: st.warning("Departman adı boş bırakılamaz.")

    # --- LİSTELEME VE CRUD (DÜZENLE/SİL) ALANI ---
    with t2:
        try:
            res = supabase.table("departmanlar").select("*").order("departman_adi").execute()
            if res.data:
                df = pd.DataFrame(res.data)
                
                for index, row in df.iterrows():
                    with st.expander(f"📌 {row['departman_adi']} ({row['departman_kodu'] or 'Kodsuz'})"):
                        # Düzenleme Formu
                        with st.form(f"edit_{row['id']}"):
                            edit_ad = st.text_input("Departman Adı", value=row['departman_adi'])
                            edit_kod = st.text_input("Departman Kodu", value=row['departman_kodu'])
                            edit_desc = st.text_area("Açıklama", value=row['aciklama'])
                            
                            c1, c2 = st.columns([1, 4])
                            if c1.form_submit_button("Güncelle"):
                                supabase.table("departmanlar").update({
                                    "departman_adi": edit_ad, "departman_kodu": edit_kod, "aciklama": edit_desc
                                }).eq("id", row['id']).execute()
                                st.success("Güncellendi!")
                                st.rerun()
                                
                        # Silme Butonu (Ayrı bir alan)
                        if st.button(f"🗑️ Bu Departmanı Sil", key=f"del_{row['id']}"):
                            supabase.table("departmanlar").delete().eq("id", row['id']).execute()
                            st.warning(f"'{row['departman_adi']}' silindi.")
                            st.rerun()
            else:
                st.info("Henüz bir departman tanımlanmamış.")
        except Exception as e:
            st.error(f"Veri yüklenemedi: {e}")
