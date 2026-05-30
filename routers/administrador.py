# Endpoints del administrador

from typing import List
from datetime import datetime

from fastapi import APIRouter, Cookie, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import joinedload

from modelos import Asistencia, Empleado, SessionLocal, Sucursal, Log
from schemas import EmpleadoCreate, EmpleadoResponse, EmpleadoUpdate

templates = Jinja2Templates(directory="templates")
router = APIRouter()


# ══════════════════════════════════════════════
# EMPLEADOS — API JSON
# ══════════════════════════════════════════════

@router.post("/empleado", response_model=EmpleadoResponse)
def registrar_empleado(emp: EmpleadoCreate):
    db = SessionLocal()
    existe = db.query(Empleado).filter(Empleado.cedula == emp.cedula).first()
    if existe:
        db.close()
        raise HTTPException(status_code=400, detail="Ya existe un empleado con ese número de cédula")
    empleado_nuevo = Empleado(
        cedula=emp.cedula, nombre=emp.nombre, apellido=emp.apellido,
        email=emp.email, contrasena=emp.contrasena,
        departamento=emp.departamento, rol=emp.rol
    )
    db.add(empleado_nuevo)
    db.commit()
    db.refresh(empleado_nuevo)
    db.close()
    return empleado_nuevo


@router.get("/empleado", response_model=List[EmpleadoResponse])
def listar_empleados():
    db = SessionLocal()
    empleados = db.query(Empleado).all()
    db.close()
    return empleados


@router.put("/empleado/{cedula_empleado}", response_model=EmpleadoResponse)
def actualizar_empleado(cedula_empleado: str, datos: EmpleadoUpdate):
    db = SessionLocal()
    empleado = db.query(Empleado).filter(Empleado.cedula == cedula_empleado).first()
    if not empleado:
        db.close()
        raise HTTPException(status_code=404, detail="Empleado no registrado")
    empleado.nombre = datos.nombre
    empleado.apellido = datos.apellido
    empleado.email = datos.email
    empleado.contrasena = datos.contrasena
    empleado.departamento = datos.departamento
    db.commit()
    db.refresh(empleado)
    db.close()
    return empleado


@router.delete("/empleado/{cedula_empleado}")
def eliminar_empleado(cedula_empleado: str):
    db = SessionLocal()
    empleado = db.query(Empleado).filter(Empleado.cedula == cedula_empleado).first()
    if not empleado:
        db.close()
        raise HTTPException(status_code=404, detail="Empleado no registrado")
    empleado.activo = False
    db.commit()
    db.close()
    return {"mensaje": "Empleado dado de baja"}


@router.get("/empleado/{cedula_empleado}", response_model=EmpleadoResponse)
def buscar_empleado(cedula_empleado: str):
    db = SessionLocal()
    empleado = db.query(Empleado).filter(Empleado.cedula == cedula_empleado).first()
    db.close()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no registrado")
    return empleado


# ══════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════

@router.get("/dashboard/administrador")
def dashboard_administrador(request: Request, cedula: str = Cookie(None)):
    if not cedula:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()
    usuario_logueado = db.query(Empleado).filter(Empleado.cedula == cedula).first()
    empleados   = db.query(Empleado).all()
    asistencias = db.query(Asistencia).options(
        joinedload(Asistencia.empleado),
        joinedload(Asistencia.sucursal)
    ).all()
    sucursales  = db.query(Sucursal).all()

    response = templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "request": request,
            "empleados": empleados,
            "asistencias": asistencias,
            "sucursales": sucursales,
            "usuario": usuario_logueado
        }
    )
    db.close()
    return response


# ══════════════════════════════════════════════
# EMPLEADOS — ENDPOINTS WEB (formularios HTML)
# ══════════════════════════════════════════════

@router.post("/web/empleado/registrar")
def registrar_empleado_web(
    cedula: str = Form(...), nombre: str = Form(...), apellido: str = Form(...),
    email: str = Form(...), contrasena: str = Form(...),
    departamento: str = Form(...), rol: str = Form(...)
):
    db = SessionLocal()
    if db.query(Empleado).filter(Empleado.cedula == cedula).first():
        db.close()
        raise HTTPException(status_code=400, detail="Ya existe un empleado con ese número de cédula")
    if db.query(Empleado).filter(Empleado.email == email).first():
        db.close()
        raise HTTPException(status_code=400, detail="Ya existe un empleado con ese correo electrónico")
    db.add(Empleado(cedula=cedula, nombre=nombre, apellido=apellido,
                    email=email, contrasena=contrasena,
                    departamento=departamento, rol=rol))
    db.commit()
    db.close()
    return RedirectResponse(url="/dashboard/administrador", status_code=303)


@router.post("/web/empleado/editar/{cedula}")
def editar_empleado_web(
    cedula: str,
    nombre: str = Form(...), apellido: str = Form(...),
    email: str = Form(...), contrasena: str = Form(...),
    departamento: str = Form(...), rol: str = Form(...)
):
    db = SessionLocal()
    empleado = db.query(Empleado).filter(Empleado.cedula == cedula).first()
    if not empleado:
        db.close()
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    empleado.nombre = nombre
    empleado.apellido = apellido
    empleado.email = email
    empleado.contrasena = contrasena
    empleado.departamento = departamento
    empleado.rol = rol
    db.commit()
    db.close()
    return RedirectResponse(url="/dashboard/administrador", status_code=303)


@router.get("/web/empleado/baja/{cedula}")
def dar_baja_empleado(cedula: str, cedula_cookie: str = Cookie(None)):
    """Desactiva al empleado en lugar de eliminarlo."""
    db = SessionLocal()
    empleado = db.query(Empleado).filter(Empleado.cedula == cedula).first()
    if not empleado:
        db.close()
        raise HTTPException(status_code=404, detail="Empleado no registrado")
    empleado.activo = False
    log = Log(
        accion="baja_empleado",
        detalle=f"Empleado {empleado.nombre} {empleado.apellido} ({cedula}) dado de baja",
        cedula_empleado=cedula_cookie or cedula
    )
    db.add(log)
    db.commit()
    db.close()
    return RedirectResponse(url="/dashboard/administrador", status_code=303)


@router.get("/web/empleado/reactivar/{cedula}")
def reactivar_empleado(cedula: str, cedula_cookie: str = Cookie(None)):
    """Reactiva un empleado dado de baja."""
    db = SessionLocal()
    empleado = db.query(Empleado).filter(Empleado.cedula == cedula).first()
    if not empleado:
        db.close()
        raise HTTPException(status_code=404, detail="Empleado no registrado")
    empleado.activo = True
    log = Log(
        accion="reactivar_empleado",
        detalle=f"Empleado {empleado.nombre} {empleado.apellido} ({cedula}) reactivado",
        cedula_empleado=cedula_cookie or cedula
    )
    db.add(log)
    db.commit()
    db.close()
    return RedirectResponse(url="/dashboard/administrador", status_code=303)


# ══════════════════════════════════════════════
# SUCURSALES — ENDPOINTS WEB
# ══════════════════════════════════════════════

@router.post("/web/sucursal/registrar")
def registrar_sucursal(nombre: str = Form(...)):
    db = SessionLocal()
    if db.query(Sucursal).filter(Sucursal.nombre == nombre).first():
        db.close()
        raise HTTPException(status_code=400, detail="Ya existe una sucursal con ese nombre")
    db.add(Sucursal(nombre=nombre))
    db.commit()
    db.close()
    return RedirectResponse(url="/dashboard/administrador", status_code=303)


@router.post("/web/sucursal/editar/{sucursal_id}")
def editar_sucursal(sucursal_id: int, nombre: str = Form(...)):
    db = SessionLocal()
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        db.close()
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    sucursal.nombre = nombre
    db.commit()
    db.close()
    return RedirectResponse(url="/dashboard/administrador", status_code=303)


@router.get("/web/sucursal/desactivar/{sucursal_id}")
def desactivar_sucursal(sucursal_id: int):
    db = SessionLocal()
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        db.close()
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    sucursal.activo = False
    db.commit()
    db.close()
    return RedirectResponse(url="/dashboard/administrador", status_code=303)


@router.get("/web/sucursal/activar/{sucursal_id}")
def activar_sucursal(sucursal_id: int):
    db = SessionLocal()
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        db.close()
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    sucursal.activo = True
    db.commit()
    db.close()
    return RedirectResponse(url="/dashboard/administrador", status_code=303)


# ══════════════════════════════════════════════
# ASISTENCIAS — ENDPOINTS WEB
# ══════════════════════════════════════════════

@router.post("/web/asistencia/editar/{asistencia_id}")
def editar_asistencia_web(
    asistencia_id: int,
    cedula_cookie: str = Cookie(None),
    fecha_entrada_1: str = Form(None), hora_entrada_1: str = Form(None),
    fecha_salida_1:  str = Form(None), hora_salida_1:  str = Form(None),
    fecha_entrada_2: str = Form(None), hora_entrada_2: str = Form(None),
    fecha_salida_2:  str = Form(None), hora_salida_2:  str = Form(None),
    sucursal_id: str = Form(None)
):
    def parse_date(s):
        try: return datetime.strptime(s, "%Y-%m-%d").date() if s else None
        except: return None

    def parse_time(s):
        try: return datetime.strptime(s, "%H:%M").time() if s else None
        except: return None

    db = SessionLocal()
    reg = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if not reg:
        db.close()
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # Guardar estado anterior en log
    detalle_anterior = (
        f"T1: {reg.fecha_entrada_1} {reg.hora_entrada_1} → {reg.fecha_salida_1} {reg.hora_salida_1} | "
        f"T2: {reg.fecha_entrada_2} {reg.hora_entrada_2} → {reg.fecha_salida_2} {reg.hora_salida_2} | "
        f"Sucursal: {reg.sucursal_id}"
    )
    db.add(Log(
        accion="edicion_asistencia",
        detalle=f"Asistencia #{asistencia_id} editada. Antes: {detalle_anterior}",
        cedula_empleado=cedula_cookie or reg.cedula_empleado
    ))

    reg.fecha_entrada_1 = parse_date(fecha_entrada_1)
    reg.hora_entrada_1  = parse_time(hora_entrada_1)
    reg.fecha_salida_1  = parse_date(fecha_salida_1)
    reg.hora_salida_1   = parse_time(hora_salida_1)
    reg.fecha_entrada_2 = parse_date(fecha_entrada_2)
    reg.hora_entrada_2  = parse_time(hora_entrada_2)
    reg.fecha_salida_2  = parse_date(fecha_salida_2)
    reg.hora_salida_2   = parse_time(hora_salida_2)
    if sucursal_id:
        reg.sucursal_id = int(sucursal_id)

    db.commit()
    db.close()
    return RedirectResponse(url="/dashboard/administrador", status_code=303)


@router.get("/web/asistencia/eliminar/{asistencia_id}")
def eliminar_asistencia_web(asistencia_id: int, cedula_cookie: str = Cookie(None)):
    db = SessionLocal()
    reg = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if not reg:
        db.close()
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    db.add(Log(
        accion="eliminacion_asistencia",
        detalle=f"Asistencia #{asistencia_id} de {reg.cedula_empleado} eliminada",
        cedula_empleado=cedula_cookie or reg.cedula_empleado
    ))
    db.delete(reg)
    db.commit()
    db.close()
    return RedirectResponse(url="/dashboard/administrador", status_code=303)


@router.get("/api/asistencia/historial/{asistencia_id}")
def historial_asistencia(asistencia_id: int):
    """Devuelve logs de un registro de asistencia en JSON para el modal."""
    db = SessionLocal()
    logs = db.query(Log).filter(
        Log.detalle.like(f"%#{asistencia_id}%")
    ).order_by(Log.fecha_hora.desc()).all()
    db.close()
    return JSONResponse(content=[
        {
            "fecha_hora": l.fecha_hora.strftime("%d/%m/%Y %H:%M:%S"),
            "accion": l.accion,
            "detalle": l.detalle,
            "cedula_empleado": l.cedula_empleado
        } for l in logs
    ])

@router.get("/exportar/asistencia/excel/admin")
def exportar_asistencia_excel_admin(cedula: str = Cookie(None)):
    """Exporta TODAS las asistencias a Excel — solo para admin."""
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from fastapi.responses import StreamingResponse
    import io

    if not cedula:
        raise HTTPException(status_code=401, detail="No autorizado")

    db = SessionLocal()
    registros = (
        db.query(Asistencia)
        .options(joinedload(Asistencia.empleado), joinedload(Asistencia.sucursal))
        .order_by(Asistencia.fecha_entrada_1.desc())
        .all()
    )
    db.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Control de Asistencia"

    # Estilos
    fuente_titulo  = Font(name="Calibri", bold=True, size=14, color="FFFFFF")
    fuente_header  = Font(name="Calibri", bold=True, size=10, color="FFFFFF")
    fuente_info    = Font(name="Calibri", size=10)
    fuente_bold    = Font(name="Calibri", bold=True, size=10)
    relleno_titulo = PatternFill("solid", fgColor="0A1628")
    relleno_header = PatternFill("solid", fgColor="2E75B6")
    relleno_info   = PatternFill("solid", fgColor="D9E1F2")
    relleno_alt    = PatternFill("solid", fgColor="EEF2F8")
    centro         = Alignment(horizontal="center", vertical="center", wrap_text=True)
    izquierda      = Alignment(horizontal="left",   vertical="center")

    # Fila 1: Título
    ws.merge_cells("A1:L1")
    ws["A1"] = "REPORTE GENERAL DE ASISTENCIA — EMPRESA XYZ"
    ws["A1"].font      = fuente_titulo
    ws["A1"].fill      = relleno_titulo
    ws["A1"].alignment = centro
    ws.row_dimensions[1].height = 30

    # Fila 2: Fecha de generación
    ws.merge_cells("A2:L2")
    ws["A2"] = f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws["A2"].font      = fuente_bold
    ws["A2"].fill      = relleno_info
    ws["A2"].alignment = izquierda

    # Fila 4: Encabezados
    headers = [
        "ID", "Empleado", "Cédula", "Sucursal",
        "F. Entrada T1", "H. Entrada T1", "F. Salida T1", "H. Salida T1",
        "F. Entrada T2", "H. Entrada T2", "F. Salida T2", "H. Salida T2"
    ]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col, value=h)
        cell.font      = fuente_header
        cell.fill      = relleno_header
        cell.alignment = centro
    ws.row_dimensions[4].height = 28

    def fmt_date(d): return d.strftime("%d/%m/%Y") if d else "—"
    def fmt_time(t): return t.strftime("%H:%M:%S") if t else "—"

    for fila, r in enumerate(registros, start=5):
        nombre_completo = f"{r.empleado.nombre} {r.empleado.apellido}" if r.empleado else "—"
        sucursal_nombre = r.sucursal.nombre if r.sucursal else "—"
        datos = [
            r.id, nombre_completo, r.cedula_empleado, sucursal_nombre,
            fmt_date(r.fecha_entrada_1), fmt_time(r.hora_entrada_1),
            fmt_date(r.fecha_salida_1),  fmt_time(r.hora_salida_1),
            fmt_date(r.fecha_entrada_2), fmt_time(r.hora_entrada_2),
            fmt_date(r.fecha_salida_2),  fmt_time(r.hora_salida_2),
        ]
        relleno_fila = relleno_alt if fila % 2 == 0 else None
        for col, valor in enumerate(datos, start=1):
            cell = ws.cell(row=fila, column=col, value=valor)
            cell.font      = fuente_info
            cell.alignment = centro
            if relleno_fila:
                cell.fill = relleno_fila

    # Anchos de columnas
    anchos = [5, 22, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13]
    for col, ancho in enumerate(anchos, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = ancho

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    nombre_archivo = f"asistencia_general_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"}
    )