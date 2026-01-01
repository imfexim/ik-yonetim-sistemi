import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Ayarları ve Keskin Görsel Stil
st.set_page_config(page_title="İM-FEXİM Organizasyon", layout="wide")

st.markdown("""
    <style>
    /* Zemin Beyaz, Yazılar Siyah */
    .stApp { background-color: #FFFFFF; color: #000000; }
    
    /* Sidebar Tasarımı */
    [data-testid="stSidebar"] { background-color: #FDFDFD !important; border-right: 1px solid #EEEEEE !important; }
    [data-testid="stSidebar"] * { color: #000000 !important; }
    
    /* Input ve Dropbox Kutuları (İçleri siyah olmasın) */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #F8F9FA !important;
        color: #000000 !important;
        border: 1px solid #DDE1E6 !important;
    }
    input, textarea { color: #000000 !important; }
    
    /* Genel Metinler Siyah */
    h1, h2, h3, h4, h5, h6, p, label, span { color: #000000 !important; font-weight: 500; }
    
    /* Tab ve Buton Düzeni */
    .stTabs [data-baseweb="tab"] { color: #666666; }
    .stTabs [aria-selected="true"] { color: #000000 !important; font-weight: bold; }
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
    org_menu = st.radio("", ["🏢 Departmanlar", "👔 Pozisyonlar", "👥 Personel"])

# --- MODÜL 1: DEPARTMANLAR ---
if org_menu == "🏢 Departmanlar":
    st.header("Departman Yönetimi")
    t1, t2 = st.tabs(["➕ Ekle", "📋 Liste"])
    
    with t1:
        with st.form("dep_ekle", clear_on_submit=True):
            d_ad = st.text_input("Yeni Departman Adı")
            if st.form_submit_button("Kaydet"):
                if d_ad:
                    supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute()
                    st.success("Kaydedildi.")
                    st.rerun()

    with t2:
        res = supabase.table("departmanlar").select("*").order("departman_adi").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"📌 {row['departman_adi']}"):
                    if st.button("Sil", key=f"d_{row['id']}"):
                        supabase.table("departmanlar").delete().eq("id", row['id']).execute()
                        st.rerun()

# --- MODÜL 2: POZİSYONLAR (YENİ) ---
elif org_menu == "👔 Pozisyonlar":
    st.header("Pozisyon (Unvan) Yönetimi")
    t1, t2 = st.tabs(["➕ Yeni Pozisyon Ekle", "📋 Pozisyon Listesi"])

    # Departmanları çekelim (Dropbox için)
    dep_res = supabase.table("departmanlar").select("id, departman_adi").order("departman_adi").execute()
    dep_df = pd.DataFrame(dep_res.data)

    with t1:
        if not dep_df.empty:
            with st.form("poz_ekle", clear_on_submit=True):
                target_dep_name = st.selectbox("Bağlı Olduğu Departman", dep_df['departman_adi'].tolist())
                p_ad = st.text_input("Pozisyon Adı (Örn: Kıdemli Uzman)")
                
                if st.form_submit_button("Pozisyonu Kaydet"):
                    if p_ad:
                        target_id = dep_df[dep_df['departman_adi'] == target_dep_name]['id'].values[0]
                        supabase.table("pozisyonlar").insert({
                            "departman_id": target_id,
                            "pozisyon_adi": p_ad
                        }).execute()
                        st.success(f"'{p_ad}' başarıyla eklendi.")
                        st.rerun()
        else:
            st.warning("Pozisyon ekleyebilmek için önce bir departman oluşturmalısınız.")

    with t2:
        # Pozisyonları departman isimleriyle birlikte çekelim
        poz_res = supabase.table("pozisyonlar").select("id, pozisyon_adi, departmanlar(departman_adi)").execute()
        if poz_res.data:
            p_data = []
            for r in poz_res.data:
                p_data.append({
                    "Pozisyon": r['pozisyon_adi'],
                    "Departman": r['departmanlar']['departman_adi'],
                    "ID": r['id']
                })
            st.table(pd.DataFrame(p_data)[["Pozisyon", "Departman"]])
        else:
            st.info("Henüz pozisyon tanımlanmamış.")
