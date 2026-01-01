import streamlit as st
from supabase import create_client
import pandas as pd

# Bağlantı Ayarları
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### İM-FEXİM")
    st.markdown("<p style='font-size:11px; color:#ADB5BD; letter-spacing:1px; margin-top:-15px;'>ORGANİZASYONEL YÖNETİM</p>", unsafe_allow_html=True)
    menu = st.radio("SİSTEM MENÜSÜ", ["Şirket Tanımlama", "Lokasyon Yönetimi", "Birim Yönetimi", "Personel İşlemleri"])

# --- LOKASYON YÖNETİMİ ALANI ---
if menu == "Lokasyon Yönetimi":
    st.subheader("Lokasyon ve Fiziksel Alan Yönetimi")
    st.markdown("<p style='font-size:14px; color:#67748E;'>Şirketin genel merkezi, depoları, şubeleri ve bayileri bu alandan yönetilir.</p>", unsafe_allow_html=True)

    # Önce hangi şirkete lokasyon ekleneceğini seçtiriyoruz
    sirketler_res = supabase.table("sirketler").select("id, sirket_adi").execute()
    sirket_df = pd.DataFrame(sirket_res.data)

    if not sirket_df.empty:
        selected_sirket_name = st.selectbox("İşlem Yapılacak Şirketi Seçin", sirket_df['sirket_adi'])
        selected_sirket_id = sirket_df[sirket_df['sirket_adi'] == selected_sirket_name]['id'].values[0]

        tab_l_add, tab_l_list = st.tabs(["Yeni Lokasyon Tanımla", "Mevcut Lokasyonlar"])

        with tab_l_add:
            with st.form("lokasyon_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                l_ad = col1.text_input("Lokasyon / Şube Adı", placeholder="Örn: Tuzla Depo")
                l_tip = col2.selectbox("Lokasyon Tipi", ["Genel Merkez", "Ofis", "Depo", "Bayi", "Fabrika", "Şube"])
                
                l_adres = st.text_area("Fiziksel Adres")
                l_tel = st.text_input("Lokasyon İletişim Hattı")
                
                if st.form_submit_button("Lokasyonu Kaydet"):
                    try:
                        data = {
                            "sirket_id": str(selected_sirket_id),
                            "lokasyon_adi": l_ad,
                            "lokasyon_tipi": l_tip,
                            "adres": l_adres,
                            "telefon": l_tel
                        }
                        supabase.table("lokasyonlar").insert(data).execute()
                        st.success(f"{l_ad} ({l_tip}) başarıyla tanımlandı.")
                    except Exception as e:
                        st.error(f"Hata: {e}")

        with tab_l_list:
            # Sadece seçilen şirkete ait lokasyonları listeliyoruz
            res = supabase.table("lokasyonlar").select("*").eq("sirket_id", selected_sirket_id).execute()
            l_df = pd.DataFrame(res.data)
            if not l_df.empty:
                st.dataframe(l_df[['lokasyon_adi', 'lokasyon_tipi', 'telefon', 'adres']], use_container_width=True, hide_index=True)
            else:
                st.info("Bu şirkete ait tanımlanmış lokasyon bulunmuyor.")
    else:
        st.warning("Lütfen önce 'Şirket Tanımlama' menüsünden bir şirket oluşturun.")
