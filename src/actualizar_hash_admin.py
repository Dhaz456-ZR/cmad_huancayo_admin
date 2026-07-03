import bcrypt
from src.database import SessionLocal
from src.models import Administrador

def actualizar_hash():
    db = SessionLocal()
    
    admin = db.query(Administrador).filter(
        Administrador.email == "admin@cmac.huancayo"
    ).first()
    
    if not admin:
        print("⚠️ Administrador no encontrado")
        db.close()
        return
    
    # Generar nuevo hash para la contraseña "admin123"
    password = "admin123"
    new_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    new_hash_str = new_hash.decode("utf-8")
    
    admin.password = new_hash_str
    db.commit()
    
    print("✅ Hash actualizado correctamente!")
    print(f"   Email: {admin.email}")
    print(f"   Contraseña: {password}")
    print(f"   Nuevo Hash: {new_hash_str}")
    
    db.close()

if __name__ == "__main__":
    actualizar_hash()