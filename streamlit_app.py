import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Konfigürasyon ve Stil
st.set_page_config(page_title="İM-FEXİM Kurumsal Yönetim", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"], .stMarkdown, p, span, label { color: #344767 !important; font-family: 'Segoe UI', sans-serif; }
    .data-box { border: 1px solid #E9ECEF; padding: 10px; border-radius: 5px; margin-bottom: 5px; background: #FBFBFB; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Bağlantı
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# 3. Dinamik Liste Yönetimi (Session State)
if 'gecici_lokasyonlar' not in st.session_state: st.session_state.gecici_lokasyonlar = []
if 'gecici_iliskiler' not in st.session_state: st.session_state.gecici_iliskiler = []

# 4. Yan Menü
with st.sidebar:
    st.markdown("### İM-FEXİM")
    menu = st.radio("SİSTEM MENÜSÜ", ["Şirket ve İlişki Tanımlama", "Birim Yönetimi", "Personel İşlemleri"])

if menu == "Şirket ve İlişki Tanımlama":
    st.subheader("Kurumsal Şirket, Lokasyon ve İlişki Yönetimi")
    t1, t2 = st.tabs(["Yeni Kayıt Tanımla", "Ekosistem Listesi"])
    
    with t1:
        # BÖLÜM 1: ŞİRKET TEMEL BİLGİLERİ
        st.markdown("##### 🏢 1. Şirket Genel Bilgileri")
        c1, c2, c3 = st.columns(3)
        s_ad = c1.text_input("Şirket Adı")
        s_turu = c2.selectbox("Şirket Türü", ["Grup Şirketi", "Tedarikçi", "Satış Kanalı", "Hizmet Sağlayıcı", "Resmi Kurum"])
        s_mail = c3.text_input("Şirket Kurumsal Mail")
        
        y1, y2, y3 = st.columns(3)
        y_ad = y1.text_input("Yönetici Ad Soyad")
        y_tel = y2.text_input("Yönetici Telefon")
        y_mail = y3.text_input("Yönetici Mail")

        st.divider()

        # BÖLÜM 2: DİNAMİK LOKASYON EKLEME
        st.markdown("##### 📍 2. Lokasyon / Şube / Bayi Ekleme")
        l1, l2, l3 = st.columns(3)
        l_ad = l1.text_input("Lokasyon Adı", placeholder="Örn: Tuzla Depo")
        l_tip = l2.selectbox("Tipi", ["Genel Merkez", "Şube", "Depo", "Bayi", "Fabrika"])
        l_tel = l3.text_input("Lokasyon Telefon")
        
        lx, ly = st.columns(2)
        l_x = lx.text_input("Koordinat X (Enlem)")
        l_y = ly.text_input("Koordinat Y (Boylam)")
        
        st.markdown("###### Lokasyon Sorumlusu")
        ls1, ls2, ls3 = st.columns(3)
        ls_ad = ls1.text_input("Sorumlu Ad Soyad")
        ls_tel = ls2.text_input("Sorumlu Telefon")
        ls_mail = ls3.text_input("Sorumlu Mail")
        
        if st.button("➕ Lokasyonu Listeye Ekle"):
            if l_ad:
                st.session_state.gecici_lokasyonlar.append({
                    "lokasyon_adi": l_ad, "lokasyon_tipi": l_tip, "telefon": l_tel,
                    "koordinat_x": l_x, "koordinat_y": l_y, "sorumlu_ad_soyad": ls_ad,
                    "sorumlu_telefon": ls_tel, "sorumlu_mail": ls_mail
                })
            else: st.error("Lokasyon adı gereklidir.")

        if st.session_state.gecici_lokasyonlar:
            st.table(pd.DataFrame(st.session_state.gecici_lokasyonlar)[['lokasyon_adi', 'lokasyon_tipi', 'sorumlu_ad_soyad']])

        st.divider()

        # BÖLÜM 3: İLİŞKİLİ ŞİRKET EKLEME
        st.markdown("##### 🔗 3. Muhatap / İlişkili Şirket Ekleme")
        try:
            grup_res = supabase.table("sirketler").select("id, sirket_adi").eq("sirket_turu", "Grup Şirketi").execute()
            grup_df = pd.DataFrame(grup_res.data)
            
            if not grup_df.empty:
                r1, r2 = st.columns(2)
                muhatap_secim = r1.selectbox("Bizim Şirketimiz", grup_df['sirket_adi'].tolist())
                iliski_tipi = r2.text_input("İlişki Türü", placeholder="Örn: Satış Kanalı, İSG Hizmeti")
                
                if st.button("🔗 İlişkiyi Listeye Ekle"):
                    target_id = grup_df[grup_df['sirket_adi'] == muhatap_secim]['id'].values[0]
                    st.session_state.gecici_iliskiler.append({
                        "hedef_sirket_id": target_id,
                        "hedef_sirket_adi": muhatap_secim,
                        "iliski_turu": iliski_tipi
                    })
                
                if st.session_state.gecici_iliskiler:
                    st.table(pd.DataFrame(st.session_state.gecici_iliskiler)[['hedef_sirket_adi', 'iliski_turu']])
            else:
                st.info("İlişki tanımlamak için önce bir 'Grup Şirketi' kaydetmelisiniz.")
        except: pass

        st.divider()

        # BÖLÜM 4: ANA KAYIT
        if st.button("🚀 TÜM BİLGİLERİ VE TABLOLARI KAYDET"):
            if s_ad and st.session_state.gecici_lokasyonlar:
                try:
                    # 1. Şirket
                    s_res = supabase.table("sirketler").insert({"sirket_adi": s_ad, "sirket_turu": s_turu, "sirket_mail": s_mail, "yonetici_adi": y_ad, "yonetici_telefon": y_tel, "yonetici_mail": y_mail}).execute()
                    s_id = s_res.data[0]['id']

                    # 2. Lokasyonlar
                    for l in st.session_state.gecici_lokasyonlar: l['sirket_id'] = s_id
                    supabase.table("lokasyonlar").insert(st.session_state.gecici_lokasyonlar).execute()

                    # 3. İlişkiler
                    for r in st.session_state.gecici_iliskiler:
                        supabase.table("sirket_iliskileri").insert({
                            "kaynak_sirket_id": s_id,
                            "hedef_sirket_id": r['hedef_sirket_id'],
                            "iliski_turu": r['iliski_turu']
                        }).execute()

                    st.success("Kayıt başarıyla tamamlandı!")
                    st.session_state.gecici_lokasyonlar = []; st.session_state.gecici_iliskiler = []
                    st.rerun()
                except Exception as e: st.error(f"Hata: {e}")
            else: st.warning("Şirket adı ve en az bir lokasyon zorunludur.")

    with t2:
        # LİSTELEME
        try:
            res = supabase.table("sirketler").select("*, lokasyonlar(*), sirket_iliskileri!kaynak_sirket_id(*, sirketler!hedef_sirket_id(sirket_adi))").execute()
            for item in res.data:
                with st.expander(f"🏢 {item['sirket_adi']} ({item['sirket_turu']})"):
                    st.markdown("**Lokasyonlar:**")
                    st.table(pd.DataFrame(item['lokasyonlar'])[['lokasyon_adi', 'lokasyon_tipi', 'sorumlu_ad_soyad']] if item['lokasyonlar'] else "Yok")
                    
                    st.markdown("**Muhataplıklar:**")
                    if item['sirket_iliskileri']:
                        rel_data = [{"Muhatap Şirket": r['sirketler']['sirket_adi'], "İlişki Türü": r['iliski_turu']} for r in item['sirket_iliskileri']]
                        st.table(pd.DataFrame(rel_data))
        except: pass
