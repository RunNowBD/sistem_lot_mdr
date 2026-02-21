import streamlit as st
import pandas as pd
import random
import qrcode
from io import BytesIO

st.set_page_config(page_title="Sistem Lot", layout="wide")

# Ambil maklumat dari URL
query_params = st.query_params

# --- FUNGSI BACA & SIMPAN DATA ---
def load_data():
    try:
        return pd.read_excel('senarai_peniaga.xlsx')
    except:
        return pd.DataFrame(columns=['Nama', 'No_Telefon', 'No_Lot', 'Status'])

def save_data(dataframe):
    dataframe.to_excel('senarai_peniaga.xlsx', index=False)

df = load_data()

# ==========================================
# PAPARAN PENIAGA (Di Telefon Bimbit Selepas Scan QR)
# ==========================================
if "user_id" in query_params:
    user_index = int(query_params["user_id"])
    jumlah_lot = int(query_params.get("total_lot", 50))
    
    if user_index < len(df):
        peniaga = df.iloc[user_index]
        st.title("📱 Tiket Cabutan Lot")
        st.write(f"Selamat Datang, **{peniaga['Nama']}**!")
        st.write(f"📞 No. Tel: {peniaga['No_Telefon']}")
        st.divider()
        
        if peniaga['Status'] == 'Selesai':
            st.balloons()
            st.success(f"🎉 TAHNIAH! Anda mendapat Lot Nombor: {int(peniaga['No_Lot'])}")
            st.info("Sila 'Screenshot' skrin ini sebagai bukti.")
        else:
            st.warning("Sila tekan butang di bawah untuk membuat cabutan undi anda.")
            # Peniaga tekan butang ini di telefon mereka
            if st.button("🎲 TEKAN UNTUK CABUT UNDI", use_container_width=True):
                semua_lot = list(range(1, jumlah_lot + 1))
                lot_diambil = df['No_Lot'].dropna().tolist()
                baki = [l for l in semua_lot if l not in lot_diambil]
                
                if baki:
                    nombor_berjaya = random.choice(baki)
                    df.at[user_index, 'No_Lot'] = nombor_berjaya
                    df.at[user_index, 'Status'] = "Selesai"
                    save_data(df)
                    st.rerun() # Refresh skrin telefon
                else:
                    st.error("Maaf, semua lot telah habis!")
    else:
        st.error("Data tidak dijumpai.")

# ==========================================
# PAPARAN ADMIN (Di Skrin Laptop)
# ==========================================
else:
    st.title("🖥️ Kaunter Utama Cabutan Lot")
    
    # --- MENU TEPI (SIDEBAR) ---
    st.sidebar.header("⚙️ Tetapan Admin")
    app_url = st.sidebar.text_input("🔗 Link Aplikasi Anda:", value="https://LETAK-LINK-ANDA-DI-SINI.streamlit.app")
    jumlah_lot = st.sidebar.number_input("Jumlah Lot Tersedia:", min_value=1, value=50)
    
    st.sidebar.divider()
    st.sidebar.header("📁 Upload Senarai Excel")
    fail_upload = st.sidebar.file_uploader("Upload fail (.xlsx)", type=['xlsx'])
    if fail_upload is not None:
        if st.sidebar.button("Masukkan Data"):
            df_baru = pd.read_excel(fail_upload)
            if 'Status' not in df_baru.columns: df_baru['Status'] = 'Belum Cabut'
            if 'No_Lot' not in df_baru.columns: df_baru['No_Lot'] = None
            df = pd.concat([df, df_baru], ignore_index=True)
            save_data(df)
            st.sidebar.success("Berjaya dimasukkan!")
            st.rerun()

    # --- BAHAGIAN TENGAH (CARIAN, QR & MANUAL ASSIGN) ---
    kolum_kiri, kolum_kanan = st.columns([2, 1])
    
    with kolum_kiri:
        st.subheader("🔍 Carian Peniaga & QR Code")
        nama_dicari = st.text_input("Taip Nama Peniaga untuk cabutan:")
        
        if nama_dicari:
            hasil = df[df['Nama'].str.contains(nama_dicari, case=False, na=False)]
            
            if not hasil.empty:
                index_peniaga = hasil.index[0]
                peniaga = df.iloc[index_peniaga]
                
                st.write("---")
                c1, c2 = st.columns(2)
                
                with c1:
                    st.write(f"👤 **Nama:** {peniaga['Nama']}")
                    st.write(f"📞 **No Tel:** {peniaga['No_Telefon']}")
                    st.write(f"📌 **Status:** {peniaga['Status']}")
                    
                    if peniaga['Status'] == 'Selesai':
                        st.success(f"Telah selesai. Lot: {int(peniaga['No_Lot'])}")
                    else:
                        st.info("Peniaga sedang membuat cabutan...")
                        
                        # FUNGSI BARU: Masukkan Nombor Manual
                        st.write("---")
                        st.write("Atau masukkan nombor secara manual:")
                        lot_manual = st.number_input("Nombor Lot", min_value=1, max_value=int(jumlah_lot), step=1)
                        if st.button("Simpan Lot Manual"):
                            lot_diambil = df['No_Lot'].dropna().tolist()
                            if lot_manual in lot_diambil:
                                st.error("Maaf, nombor lot ini telah diambil!")
                            else:
                                df.at[index_peniaga, 'No_Lot'] = lot_manual
                                df.at[index_peniaga, 'Status'] = "Selesai"
                                save_data(df)
                                st.success("Disimpan!")
                                st.rerun()

                with c2:
                    if peniaga['Status'] != 'Selesai':
                        # JANA QR CODE UNTUK PENIAGA SCAN (Hantar ID dan Jumlah Lot ke telefon)
                        link_unik = f"{app_url}?user_id={index_peniaga}&total_lot={jumlah_lot}"
                        qr = qrcode.make(link_unik)
                        buf = BytesIO()
                        qr.save(buf)
                        st.image(buf, caption="Peniaga: Scan QR ini untuk cabut undi", width=200)

    # --- TAMBAH MANUAL (JIKA TERTINGGAL NAMA) ---
    with kolum_kanan:
        st.subheader("📝 Tambah Nama Tercicir")
        with st.form("tambah_manual"):
            nama_baru = st.text_input("Nama Peniaga:")
            tel_baru = st.text_input("No Telefon:")
            submit = st.form_submit_button("Simpan Peniaga Baru")
            if submit and nama_baru:
                data_baru = pd.DataFrame({'Nama': [nama_baru], 'No_Telefon': [tel_baru], 'No_Lot': [None], 'Status': ['Belum Cabut']})
                df = pd.concat([df, data_baru], ignore_index=True)
                save_data(df)
                st.success("Berjaya ditambah!")
                st.rerun()

    # --- PAPARAN JADUAL & BUTANG BAWAH ---
    st.divider()
    
    col_tabel, col_refresh = st.columns([4,1])
    with col_tabel:
        st.subheader("📋 Senarai Keputusan")
    with col_refresh:
        # Butang Refresh untuk Admin tengok result lepas peniaga tekan di telefon
        if st.button("🔄 Refresh Jadual"):
            st.rerun()

    st.dataframe(df, use_container_width=True)
    
    col_dl, col_reset = st.columns(2)
    with col_dl:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Keputusan", data=csv, file_name='keputusan_lot.csv', mime='text/csv')
    
    with col_reset:
        if st.button("⚠️ Kosongkan Semua Keputusan"):
            df['No_Lot'] = None
            df['Status'] = 'Belum Cabut'
            save_data(df)
            st.rerun()
