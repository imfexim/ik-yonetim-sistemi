import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Konfigürasyon
st.set_page_config(page_title="İM-FEXİM Kurumsal Yönetim", layout="wide")

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

# 3. Session State Yönetimi
if 'gecici_lokasyonlar' not in st.session_state: st.session_state.gecici_lokasyonlar = []
if 'gecici_iliskiler' not in st.session_state: st.session_state.gecici_iliskiler = []

# 4. Menü
with st.sidebar:
    st.markdown("### İM-FEXİM")
    menu = st.radio("SİSTEM MENÜSÜ", ["Şirket Yönetimi", "Birim Yönetimi", "Personel İşlemleri"])

if menu == "Şirket Yönetimi":
    st.subheader("Kurumsal Ekosistem Yönetimi")
    t1, t2 = st.tabs(["Yeni Kayıt Tanımla", "Düzenle / Listele / Sil"])
    
    with t1:
        # --- BÖLÜM 1: ŞİRKET GENEL BİLGİLERİ ---
        st.markdown("##### 🏢 1. Şirket Genel Bilgileri")
        c1, c2 = st.columns(2)
        s_ad = c1.text_input("Şirket Adı")
        s_mail = c2.text_input("Kurumsal Mail")
        
        y1, y2, y3 = st.columns(3)
        y_ad = y1.text_input("Yönetici Ad Soyad")
        y_tel = y2.text_input("Yönetici Telefon")
        y_mail = y3.text_input("Yönetici Mail")

        st.divider()

        # --- BÖLÜM 2: LOKASYON EKLEME ---
        st.markdown("##### 📍 2. Lokasyon / Şube Bilgileri")
        l1, l2, l3 = st.columns(3)
        l_ad = l1.text_input("Lokasyon Adı", placeholder="Örn: Kadıköy Ofis")
        l_tip = l2.selectbox("Tipi", ["Genel Merkez", "Şube", "Depo", "Bayi", "Fabrika"])
        l_tel = l3.text_input("Lokasyon Telefon")
        
        l_adr = st.text_area("Lokasyon Adresi", height=70)
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
                    "lokasyon_adi": l_ad, "lokasyon_tipi": l_tip, "telefon": l_tel, "adres": l_adr,
                    "koordinat_x": l_x, "koordinat_y": l_y, "sorumlu_ad_soyad": ls_ad,
                    "sorumlu_telefon": ls_tel, "sorumlu_mail": ls_mail
                })
            else: st.error("Lokasyon adı gereklidir.")

        if st.session_state.gecici_lokasyonlar:
            st.table(pd.DataFrame(st.session_state.gecici_lokasyonlar)[['lokasyon_adi', 'lokasyon_tipi', 'sorumlu_ad_soyad']])

        st.divider()

        # --- BÖLÜM 3: MUHATAPLIK VE İLİŞKİ TÜRÜ ---
        st.markdown("##### 🔗 3. Muhataplık ve İlişkili Şirket Tanımlama")
        
        # Bu şirketin türü burada belirleniyor
        m_turu = st.selectbox("Bu Şirketin Bizim İçin Türü", ["Grup Şirketi", "Tedarikçi", "Satış Kanalı", "Hizmet Sağlayıcı", "Resmi Kurum"])
        
        try:
            # Sistemdeki mevcut şirketleri çekiyoruz
            mevcut_res = supabase.table("sirketler").select("id, sirket_adi").execute()
            mevcut_df = pd.DataFrame(mevcut_res.data)
            
            if not mevcut_df.empty:
                r1, r2 = st.columns(2)
                muhatap_secim = r1.selectbox("Muhatap Olduğu Şirket", mevcut_df['sirket_adi'].tolist())
                iliski_notu = r2.text_input("Muhataplık Durumu / Notu", placeholder="Örn: İSG Danışmanlık Alıyor")
                
                if st.button("🔗 İlişkiyi Listeye Ekle"):
                    target_id = mevcut_df[mevcut_df['sirket_adi'] == muhatap_secim]['id'].values[0]
                    st.session_state.gecici_iliskiler.append({
                        "hedef_sirket_id": target_id,
                        "hedef_sirket_adi": muhatap_secim,
                        "iliski_turu": iliski_notu
                    })
                
                if st.session_state.gecici_iliskiler:
                    st.table(pd.DataFrame(st.session_state.gecici_iliskiler)[['hedef_sirket_adi', 'iliski_turu']])
            else:
                st.info("İlişki kurmak için sistemde en az bir şirket kayıtlı olmalıdır. (İlk şirket için burayı boş bırakın)")
        except: pass

        if st.button("🚀 TÜM KAYDI TAMAMLA"):
            if s_ad and st.session_state.gecici_lokasyonlar:
                try:
                    # 1. Şirket (Tür bilgisi burada kaydedilir)
                    s_res = supabase.table("sirketler").insert({
                        "sirket_adi": s_ad, "sirket_mail": s_mail, "sirket_turu": m_turu,
                        "yonetici_adi": y_ad, "yonetici_telefon": y_tel, "yonetici_mail": y_mail
                    }).execute()
                    s_id = s_res.data[0]['id']

                    # 2. Lokasyonlar
                    for l in st.session_state.gecici_lokasyonlar: l['sirket_id'] = s_id
                    supabase.table("lokasyonlar").insert(st.session_state.gecici_lokasyonlar).execute()

                    # 3. İlişkiler
                    for r in st.session_state.gecici_iliskiler:
                        supabase.table("sirket_iliskileri").insert({
                            "kaynak_sirket_id": s_id, "hedef_sirket_id": r['hedef_sirket_id'], "iliski_turu": r['iliski_turu']
                        }).execute()

                    st.success("Şirket ve tüm bağlantıları başarıyla kaydedildi!")
                    st.session_state.gecici_lokasyonlar = []; st.session_state.gecici_iliskiler = []
                    st.rerun()
                except Exception as e: st.error(f"Hata: {e}")
            else: st.warning("Şirket adı ve en az bir lokasyon zorunludur.")

    with t2:
        # --- DÜZENLEME VE YÖNETİM ALANI ---
        res = supabase.table("sirketler").select("*, lokasyonlar(*), sirket_iliskileri!kaynak_sirket_id(*)").execute()
        for item in res.data:
            with st.expander(f"🏢 {item['sirket_adi']} ({item['sirket_turu']})"):
                col_edit, col_del = st.columns([5, 1])
                if col_del.button("Sil", key=f"del_{item['id']}"):
                    supabase.table("sirketler").delete().eq("id", item['id']).execute()
                    st.rerun()
                
                # Düzenleme Formu
                with st.form(f"edit_{item['id']}"):
                    new_name = st.text_input("Şirket Adı", value=item['sirket_adi'])
                    new_mail = st.text_input("Kurumsal Mail", value=item['sirket_mail'])
                    new_turu = st.selectbox("Şirket Türü", ["Grup Şirketi", "Tedarikçi", "Satış Kanalı", "Hizmet Sağlayıcı"], 
                                            index=["Grup Şirketi", "Tedarikçi", "Satış Kanalı", "Hizmet Sağlayıcı"].index(item['sirket_turu']) if item['sirket_turu'] in ["Grup Şirketi", "Tedarikçi", "Satış Kanalı", "Hizmet Sağlayıcı"] else 0)
                    
                    if st.form_submit_button("Güncelle"):
                        supabase.table("sirketler").update({"sirket_adi": new_name, "sirket_mail": new_mail, "sirket_turu": new_turu}).eq("id", item['id']).execute()
                        st.success("Güncellendi!")
                        st.rerun()
