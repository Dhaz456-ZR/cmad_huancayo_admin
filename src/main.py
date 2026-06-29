from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from sqlalchemy.orm import joinedload
from src.database import SessionLocal
from src.models import Credito, Usuario, Cuenta, Transferencia, Pago, Movimiento, Administrador
from starlette.middleware.sessions import SessionMiddleware
import bcrypt
import base64

app = FastAPI(
    title="CMAD HUANCAYO ADMIN"
)

# Middleware de sesiones
app.add_middleware(
    SessionMiddleware,
    secret_key="mi_clave_secreta_muy_segura_para_sesiones_2026",
    max_age=3600,
    https_only=False,
    same_site="lax"
)

# Archivos estáticos
app.mount("/css", StaticFiles(directory="src/css"), name="css")
app.mount("/js", StaticFiles(directory="src/js"), name="js")
app.mount("/img", StaticFiles(directory="src/img"), name="img")

templates = Jinja2Templates(directory="src/html")

# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if request.session.get("admin_id"):
        return RedirectResponse("/admin", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="login_admin.html",
        context={"request": request}
    )


@app.get("/login-admin", response_class=HTMLResponse)
def login_admin(request: Request):
    if request.session.get("admin_id"):
        return RedirectResponse("/admin", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="login_admin.html",
        context={"request": request}
    )


@app.post("/login-admin")
def login_admin_post(
    request: Request,
    usuario: str = Form(...),
    password: str = Form(...)
):
    db = SessionLocal()

    admin = db.query(Administrador).filter(
        Administrador.usuario == usuario
    ).first()

    if not admin:
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="login_admin.html",
            context={
                "request": request,
                "error": "Usuario incorrecto"
            }
        )

    if admin.estado != "Activo":
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="login_admin.html",
            context={
                "request": request,
                "error": "Administrador inactivo"
            }
        )

    # Obtener el hash de la base de datos
    password_hash = admin.password
    
    # Verificar que el hash sea válido
    if not password_hash or not password_hash.startswith('$2'):
        db.close()
        print(f"❌ Hash inválido: {password_hash[:20] if password_hash else 'None'}")
        return templates.TemplateResponse(
            request=request,
            name="login_admin.html",
            context={
                "request": request,
                "error": "Hash de contraseña inválido"
            }
        )

    print(f"🔍 Hash desde DB: {password_hash[:30]}...")
    print(f"🔍 Longitud del hash: {len(password_hash)}")
    
    # Verificar contraseña con bcrypt
    try:
        # Convertir a bytes de manera segura
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        
        print(f"🔍 Contraseña bytes: {password_bytes[:10]}...")
        print(f"🔍 Hash bytes: {hash_bytes[:30]}...")
        
        if not bcrypt.checkpw(password_bytes, hash_bytes):
            db.close()
            return templates.TemplateResponse(
                request=request,
                name="login_admin.html",
                context={
                    "request": request,
                    "error": "Contraseña incorrecta"
                }
            )
    except ValueError as e:
        db.close()
        print(f"❌ Error de ValueError: {str(e)}")
        return templates.TemplateResponse(
            request=request,
            name="login_admin.html",
            context={
                "request": request,
                "error": f"Error al verificar contraseña: {str(e)}"
            }
        )
    except Exception as e:
        db.close()
        print(f"❌ Error general: {str(e)}")
        return templates.TemplateResponse(
            request=request,
            name="login_admin.html",
            context={
                "request": request,
                "error": f"Error en verificación: {str(e)}"
            }
        )

    # Guardar sesión
    request.session["admin_id"] = admin.id
    request.session["usuario"] = admin.usuario
    
    print(f"✅ Login exitoso - admin_id: {admin.id}")
    print(f"📝 Sesión guardada: {dict(request.session)}")

    db.close()
    
    return RedirectResponse("/admin", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login-admin", status_code=302)


# ==================== RUTAS PROTEGIDAS ====================

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    if not request.session.get("admin_id"):
        return RedirectResponse("/login-admin", status_code=302)
    
    db = SessionLocal()

    total_clientes = db.query(Usuario).count()
    total_creditos = db.query(Credito).count()

    creditos = db.query(Credito).options(
        joinedload(Credito.usuario)
    ).order_by(
        Credito.fecha_creacion.desc()
    ).limit(10).all()

    vigente = sum(
        float(c.monto_total)
        for c in creditos
        if c.estado in ["Aprobado", "Desembolsado"]
    )

    vencida = sum(
        float(c.monto_total)
        for c in creditos
        if c.estado == "Rechazado"
    )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "request": request,
            "total_clientes": total_clientes,
            "total_creditos": total_creditos,
            "vigente": vigente,
            "vencida": vencida,
            "normal": 20,
            "cpp": 10,
            "deficiente": 5,
            "dudoso": 3,
            "perdida": 1,
            "creditos": creditos
        }
    )


@app.get("/core-creditos", response_class=HTMLResponse)
def core_creditos_page(request: Request):
    if not request.session.get("admin_id"):
        return RedirectResponse("/login-admin", status_code=302)
    
    db = SessionLocal()

    creditos = db.query(Credito).options(
        joinedload(Credito.usuario)
    ).order_by(
        Credito.fecha_creacion.desc()
    ).all()

    total_creditos = len(creditos)

    aprobados = len([c for c in creditos if c.estado == "Aprobado"])
    pendientes = len([c for c in creditos if c.estado == "Pendiente"])
    rechazados = len([c for c in creditos if c.estado == "Rechazado"])

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="core_creditos.html",
        context={
            "request": request,
            "creditos": creditos,
            "total_creditos": total_creditos,
            "aprobados": aprobados,
            "pendientes": pendientes,
            "rechazados": rechazados
        }
    )


@app.post("/core-creditos/{credito_id}/aprobar")
def aprobar_credito(credito_id: int):
    db = SessionLocal()

    credito = db.query(Credito).filter(Credito.id == credito_id).first()

    if credito:
        credito.estado = "Aprobado"
        db.commit()

    db.close()

    return RedirectResponse(url="/core-creditos", status_code=303)


@app.post("/core-creditos/{credito_id}/rechazar")
def rechazar_credito(credito_id: int):
    db = SessionLocal()

    credito = db.query(Credito).filter(Credito.id == credito_id).first()

    if credito:
        credito.estado = "Rechazado"
        db.commit()

    db.close()

    return RedirectResponse(url="/core-creditos", status_code=303)


@app.post("/core-creditos/{credito_id}/desembolsar")
def desembolsar_credito(credito_id: int):
    db = SessionLocal()

    credito = db.query(Credito).filter(Credito.id == credito_id).first()

    if credito and credito.estado == "Aprobado":
        cuenta = db.query(Cuenta).filter(Cuenta.usuario_id == credito.usuario_id).first()

        if cuenta:
            cuenta.saldo += credito.monto_total
            credito.estado = "Desembolsado"
            db.commit()

    db.close()

    return RedirectResponse(url="/core-creditos", status_code=303)


@app.get("/clientes", response_class=HTMLResponse)
def clientes_page(request: Request):
    if not request.session.get("admin_id"):
        return RedirectResponse("/login-admin", status_code=302)
    
    db = SessionLocal()

    usuarios = db.query(Usuario).order_by(Usuario.id.desc()).all()

    total_clientes = len(usuarios)
    verificados = len([usuario for usuario in usuarios if usuario.estado == "Verificado"])

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="clientes.html",
        context={
            "request": request,
            "usuarios": usuarios,
            "total_clientes": total_clientes,
            "verificados": verificados
        }
    )


@app.get("/operaciones", response_class=HTMLResponse)
def operaciones_page(request: Request):
    if not request.session.get("admin_id"):
        return RedirectResponse("/login-admin", status_code=302)
    
    db = SessionLocal()

    total_transferencias = db.query(Transferencia).count()
    total_pagos = db.query(Pago).count()
    total_movimientos = db.query(Movimiento).count()

    movimientos = db.query(Movimiento).order_by(
        Movimiento.fecha.desc()
    ).limit(50).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="operaciones.html",
        context={
            "request": request,
            "total_transferencias": total_transferencias,
            "total_pagos": total_pagos,
            "total_movimientos": total_movimientos,
            "movimientos": movimientos
        }
    )


@app.get("/reportes", response_class=HTMLResponse)
def reportes_page(request: Request):
    if not request.session.get("admin_id"):
        return RedirectResponse("/login-admin", status_code=302)
    
    db = SessionLocal()

    total_clientes = db.query(Usuario).count()
    total_creditos = db.query(Credito).count()
    total_pagos = db.query(Pago).count()
    total_transferencias = db.query(Transferencia).count()
    total_movimientos = db.query(Movimiento).count()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="reportes.html",
        context={
            "request": request,
            "total_clientes": total_clientes,
            "total_creditos": total_creditos,
            "total_pagos": total_pagos,
            "total_transferencias": total_transferencias,
            "total_movimientos": total_movimientos
        }
    )


@app.get("/configuracion", response_class=HTMLResponse)
def configuracion_page(request: Request):
    if not request.session.get("admin_id"):
        return RedirectResponse("/login-admin", status_code=302)
    
    db = SessionLocal()

    total_clientes = db.query(Usuario).count()
    total_creditos = db.query(Credito).count()
    total_transferencias = db.query(Transferencia).count()
    total_pagos = db.query(Pago).count()
    total_movimientos = db.query(Movimiento).count()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="configuracion.html",
        context={
            "request": request,
            "total_clientes": total_clientes,
            "total_creditos": total_creditos,
            "total_transferencias": total_transferencias,
            "total_pagos": total_pagos,
            "total_movimientos": total_movimientos
        }
    )


@app.get("/debug-session")
def debug_session(request: Request):
    """Endpoint para debuggear la sesión"""
    return {
        "session": dict(request.session),
        "admin_id": request.session.get("admin_id"),
        "has_session": bool(request.session.get("admin_id"))
    }


@app.get("/debug-hash")
def debug_hash(request: Request):
    """Endpoint para ver el hash de la base de datos"""
    db = SessionLocal()
    admin = db.query(Administrador).filter(
        Administrador.usuario == "admin"
    ).first()
    db.close()
    
    if admin:
        return {
            "usuario": admin.usuario,
            "password_hash": admin.password,
            "hash_length": len(admin.password),
            "hash_starts_with": admin.password[:10] if admin.password else None
        }
    return {"error": "Admin no encontrado"}