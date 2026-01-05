import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- Konfigurasi Database (SQLite) ---
def init_db():
    conn = sqlite3.connect('data_siswa.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS nilai (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            skor_pretest INTEGER,
            skor_posttest INTEGER,
            waktu_selesai TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def simpan_pretest(nama, skor):
    conn = sqlite3.connect('data_siswa.db')
    c = conn.cursor()
    c.execute('INSERT INTO nilai (nama, skor_pretest, waktu_selesai) VALUES (?, ?, ?)', 
              (nama, skor, datetime.now()))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return user_id

def update_posttest(user_id, skor):
    conn = sqlite3.connect('data_siswa.db')
    c = conn.cursor()
    c.execute('UPDATE nilai SET skor_posttest = ? WHERE id = ?', (skor, user_id))
    conn.commit()
    conn.close()

# --- Data Soal (10 Soal) ---
kunci_jawaban = {
    "q1": "A", "q2": "B", "q3": "C", "q4": "A", "q5": "D",
    "q6": "B", "q7": "C", "q8": "A", "q9": "D", "q10": "B"
}

def tampilkan_soal(prefix):
    st.write("Jawablah pertanyaan berikut:")
    jawaban_user = {}
    jawaban_user["q1"] = st.radio("1. Soal nomor satu adalah...?", ["A. Opsi 1", "B. Opsi 2", "C. Opsi 3", "D. Opsi 4"], key=f"{prefix}_1")
    jawaban_user["q2"] = st.radio("2. Soal nomor dua adalah...?", ["A. Opsi 1", "B. Opsi 2", "C. Opsi 3", "D. Opsi 4"], key=f"{prefix}_2")
    # ... Tambahkan hingga 10 soal sesuai kebutuhan ...
    # Untuk contoh ini saya singkat, Anda bisa copy paste format di atas sampai q10
    
    # Dummy soal 3-10 agar kode jalan (Silakan diganti dengan soal asli)
    for i in range(3, 11):
        jawaban_user[f"q{i}"] = st.radio(f"{i}. Soal nomor {i}...", ["A", "B", "C", "D"], key=f"{prefix}_{i}")
        
    return jawaban_user

def hitung_skor(jawaban_user):
    skor = 0
    total_soal = 10
    # Logika sederhana: Ambil karakter pertama dari jawaban (misal "A. Opsi 1" diambil "A")
    for key, val in jawaban_user.items():
        if val and val[0] == kunci_jawaban[key]:
            skor += 1
    return skor * 10  # Skala 100

# --- Logika Utama Aplikasi ---
def main():
    st.title("Aplikasi Pembelajaran Interaktif")
    init_db()

    # Inisialisasi Session State untuk navigasi halaman
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'score_pre' not in st.session_state:
        st.session_state['score_pre'] = 0

    # Halaman 1: Login
    if st.session_state['page'] == 'login':
        st.subheader("Selamat Datang")
        nama = st.text_input("Masukkan Nama Lengkap:")
        if st.button("Mulai Pre-Test"):
            if nama:
                st.session_state['nama_user'] = nama
                st.session_state['page'] = 'pretest'
                st.rerun()
            else:
                st.warning("Nama wajib diisi!")

    # Halaman 2: Pre-Test
    elif st.session_state['page'] == 'pretest':
        st.subheader(f"Halo {st.session_state['nama_user']}, Silakan kerjakan Pre-Test")
        jawaban = tampilkan_soal("pre")
        
        if st.button("Kirim Jawaban Pre-Test"):
            skor = hitung_skor(jawaban)
            st.session_state['score_pre'] = skor
            # Simpan ke database
            uid = simpan_pretest(st.session_state['nama_user'], skor)
            st.session_state['user_id'] = uid
            st.session_state['page'] = 'hasil_pretest'
            st.rerun()

    # Halaman 3: Hasil Pre-Test & Materi
    elif st.session_state['page'] == 'hasil_pretest':
        st.subheader("Hasil Pre-Test")
        st.write(f"Skor Anda: {st.session_state['score_pre']} / 100")
        
        st.markdown("---")
        st.subheader("Materi Pembelajaran")
        st.write("Silakan pelajari materi berikut dengan seksama.")
        
        # Masukkan materi di sini (Teks, Gambar, atau Video)
        st.info("Di sini adalah tempat Anda menaruh teks materi pembelajaran panjang lebar. Bisa berupa penjelasan konsep, rumus, dan teori.")
        # Contoh video (opsional): st.video("link_youtube")

        if st.button("Lanjut ke Post-Test"):
            st.session_state['page'] = 'posttest'
            st.rerun()

    # Halaman 4: Post-Test
    elif st.session_state['page'] == 'posttest':
        st.subheader("Post-Test")
        st.write("Kerjakan soal yang sama setelah memahami materi.")
        jawaban = tampilkan_soal("post")
        
        if st.button("Kirim Jawaban Post-Test"):
            skor_akhir = hitung_skor(jawaban)
            st.session_state['score_post'] = skor_akhir
            # Update database
            update_posttest(st.session_state['user_id'], skor_akhir)
            st.session_state['page'] = 'final'
            st.rerun()

    # Halaman 5: Hasil Akhir
    elif st.session_state['page'] == 'final':
        st.subheader("Hasil Akhir Pembelajaran")
        st.write(f"Nama: {st.session_state['nama_user']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Skor Pre-Test", st.session_state['score_pre'])
        with col2:
            st.metric("Skor Post-Test", st.session_state['score_post'])
            
        improvement = st.session_state['score_post'] - st.session_state['score_pre']
        if improvement > 0:
            st.success(f"Hebat! Nilai kamu meningkat sebesar {improvement} poin.")
        elif improvement == 0:
            st.warning("Nilai kamu tetap. Belajar lagi ya!")
        else:
            st.error("Nilai kamu menurun. Coba baca materi dengan lebih teliti.")

    # Opsional: Admin View (Hanya muncul jika nama 'Admin')
    if st.session_state.get('nama_user') == 'Admin':
        st.markdown("---")
        st.subheader("Data Siswa (Admin Only)")
        conn = sqlite3.connect('data_siswa.db')
        df = pd.read_sql_query("SELECT * FROM nilai", conn)
        st.dataframe(df)
        conn.close()

if __name__ == '__main__':
    main()
