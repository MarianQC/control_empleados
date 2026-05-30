# Sistema de Control de Empleados
**Empresa XYZ** — Proyecto Final | Programación usando Framework

---

## Descripción
Aplicación web desarrollada con Python y FastAPI para gestionar el control de asistencia del personal de una empresa. Permite registrar empleados, controlar horarios de entrada y salida por turnos, gestionar sucursales y mantener un historial de cambios mediante logs.

---

## Tecnologías utilizadas
- **Python** — Lenguaje principal
- **FastAPI** — Framework web
- **SQLAlchemy** — ORM para manejo de base de datos
- **SQLite** — Base de datos relacional
- **Pydantic** — Validación de datos
- **Jinja2** — Plantillas HTML
- **Bootstrap 5** — Interfaz de usuario
- **Brevo (API externa)** — Envío de correos para recuperación de contraseña
- **openpyxl** — Exportación de reportes en Excel

---

## Requisitos previos
- Python 3.10 o superior
- pip

---

## Instalación

1. Clona o descarga el proyecto:
```
git clone <url-del-repositorio>
```

2. Entra a la carpeta del proyecto:
```
cd control_empleados
```

3. Instala las dependencias:
```
pip install -r requirements.txt
```

---

## Ejecución

Desde dentro de la carpeta `control_empleados`, ejecuta:

```
python -m uvicorn main:app --reload
```

O directamente:
```
python main.py
```

Luego abre el navegador en:
```
http://127.0.0.1:8000/login
```

---

## Estructura del proyecto

```
control_empleados/
│
├── main.py                  # Punto de entrada de la aplicación
├── modelos.py               # Entidades de la base de datos (SQLAlchemy)
├── schemas.py               # Validaciones de datos (Pydantic)
├── requirements.txt         # Dependencias del proyecto
├── README.md                # Este archivo
│
├── routers/
│   ├── __init__.py
│   ├── auth.py              # Login, logout y recuperación de contraseña
│   ├── administrador.py     # Endpoints del administrador
│   └── empleado.py          # Endpoints del empleado
│
├── templates/
│   ├── base.html            # Plantilla base
│   ├── login.html           # Página de login
│   ├── admin/
│   │   └── dashboard.html   # Dashboard del administrador
│   └── empleado/
│       └── dashboard.html   # Dashboard del empleado
│
└── static/
    └── logo.png             # Logo de la empresa
```

---

## Funcionalidades principales

### Administrador
- Registrar, editar, dar de baja y reactivar empleados
- Gestionar sucursales (crear, editar, activar/desactivar)
- Ver y editar registros de asistencia
- Ver historial de cambios (logs)

### Empleado
- Iniciar sesión de forma segura
- Marcar entrada y salida (hasta 2 turnos por día)
- Seleccionar sucursal al marcar asistencia
- Ver historial de asistencia
- Exportar reporte de asistencia en Excel

### Seguridad
- Autenticación con cookies de sesión
- Verificación de usuario activo al iniciar sesión
- Recuperación de contraseña por correo con código de verificación (API Brevo)
- Confirmación de cédula al marcar asistencia

---

## Base de datos
El archivo `control_empleados.db` se crea automáticamente al ejecutar el proyecto por primera vez.

### Tablas
- **empleados** — Datos del personal
- **sucursales** — Sucursales de la empresa
- **asistencia** — Registros de entrada/salida por turnos
- **logs** — Historial de cambios y acciones del sistema