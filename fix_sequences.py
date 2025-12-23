
import psycopg2
import os

# Konfigurasi
PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB = "marketplace"
PG_USER = "postgres"
PG_PASSWORD = "1q2w3e" 

def fix_sequences():
    print("=== Memperbaiki Sequences PostgreSQL ===")
    
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )
    cursor = conn.cursor()
    
    tables = ['user', 'category', 'product', 'product_image', 'banner']
    
    try:
        for table in tables:
            # Query sakti untuk reset sequence ke ID terakhir + 1
            query = f"""
            SELECT setval(pg_get_serial_sequence('"{table}"', 'id'), COALESCE(MAX(id), 0) + 1, false) 
            FROM "{table}";
            """
            try:
                cursor.execute(query)
                print(f"[OK] Sequence tabel '{table}' berhasil di-reset.")
            except Exception as e:
                # Kadang tabel kosong atau sequence beda nama, kita catch warn saja
                print(f"[Warn] Gagal reset sequence '{table}': {e}")
                conn.rollback() 
                continue

        conn.commit()
        print("\n=== Selesai! Sequence ID sudah sinkron. ===")
        print("Silakan coba tambah produk lagi sekarang.")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_sequences()
