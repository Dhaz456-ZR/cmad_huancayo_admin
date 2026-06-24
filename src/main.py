from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from sqlalchemy.orm import joinedload
from jose import jwt
from src.database import SessionLocal
from src.models import Credito, Usuario, Cuenta
from src.models import (
    Credito,
    Usuario,
    Cuenta,
    Transferencia,
    Pago,
    Movimiento
)

app = FastAPI(
    title="CMAD HUANCAYO ADMIN"
)

# Archivos estáticos
app.mount("/css", StaticFiles(directory="src/css"), name="css")
app.mount("/js", StaticFiles(directory="src/js"), name="js")
app.mount("/img", StaticFiles(directory="src/img"), name="img")  # <- AGREGAR ESTO

templates = Jinja2Templates(directory="src/html")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin.html"
    )


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):

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

    db = SessionLocal()

    creditos = db.query(Credito).options(
        joinedload(Credito.usuario)
    ).order_by(
        Credito.fecha_creacion.desc()
    ).all()

    total_creditos = len(creditos)

    aprobados = len([
        c for c in creditos
        if c.estado == "Aprobado"
    ])

    pendientes = len([
        c for c in creditos
        if c.estado == "Pendiente"
    ])

    rechazados = len([
        c for c in creditos
        if c.estado == "Rechazado"
    ])

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="core_creditos.html",
        context={
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

    credito = db.query(Credito).filter(
        Credito.id == credito_id
    ).first()

    if credito:
        credito.estado = "Aprobado"
        db.commit()

    db.close()

    return RedirectResponse(
        url="/core-creditos",
        status_code=303
    )


@app.post("/core-creditos/{credito_id}/rechazar")
def rechazar_credito(credito_id: int):

    db = SessionLocal()

    credito = db.query(Credito).filter(
        Credito.id == credito_id
    ).first()

    if credito:
        credito.estado = "Rechazado"
        db.commit()

    db.close()

    return RedirectResponse(
        url="/core-creditos",
        status_code=303
    )


@app.post("/core-creditos/{credito_id}/desembolsar")
def desembolsar_credito(credito_id: int):

    db = SessionLocal()

    credito = db.query(Credito).filter(
        Credito.id == credito_id
    ).first()

    if credito and credito.estado == "Aprobado":

        cuenta = db.query(Cuenta).filter(
            Cuenta.usuario_id == credito.usuario_id
        ).first()

        if cuenta:
            cuenta.saldo += credito.monto_total
            credito.estado = "Desembolsado"
            db.commit()

    db.close()

    return RedirectResponse(
        url="/core-creditos",
        status_code=303
    )


@app.get("/clientes", response_class=HTMLResponse)
def clientes_page(request: Request):

    db = SessionLocal()

    usuarios = db.query(Usuario).order_by(
        Usuario.id.desc()
    ).all()

    total_clientes = len(usuarios)

    verificados = len([
        usuario
        for usuario in usuarios
        if usuario.estado == "Verificado"
    ])

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="clientes.html",
        context={
            "usuarios": usuarios,
            "total_clientes": total_clientes,
            "verificados": verificados
        }
    )

@app.get("/operaciones", response_class=HTMLResponse)
def operaciones_page(request: Request):

    db = SessionLocal()

    total_transferencias = db.query(
        Transferencia
    ).count()

    total_pagos = db.query(
        Pago
    ).count()

    total_movimientos = db.query(
        Movimiento
    ).count()

    movimientos = db.query(
        Movimiento
    ).order_by(
        Movimiento.fecha.desc()
    ).limit(50).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="operaciones.html",
        context={
            "total_transferencias": total_transferencias,
            "total_pagos": total_pagos,
            "total_movimientos": total_movimientos,
            "movimientos": movimientos
        }
    )


@app.get("/reportes", response_class=HTMLResponse)
def reportes_page(request: Request):

    db = SessionLocal()

    total_clientes = db.query(
        Usuario
    ).count()

    total_creditos = db.query(
        Credito
    ).count()

    total_pagos = db.query(
        Pago
    ).count()

    total_transferencias = db.query(
        Transferencia
    ).count()

    total_movimientos = db.query(
        Movimiento
    ).count()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="reportes.html",
        context={
            "total_clientes": total_clientes,
            "total_creditos": total_creditos,
            "total_pagos": total_pagos,
            "total_transferencias": total_transferencias,
            "total_movimientos": total_movimientos
        }
    )

@app.get("/configuracion", response_class=HTMLResponse)
def configuracion_page(request: Request):

    db = SessionLocal()

    total_clientes = db.query(
        Usuario
    ).count()

    total_creditos = db.query(
        Credito
    ).count()

    total_transferencias = db.query(
        Transferencia
    ).count()

    total_pagos = db.query(
        Pago
    ).count()

    total_movimientos = db.query(
        Movimiento
    ).count()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="configuracion.html",
        context={
            "total_clientes": total_clientes,
            "total_creditos": total_creditos,
            "total_transferencias": total_transferencias,
            "total_pagos": total_pagos,
            "total_movimientos": total_movimientos
        }
    )