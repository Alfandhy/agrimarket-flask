
import os
from sqlalchemy import text
from app import app, db

# Force config to use Postgres
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1q2w3e@localhost/marketplace"

def fix():
    with app.app_context():
        print("Altering user table columns to TEXT...")
        try:
            db.session.execute(text('ALTER TABLE "user" ALTER COLUMN password_hash TYPE TEXT'))
            db.session.execute(text('ALTER TABLE "user" ALTER COLUMN profile_image TYPE TEXT'))
            db.session.commit()
            print("Success.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    fix()
