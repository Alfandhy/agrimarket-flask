
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# --- KONFIGURASI ---
# Sesuaikan data koneksi PostgreSQL Anda di sini setelah install
PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB = "marketplace"      # Pastikan database ini sudah dibuat di pgAdmin/CLI
PG_USER = "postgres"       # Default user biasanya postgres
PG_PASSWORD = "1q2w3e"   # Ganti dengan password yang Anda buat saat install

SQLITE_DB_PATH = os.path.join("instance", "marketplace_v5.db")

def migrate():
    print("=== Mulai Migrasi Data dari SQLite ke PostgreSQL ===")
    
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"Error: File SQLite {SQLITE_DB_PATH} tidak ditemukan.")
        return

    # 1. Koneksi ke SQLite (Sumber)
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        print("[OK] Terhubung ke SQLite.")
    except Exception as e:
        print(f"[Gagal] Koneksi SQLite: {e}")
        return

    # 2. Koneksi ke PostgreSQL (Tujuan)
    try:
        pg_conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        pg_cursor = pg_conn.cursor()
        print("[OK] Terhubung ke PostgreSQL.")
    except Exception as e:
        print(f"[Gagal] Koneksi PostgreSQL: {e}")
        print("Pastikan PostgreSQL sudah berjalan, database sudah dibuat, dan credentials benar.")
        return

    # Daftar tabel yang harus dimigrasi
    # Urutan penting karena Foreign Key! (User/Category -> Product -> Images)
    tables = [
        'user', 
        'category', 
        'banner', 
        'product', 
        'product_image' 
    ]
    
    try:
        for table in tables:
            print(f"\nMemproses tabel: {table}...")
            
            # Ambil data dari SQLite
            try:
                sqlite_cursor.execute(f"SELECT * FROM {table}")
                rows = sqlite_cursor.fetchall()
            except sqlite3.OperationalError:
                print(f"  - Tabel {table} tidak ditemukan di SQLite, skip.")
                continue

            if not rows:
                print("  - Data kosong.")
                continue
                
            print(f"  - Menemukan {len(rows)} baris data.")
            
            # Dapatkan nama kolom
            columns = rows[0].keys()
            col_names = ",".join([f'"{c}"' for c in columns]) # Quote columns
            placeholders = ",".join(["%s"] * len(columns))
            
            # Buat query INSERT untuk Postgres
            # Gunakan ON CONFLICT DO NOTHING agar tidak error jika dijalankan berulang
            insert_query = f"""
                INSERT INTO "{table}" ({col_names}) 
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING;
            """
            
            bool_cols = ['is_verified', 'is_active']
            
            for row in rows:
                # Konversi row sqlite ke tuple values dengan penyesuaian tipe data
                processed_values = []
                for col in columns:
                    val = row[col]
                    if col in bool_cols and val is not None:
                        val = bool(val) # Convert 0/1 to False/True
                    processed_values.append(val)
                    
                values = tuple(processed_values)
                
                # Di Postgres, boolean harus true/false, tapi psycopg2 biasanya handle int 1/0
                # Kita coba insert langsung
                pg_cursor.execute(insert_query, values)
                
            print(f"  - Sukses memindahkan data {table}.")
            
        pg_conn.commit()
        print("\n=== Migrasi Selesai! ===")
        print("Semua data berhasil dipindahkan ke PostgreSQL.")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"\n[ERROR] Terjadi kesalahan saat migrasi: {e}")
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate()
