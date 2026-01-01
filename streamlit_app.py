import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Konfigürasyon ve Stil
st.set_page_config(page_title="İM-FEXİM Organizasyon", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    [data-testid="stSidebar"] { background-color: #FDFDFD !important; border-right: 1px solid #EEEEEE !important; }
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { background-color: #F8F9FA !important; color: #000000 !important; }
    h1, h2, h3, label, span { color: #000000 !important; }
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
    org_menu = st.radio("", ["🏢 Departmanlar", "👔 Pozisyonlar", "📊 Seviyeler", "👥 Personel"])

# --- MODÜL 1: DEPARTMANLAR ---
if org_menu == "🏢 Departmanlar":
    st.header("Departman Yönetimi")
    with st.form("dep_ekle", clear_on_submit=True):
        d_ad = st.text_input("Yeni Departman Adı")
        if st.form_submit_button("Kaydet"):
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
        # Default boş seçenekli dropbox
        dep_list = ["Departman Seçiniz..."] + (dep_df['departman_adi'].tolist() if not dep_df.empty else [])
        secilen_dep = st.selectbox("Bağlı Olduğu Departman", options=dep_list, index=0)
        p_ad = st.text_input("Pozisyon Adı (Örn: Teknisyen)")
        
        if st.form_submit_button("Pozisyonu ve Seviyeleri Oluştur"):
            if secilen_dep != "Departman Seçiniz..." and p_ad:
                # 1. Pozisyonu Kaydet
                target_id = dep_df[dep_df['departman_adi'] == secilen_dep]['id'].values[0]
                p_res = supabase.table("pozisyonlar").insert({"departman_id": target_id, "pozisyon_adi": p_ad}).execute()
                new_poz_id = p_res.data[0]['id']
                
                # 2. 6 Seviyeyi Otomatik Oluştur (J1, J2, M1, M2, M3, S)
                seviye_kodlari = ["J1", "J2", "M1", "M2", "M3", "S"]
                seviye_listesi = []
                for kod in seviye_kodlari:
                    seviye_listesi.append({
                        "pozisyon_id": new_poz_id,
                        "seviye_adi": f"{p_ad} {kod}",
                        "seviye_kodu": kod
                    })
                supabase.table("seviyeler").insert(seviye_listesi).execute()
                
                st.success(f"'{p_ad}' pozisyonu ve 6 kariyer seviyesi başarıyla oluşturuldu.")
            else:
                st.error("Lütfen departman seçin ve pozisyon adı girin.")

# --- MODÜL 3: SEVİYELER (YENİ) ---
elif org_menu == "📊 Seviyeler":
    st.header("Kariyer Seviyeleri ve Yetkinlik Matrisi")
    
    # Seviyeleri Pozisyon ve Departman bilgisiyle çekiyoruz
    query = """
        id, seviye_adi, seviye_kodu, yetkinlikler, 
        belge_is_ilani, belge_gorev_tanimi, 
        pozisyonlar (pozisyon_adi, departmanlar (departman_adi))
    """
    res = supabase.table("seviyeler").select(query).execute()
    
    if res.data:
        disp_data = []
        for r in res.data:
            disp_data.append({
                "Seviye Tam Adı": r['seviye_adi'],
                "Kod": r['seviye_kodu'],
                "Pozisyon": r['pozisyonlar']['pozisyon_adi'],
                "Departman": r['pozisyonlar']['departmanlar']['departman_adi'],
                "Görev Tanımı": "✅" if r['belge_gorev_tanimi'] else "❌",
                "İş İlanı": "✅" if r['belge_is_ilani'] else "❌"
            })
        
        df_show = pd.DataFrame(disp_data)
        st.dataframe(df_show, use_container_width=True)
        
        st.info("💡 Seviye detaylarını, yetkinlikleri ve belgeleri güncellemek için ileride 'Detaylı Düzenleme' modu eklenecektir.")
    else:
        st.info("Henüz bir seviye oluşturulmamış. Lütfen önce Pozisyon ekleyiniz.")
