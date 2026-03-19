---
description: Panduan Deployment ke Render.com (Tanpa Kartu Kredit)
---

# Cara Upload Website ke Render.com (Tanpa Kartu Kredit)

Karena Render meminta kartu kredit untuk membuat database PostgreSQL, kita akan menggunakan **trik kombinasi**:
1.  **Aplikasi** dihosting di **Render** (Gratis).
2.  **Database** dihosting di **Neon.tech** atau **Supabase** (Gratis & Tanpa Kartu Kredit).

---

## Langkah 1: Persiapan GitHub (Sudah Anda Lakukan ✅)
Kode Anda sudah ada di GitHub, jadi kita bisa lanjut ke langkah berikutnya.

---

## Langkah 2: Buat Database Gratis di Neon.tech
Neon adalah penyedia database PostgreSQL gratis yang sangat populer dan tidak meminta kartu kredit.

1.  Buka [neon.tech](https://neon.tech) dan klik **Sign Up**.
2.  Login menggunakan akun **Google** atau **GitHub** Anda.
3.  Buat Project baru:
    *   **Project Name**: `agrimarket-db`
    *   **Postgres Version**: Pilih yang terbaru (misal: 16).
    *   **Region**: Singapore (aws-ap-southeast-1) - *Agar website cepat*.
    *   Klik **Create Project**.
4.  Setelah selesai, Anda akan melihat **Connection String** (URL).
5.  Pastikan pilih format **Postgres** (bukan *Poooled* untuk awal, atau *Direct* juga boleh).
6.  Klik tombol "Copy" untuk menyalin URL tersebut.
    *   Bentuknya seperti: `postgresql://neondb_owner:npg_ad8...2@ep-cool-....neon.tech/neondb?sslmode=require`
    *   **Simpan URL ini**, kita butuh di langkah selanjutnya.

---

## Langkah 3: Deploy Aplikasi di Render

1.  Login ke [dashboard.render.com](https://dashboard.render.com).
2.  Klik tombol **New +** -> pilih **Web Service**.
3.  Pilih **Build and deploy from a Git repository**.
4.  Cari repository `agrimarket-flask` Anda, klik **Connect**.
5.  Isi konfigurasi dasar:
    *   **Name**: `agrimarket-app`
    *   **Region**: Singapore (Sesuaikan dengan lokasi database Neon tadi agar cepat).
    *   **Branch**: `main`
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn app:app`
    *   **Plan**: Free
6.  **PENTING: Environment Variables**
    Scroll ke bawah, klik **Add Environment Variable** dan isi dua data ini:

    | Key | Value |
    | :--- | :--- |
    | `DATABASE_URL` | **Paste URL dari Neon.tech tadi di sini** |
    | `SECRET_KEY` | Isi dengan sembarang teks acak panjang (contoh: `kjsd7823hkjsdf8723`) |
    | `PYTHON_VERSION` | `3.10.0` |

7.  Klik **Create Web Service**.

---

## Selesai!

Render akan mulai memproses. Tunggu 2-5 menit.
Jika berhasil, status akan menjadi **Live** (Hijau). Coba buka link website Anda.

### Catatan:
Data pengguna dan produk Anda sekarang tersimpan aman di Neon.tech clouds, bukan di file komputer Anda lagi.
