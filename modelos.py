#Aquí van las entidades de la base de datos. Cada clase representa una tabla.
#  También va la conexión a la base de datos

from sqlalchemy import create_engine, Column, Integer, String, Date, Time, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# CONEXIÓN A LA BASE DE DATOS
DATABASE_URL = "sqlite:///control_empleados.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ─────────────────────────────────────────────
# ENTIDAD: SUCURSAL
# ─────────────────────────────────────────────

class Sucursal(Base):
    __tablename__ = "sucursales"

    id     = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    # activo: True = visible en dropdowns, False = desactivada
    activo = Column(Boolean, default=True, nullable=False)

    asistencias = relationship("Asistencia", back_populates="sucursal")


# ─────────────────────────────────────────────
# ENTIDAD: EMPLEADO
# ─────────────────────────────────────────────

class Empleado(Base):
    __tablename__ = "empleados"

    cedula       = Column(String(10), primary_key=True, index=True)
    nombre       = Column(String, nullable=False)
    apellido     = Column(String, nullable=False)
    email        = Column(String, unique=True, nullable=False)
    contrasena   = Column(String, nullable=False)
    departamento = Column(String, nullable=False)
    rol          = Column(String, nullable=False, default="empleado")
    # activo: False = empleado dado de baja
    activo       = Column(Boolean, default=True, nullable=False)

    asistencias = relationship("Asistencia", back_populates="empleado")
    logs        = relationship("Log", back_populates="empleado")


# ─────────────────────────────────────────────
# ENTIDAD: ASISTENCIA
# ─────────────────────────────────────────────

class Asistencia(Base):
    __tablename__ = "asistencia"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # TURNO 1
    fecha_entrada_1 = Column(Date, nullable=True)
    hora_entrada_1  = Column(Time, nullable=True)
    fecha_salida_1  = Column(Date, nullable=True)
    hora_salida_1   = Column(Time, nullable=True)

    # TURNO 2 (opcional - jornada partida)
    fecha_entrada_2 = Column(Date, nullable=True)
    hora_entrada_2  = Column(Time, nullable=True)
    fecha_salida_2  = Column(Date, nullable=True)
    hora_salida_2   = Column(Time, nullable=True)

    # FK al empleado
    cedula_empleado = Column(String(10), ForeignKey("empleados.cedula"), nullable=False)
    # FK a la sucursal
    sucursal_id     = Column(Integer, ForeignKey("sucursales.id"), nullable=True)

    empleado = relationship("Empleado", back_populates="asistencias")
    sucursal = relationship("Sucursal", back_populates="asistencias")


# ─────────────────────────────────────────────
# ENTIDAD: LOG
# ─────────────────────────────────────────────

class Log(Base):
    __tablename__ = "logs"

    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_hora  = Column(DateTime, default=datetime.now, nullable=False)
    # Tipo: "inicio_sesion", "edicion_asistencia", "baja_empleado", etc.
    accion      = Column(String, nullable=False)
    # Qué había antes y qué quedó después
    detalle     = Column(String, nullable=True)

    cedula_empleado = Column(String(10), ForeignKey("empleados.cedula"), nullable=False)
    empleado        = relationship("Empleado", back_populates="logs")


# CREAR LAS TABLAS EN LA BASE DE DATOS
Base.metadata.create_all(bind=engine)