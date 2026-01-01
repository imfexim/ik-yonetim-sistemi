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
    /* Dinamik Liste Alanı */
    .loc-box { border: 1px solid #E9ECEF; padding: 10px; border-radius: 5px; margin-bottom: 5px; background: #FBFBFB; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Dinamik Liste Durum Yönetimi (Session State)
if 'gecici_lokasyonlar' not in st.session_state:
    st.session_state.gecici_lokasyonlar = []

# 4. Yan Menü
with st.sidebar:
    st.markdown("### İM-FEXİM")
    menu = st.radio("SİSTEM MENÜSÜ", ["Şirket ve Lokasyon Tanımlama", "Birim Yönetimi", "Personel İşlemleri"])

if menu == "Şirket ve Lokasyon Tanımlama":
    st.subheader("Kurumsal Şirket ve Çoklu Lokasyon Yönetimi")
    
    t1, t2 = st.tabs(["Yeni Şirket ve Şube Kaydı", "Kayıtlı Şirketler ve Şubeleri"])
    
    with t1:
        # --- BÖLÜM 1: ŞİRKET BİLGİLERİ (Form Dışında Tutuyoruz ki Liste Eklenince Sıfırlanmasın) ---
        st.markdown("##### 🏢 1. Şirket Genel Bilgileri")
        c1, c2 = st.columns(2)
        s_ad = c1.text_input("Şirket Adı (Resmi Ünvan)")
        s_mail = c2.text_input("Kurumsal Mail")
        
        st.markdown("##### 👤 2. Şirket Üst Yöneticisi")
        y1, y2, y3 = st.columns(3)
        y_ad = y1.text_input("Yönetici Ad Soyad")
        y_tel = y2.text_input("Yönetici Telefon")
        y_mail = y3.text_input("Yönetici Mail")

        st.divider()

        # --- BÖLÜM 2: DİNAMİK LOKASYON EKLEME ALANI ---
        st.markdown("##### 📍 3. Lokasyon / Şube / Bayi Ekleme")
        with st.container():
            l1, l2, l3 = st.columns(3)
            l_ad = l1.text_input("Lokasyon Adı", placeholder="Örn: Tuzla Depo")
            l_tip = l2.selectbox("Tipi", ["Genel Merkez", "Ofis", "Şube", "Depo", "Fabrika", "Bayi"])
            l_tel = l3.text_input("Lokasyon Telefon")
            
            l_adr = st.text_area("Lokasyon Adresi", height=70)
            
            lx, ly = st.columns(2)
            l_x = lx.text_input("Koordinat X (Enlem)")
            l_y = ly.text_input("Koordinat Y (Boylam)")

            st.markdown("##### 📞 4. Lokasyon Sorumlusu")
            m1, m2, m3 = st.columns(3)
            m_ad = m1.text_input("Sorumlu Adı")
            m_tel = m2.text_input("Sorumlu Telefon")
            m_mail = m3.text_input("Sorumlu Mail")

            if st.button("➕ Bu Lokasyonu Listeye Ekle"):
                if l_ad:
                    yeni_lok = {
                        "lokasyon_adi": l_ad, "lokasyon_tipi": l_tip, "telefon": l_tel,
                        "adres": l_adr, "koordinat_x": l_x, "koordinat_y": l_y,
                        "sorumlu_ad_soyad": m_ad, "sorumlu_telefon": m_tel, "sorumlu_mail": m_mail
                    }
                    st.session_state.gecici_lokasyonlar.append(yeni_lok)
                    st.toast(f"{l_ad} listeye eklendi!")
                else:
                    st.error("Lokasyon adı boş bırakılamaz.")

        # --- BÖLÜM 3: EKLENEN LOKASYONLARIN ÖNİZLEMESİ ---
        if st.session_state.gecici_lokasyonlar:
            st.markdown("##### 📋 Eklenecek Lokasyon Listesi")
            for i, loc in enumerate(st.session_state.gecici_lokasyonlar):
                st.markdown(f"""
                <div class="loc-box">
                    <b>{i+1}. {loc['lokasyon_adi']}</b> ({loc['lokasyon_tipi']}) - 
                    Sorumlu: {loc['sorumlu_ad_soyad']} | {loc['adres'][:30]}...
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🗑️ Listeyi Temizle"):
                st.session_state.gecici_lokasyonlar = []
                st.rerun()

        st.divider()

        # --- BÖLÜM 4: ANA KAYIT BUTONU ---
        if st.button("🚀 ŞİRKETİ VE TÜM LOKASYONLARI VERİTABANINA KAYDET"):
            if not s_ad:
                st.error("Şirket adı girmek zorunludur.")
            elif not st.session_state.gecici_lokasyonlar:
                st.error("En az bir lokasyon eklemelisiniz.")
            else:
                try:
                    # 1. Şirketi Kaydet
                    s_res = supabase.table("sirketler").insert({
                        "sirket_adi": s_ad, "sirket_mail": s_mail,
                        "yonetici_adi": y_ad, "yonetici_telefon": y_tel, "yonetici_mail": y_mail
                    }).execute()
                    new_sirket_id = s_res.data[0]['id']

                    # 2. Tüm Lokasyonları Toplu Kaydet
                    final_loc_list = []
                    for loc in st.session_state.gecici_lokasyonlar:
                        loc['sirket_id'] = new_sirket_id # Şirket ID'sini her lokasyona bağla
                        final_loc_list.append(loc)
                    
                    supabase.table("lokasyonlar").insert(final_loc_list).execute()
                    
                    st.success(f"'{s_ad}' şirketi ve {len(final_loc_list)} lokasyon başarıyla kaydedildi!")
                    st.session_state.gecici_lokasyonlar = [] # Listeyi sıfırla
                except Exception as e:
                    st.error(f"Kayıt Hatası: {e}")

    with t2:
        # Kayıtlı verileri listeleme (Aynı expander yapısı)
        try:
            res = supabase.table("sirketler").select("*, lokasyonlar(*)").execute()
            for item in res.data:
                with st.expander(f"🏢 {item['sirket_adi']} ({len(item['lokasyonlar'])} Lokasyon)"):
                    if item['lokasyonlar']:
                        ldf = pd.DataFrame(item['lokasyonlar'])
                        st.table(ldf[['lokasyon_adi', 'lokasyon_tipi', 'sorumlu_ad_soyad', 'adres']])
        except: pass
