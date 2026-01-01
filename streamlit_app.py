import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Konfigürasyon
st.set_page_config(page_title="İM-FEXİM Operasyon Yönetimi", layout="wide")

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Session State
if 'v_list' not in st.session_state: st.session_state.v_list = []

# 4. Yan Menü
with st.sidebar:
    st.title("İM-FEXİM OPS")
    menu = st.radio("SİSTEM MENÜSÜ", ["Lokasyon Bankası", "Şirket & Bayi Yapılandırma", "Saha Operasyon İzleme"])

# --- LOKASYON BANKASI ---
if menu == "Lokasyon Bankası":
    st.subheader("📍 Fiziksel Mağaza/Bayi Lokasyonları")
    with st.form("lokasyon_ekle"):
        c1, c2 = st.columns(2)
        l_ad = c1.text_input("Lokasyon/AVM Adı", placeholder="Örn: Meydan AVM")
        l_tip = c2.selectbox("Tür", ["AVM Mağaza", "Cadde Mağaza", "Depo", "Ofis", "Fabrika"])
        l_adr = st.text_area("Açık Adres")
        lx, ly = st.columns(2)
        if st.form_submit_button("Lokasyonu Kaydet"):
            supabase.table("lokasyonlar").insert({"lokasyon_adi": l_ad, "lokasyon_tipi": l_tip, "adres": l_adr, "koordinat_x": lx.text_input("Enlem (X)"), "koordinat_y": ly.text_input("Boylam (Y)")}).execute()
            st.success("Lokasyon havuza eklendi.")

# --- ŞİRKET & BAYİ YAPILANDIRMA ---
elif menu == "Şirket & Bayi Yapılandırma":
    st.subheader("🏢 Kurumsal Hiyerarşi ve Saha Yapısı")
    t1, t2 = st.tabs(["Yeni Şirket/Bayi Tanımla", "Hiyerarşi Görüntüle"])

    with t1:
        st.markdown("##### 1. Şirket/Bayi Kimlik Bilgileri")
        c1, c2, c3 = st.columns(3)
        s_ad = c1.text_input("Şirket/Bayi Adı")
        s_kat = c2.selectbox("Kategori", ["Operatör (Turkcell/Vodafone)", "Zincir Mağaza (MediaMarkt/Teknosa)", "Tedarikçi (Üretim/Sarf)", "Distribütör", "Lojistik/Gümrük"])
        s_rol = c3.selectbox("Rol", ["Ana Marka", "Distribütör", "Üst Bayi", "Mağaza/Alt Bayi"])

        # HİYERARŞİ BAĞLANTISI (Örn: Bu bayi hangi distribütöre bağlı?)
        st.markdown("##### 2. Bağlantı Bilgileri")
        res_s = supabase.table("sirketler").select("id, sirket_adi").execute()
        s_df = pd.DataFrame(res_s.data)
        ust_id = None
        if not s_df.empty:
            ust_secim = st.selectbox("Bağlı Olduğu Üst Şirket/Distribütör (Varsa)", ["Yok"] + s_df['sirket_adi'].tolist())
            if ust_secim != "Yok":
                ust_id = s_df[s_df['sirket_adi'] == ust_secim]['id'].values[0]

        # SAHA MUHATAPLARI (Mağaza Bazlı)
        st.divider()
        st.markdown("##### 3. Lokasyon Mevcudiyeti ve Saha Muhatapları")
        res_l = supabase.table("lokasyonlar").select("id, lokasyon_adi").execute()
        l_df = pd.DataFrame(res_l.data)
        
        if not l_df.empty:
            col_l1, col_l2 = st.columns([1, 2])
            l_secim = col_l1.selectbox("Mağaza Lokasyonu", l_df['lokasyon_adi'].tolist())
            l_id = l_df[l_df['lokasyon_adi'] == l_secim]['id'].values[0]
            
            st.caption("Bu mağazadaki/lokasyondaki muhatabımız:")
            m1, m2, m3 = st.columns(3)
            m_ad = m1.text_input("Muhatap Ad Soyad")
            m_tel = m2.text_input("Telefon")
            m_mail = m3.text_input("E-Posta")
            
            if st.button("➕ Mağaza/Varlık Ekle"):
                st.session_state.v_list.append({
                    "id": l_id, "ad": l_secim, "m_ad": m_ad, "m_tel": m_tel, "m_mail": m_mail
                })
            
            if st.session_state.v_list:
                st.dataframe(pd.DataFrame(st.session_state.gecici_varliklar if 'gecici_varliklar' in locals() else st.session_state.v_list), use_container_width=True)

        if st.button("🚀 TÜM HİYERARŞİYİ KAYDET"):
            try:
                # 1. Şirketi Kaydet
                s_data = {"sirket_adi": s_ad, "sirket_kategorisi": s_kat, "sirket_rolu": s_rol, "ust_sirket_id": ust_id}
                s_res = supabase.table("sirketler").insert(s_data).execute()
                new_id = s_res.data[0]['id']
                
                # 2. Lokasyon Varlıklarını Kaydet
                for v in st.session_state.v_list:
                    supabase.table("sirket_lokasyon_varliklari").insert({
                        "sirket_id": new_id, "lokasyon_id": v['id'],
                        "muhatap_ad_soyad": v['m_ad'], "muhatap_telefon": v['m_tel'], "muhatap_mail": v['m_mail']
                    }).execute()
                
                st.success("Hiyerarşik kayıt tamamlandı.")
                st.session_state.v_list = []
                st.rerun()
            except Exception as e: st.error(str(e))
