
# Panduan Implementasi Deployment (Production Ready)

Untuk men-deploy aplikasi Marketplace ini ke internet, kita harus memastikan 3 komponen utama berjalan di Cloud:
1. **Aplikasi (Python Code)**: Hosting server.
2. **Database (PostgreSQL)**: Penyimpanan data (User, Produk).
3. **Media Storage (Gambar)**: Penyimpanan foto produk & profil.

## Tahap 1: Persiapan Code (Lokal)
Sebelum upload, pastikan konfigurasi ini siap.

### 1. Update `requirements.txt`
Pastikan library production server (`gunicorn`) dan database adapter (`psycopg2-binary`) sudah ada.

### 2. Konfigurasi `config.py`
Aplikasi Anda sudah mendukung Environment Variables (Bagus!). Pastikan variabel ini tidak dicode keras (hardcoded):
- `SECRET_KEY`: Jangan gunakan 'dev_key_very_secret...'.
- `DATABASE_URL`: Alamat PostgreSQL production.
- `FLASK_APP`: `run.py`

## Tahap 2: Memilih Hosting
Saya merekomendasikan **Render.com** (Gratis & Modern) atau **PythonAnywhere** (Mudah & Klasik).

### Opsi A: Modern Scalable (Rekomendasi)
- **Web Server**: Render.com (Free Tier tersedia).
- **Database**: Neon.tech atau Supabase (Free Tier PostgreSQL terbaik).
- **Gambar**: Cloudinary (Penting! Karena Render menghapus file upload jika server restart).

### Opsi B: Simpel (Tanpa Cloudinary)
- **All-in-One**: PythonAnywhere ($5/bulan).
- **Kelebihan**: Bisa simpan gambar langsung di folder `static/uploads` tanpa hilang.
- **Kekurangan**: Performa database shared kadang lambat.

## Tahap 3: Solusi Penyimpanan Gambar (ISU KRITIKAL)
Saat ini codingan upload gambar Anda tersimpan di folder:
`c:\...\static\uploads\`

Jika Anda deploy ke **Render/Heroku/Railway**, semua file di folder `uploads` akan **HILANG** setiap kali Anda update aplikasi.

**Solusi:**
1. Daftar akun **Cloudinary** (Gratis).
2. Install library: `pip install cloudinary`
3. Ubah kode upload di backend agar mengirim gambar ke Cloudinary, bukan ke folder lokal.

## Checklist Langkah Selanjutnya
[ ] Buat akun GitHub & Push kode ini ke GitHub.
[ ] Buat akun Render.com / PythonAnywhere.
[ ] Putuskan: Mau pakai Cloudinary (agar skalabel) atau tetap Local Storage (harus pakai VPS/PythonAnywhere)?
