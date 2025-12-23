
import psycopg2
import os

# Konfigurasi (Sama seperti sebelumnya)
PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB = "marketplace"
PG_USER = "postgres"
PG_PASSWORD = "1q2w3e" 

def check_path():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("SHOW data_directory;")
        path = cursor.fetchone()[0]
        
        print("\n=== Lokasi Database PostgreSQL ===")
        print(f"Data disimpan di folder ini:\n{path}")
        print("\n[PENTING] Jangan ubah file di dalam folder ini secara manual!")
        print("Gunakan pgAdmin untuk melihat data, atau perintah 'pg_dump' untuk backup.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn: conn.close()

if __name__ == "__main__":
    check_path()
