import streamlit as st
import pandas as pd
import random
import qrcode
from io import BytesIO

# ==========================================
# 🛑 LETAK LINK RASMI APLIKASI ANDA DI BAWAH INI
LINK_RASMI_SISTEM = "https://sistem-lot-mdr.streamlit.app"
# ==========================================

st.set_page_config(
    page_title="Sistem Lot Peniaga",
    page_icon="🎟️", # Anda boleh tukar emoji ini kepada link gambar logo anda
    layout="wide"
)

# TAMBAH GAMBAR HEADER DI SINI
# Gantikan URL di bawah dengan link gambar logo anda
st.image("https://mdranau.sabah.gov.my/wp-content/uploads/2025/07/Majlis_Daerah_Ranau_Logo-1.png", use_container_width=True)

query_params = st.query_params

# --- FUNGSI BACA & SIMPAN DATA ---
def load_data():
    try:
        return pd.read_excel('senarai_peniaga.xlsx')
    except:
        return pd.DataFrame(columns=['Nama', 'No_Telefon', 'No_Lot', 'Status'])

def save_data(dataframe):
    dataframe.to_excel('senarai_peniaga.xlsx', index=False)

def senarai_lot_terambil(df):
    ambil = []
    for val in df['No_Lot'].dropna():
        if isinstance(val, str):
            for v in val.split(','):
                if v.strip().isdigit():
                    ambil.append(int(v.strip()))
        elif isinstance(val, (int, float)):
            ambil.append(int(val))
    return ambil

def format_lot(val):
    return str(val).replace('.0', '')

df = load_data()

# ==========================================
# PAPARAN PENIAGA (Di Telefon Bimbit)
# ==========================================
if "user_id" in query_params:
    user_index = int(query_params["user_id"])
    jumlah_lot = int(query_params.get("total_lot", 50))
    dua_lot = query_params.get("dua_lot", "False") == "True"
    
    if user_index < len(df):
        peniaga = df.iloc[user_index]
        st.title("📱 Tiket Cabutan Lot")
        st.write(f"Selamat Datang, **{peniaga['Nama']}**!")
        st.write(f"📞 No. Tel: {peniaga['No_Telefon']}")
        st.divider()
        
        if peniaga['Status'] == 'Selesai':
            st.balloons()
            st.success(f"🎉 TAHNIAH! Anda mendapat Lot Nombor: {format_lot(peniaga['No_Lot'])}")
            st.info("Sila 'Screenshot' skrin ini sebagai bukti.")
        else:
            if dua_lot:
                st.info("🎟️ **Perhatian:** Anda akan mencabut **2 Lot Bersebelahan**.")
            else:
                st.info("🎟️ **Perhatian:** Anda akan mencabut **1 Lot**.")
                
            st.warning("Sila tekan butang di bawah untuk membuat cabutan undi anda.")
            
            if st.button("🎲 TEKAN UNTUK CABUT UNDI", use_container_width=True):
                semua_lot = list(range(1, jumlah_lot + 1))
                lot_diambil = senarai_lot_terambil(df)
                baki = [l for l in semua_lot if l not in lot_diambil]
                
                if dua_lot:
                    pasangan = [l for l in baki if (l + 1) in baki]
                    if pasangan:
                        pilihan = random.choice(pasangan)
                        nombor_berjaya = f"{pilihan}, {pilihan + 1}"
                        df.at[user_index, 'No_Lot'] = nombor_berjaya
                        df.at[user_index, 'Status'] = "Selesai"
                        save_data(df)
                        st.rerun()
                    else:
                        st.error("Maaf, tiada lagi lot bersebelahan yang kosong!")
                else:
                    if baki:
                        nombor_berjaya = str(random.choice(baki))
                        df.at[user_index, 'No_Lot'] = nombor_berjaya
                        df.at[user_index, 'Status'] = "Selesai"
                        save_data(df)
                        st.rerun()
                    else:
                        st.error("Maaf, semua lot telah habis!")
    else:
        st.error("Data tidak dijumpai.")

# ==========================================
# PAPARAN ADMIN (Di Skrin Laptop)
# ==========================================
else:
    st.title("🖥️ Kaunter Utama Cabutan Lot")
    app_url = LINK_RASMI_SISTEM # Link kini diambil secara automatik!
    
    # --- MENU TEPI (SIDEBAR) ---
    st.sidebar.header("⚙️ Tetapan Admin")
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

    # --- BAHAGIAN TENGAH ---
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
                        st.success(f"Telah selesai. Lot: {format_lot(peniaga['No_Lot'])}")
                    else:
                        st.info("Peniaga sedang bersedia...")
                        dua_lot_admin = st.checkbox("☑️ Peniaga ini menempah 2 Lot Bersebelahan")
                        
                        st.write("---")
                        lot_manual = st.text_input("Manual Lot (Contoh: 14 atau 14, 15):")
                        if st.button("Simpan Lot Manual"):
                            if lot_manual:
                                lot_diambil = senarai_lot_terambil(df)
                                lot_req = []
                                for v in str(lot_manual).split(','):
                                    if v.strip().isdigit():
                                        lot_req.append(int(v.strip()))
                                
                                bertindih = [l for l in lot_req if l in lot_diambil]
                                if bertindih:
                                    st.error(f"Maaf, lot {bertindih} telah diambil orang lain!")
                                else:
                                    df.at[index_peniaga, 'No_Lot'] = str(lot_manual)
                                    df.at[index_peniaga, 'Status'] = "Selesai"
                                    save_data(df)
                                    st.success("Disimpan!")
                                    st.rerun()
                            else:
                                st.error("Sila taip nombor lot dahulu.")

                with c2:
                    if peniaga['Status'] != 'Selesai':
                        # Buang tanda / di hujung link jika ada untuk elak error
                        bersih_url = app_url.rstrip('/') 
                        link_unik = f"{bersih_url}?user_id={index_peniaga}&total_lot={jumlah_lot}&dua_lot={dua_lot_admin}"
                        qr = qrcode.make(link_unik)
                        buf = BytesIO()
                        qr.save(buf)
                        st.image(buf, caption="Peniaga: Scan QR ini", width=200)

    # --- TAMBAH MANUAL ---
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

    # --- PAPARAN JADUAL & BUTANG RESET ---
    st.divider()
    
    col_tabel, col_refresh = st.columns([4,1])
    with col_tabel:
        st.subheader("📋 Senarai Keputusan")
    with col_refresh:
        if st.button("🔄 Refresh Jadual"):
            st.rerun()

    st.dataframe(df, use_container_width=True)
    
    st.write("---")
    st.write("⚙️ **PENGURUSAN DATA SISTEM**")
    col_dl, col_reset, col_delete = st.columns(3)
    
    with col_dl:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Keputusan (CSV)", data=csv, file_name='keputusan_lot.csv', mime='text/csv')
    
    with col_reset:
        if st.button("⚠️ Kosongkan Lot Sahaja"):
            if not df.empty:
                df['No_Lot'] = None
                df['Status'] = 'Belum Cabut'
                save_data(df)
                st.rerun()
                
    with col_delete:
        if st.button("🗑️ Padam SEMUA Data (Reset)"):
            df_kosong = pd.DataFrame(columns=['Nama', 'No_Telefon', 'No_Lot', 'Status'])
            save_data(df_kosong)
            st.rerun()

