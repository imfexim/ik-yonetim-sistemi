import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Konfigürasyon ve Yüksek Kontrastlı Stil
st.set_page_config(page_title="İM-FEXİM Organizasyon", layout="wide")

st.markdown("""
    <style>
    /* Temel Zemin ve Yazı Renkleri */
    .stApp { background-color: #FFFFFF !important; }
    * { color: #000000 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Yan Menü (Sidebar) Beyazlaştırma */
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #000000 !important; }
    
    /* Form ve Girdi Alanları (Input, Select, Textarea) */
    input, select, textarea, div[role="listbox"], div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    
    /* Tablo Görünümü */
    .stDataFrame, div[data-testid="stTable"] { background-color: #FFFFFF !important; }
    thead tr th { background-color: #F0F0F0 !important; color: #000000 !important; }
    tbody tr td { background-color: #FFFFFF !important; color: #000000 !important; }

    /* Butonlar */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    .stButton>button:hover { border-color: #444444 !important; color: #444444 !important; }

    /* Expander (Açılır Kutular) */
    .streamlit-expanderHeader { background-color: #FFFFFF !important; border: 1px solid #EEEEEE !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Sol Menü
with st.sidebar:
    st.markdown("## İM-FEXİM")
    st.markdown("---")
    org_menu = st.radio("ORGANİZASYON", ["🏢 Departmanlar", "👔 Pozisyonlar", "📊 Seviyeler", "👥 Personel"])

# --- MODÜL 1: DEPARTMANLAR ---
if org_menu == "🏢 Departmanlar":
    st.header("Departman Yönetimi")
    with st.form("dep_ekle", clear_on_submit=True):
        d_ad = st.text_input("Yeni Departman Adı")
        if st.form_submit_button("Departmanı Kaydet"):
            if d_ad:
                supabase.table("departmanlar").insert({"departman_adi": d_ad}).execute()
                st.success("Departman eklendi.")
                st.rerun()

# --- MODÜL 2: POZİSYONLAR ---
elif org_menu == "👔 Pozisyonlar":
    st.header("Pozisyon Yönetimi")
    
    dep_res = supabase.table("departmanlar").select("id, departman_adi").order("departman_adi").execute()
    dep_df = pd.DataFrame(dep_res.data)

    with st.form("poz_ekle", clear_on_submit=True):
        # 1. İstek: Default "Seçiniz" ayarı ve seçim sonrası sıfırlama
        dep_list = ["Lütfen Departman Seçiniz..."] + (dep_df['departman_adi'].tolist() if not dep_df.empty else [])
        secilen_dep = st.selectbox("Bağlı Olduğu Departman", options=dep_list, index=0)
        
        p_ad = st.text_input("Pozisyon Adı (Örn: Teknisyen)")
        
        if st.form_submit_button("Pozisyonu ve 6 Seviyeyi Oluştur"):
            if secilen_dep != "Lütfen Departman Seçiniz..." and p_ad:
                # Pozisyon Kaydı
                target_id = dep_df[dep_df['departman_adi'] == secilen_dep]['id'].values[0]
                p_res = supabase.table("pozisyonlar").insert({"departman_id": target_id, "pozisyon_adi": p_ad}).execute()
                new_poz_id = p_res.data[0]['id']
                
                # 2. İstek: 6 Seviye Otomatik Oluşturma (J1, J2, M1, M2, M3, S)
                seviye_kodlari = ["J1", "J2", "M1", "M2", "M3", "S"]
                seviye_payload = []
                for kod in seviye_kodlari:
                    seviye_payload.append({
                        "pozisyon_id": new_poz_id,
                        "seviye_adi": f"{p_ad} {kod}",
                        "seviye_kodu": kod
                    })
                supabase.table("seviyeler").insert(seviye_payload).execute()
                st.success(f"{p_ad} pozisyonu ve bağlı 6 seviye oluşturuldu.")
            else:
                st.error("Eksik bilgi: Departman seçin ve pozisyon adı yazın.")

# --- MODÜL 3: SEVİYELER ---
elif org_menu == "📊 Seviyeler":
    st.header("Seviye ve Belge Yönetimi")
    # 4. İstek: Seviyeler tablosunun gösterilmesi
    query = "id, seviye_adi, seviye_kodu, pozisyonlar(pozisyon_adi, departmanlar(departman_adi))"
    res = supabase.table("seviyeler").select(query).execute()
    
    if res.data:
        disp_data = []
        for r in res.data:
            disp_data.append({
                "Seviye Adı": r['seviye_adi'],
                "Kod": r['seviye_kodu'],
                "Pozisyon": r['pozisyonlar']['pozisyon_adi'],
                "Departman": r['pozisyonlar']['departmanlar']['departman_adi']
            })
        st.table(pd.DataFrame(disp_data)) # Siyah yazı beyaz zemin için table kullanıldı
    else:
        st.info("Henüz seviye bilgisi bulunmuyor.")
