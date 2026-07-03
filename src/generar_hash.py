# generar_hash.py
import bcrypt

password = "admin123"
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
hash_str = hashed.decode("utf-8")

print("=" * 60)
print("HASH GENERADO PARA LA CONTRASEÑA: admin123")
print("=" * 60)
print(hash_str)
print("=" * 60)
print("\nCopia este hash y pégualo en MySQL:")