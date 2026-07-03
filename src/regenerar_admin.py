import bcrypt
from src.database import SessionLocal
from src.models import Administrador
from datetime import datetime

def regenerar_admin():
    db = SessionLocal()
    
    # Eliminar administrador existente
    existing = db.query(Administrador).filter(
        Administrador.email == "admin@cmac.huancayo"
    ).first()
    
    if existing:
        print(f"⚠️ Eliminando administrador existente: {existing.email}")
        db.delete(existing)
        db.commit()
    
    # Crear nuevo administrador
    password = "admin123"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    
    admin = Administrador(
        nombre="Administrador",
        email="admin@cmac.huancayo",
        password=hashed.decode("utf-8"),
        rol="SuperAdmin",
        estado="Activo",
        fecha_creacion=datetime.now()
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print("=" * 50)
    print("✅ ADMINISTRADOR CREADO CORRECTAMENTE!")
    print("=" * 50)
    print(f"   ID: {admin.id}")
    print(f"   Email: {admin.email}")
    print(f"   Contraseña: {password}")
    print(f"   Rol: {admin.rol}")
    print(f"   Estado: {admin.estado}")
    print("=" * 50)
    
    db.close()

if __name__ == "__main__":
    regenerar_admin()