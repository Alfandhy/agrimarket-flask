---
description: Panduan Deployment ke Render.com
---

# Cara Upload Website ke Render.com (Gratis)

Render.com adalah platform cloud modern yang sangat mudah digunakan. Ikuti langkah-langkah ini untuk mengonlinekan website Anda.

## Persiapan 1: Masukkan Kode ke GitHub
Render mengambil kode website Anda langsung dari GitHub. Jadi langkah pertama adalah mengamankan kode Anda di sana.

1.  **Buat Akun GitHub** (jika belum punya) di [github.com](https://github.com).
2.  **Buat Repository Baru**:
    *   Klik tombol **+** di pojok kanan atas -> **New repository**.
    *   Nama Repository: `agrimarket-flask` (atau nama lain yang Anda suka).
    *   Pilih **Public** (atau Private, bebas).
    *   **PENTING**: Jangan centang "Add README" atau "Add .gitignore" dulu agar repo tetap kosong. Klik **Create repository**.

3.  **Upload Kode dari Komputer Anda** (Buka Terminal di VS Code):
    Ketik perintah berikut satu per satu (tekan Enter setelah setiap baris):
    ```bash
    git init
    git add .
    git commit -m "Siap deploy ke Render"
    git branch -M main
    # Ganti URL di bawah dengan URL repository Anda sendiri (dari langkah 2)
    git remote add origin https://github.com/USERNAME_ANDA/NAMA_REPO.git
    git push -u origin main
    ```
    *(Jika diminta login, ikuti instruksi yang muncul di layar)*.

---

## Persiapan 2: Setup Database PostgreSQL (Gratis di Render)
Kita butuh database online yang kuat.

1.  Login ke [dashboard.render.com](https://dashboard.render.com).
2.  Klik tombol **New +** -> pilih **PostgreSQL**.
3.  Isi data:
    *   **Name**: `agrimarket-db`
    *   **Region**: Singapore (paling dekat dengan Indonesia).
    *   **PostgreSQL Version**: Pilih yang terbaru (default).
    *   **Instance Type**: Free (Gratis).
4.  Klik **Create Database**.
5.  Tunggu sampai statusnya "Available".
6.  Scroll ke bawah, cari bagian **Connections**.
7.  Copy **Internal Database URL** (kita akan butuh ini nanti).

---

## Langkah 3: Deploy Website (Web Service)

1.  Kembali ke Dashboard, klik **New +** -> pilih **Web Service**.
2.  Pilih **Build and deploy from a Git repository**.
3.  Cari repository Anda yang tadi dibuat, klik **Connect**.
4.  Isi konfigurasi:
    *   **Name**: `agrimarket-app`
    *   **Region**: Singapore (samakan dengan database).
    *   **Branch**: `main`
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn app:app` (Render biasanya otomatis mengisi ini, tapi pastikan isinya benar).
5.  **PENTING: Environment Variables**
    Scroll ke bawah ke bagian "Environment Variables", klik **Add Environment Variable**. Tambahkan kunci dan nilai berikut:

    | Key | Value |
    | :--- | :--- |
    | `PYTHON_VERSION` | `3.10.0` (atau `3.9.0`) |
    | `SECRET_KEY` | Isi dengan text acak yang panjang & rahasia (contoh: `kjsd7823hkjsdf8723`) |
    | `DATABASE_URL` | Paste **Internal Database URL** yang Anda copy dari langkah Database tadi. |
    | `Multi_Line_Input` | (Kosongkan/Tidak perlu) |

6.  Pastikan pilih **Free Plan**.
7.  Klik **Create Web Service**.

---

## Selesai!

Render akan mulai memproses ("Building"). Tunggu sekitar 2-5 menit.
Jika berhasil, Anda akan melihat status **Live** berwarna hijau dan link website Anda (contoh: `https://agrimarket-app.onrender.com`) di bagian atas.

Klik link tersebut, dan website Anda sudah online! 🎉
