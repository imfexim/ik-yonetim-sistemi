import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="İM-FEXİM Kurumsal Yönetim", layout="wide")

# --- KURUMSAL STİL (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #344767 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 { color: #1B1B1B !important; font-weight: 700 !important; }
    section[data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı Kurulumu
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Yan Menü
with st.sidebar:
    st.markdown("### İM-FEXİM")
    st.markdown("<p style='font-size:11px; color:#ADB5BD; letter-spacing:1px; margin-top:-15px;'>ORGANİZASYONEL YÖNETİM</p>", unsafe_allow_html=True)
    menu = st.radio("SİSTEM MENÜSÜ", ["Şirket Tanımlama", "Lokasyon Yönetimi", "Birim Yönetimi", "Personel İşlemleri"])

# --- LOKASYON YÖNETİMİ ---
if menu == "Lokasyon Yönetimi":
    st.subheader("Lokasyon ve Fiziksel Alan Yönetimi")
    
    # Şirketleri çekiyoruz
    try:
        query_res = supabase.table("sirketler").select("id, sirket_adi").execute()
        sirket_df = pd.DataFrame(query_res.data)
    except Exception as e:
        st.error(f"Şirket listesi alınamadı: {e}")
        sirket_df = pd.DataFrame()

    if not sirket_df.empty:
        # Seçim Alanı
        col_sel1, col_sel2 = st.columns([2, 1])
        with col_sel1:
            selected_sirket_name = st.selectbox("İşlem Yapılacak Şirketi Seçin", sirket_df['sirket_adi'])
        
        selected_sirket_id = sirket_df[sirket_df['sirket_adi'] == selected_sirket_name]['id'].values[0]

        tab_add, tab_list = st.tabs(["Yeni Lokasyon Tanımla", "Mevcut Lokasyonlar"])

        with tab_add:
            with st.form("lokasyon_yeni_form", clear_on_submit=True):
                st.markdown("##### Şube / Birim Lokasyon Bilgileri")
                c1, c2 = st.columns(2)
                l_ad = c1.text_input("Lokasyon Adı", placeholder="Örn: Tuzla Lojistik Merkezi")
                l_tip = c2.selectbox("Lokasyon Tipi", ["Genel Merkez", "Bölge Müdürlüğü", "Şube", "Depo", "Antrepo", "Fabrika", "Bayi / Satış Noktası"])
                
                l_adres = st.text_area("Açık Adres / Konum Bilgisi")
                l_tel = st.text_input("Lokasyon Sabit Hattı")
                
                if st.form_submit_button("Lokasyon Profilini Kaydet"):
                    if l_ad:
                        new_loc = {
                            "sirket_id": str(selected_sirket_id),
                            "lokasyon_adi": l_ad,
                            "lokasyon_tipi": l_tip,
                            "adres": l_adres,
                            "telefon": l_tel
                        }
                        try:
                            supabase.table("lokasyonlar").insert(new_loc).execute()
                            st.success(f"'{l_ad}' sisteme başarıyla işlendi.")
                        except Exception as e:
                            st.error(f"Kayıt Hatası: {e}")
                    else:
                        st.warning("Lütfen Lokasyon Adı alanını doldurun.")

        with tab_list:
            try:
                # Sadece seçilen şirketin lokasyonlarını getir
                res_l = supabase.table("lokasyonlar").select("*").eq("sirket_id", selected_sirket_id).execute()
                l_data = pd.DataFrame(res_l.data)
                if not l_data.empty:
                    # Tabloyu daha şık gösterelim
                    l_data.columns = [c.replace('_', ' ').title() for c in l_data.columns]
                    st.dataframe(l_data[['Lokasyon Adi', 'Lokasyon Tipi', 'Telefon', 'Adres']], use_container_width=True, hide_index=True)
                else:
                    st.info("Bu şirkete tanımlanmış bir dış lokasyon bulunamadı.")
            except:
                st.info("Veriler yüklenirken bir sorun oluştu veya tablo henüz boş.")
    else:
        st.warning("Lokasyon tanımlayabilmek için önce 'Şirket Tanımlama' menüsünden en az bir şirket oluşturmalısınız.")

# --- ŞİRKET TANIMLAMA (Önceki kodun aynısı, hata payı bırakılmadı) ---
elif menu == "Şirket Tanımlama":
    st.subheader("Kurumsal Şirket Profil Yönetimi")
    # ... (Şirket tanımlama kodun burada devam edebilir)
