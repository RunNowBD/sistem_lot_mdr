import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Sistem Lot", layout="wide")

st.title("🎟️ Sistem Cabutan Lot Peniaga")

# --- BACA FAIL EXCEL UTAMA ---
df = pd.read_excel('senarai_peniaga.xlsx')

# --- MENU TEPI (SIDEBAR): FUNGSI UPLOAD ---
st.sidebar.header("📁 Upload Senarai Nama (Excel)")
st.sidebar.write("Ada banyak nama? Upload fail Excel anda di sini.")

# Butang untuk upload fail
fail_upload = st.sidebar.file_uploader("Pilih fail .xlsx", type=['xlsx'])

if fail_upload is not None:
    if st.sidebar.button("Masukkan Data ke Sistem"):
        # Baca fail yang di-upload
        df_baru = pd.read_excel(fail_upload)
        
        # Sistem tolong tambahkan kolum secara automatik jika tak ada
        if 'Status' not in df_baru.columns:
            df_baru['Status'] = 'Belum Cabut'
        if 'No_Lot' not in df_baru.columns:
            df_baru['No_Lot'] = None
            
        # Gabungkan senarai baru dengan senarai yang sedia ada
        df = pd.concat([df, df_baru], ignore_index=True)
        df.to_excel('senarai_peniaga.xlsx', index=False)
        
        st.sidebar.success("Berjaya! Nama baru telah dimasukkan.")
        st.rerun() # Refresh skrin secara automatik

st.sidebar.divider()

# --- BAHAGIAN UTAMA SISTEM ---
kolum_kiri, kolum_kanan = st.columns([2, 1])

with kolum_kiri:
    st.subheader("🎲 Kaunter Cabutan")
    jumlah_lot = st.sidebar.number_input("Berapa jumlah lot yang ada?", min_value=1, value=50)
    nama_dicari = st.text_input("🔍 Taip Nama Peniaga untuk Cabutan:")

    if nama_dicari:
        hasil_carian = df[df['Nama'].str.contains(nama_dicari, case=False, na=False)]
        
        if not hasil_carian.empty:
            index_peniaga = hasil_carian.index[0]
            nama_peniaga = df.at[index_peniaga, 'Nama']
            status_sekarang = df.at[index_peniaga, 'Status']
            
            st.info(f"**Peniaga Dijumpai:** {nama_peniaga} ({df.at[index_peniaga, 'No_Telefon']})")
            
            if status_sekarang == "Selesai":
                st.success(f"Selesai! Lot Nombor: {df.at[index_peniaga, 'No_Lot']}")
            else:
                if st.button("🎲 Cabut Nombor Lot Sekarang!"):
                    semua_lot = list(range(1, int(jumlah_lot) + 1))
                    lot_diambil = df['No_Lot'].dropna().tolist()
                    lot_kosong = [lot for lot in semua_lot if lot not in lot_diambil]
                    
                    if len(lot_kosong) > 0:
                        nombor_berjaya = random.choice(lot_kosong)
                        df.at[index_peniaga, 'No_Lot'] = nombor_berjaya
                        df.at[index_peniaga, 'Status'] = "Selesai"
                        df.to_excel('senarai_peniaga.xlsx', index=False)
                        st.balloons()
                        st.success(f"Tahniah! Dapat Nombor Lot: {nombor_berjaya}")
                        st.rerun()
                    else:
                        st.error("Semua nombor lot telah habis!")
        else:
            st.warning("Nama tidak dijumpai.")

with kolum_kanan:
    st.subheader("📝 Tambah Manual")
    with st.form("borang_tambah"):
        nama_baru = st.text_input("Nama Peniaga:")
        tel_baru = st.text_input("No Telefon:")
        submit = st.form_submit_button("Simpan")
        
        if submit and nama_baru != "":
            data_baru = pd.DataFrame({'Nama': [nama_baru], 'No_Telefon': [tel_baru], 'No_Lot': [None], 'Status': ['Belum Cabut']})
            df = pd.concat([df, data_baru], ignore_index=True)
            df.to_excel('senarai_peniaga.xlsx', index=False)
            st.success("Berjaya ditambah!")
            st.rerun()

# --- PAPARAN JADUAL & DOWNLOAD ---
st.divider()
st.subheader("📋 Senarai Terkini Peniaga")
st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Download Keputusan", data=csv, file_name='keputusan_lot.csv', mime='text/csv')