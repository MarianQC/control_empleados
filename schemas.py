#Aquí van las validaciones de datos con Pydantic. 
# Cada clase define qué datos se esperan recibir o devolver en los endpoints.

from datetime import date, time
from typing import Optional

from pydantic import BaseModel

class EmpleadoCreate(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    email: str
    contrasena: str
    departamento: str
    rol: str


class EmpleadoUpdate(BaseModel):
    nombre: str
    apellido: str
    email: str
    contrasena: str
    departamento: str
    rol: str  # agregado para poder cambiar el rol desde el modal de editar


class EmpleadoResponse(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    email: str
    departamento: str
    rol: str
    activo: bool  # agregado para ver si el empleado está activo o dado de baja

    class Config:
        from_attributes = True


class AsistenciaResponse(BaseModel):
    id: int
    fecha_entrada_1: Optional[date]
    hora_entrada_1:  Optional[time]
    fecha_salida_1:  Optional[date]
    hora_salida_1:   Optional[time]
    fecha_entrada_2: Optional[date]
    hora_entrada_2:  Optional[time]
    fecha_salida_2:  Optional[date]
    hora_salida_2:   Optional[time]
    cedula_empleado: str
    sucursal_id:     Optional[int]

    class Config:
        from_attributes = True


class SucursalResponse(BaseModel):
    id: int
    nombre: str
    activo: bool

    class Config:
        from_attributes = True


class LogResponse(BaseModel):
    id: int
    fecha_hora: str
    accion: str
    detalle: Optional[str]
    cedula_empleado: str

    class Config:
        from_attributes = True


class Login(BaseModel):
    cedula: str
    contrasena: str