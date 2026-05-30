from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers import administrador, empleado, auth

import os

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), 
          name="static")
app.include_router(auth.router)
app.include_router(administrador.router)
app.include_router(empleado.router)

templates = Jinja2Templates(directory="templates")