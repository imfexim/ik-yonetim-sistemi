import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Konfigürasyon
st.set_page_config(page_title="İM-FEXİM Kurumsal Ekosistem", layout="wide")

# Kurumsal Stil
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"], .stMarkdown, p, span, label { color: #344767 !important; font-family: 'Segoe UI', sans-serif; }
    .loc-box { border: 1px solid #E9ECEF; padding: 10px; border-radius: 5px; margin-bottom: 5px; background: #FBFBFB; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Durum Yönetimi
if 'gecici_lokasyonlar' not in st.session_state: st.session_state.gecici_lokasyonlar = []

# 4. Yan Menü
with st.sidebar:
    st.markdown("### İM-FEXİM")
    menu = st.radio("SİSTEM MENÜSÜ", ["Şirket ve İlişki Tanımlama", "Birim Yönetimi", "Personel İşlemleri"])

if menu == "Şirket ve İlişki Tanımlama":
    st.subheader("Kurumsal Ekosistem ve İlişki Yönetimi")
    t1, t2 = st.tabs(["Yeni Şirket ve İlişki Tanımla", "Ekosistem Haritası"])
    
    with t1:
        st.markdown("##### 🏢 1. Şirket Temel Bilgileri")
        c1, c2, c3 = st.columns(3)
        s_ad = c1.text_input("Şirket Adı")
        s_turu = c2.selectbox("Şirket Türü", ["Grup Şirketi", "Tedarikçi", "Satış Kanalı", "Hizmet Sağlayıcı (Danışman vb.)", "Resmi Kurum"])
        s_mail = c3.text_input("Kurumsal Mail")

        # İLİŞKİ TANIMLAMA: Eğer dış şirketse, bizim hangi şirketlerimizle muhatap?
        st.markdown("##### 🔗 2. Şirket İlişkileri")
        try:
            # Mevcut grup şirketlerini çekiyoruz
            grup_res = supabase.table("sirketler").select("id, sirket_adi").eq("sirket_turu", "Grup Şirketi").execute()
            grup_df = pd.DataFrame(grup_res.data)
            
            if not grup_df.empty:
                muhatap_sirketler = st.multiselect(
                    f"Bu şirket ({s_ad}) bizim hangi şirketlerimizle muhatap?",
                    options=grup_df['sirket_adi'].tolist(),
                    help="Örn: Media Markt için sadece 'IMF Elektronik' seçin. İSG firması için her ikisini seçebilirsiniz."
                )
                iliski_aciklamasi = st.text_input("Muhataplık Türü / Notu", placeholder="Örn: Beyaz Eşya Satış Kanalı, İSG Danışmanlık Hizmeti")
            else:
                st.info("İlişki kurabilmek için önce en az bir 'Grup Şirketi' tanımlamalısınız.")
        except: pass

        st.markdown("##### 📍 3. Lokasyon Ekleme")
        # (Önceki dinamik lokasyon ekleme yapısı buraya gelecek - l_ad, l_tip vb.)
        # ... (Kodun bu kısmı öncekiyle aynı kalıyor, yer kazanmak için özet geçiyorum) ...
        # [Kısa Not: Lokasyon ekleme butonu ve st.session_state.gecici_lokasyonlar mantığı burada aktif çalışır]

        if st.button("🚀 ŞİRKETİ VE İLİŞKİLERİ KAYDET"):
            if s_ad:
                try:
                    # 1. Şirketi Kaydet
                    s_ins = supabase.table("sirketler").insert({
                        "sirket_adi": s_ad, "sirket_turu": s_turu, "sirket_mail": s_mail
                    }).execute()
                    new_id = s_ins.data[0]['id']

                    # 2. İlişkileri Kaydet
                    if muhatap_sirketler:
                        iliski_listesi = []
                        for m_ad in muhatap_sirketler:
                            target_id = grup_df[grup_df['sirket_adi'] == m_ad]['id'].values[0]
                            iliski_listesi.append({
                                "kaynak_sirket_id": new_id,
                                "hedef_sirket_id": target_id,
                                "iliski_turu": iliski_aciklamasi
                            })
                        supabase.table("sirket_iliskileri").insert(iliski_listesi).execute()

                    # 3. Lokasyonları Kaydet
                    # ... (Lokasyon insert işlemi) ...
                    
                    st.success(f"'{s_ad}' ve tanımlanan {len(muhatap_sirketler)} ilişki başarıyla kaydedildi.")
                except Exception as e: st.error(f"Hata: {e}")

    with t2:
        # EKOSİSTEM GÖRÜNÜMÜ: Kim kiminle muhatap?
        res = supabase.table("sirketler").select("*, sirket_iliskileri!kaynak_sirket_id(*, sirketler!hedef_sirket_id(s_adi:sirket_adi))").execute()
        # Bu kısımda veriyi işleyip "Media Markt -> IMF (Satış Kanalı)" şeklinde listeliyoruz.
