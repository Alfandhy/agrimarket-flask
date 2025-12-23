# Project Plan: Marketplace Sederhana (Flask & PostgreSQL)

Tujuan: Membangun aplikasi marketplace modern, aman, dan skalabel.

## Status Sistem Saat Ini (V5 - Refactored)
Sistem telah mengalami pembaruan besar-besaran dari versi V4 ke V5. Fokus utama adalah skalabilitas, keamanan, dan maintainability.

### Updates Terbaru (Dilakukan pada Sesi Ini)

#### 1. Migrasi Database (SQLite -> PostgreSQL)
- **Status**: Selesai ✅
- **Detail**:
    - Berpindah dari SQLite file-based ke PostgreSQL Server untuk menangani concurrency tinggi.
    - Script migrasi data otomatis (`migrate_db.py`) berhasil memindahkan semua data user, produk, dan transaksi.
    - Perbaikan Schema otomatis (Konversi Boolean Integer -> Native Boolean, Text Length adjustments).
    - Sinkronisasi Sequence ID (`fix_sequences.py`) untuk mencegah error duplicate key.

#### 2. Arsitektur Modular (Refactoring)
- **Status**: Selesai ✅
- **Detail**:
    - **Monolith to Blueprints**: File `app.py` (600+ baris) dipecah menjadi struktur modular:
        - `app/__init__.py`: Application Factory.
        - `app/routes/`: Folder logika (`auth.py`, `admin.py`, `product.py`, `main.py`).
        - `config.py`: Sentralisasi konfigurasi.
        - `run.py`: Entry point baru.
    - Kode lebih bersih, mudah dibaca, dan siap untuk kerja tim.

#### 3. Peningkatan Keamanan (Security Hardening)
- **Status**: Selesai ✅
- **Detail**:
    - **Secure Upload**: Whitelist ekstensi file gambar (hanya .jpg, .png, .webp) untuk mencegah upload malware/shell.
    - **HTTP Headers**: Implementasi Security Headers (`X-Frame-Options`, `X-Content-Type-Options`) anti-clickjacking.
    - **Config Management**: Support Environment Variables untuk Database URL dan Secret Key.

#### 4. Fitur Konten (Blog & Pages)
- **Status**: Dibatalkan (Reverted) ❌
- **Detail**: Sempat diimplementasikan fitur manajemen Blog dan Edit About Us dinamis, namun diminta untuk dihapus kembali agar sistem tetap ramping. Halaman About dan Blog kembali statis.

---

## Tech Stack (Updated)
- **Backend:** Python (Flask) - **Modular Blueprint Architecture**
- **Database:** **PostgreSQL** (Prod) / SQLite (Dev Fallback)
- **ORM:** SQLAlchemy
- **Frontend:** HTML + Bootstrap 5 + Vanilla CSS
- **Auth:** Flask-Login
- **Security:** Flask-WTF (CSRF), Flask-Limiter, Secure Headers

## Roadmap Pengembangan Selanjutnya (Future)

### Priority High
- [ ] **Deployment**: Setup Docker atau Deploy ke VPS/Cloud (Heroku/Render).
- [ ] **Image Storage**: Migrasi penyimpanan gambar dari lokal (`static/uploads`) ke Cloud Storage (AWS S3 / Google Cloud Storage) agar stateless.

### Priority Medium
- [ ] **User Profile**: Halaman profil publik untuk User (bukan hanya Seller).
- [ ] **Rating & Review**: Fitur ulasan produk bintang 1-5.
- [ ] **Search Improvement**: Upgrade pencarian menggunakan PostgreSQL Full Text Search (TsVector).

### Priority Low
- [ ] **Payment Gateway**: Integrasi Midtrans/Xendit (saat ini masih via WhatsApp).
- [ ] **Notification System**: Notifikasi email/WA otomatis saat ada pesanan.

## Struktur Folder Terbaru
```
Marketplace/
├── app/                  <-- Core Logic
│   ├── __init__.py
│   ├── models.py
│   ├── extensions.py
│   └── routes/
│       ├── auth.py
│       ├── main.py
│       ├── admin.py
│       └── product.py
├── config.py             <-- Settings
├── run.py                <-- Entry Point
├── migrations/           <-- Database Migrations
├── static/
│   └── uploads/
├── templates/
└── requirements.txt
```