import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Sayfa Ayarları
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

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Yan Menü (Daha yalın)
with st.sidebar:
    st.markdown("### İM-FEXİM")
    st.markdown("<p style='font-size:11px; color:#ADB5BD; letter-spacing:1px; margin-top:-15px;'>ORGANİZASYONEL YÖNETİM</p>", unsafe_allow_html=True)
    menu = st.radio("SİSTEM MENÜSÜ", ["Şirket ve Lokasyon Tanımlama", "Birim Yönetimi", "Personel İşlemleri"])

# --- ŞİRKET VE LOKASYON BİRLEŞİK YÖNETİMİ ---
if menu == "Şirket ve Lokasyon Tanımlama":
    st.subheader("Kurumsal Şirket ve Birincil Lokasyon Yönetimi")
    
    tab_create, tab_list = st.tabs(["Yeni Şirket ve Lokasyon Kaydı", "Kayıtlı Şirketler ve Şubeleri"])
    
    with tab_create:
        with st.form("birlesik_kayit_formu", clear_on_submit=True):
            # BÖLÜM 1: ŞİRKET BİLGİLERİ
            st.markdown("##### 1. Kurumsal Şirket Bilgileri")
            c1, c2 = st.columns(2)
            s_ad = c1.text_input("Şirket Adı (Resmi Ünvan)")
            s_mail = c2.text_input("Kurumsal Mail")
            
            # BÖLÜM 2: YÖNETİCİ BİLGİLERİ
            st.markdown("<br>##### 2. Üst Yönetici Bilgileri", unsafe_allow_html=True)
            y1, y2, y3 = st.columns(3)
            y_ad = y1.text_input("Yönetici Ad Soyad")
            y_tel = y2.text_input("Yönetici Telefon")
            y_mail = y3.text_input("Yönetici Mail")

            # BÖLÜM 3: LOKASYON BİLGİLERİ (Zorunlu İlk Lokasyon)
            st.markdown("<br>##### 3. Birincil Lokasyon / Şube Bilgileri", unsafe_allow_html=True)
            l1, l2, l3 = st.columns(3)
            l_ad = l1.text_input("Lokasyon Adı", value="Genel Merkez")
            l_tip = l2.selectbox("Lokasyon Tipi", ["Genel Merkez", "Ofis", "Şube", "Depo", "Fabrika"])
            l_tel = l3.text_input("Lokasyon Telefonu")
            
            l_adres = st.text_area("Lokasyon Açık Adresi")
            
            lx, ly = st.columns(2)
            l_x = lx.text_input("Koordinat X (Enlem)")
            l_y = ly.text_input("Koordinat Y (Boylam)")

            if st.form_submit_button("Şirket ve Lokasyonu Birlikte Kaydet"):
                if s_ad and l_ad:
                    try:
                        # 1. Şirketi Kaydet
                        s_data = {
                            "sirket_adi": s_ad, "sirket_mail": s_mail,
                            "yonetici_adi": y_ad, "yonetici_telefon": y_tel, "yonetici_mail": y_mail
                        }
                        s_res = supabase.table("sirketler").insert(s_data).execute()
                        new_sirket_id = s_res.data[0]['id']

                        # 2. Lokasyonu Kaydet (Şirket ID'sine bağlayarak)
                        l_data = {
                            "sirket_id": new_sirket_id, "lokasyon_adi": l_ad, "lokasyon_tipi": l_tip,
                            "telefon": l_tel, "adres": l_adres, "koordinat_x": l_x, "koordinat_y": l_y
                        }
                        supabase.table("lokasyonlar").insert(l_data).execute()
                        
                        st.success(f"'{s_ad}' şirketi ve '{l_ad}' lokasyonu başarıyla oluşturuldu.")
                    except Exception as e:
                        st.error(f"Kayıt sırasında hata: {e}")
                else:
                    st.warning("Lütfen Şirket Adı ve Lokasyon Adı alanlarını doldurunuz.")

    with tab_list:
        # Şirketleri ve onlara bağlı lokasyonları çekiyoruz
        try:
            res = supabase.table("sirketler").select("*, lokasyonlar(*)").execute()
            data = res.data
            
            if data:
                for item in data:
                    with st.expander(f"🏢 {item['sirket_adi']} (Yönetici: {item['yonetici_adi']})"):
                        st.markdown(f"**Kurumsal Mail:** {item['sirket_mail']}")
                        st.markdown("**Bağlı Lokasyonlar / Şubeler:**")
                        
                        # Bu şirkete ait lokasyonları tablo olarak göster
                        loc_df = pd.DataFrame(item['lokasyonlar'])
                        if not loc_df.empty:
                            loc_display = loc_df[['lokasyon_adi', 'lokasyon_tipi', 'telefon', 'adres', 'koordinat_x', 'koordinat_y']]
                            loc_display.columns = ["Lokasyon", "Tip", "Telefon", "Adres", "X", "Y"]
                            st.table(loc_display)
                        
                        # Ek lokasyon ekleme butonu istersen buraya eklenebilir
            else:
                st.info("Kayıtlı şirket bulunamadı.")
        except Exception as e:
            st.error(f"Veri çekme hatası: {e}")
