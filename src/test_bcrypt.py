import bcrypt

# El hash de tu base de datos
hash_from_db = "$2b$12$XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # <-- Pon tu hash aquí
password_test = "Admin2026*"

try:
    if bcrypt.checkpw(password_test.encode('utf-8'), hash_from_db.encode('utf-8')):
        print("✅ Contraseña CORRECTA")
    else:
        print("❌ Contraseña INCORRECTA")
except Exception as e:
    print(f"❌ Error: {str(e)}")