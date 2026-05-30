#Aquí van los endpoints de login y logout. La lógica para verificar usuario y contraseña.

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from modelos import Empleado, SessionLocal
from schemas import EmpleadoResponse
from fastapi import Response
from fastapi import APIRouter, HTTPException, Request, Form

import random
import string
from datetime import datetime, timedelta
import sib_api_v3_sdk
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

router = APIRouter()

templates = Jinja2Templates(directory="templates")



BREVO_API_KEY = "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"
SENDER_EMAIL  = "mao77002222@gmail.com"
SENDER_NAME   = "Empresa XYZ"
 
_codigos_pendientes: dict = {}
 
 
def _generar_codigo(n: int = 6) -> str:
    return "".join(random.choices(string.digits, k=n))
 
 
# Configuracion de Recuperacion de contraseña con BREVO API EXTERNO
def _enviar_correo(destinatario: str, asunto: str, html: str) -> None:
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": destinatario}],
        sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
        subject=asunto,
        html_content=html,
    )

    api_instance.send_transac_email(send_smtp_email)
 
class SolicitarBody(BaseModel):
    email: str
 
class VerificarBody(BaseModel):
    email:  str
    codigo: str
 
class CambiarBody(BaseModel):
    email:            str
    nueva_contrasena: str
 

@router.post("/login")
def iniciar_sesion(response: Response, cedula: str = Form(...), contrasena: str = Form(...)):
    
    db = SessionLocal()

    existe=db.query(Empleado).filter(Empleado.cedula == cedula).first()
    
    if not existe:
        db.close()

        raise HTTPException(status_code=404, detail="Empleado no ha sido registrado")
    
    if not existe.activo:
        db.close()
        raise HTTPException(status_code=403, detail="Usuario inactivo, contacte al administrador")
    
    if not existe.contrasena == contrasena:
        db.close()

        raise HTTPException(status_code=404, detail="Contraseña incorrecta")
    
    db.close()

    if existe.rol == "empleado":
        redirect = RedirectResponse(url="/dashboard/empleado", status_code=303)
    elif existe.rol == "admin":
        redirect = RedirectResponse(url="/dashboard/administrador", status_code=303)

    redirect.set_cookie(key="cedula", value=existe.cedula)
    return redirect

@router.get("/logout")
def cerrar_sesion(response: Response):

    response.delete_cookie(key="cedula")
    return RedirectResponse(url="/login", status_code=303)

@router.get("/login")
def mostrar_login(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )



@router.post("/recuperar-password/solicitar")
def solicitar_codigo(body: SolicitarBody):
    db = SessionLocal()
    try:
        empleado = db.query(Empleado).filter(Empleado.email == body.email).first()
 
        if not empleado:
            return JSONResponse(
                status_code=404,
                content={"detail": "No existe una cuenta asociada a ese correo."}
            )
 
        codigo = _generar_codigo()
        expira = datetime.now() + timedelta(minutes=2)
        _codigos_pendientes[body.email] = {"codigo": codigo, "expira": expira}
 
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;
                    background:#0a1628;border-radius:12px;overflow:hidden;">
          <div style="height:4px;
                      background:linear-gradient(90deg,#1d9e75,#2d7dd2,#7c3aed);"></div>
          <div style="padding:28px 32px;">
            <p style="color:#7f93a8;font-size:0.78rem;letter-spacing:0.1em;
                      text-transform:uppercase;margin-bottom:8px;">
              EMPRESA XYZ — Sistema de Control de Empleados
            </p>
            <h2 style="color:#e8edf3;font-size:1.3rem;margin:0 0 16px;">
              Código de verificación
            </h2>
            <p style="color:#7f93a8;font-size:0.9rem;margin-bottom:24px;">
              Hola <strong style="color:#e8edf3">{empleado.nombre}</strong>,
              solicitaste recuperar tu contraseña. Usa este código:
            </p>
            <div style="background:rgba(45,125,210,0.1);
                        border:1px solid rgba(45,125,210,0.3);
                        border-radius:10px;padding:20px;text-align:center;
                        margin-bottom:20px;">
              <span style="font-size:2.4rem;font-weight:700;letter-spacing:0.4em;
                           color:#e8edf3;font-family:'Courier New',monospace;">
                {codigo}
              </span>
            </div>
            <p style="color:#4d6070;font-size:0.78rem;text-align:center;">
              Expira en <strong style="color:#ef9f27">2 minutos</strong>.<br>
              Si no solicitaste este código, ignora este mensaje.
            </p>
          </div>
          <div style="background:rgba(10,21,32,0.6);padding:12px 32px;">
            <p style="color:#2d4055;font-size:0.7rem;margin:0;">
              Mensaje automático — no respondas a este correo.
            </p>
          </div>
        </div>
        """
 
        try:
            _enviar_correo(body.email, "Empresa XYZ — Código de verificación", html)
        except Exception:
            _codigos_pendientes.pop(body.email, None)
            return JSONResponse(
                status_code=500,
                content={"detail": "No se pudo enviar el correo. Intenta más tarde."}
            )
 
        return JSONResponse(status_code=200, content={"ok": True})
    finally:
        db.close()
 
 
@router.post("/recuperar-password/verificar")
def verificar_codigo(body: VerificarBody):
    entrada = _codigos_pendientes.get(body.email)
 
    if not entrada:
        return JSONResponse(status_code=400,
            content={"detail": "No hay un código pendiente para ese correo."})
 
    if datetime.now() > entrada["expira"]:
        _codigos_pendientes.pop(body.email, None)
        return JSONResponse(status_code=400,
            content={"detail": "El código ha expirado. Solicita uno nuevo."})
 
    if entrada["codigo"] != body.codigo:
        return JSONResponse(status_code=400,
            content={"detail": "Código incorrecto."})
 
    return JSONResponse(status_code=200, content={"ok": True})
 
 
@router.post("/recuperar-password/cambiar")
def cambiar_contrasena(body: CambiarBody):
    entrada = _codigos_pendientes.get(body.email)
    if not entrada or datetime.now() > entrada["expira"]:
        return JSONResponse(status_code=400,
            content={"detail": "La sesión expiró. Inicia el proceso de nuevo."})
    if len(body.nueva_contrasena) < 8:
        return JSONResponse(status_code=400,
            content={"detail": "La contraseña debe tener al menos 8 caracteres."})
    db = SessionLocal()
    try:
        empleado = db.query(Empleado).filter(Empleado.email == body.email).first()
        if not empleado:
            return JSONResponse(status_code=404,
                content={"detail": "Cuenta no encontrada."})
        empleado.contrasena = body.nueva_contrasena
        db.commit()
        _codigos_pendientes.pop(body.email, None)
        return JSONResponse(status_code=200, content={"ok": True})
    finally:
        db.close()