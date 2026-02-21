import streamlit as st
import pandas as pd
import random
import qrcode
from io import BytesIO

st.set_page_config(page_title="Sistem Lot", layout="centered")

# Ambil parameter URL untuk tahu siapa yang buka (Admin atau Peniaga)
query_params = st.query_params

# Fungsi baca fail
def load_data():
    try:
        return pd.read_excel('senarai_peniaga.xlsx')
    except:
        return pd.DataFrame(columns=['Nama', 'No_Telefon', 'No_Lot', 'Status'])

df = load_data()

# ==========================================
# PAPARAN PENIAGA (Di Telefon Bimbit Selepas Scan)
# ==========================================
if "user_id" in query_params:
    user_index = int(query_params["user_id"])
    
    if user_index < len(df):
        peniaga = df.iloc[user_index]
        st.title("📱 Tiket Cabutan Lot Anda")
        st.write(f"Selamat Datang, **{peniaga['Nama']}**!")
        st.write(f"📞 No. Tel: {peniaga['No_Telefon']}")
        st.divider()
        
        if peniaga['Status'] == 'Selesai':
            st.balloons()
            st.success(f"🎉 TAHNIAH! Anda mendapat Lot Nombor: {peniaga['No_Lot']}")
            st.info("Sila 'Screenshot' skrin ini dan tunjukkan kepada urusetia.")
        else:
            st.warning("Sedia... Sila minta Admin tekan butang cabut di kaunter, kemudian 'Refresh' skrin ini!")
    else:
        st.error("Data tidak dijumpai.")

# ==========================================
# PAPARAN ADMIN (Di Laptop Kaunter)
# ==========================================
else:
    st.title("🖥️ Kaunter Utama Cabutan Lot")
    
    # Letakkan Link Streamlit Rasmi Anda Di Sini
    app_url = st.sidebar.text_input(
        "🔗 Masukkan Link Aplikasi Anda:", 
        value="https://LETAK-LINK-ANDA-DI-SINI.streamlit.app",
        help="Copy link di bahagian atas browser anda dan paste di sini"
    )
    jumlah_lot = st.sidebar.number_input("Berapa jumlah lot?", min_value=1, value=50)
    nama_dicari = st.text_input("🔍 Cari Nama Peniaga (Contoh: Ahmad):")
    
    if nama_dicari:
        hasil = df[df['Nama'].str.contains(nama_dicari, case=False, na=False)]
        
        if not hasil.empty:
            index_peniaga = hasil.index[0]
            peniaga = df.iloc[index_peniaga]
            
            st.write("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"👤 {peniaga['Nama']}")
                st.write(f"Status: **{peniaga['Status']}**")
                
                if peniaga['Status'] != 'Selesai':
                    # Butang Cabut (Admin Tekan)
                    if st.button("🎲 Cabut Nombor Sekarang"):
                        semua_lot = list(range(1, int(jumlah_lot) + 1))
                        lot_diambil = df['No_Lot'].dropna().tolist()
                        baki = [l for l in semua_lot if l not in lot_diambil]
                        
                        if baki:
                            nombor_berjaya = random.choice(baki)
                            df.at[index_peniaga, 'No_Lot'] = nombor_berjaya
                            df.at[index_peniaga, 'Status'] = "Selesai"
                            df.to_excel('senarai_peniaga.xlsx', index=False)
                            st.success(f"Berjaya! Dapat Lot: {nombor_berjaya}")
                            st.rerun()
                        else:
                            st.error("Semua lot habis!")
                else:
                    st.success(f"Telah selesai. Lot: {peniaga['No_Lot']}")
                    
            with col2:
                # JANA QR CODE UNTUK PENIAGA SCAN
                link_unik = f"{app_url}?user_id={index_peniaga}"
                qr = qrcode.make(link_unik)
                buf = BytesIO()
                qr.save(buf)
                st.image(buf, caption="Minta peniaga Scan QR ini", width=200)

    st.divider()
    st.dataframe(df)
