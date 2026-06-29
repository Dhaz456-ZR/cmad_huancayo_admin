import bcrypt
from src.database import SessionLocal
from src.models import Administrador

def crear_admin_nuevo():
    db = SessionLocal()
    
    # Datos del nuevo administrador
    nombre = "Administrador Principal"
    usuario = "admin"
    password_plano = "Admin2026*"
    cargo = "Administrador"
    estado = "Activo"
    
    # Verificar si ya existe
    admin_existente = db.query(Administrador).filter(
        Administrador.usuario == usuario
    ).first()
    
    if admin_existente:
        print(f"⚠️ Eliminando administrador existente: {admin_existente.usuario}")
        db.delete(admin_existente)
        db.commit()
        print("✅ Administrador eliminado")
    
    # Generar hash con bcrypt
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(
        password_plano.encode("utf-8"),
        salt
    )
    
    # Crear el nuevo administrador
    admin = Administrador(
        nombre=nombre,
        usuario=usuario,
        password=password_hash.decode("utf-8"),
        cargo=cargo,
        estado=estado
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print("=" * 60)
    print("✅ NUEVO ADMINISTRADOR CREADO CON BCRYPT")
    print("=" * 60)
    print(f"   ID:          {admin.id}")
    print(f"   Usuario:     {admin.usuario}")
    print(f"   Nombre:      {admin.nombre}")
    print(f"   Contraseña:  {password_plano}")
    print(f"   Hash:        {admin.password[:50]}...")
    print("=" * 60)
    print("🔑 ¡Ya puedes iniciar sesión!")
    
    db.close()

if __name__ == "__main__":
    crear_admin_nuevo()