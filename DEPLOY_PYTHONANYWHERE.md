---
description: Panduan Deployment ke PythonAnywhere
---

# Cara Upload Website ke PythonAnywhere (Mudah & Gratis)

PythonAnywhere adalah pilihan terbaik untuk pemula Flask karena gratis, tidak butuh kartu kredit, dan **bisa langsung menggunakan database SQLite** (tidak perlu setup Neon/Postgres).

## Langkah 1: Daftar Akun
1.  Buka [www.pythonanywhere.com](https://www.pythonanywhere.com/).
2.  Klik **Pricing & Signup**.
3.  Klik tombol **Create a Beginner account** (Gratis).
4.  Isi Username, Email, Password, dan klik Register.
    *   *Ingat Username Anda, ini akan menjadi alamat website Anda (contoh: alfandhy.pythonanywhere.com)*.

---

## Langkah 2: Ambil Kode dari GitHub
Kita akan menggunakan terminal di PythonAnywhere untuk mengambil kode yang sudah Anda upload ke GitHub.

1.  Setelah login, klik tab **Consoles** di menu atas.
2.  Klik **Bash** (di bawah "Start a new console").
3.  Layar hitam terminal akan muncul. Ketik perintah berikut satu per satu (tekan Enter setelah setiap baris):

    ```bash
    # 1. Clone repository Anda
    git clone https://github.com/Alfandhy/agrimarket-flask.git mysite

    # 2. Masuk ke folder
    cd mysite

    # 3. Buat Virtual Environment (wadah isolasi)
    python3 -m venv venv

    # 4. Aktifkan Virtual Environment
    source venv/bin/activate

    # 5. Install library yang dibutuhkan
    pip install -r requirements.txt
    ```
    *(Tunggu proses install selesai sampai muncul tanda `$` lagi)*.

---

## Langkah 3: Setting Web App
1.  Klik tab **Web** di menu atas (ikon bola dunia 🌐).
2.  Klik tombol biru **Add a new web app**.
3.  Klik **Next**.
4.  Pilih **Manual configuration** (PENTING: Jangan pilih Flask).
5.  Pilih **Python 3.10** (atau versi Python terbaru yang tersedia).
6.  Klik **Next** hingga selesai.

---

## Langkah 4: Konfigurasi Virtual Environment & Code
Sekarang Anda berada di halaman konfigurasi Web. Scroll ke bawah.

1.  **Bagian Virtualenv:**
    *   Cari tulisan "Enter path to a virtualenv, if desired".
    *   Klik tulisan merah dan ketik: `/home/USERNAME_ANDA/mysite/venv`
    *   *(Ganti `USERNAME_ANDA` dengan username PythonAnywhere Anda)*.
    *   Pastikan muncul tanda centang ✅ setelah di-enter.

2.  **Bagian Code:**
    *   **Source code:** Isi dengan `/home/USERNAME_ANDA/mysite`
    *   **Working directory:** Isi dengan `/home/USERNAME_ANDA/mysite`

3.  **Bagian WSGI Configuration File:**
    *   Klik link file WSGI configuration (biasanya bernama: `/var/www/username_pythonanywhere_com_wsgi.py`).
    *   Hapus **SEMUA** isinya.
    *   Ganti dengan kode berikut:

    ```python
    import sys
    import os

    # Tambahkan folder project ke system path
    path = '/home/USERNAME_ANDA/mysite'
    if path not in sys.path:
        sys.path.append(path)

    # Set environment variables (Kunci Rahasia)
    os.environ['SECRET_KEY'] = 'ganti-dengan-kunci-rahasia-acak-panjang'
    # Kita tidak perlu DATABASE_URL karena pakai SQLite bawaan

    # Import aplikasi Flask
    from app import app as application
    ```
    *   **PENTING:** Jangan lupa ganti `USERNAME_ANDA` dengan username asli Anda di baris `path = ...`.
    *   Klik **Save** (Pojok kanan atas editor).

---

## Langkah 5: Selesai!
1.  Kembali ke tab **Web**.
2.  Klik tombol hijau besar **Reload <username>.pythonanywhere.com**.
3.  Klik link website Anda di bagian atas (contoh: `https://alfandhy.pythonanywhere.com`).

Website Anda sudah online! 🎉

### Catatan Tambahan:
*   Karena pakai SQLite, data produk/user yang Anda input di Localhost **tidak ikut terbawa**. Website dimulai dari kosong (fresh).
*   Anda harus membuat akun Admin baru lagi lewat halaman Register atau Login.
