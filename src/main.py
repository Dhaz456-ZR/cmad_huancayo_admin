from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from decimal import Decimal
import os
from datetime import datetime

from sqlalchemy.orm import joinedload
from sqlalchemy import func, desc

from src.database import Base, engine, SessionLocal
from src.models import Usuario, Cuenta, Credito, Movimiento, Transferencia, Pago, Administrador, Recuperacion
from src.security import hash_password, verify_password


load_dotenv()

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de sesión
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "clave_secreta_temporal_para_desarrollo")
)

# Archivos estáticos
app.mount("/css", StaticFiles(directory="src/css"), name="css")
app.mount("/js", StaticFiles(directory="src/js"), name="js")
app.mount("/img", StaticFiles(directory="src/img"), name="img")

templates = Jinja2Templates(directory="src/html")


def get_admin_logueado(request: Request):
    """Obtiene el administrador actual de la sesión"""
    admin_id = request.session.get("admin_id")
    
    if not admin_id:
        return None
    
    db = SessionLocal()
    admin = db.query(Administrador).filter(Administrador.id == admin_id).first()
    db.close()
    
    return admin


def get_usuario_logueado(request: Request):
    """Obtiene el usuario actual de la sesión"""
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return None

    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    db.close()

    return usuario


def get_dashboard_data(usuario):
    """Obtiene todos los datos del dashboard para un usuario"""
    db = SessionLocal()

    cuenta = db.query(Cuenta).filter(Cuenta.usuario_id == usuario.id).first()

    credito = db.query(Credito).filter(
        Credito.usuario_id == usuario.id
    ).order_by(Credito.fecha_creacion.desc()).first()

    creditos = db.query(Credito).filter(
        Credito.usuario_id == usuario.id
    ).order_by(Credito.fecha_creacion.desc()).limit(5).all()

    movimientos = db.query(Movimiento).filter(
        Movimiento.usuario_id == usuario.id
    ).order_by(Movimiento.fecha.desc()).limit(5).all()

    transferencias = db.query(Transferencia).filter(
        Transferencia.usuario_id == usuario.id
    ).order_by(Transferencia.fecha.desc()).limit(5).all()

    pagos = db.query(Pago).filter(
        Pago.usuario_id == usuario.id
    ).order_by(Pago.fecha.desc()).limit(5).all()

    context = {
        "nombre": usuario.nombre,
        "dni": usuario.dni,
        "tarjeta": usuario.tarjeta,
        "estado": usuario.estado,
        "cuenta": cuenta,
        "credito": credito,
        "creditos": creditos,
        "movimientos": movimientos,
        "transferencias": transferencias,
        "pagos": pagos,
        "error": None,
        "success": None
    }

    db.close()
    return context


# ==========================================
# REDIRECCIONES
# ==========================================

@app.get("/")
def root():
    """Redirige a /admin"""
    return RedirectResponse(url="/admin", status_code=302)


# ==========================================
# RUTAS DE ADMINISTRACIÓN - LOGIN
# ==========================================

@app.get("/admin", response_class=HTMLResponse)
def admin_login_page(request: Request):
    """Página de login del panel administrativo"""
    admin = get_admin_logueado(request)
    if admin:
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="login_admin.html")


@app.post("/admin/login")
def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Login para administradores"""
    db = SessionLocal()
    
    try:
        admin = db.query(Administrador).filter(
            Administrador.email == email,
            Administrador.estado == "Activo"
        ).first()
        
        if not admin:
            db.close()
            return templates.TemplateResponse(
                request=request,
                name="login_admin.html",
                context={"error": "Credenciales incorrectas"}
            )
        
        if not verify_password(password, admin.password):
            db.close()
            return templates.TemplateResponse(
                request=request,
                name="login_admin.html",
                context={"error": "Contraseña incorrecta"}
            )
        
        admin.ultimo_acceso = datetime.now()
        db.commit()
        
        request.session["admin_id"] = admin.id
        request.session["admin_nombre"] = admin.nombre
        request.session["admin_rol"] = admin.rol
        
        db.close()
        
        return RedirectResponse(url="/admin/dashboard", status_code=303)
        
    except Exception as e:
        db.rollback()
        db.close()
        print(f"❌ Error en login admin: {str(e)}")
        return templates.TemplateResponse(
            request=request,
            name="login_admin.html",
            context={"error": f"Error: {str(e)}"}
        )


@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard_page(request: Request):
    """Dashboard del panel administrativo"""
    admin = get_admin_logueado(request)
    if not admin:
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "admin_nombre": admin.nombre,
            "admin_rol": admin.rol
        }
    )


@app.get("/admin/logout")
def admin_logout(request: Request):
    """Cierra sesión del administrador"""
    request.session.clear()
    return RedirectResponse(url="/admin", status_code=303)


# ==========================================
# RUTAS ADMIN - CLIENTES
# ==========================================

@app.get("/clientes", response_class=HTMLResponse)
def clientes_page(request: Request):
    admin = get_admin_logueado(request)
    if not admin:
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="clientes.html",
        context={"admin_nombre": admin.nombre, "admin_rol": admin.rol}
    )


@app.get("/api/clientes")
def get_clientes(
    search: str = "",
    page: int = 1,
    limit: int = 10,
    sort_by: str = "id",
    sort_order: str = "desc"
):
    db = SessionLocal()
    
    try:
        query = db.query(Usuario)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Usuario.nombre.like(search_term)) |
                (Usuario.dni.like(search_term))
            )
        
        if sort_order.lower() == "asc":
            query = query.order_by(getattr(Usuario, sort_by).asc())
        else:
            query = query.order_by(getattr(Usuario, sort_by).desc())
        
        total = query.count()
        offset = (page - 1) * limit
        clientes = query.offset(offset).limit(limit).all()
        
        result = []
        for cliente in clientes:
            result.append({
                "id": cliente.id,
                "nombre": cliente.nombre,
                "dni": cliente.dni,
                "tarjeta": cliente.tarjeta,
                "estado": cliente.estado,
                "fecha_creacion_formateada": cliente.fecha_creacion.strftime("%d/%m/%Y") if cliente.fecha_creacion else "N/A"
            })
        
        db.close()
        
        return {
            "success": True,
            "data": result,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    
    except Exception as e:
        db.close()
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/clientes/estadisticas")
def get_clientes_estadisticas():
    db = SessionLocal()
    
    try:
        total = db.query(Usuario).count()
        verificados = db.query(Usuario).filter(Usuario.estado == "Verificado").count()
        bloqueados = db.query(Usuario).filter(Usuario.estado == "Bloqueado").count()
        pendientes = db.query(Usuario).filter(Usuario.estado == "Pendiente").count()
        
        hoy = datetime.now().date()
        registrados_hoy = db.query(Usuario).filter(
            func.date(Usuario.fecha_creacion) == hoy
        ).count()
        
        db.close()
        
        return {
            "success": True,
            "data": {
                "total": total,
                "verificados": verificados,
                "bloqueados": bloqueados,
                "pendientes": pendientes,
                "registrados_hoy": registrados_hoy
            }
        }
    
    except Exception as e:
        db.close()
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/clientes/{cliente_id}")
def get_cliente(cliente_id: int):
    db = SessionLocal()
    
    try:
        cliente = db.query(Usuario).filter(Usuario.id == cliente_id).first()
        
        if not cliente:
            db.close()
            return {
                "success": False,
                "error": "Cliente no encontrado"
            }
        
        result = {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "dni": cliente.dni,
            "tarjeta": cliente.tarjeta,
            "estado": cliente.estado,
            "fecha_creacion_formateada": cliente.fecha_creacion.strftime("%d/%m/%Y") if cliente.fecha_creacion else "N/A"
        }
        
        db.close()
        
        return {
            "success": True,
            "data": result
        }
    
    except Exception as e:
        db.close()
        return {
            "success": False,
            "error": str(e)
        }


@app.put("/api/clientes/{cliente_id}")
def update_cliente(
    cliente_id: int,
    nombre: str = Form(None),
    dni: str = Form(None),
    tarjeta: str = Form(None),
    estado: str = Form(None)
):
    db = SessionLocal()
    
    try:
        cliente = db.query(Usuario).filter(Usuario.id == cliente_id).first()
        
        if not cliente:
            db.close()
            return {
                "success": False,
                "error": "Cliente no encontrado"
            }
        
        if nombre:
            cliente.nombre = nombre
        if dni:
            existing = db.query(Usuario).filter(
                Usuario.dni == dni,
                Usuario.id != cliente_id
            ).first()
            if existing:
                db.close()
                return {
                    "success": False,
                    "error": "El DNI ya está registrado por otro usuario"
                }
            cliente.dni = dni
        if tarjeta:
            existing = db.query(Usuario).filter(
                Usuario.tarjeta == tarjeta,
                Usuario.id != cliente_id
            ).first()
            if existing:
                db.close()
                return {
                    "success": False,
                    "error": "La tarjeta ya está registrada por otro usuario"
                }
            cliente.tarjeta = tarjeta
        if estado:
            if estado in ["Verificado", "Pendiente", "Bloqueado"]:
                cliente.estado = estado
        
        db.commit()
        db.close()
        
        return {
            "success": True,
            "message": "Cliente actualizado correctamente"
        }
    
    except Exception as e:
        db.rollback()
        db.close()
        return {
            "success": False,
            "error": str(e)
        }


@app.delete("/api/clientes/{cliente_id}")
def delete_cliente(cliente_id: int):
    db = SessionLocal()
    
    try:
        cliente = db.query(Usuario).filter(Usuario.id == cliente_id).first()
        
        if not cliente:
            db.close()
            return {
                "success": False,
                "error": "Cliente no encontrado"
            }
        
        db.delete(cliente)
        db.commit()
        db.close()
        
        return {
            "success": True,
            "message": "Cliente eliminado correctamente"
        }
    
    except Exception as e:
        db.rollback()
        db.close()
        return {
            "success": False,
            "error": str(e)
        }


@app.put("/api/clientes/{cliente_id}/bloquear")
def bloquear_cliente(cliente_id: int):
    db = SessionLocal()
    
    try:
        cliente = db.query(Usuario).filter(Usuario.id == cliente_id).first()
        
        if not cliente:
            db.close()
            return {
                "success": False,
                "error": "Cliente no encontrado"
            }
        
        if cliente.estado == "Bloqueado":
            db.close()
            return {
                "success": False,
                "error": "El cliente ya está bloqueado"
            }
        
        cliente.estado = "Bloqueado"
        db.commit()
        db.close()
        
        return {
            "success": True,
            "message": "Cliente bloqueado correctamente"
        }
    
    except Exception as e:
        db.rollback()
        db.close()
        return {
            "success": False,
            "error": str(e)
        }


@app.put("/api/clientes/{cliente_id}/activar")
def activar_cliente(cliente_id: int):
    db = SessionLocal()
    
    try:
        cliente = db.query(Usuario).filter(Usuario.id == cliente_id).first()
        
        if not cliente:
            db.close()
            return {
                "success": False,
                "error": "Cliente no encontrado"
            }
        
        if cliente.estado == "Verificado":
            db.close()
            return {
                "success": False,
                "error": "El cliente ya está verificado"
            }
        
        cliente.estado = "Verificado"
        db.commit()
        db.close()
        
        return {
            "success": True,
            "message": "Cliente activado correctamente"
        }
    
    except Exception as e:
        db.rollback()
        db.close()
        return {
            "success": False,
            "error": str(e)
        }


# ==========================================
# RUTAS ADMIN - CRÉDITOS
# ==========================================

@app.get("/core-creditos", response_class=HTMLResponse)
def core_creditos_page(request: Request):
    admin = get_admin_logueado(request)
    if not admin:
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="creditos.html",
        context={"admin_nombre": admin.nombre, "admin_rol": admin.rol}
    )


@app.get("/api/creditos")
def get_creditos(search: str = ""):
    db = SessionLocal()
    
    try:
        query = db.query(Credito).options(joinedload(Credito.usuario))
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Credito.tipo_credito.like(search_term)) |
                (Credito.usuario.has(Usuario.nombre.like(search_term)))
            )
        
        creditos = query.order_by(Credito.fecha_creacion.desc()).all()
        
        result = []
        for credito in creditos:
            result.append({
                "id": credito.id,
                "cliente_nombre": credito.usuario.nombre if credito.usuario else "N/A",
                "tipo_credito": credito.tipo_credito,
                "monto_total": str(credito.monto_total),
                "cuota_mensual": str(credito.cuota_mensual),
                "cuotas_totales": credito.cuotas_totales,
                "cuotas_pagadas": credito.cuotas_pagadas,
                "estado": credito.estado,
                "fecha": credito.fecha_creacion.strftime("%d/%m/%Y") if credito.fecha_creacion else "N/A"
            })
        
        db.close()
        return {"success": True, "data": result}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}


@app.get("/api/creditos/estadisticas")
def get_creditos_estadisticas():
    db = SessionLocal()
    
    try:
        total = db.query(Credito).count()
        aprobados = db.query(Credito).filter(Credito.estado == "Aprobado").count()
        pendientes = db.query(Credito).filter(Credito.estado == "Pendiente").count()
        rechazados = db.query(Credito).filter(Credito.estado == "Rechazado").count()
        
        db.close()
        return {
            "success": True,
            "data": {
                "total": total,
                "aprobados": aprobados,
                "pendientes": pendientes,
                "rechazados": rechazados
            }
        }
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}


# ==========================================
# RUTAS ADMIN - TRANSFERENCIAS
# ==========================================

@app.get("/transferencias-admin", response_class=HTMLResponse)
def transferencias_admin_page(request: Request):
    admin = get_admin_logueado(request)
    if not admin:
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="transferencias-admin.html",
        context={"admin_nombre": admin.nombre, "admin_rol": admin.rol}
    )


@app.get("/api/transferencias")
def get_transferencias():
    db = SessionLocal()
    
    try:
        transferencias = db.query(Transferencia).options(
            joinedload(Transferencia.usuario)
        ).order_by(Transferencia.fecha.desc()).all()
        
        result = []
        for t in transferencias:
            result.append({
                "id": t.id,
                "cliente_nombre": t.usuario.nombre if t.usuario else "N/A",
                "cuenta_destino": t.cuenta_destino,
                "destinatario": t.destinatario,
                "monto": str(t.monto),
                "motivo": t.motivo,
                "fecha": t.fecha.strftime("%d/%m/%Y %H:%M") if t.fecha else "N/A"
            })
        
        db.close()
        return {"success": True, "data": result}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}


# ==========================================
# RUTAS ADMIN - PAGOS
# ==========================================

@app.get("/pagos-admin", response_class=HTMLResponse)
def pagos_admin_page(request: Request):
    admin = get_admin_logueado(request)
    if not admin:
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="pagos-admin.html",
        context={"admin_nombre": admin.nombre, "admin_rol": admin.rol}
    )


@app.get("/api/pagos")
def get_pagos():
    db = SessionLocal()
    
    try:
        pagos = db.query(Pago).options(
            joinedload(Pago.usuario)
        ).order_by(Pago.fecha.desc()).all()
        
        result = []
        for p in pagos:
            result.append({
                "id": p.id,
                "cliente_nombre": p.usuario.nombre if p.usuario else "N/A",
                "servicio": p.servicio,
                "codigo_cliente": p.codigo_cliente,
                "monto": str(p.monto),
                "fecha": p.fecha.strftime("%d/%m/%Y %H:%M") if p.fecha else "N/A"
            })
        
        db.close()
        return {"success": True, "data": result}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}


# ==========================================
# RUTAS ADMIN - CONFIGURACIÓN
# ==========================================

@app.get("/configuracion", response_class=HTMLResponse)
def configuracion_page(request: Request):
    admin = get_admin_logueado(request)
    if not admin:
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="configuracion.html",
        context={"admin_nombre": admin.nombre, "admin_rol": admin.rol}
    )


# ==========================================
# RUTAS ADMIN - ACCIONES CRÉDITOS
# ==========================================

@app.post("/core-creditos/{credito_id}/aprobar")
def aprobar_credito(credito_id: int):
    db = SessionLocal()
    try:
        credito = db.query(Credito).filter(Credito.id == credito_id).first()
        if credito:
            credito.estado = "Aprobado"
            db.commit()
            db.close()
            return RedirectResponse(url="/core-creditos", status_code=303)
        db.close()
        return {"error": "Crédito no encontrado"}
    except Exception as e:
        db.rollback()
        db.close()
        return {"error": str(e)}


@app.post("/core-creditos/{credito_id}/rechazar")
def rechazar_credito(credito_id: int):
    db = SessionLocal()
    try:
        credito = db.query(Credito).filter(Credito.id == credito_id).first()
        if credito:
            credito.estado = "Rechazado"
            db.commit()
            db.close()
            return RedirectResponse(url="/core-creditos", status_code=303)
        db.close()
        return {"error": "Crédito no encontrado"}
    except Exception as e:
        db.rollback()
        db.close()
        return {"error": str(e)}


@app.post("/core-creditos/{credito_id}/desembolsar")
def desembolsar_credito(credito_id: int):
    db = SessionLocal()
    try:
        credito = db.query(Credito).filter(Credito.id == credito_id).first()
        if credito and credito.estado == "Aprobado":
            cuenta = db.query(Cuenta).filter(Cuenta.usuario_id == credito.usuario_id).first()
            if cuenta:
                cuenta.saldo = cuenta.saldo + credito.monto_total
                credito.estado = "Desembolsado"
                db.commit()
                db.close()
                return RedirectResponse(url="/core-creditos", status_code=303)
        db.close()
        return {"error": "No se pudo desembolsar el crédito"}
    except Exception as e:
        db.rollback()
        db.close()
        return {"error": str(e)}


# ==========================================
# PÁGINAS DE BANCA DIGITAL (PORTAL USUARIOS)
# ==========================================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@app.get("/index", response_class=HTMLResponse)
def index_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=get_dashboard_data(usuario)
    )


@app.get("/mis-cuentas", response_class=HTMLResponse)
def mis_cuentas_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="mis_cuentas.html",
        context=get_dashboard_data(usuario)
    )


@app.get("/transferencias", response_class=HTMLResponse)
def transferencias_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="transferencias.html",
        context=get_dashboard_data(usuario)
    )


@app.post("/transferencias", response_class=HTMLResponse)
def realizar_transferencia(
    request: Request,
    cuenta_destino: str = Form(...),
    destinatario: str = Form(...),
    monto: str = Form(...),
    motivo: str = Form(...)
):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()

    cuenta = db.query(Cuenta).filter(Cuenta.usuario_id == usuario.id).first()

    try:
        monto_decimal = Decimal(monto)
    except:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto ingresado no es válido."
        return templates.TemplateResponse(
            request=request,
            name="transferencias.html",
            context=context
        )

    if not cuenta:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "No tienes una cuenta registrada."
        return templates.TemplateResponse(
            request=request,
            name="transferencias.html",
            context=context
        )

    if monto_decimal <= 0:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto debe ser mayor a 0."
        return templates.TemplateResponse(
            request=request,
            name="transferencias.html",
            context=context
        )

    if cuenta.saldo < monto_decimal:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "Saldo insuficiente para realizar la transferencia."
        return templates.TemplateResponse(
            request=request,
            name="transferencias.html",
            context=context
        )

    nueva_transferencia = Transferencia(
        usuario_id=usuario.id,
        cuenta_destino=cuenta_destino,
        destinatario=destinatario,
        monto=monto_decimal,
        motivo=motivo
    )

    nuevo_movimiento = Movimiento(
        usuario_id=usuario.id,
        descripcion="Transferencia enviada a " + destinatario,
        monto=monto_decimal,
        tipo="salida"
    )

    cuenta.saldo = cuenta.saldo - monto_decimal

    db.add(nueva_transferencia)
    db.add(nuevo_movimiento)
    db.commit()
    db.close()

    return RedirectResponse(url="/transferencias", status_code=303)


@app.get("/creditos", response_class=HTMLResponse)
def creditos_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="creditos.html",
        context=get_dashboard_data(usuario)
    )


@app.post("/creditos", response_class=HTMLResponse)
def solicitar_credito(
    request: Request,
    tipo_credito: str = Form(...),
    monto_total: str = Form(...),
    cuotas_totales: int = Form(...),
    cuota_mensual: str = Form(...)
):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()

    try:
        monto_decimal = Decimal(monto_total)
        cuota_decimal = Decimal(cuota_mensual)
    except:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto o la cuota ingresada no es válida."
        return templates.TemplateResponse(
            request=request,
            name="creditos.html",
            context=context
        )

    if monto_decimal <= 0:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto solicitado debe ser mayor a 0."
        return templates.TemplateResponse(
            request=request,
            name="creditos.html",
            context=context
        )

    if cuotas_totales <= 0:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El número de meses debe ser mayor a 0."
        return templates.TemplateResponse(
            request=request,
            name="creditos.html",
            context=context
        )

    nuevo_credito = Credito(
        usuario_id=usuario.id,
        tipo_credito=tipo_credito,
        monto_total=monto_decimal,
        cuota_mensual=cuota_decimal,
        cuotas_totales=cuotas_totales,
        cuotas_pagadas=0,
        estado="Pendiente"
    )

    nuevo_movimiento = Movimiento(
        usuario_id=usuario.id,
        descripcion="Solicitud de crédito: " + tipo_credito,
        monto=monto_decimal,
        tipo="entrada"
    )

    db.add(nuevo_credito)
    db.add(nuevo_movimiento)
    db.commit()
    db.close()

    return RedirectResponse(url="/creditos", status_code=303)


@app.get("/pagos", response_class=HTMLResponse)
def pagos_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="pagos.html",
        context=get_dashboard_data(usuario)
    )


@app.post("/pagos", response_class=HTMLResponse)
def realizar_pago(
    request: Request,
    servicio: str = Form(...),
    codigo_cliente: str = Form(...),
    monto: str = Form(...)
):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()

    cuenta = db.query(Cuenta).filter(Cuenta.usuario_id == usuario.id).first()

    try:
        monto_decimal = Decimal(monto)
    except:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto ingresado no es válido."
        return templates.TemplateResponse(
            request=request,
            name="pagos.html",
            context=context
        )

    if not cuenta:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "No tienes una cuenta registrada."
        return templates.TemplateResponse(
            request=request,
            name="pagos.html",
            context=context
        )

    if monto_decimal <= 0:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "El monto debe ser mayor a 0."
        return templates.TemplateResponse(
            request=request,
            name="pagos.html",
            context=context
        )

    if cuenta.saldo < monto_decimal:
        db.close()
        context = get_dashboard_data(usuario)
        context["error"] = "Saldo insuficiente para realizar el pago."
        return templates.TemplateResponse(
            request=request,
            name="pagos.html",
            context=context
        )

    nuevo_pago = Pago(
        usuario_id=usuario.id,
        servicio=servicio,
        codigo_cliente=codigo_cliente,
        monto=monto_decimal
    )

    nuevo_movimiento = Movimiento(
        usuario_id=usuario.id,
        descripcion="Pago de servicio: " + servicio,
        monto=monto_decimal,
        tipo="salida"
    )

    cuenta.saldo = cuenta.saldo - monto_decimal

    db.add(nuevo_pago)
    db.add(nuevo_movimiento)
    db.commit()
    db.close()

    return RedirectResponse(url="/pagos", status_code=303)


@app.get("/perfil", response_class=HTMLResponse)
def perfil_page(request: Request):
    usuario = get_usuario_logueado(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="perfil.html",
        context=get_dashboard_data(usuario)
    )


# ==========================================
# REGISTRO DE USUARIOS (SIN CORREO)
# ==========================================

@app.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    nombre: str = Form(...),
    dni: str = Form(...),
    tarjeta: str = Form(...),
    password: str = Form(...),
    pin1: str = Form(...),
    pin2: str = Form(...),
    pin3: str = Form(...),
    pin4: str = Form(...)
):
    db = SessionLocal()

    existing_user_dni = db.query(Usuario).filter(Usuario.dni == dni).first()
    if existing_user_dni:
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "El DNI ya está registrado"}
        )

    existing_user_tarjeta = db.query(Usuario).filter(Usuario.tarjeta == tarjeta).first()
    if existing_user_tarjeta:
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "El número de tarjeta ya está registrado"}
        )

    codigo_seguridad = pin1 + pin2 + pin3 + pin4

    try:
        nuevo_usuario = Usuario(
            nombre=nombre,
            dni=dni,
            tarjeta=tarjeta,
            password=hash_password(password),
            codigo_seguridad=codigo_seguridad,
            estado="Verificado"
        )

        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        nueva_cuenta = Cuenta(
            usuario_id=nuevo_usuario.id,
            numero_cuenta="001-" + tarjeta[-4:] + "-" + dni,
            tipo_cuenta="Cuenta de Ahorros",
            saldo=Decimal("12450.90")
        )
        db.add(nueva_cuenta)

        nuevo_credito = Credito(
            usuario_id=nuevo_usuario.id,
            tipo_credito="Préstamo Personal",
            monto_total=Decimal("4800.00"),
            cuota_mensual=Decimal("420.00"),
            cuotas_totales=12,
            cuotas_pagadas=8,
            estado="Al día"
        )
        db.add(nuevo_credito)

        movimientos = [
            Movimiento(
                usuario_id=nuevo_usuario.id,
                descripcion="Depósito recibido",
                monto=Decimal("850.00"),
                tipo="entrada"
            ),
            Movimiento(
                usuario_id=nuevo_usuario.id,
                descripcion="Pago de servicio",
                monto=Decimal("120.00"),
                tipo="salida"
            ),
            Movimiento(
                usuario_id=nuevo_usuario.id,
                descripcion="Transferencia enviada",
                monto=Decimal("300.00"),
                tipo="salida"
            )
        ]
        for m in movimientos:
            db.add(m)

        db.commit()
        db.close()

        return RedirectResponse(url="/login", status_code=303)

    except Exception as e:
        db.rollback()
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": f"Error al registrar: {str(e)}"}
        )


# ==========================================
# LOGIN DE USUARIOS (SIN CORREO)
# ==========================================

@app.post("/login", response_class=HTMLResponse)
def login_usuario(
    request: Request,
    dni: str = Form(...),
    tarjeta: str = Form(...),
    password: str = Form(...),
    codigo_seguridad: str = Form(...)
):
    db = SessionLocal()

    usuario = db.query(Usuario).filter(
        Usuario.dni == dni,
        Usuario.tarjeta == tarjeta
    ).first()

    if not usuario:
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "DNI o tarjeta incorrectos"}
        )

    if not verify_password(password, usuario.password):
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Contraseña incorrecta"}
        )

    if usuario.codigo_seguridad != codigo_seguridad:
        db.close()
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "PIN incorrecto"}
        )

    request.session["usuario_id"] = usuario.id
    request.session["nombre"] = usuario.nombre

    db.close()

    return RedirectResponse(url="/index", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Servidor funcionando correctamente"}