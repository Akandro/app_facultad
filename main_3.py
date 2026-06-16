from fastapi import FastAPI, HTTPException, Depends, Request, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from database import get_db, Base, engine
import models 
from models import Alumno, Matricula
from schemas import AlumnoCreate
from utils import estructurar_respuesta

# Migración automática (ideal solo para desarrollo)
print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)
print("¡Tablas procesadas con éxito!")

app = FastAPI(title="Consulta de Facultad - Buscadores Independientes")
templates = Jinja2Templates(directory="templates")


# --- RUTAS DE RENDERIZADO HTML (VISTAS) ---

@app.get("/", response_class=HTMLResponse)
async def bienvenida(request: Request):
    """
    Ruta principal que carga la interfaz de usuario en home.html
    """
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"name": "Bienvenido a la Consulta de Facultad"}
    )

@app.get("/alumnos/{alumno_id}", response_class=HTMLResponse)
def obtener_alumno_por_id(alumno_id: str, request: Request, db: Session = Depends(get_db)):
    alumno = db.query(models.Alumno)\
        .options(joinedload(models.Alumno.matriculas).joinedload(models.Matricula.asignatura))\
        .filter(models.Alumno.idAlumno == alumno_id)\
        .first()
    
    if alumno is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    return templates.TemplateResponse(
        request=request,
        name="alumno.html", 
        context={"alumno": alumno}
    )

@app.get("/alumnos-vista", response_class=HTMLResponse)
async def listar_alumnos_html(request: Request, db: Session = Depends(get_db)):
    alumnos = db.query(models.Alumno)\
        .options(joinedload(models.Alumno.matriculas).joinedload(models.Matricula.asignatura))\
        .all()
    
    return templates.TemplateResponse(
        request=request,
        name="lista_alumnos.html",
        context={"alumnos": alumnos}
    )


# --- ENDPOINTS DE BÚSQUEDA (API JSON) ---

@app.get("/buscar/por-dni/{dni}")
def buscar_por_dni(dni: str, db: Session = Depends(get_db)):
    dni_clean = dni.upper().strip()
    alumno = db.query(Alumno)\
               .options(joinedload(Alumno.matriculas).joinedload(Matricula.asignatura))\
               .filter(Alumno.NIF == dni_clean)\
               .first()
               
    if not alumno:
        raise HTTPException(status_code=404, detail="No se encontró ningún alumno con ese DNI/NIF.")
    return estructurar_respuesta([alumno])


@app.get("/buscar/por-email/{email}")
def buscar_por_email(email: str, db: Session = Depends(get_db)):
    email_clean = email.lower().strip()
    alumno = db.query(Alumno)\
               .options(joinedload(Alumno.matriculas).joinedload(Matricula.asignatura))\
               .filter(Alumno.email == email_clean)\
               .first()
               
    if not alumno:
        raise HTTPException(status_code=404, detail="No se encontró ningún alumno con ese Email.")
    return estructurar_respuesta([alumno])


@app.get("/buscar/por-nombre-y-apellido")
def buscar_por_nombre_y_apellido(nombre: str, apellido: str, db: Session = Depends(get_db)):
    nombre_clean = nombre.strip()
    apellido_clean = apellido.strip()
    
    alumnos = db.query(Alumno)\
               .options(joinedload(Alumno.matriculas).joinedload(Matricula.asignatura))\
               .filter(
                   and_(
                       Alumno.nombre.ilike(f"%{nombre_clean}%"),
                       (Alumno.apellido1.ilike(f"%{apellido_clean}%")) | (Alumno.apellido2.ilike(f"%{apellido_clean}%"))
                   )
               ).all()
        
    if not alumnos:
        raise HTTPException(
            status_code=400, 
            detail=f"No se encontró ningún alumno llamado '{nombre_clean}' con el apellido '{apellido_clean}'."
        )
    return estructurar_respuesta(alumnos)


# EJERCICIO 1: BUSCADOR POR CRITERIO DE ESTAR O NO BECADOS ("si" / "no" en MariaDB)
@app.get("/alumnos-por-beca-vista", response_class=HTMLResponse)
async def listar_alumnos_por_beca_html(becado: bool, request: Request, db: Session = Depends(get_db)):
    """
    Filtra los alumnos por beca ('si'/'no') y renderiza la plantilla HTML de la lista.
    """
    # Conversión para tu base de datos MariaDB
    valor_beca_bd = "si" if becado else "no"
    
    alumnos = db.query(models.Alumno)\
        .options(joinedload(models.Alumno.matriculas).joinedload(models.Matricula.asignatura))\
        .filter(models.Alumno.beca == valor_beca_bd)\
        .all()
        
    # Reutiliza tu plantilla 'lista_alumnos.html' pasándole los alumnos filtrados
    return templates.TemplateResponse(
        request=request,
        name="lista_alumnos.html",
        context={"alumnos": alumnos}
    )


# --- ENDPOINT DE CREACIÓN ---

@app.post("/alumnos", status_code=201)
def crear_alumno(alumno_in: AlumnoCreate, db: Session = Depends(get_db)):
    dni_clean = alumno_in.NIF.upper().strip()
    email_clean = alumno_in.email.lower().strip()

    if db.query(Alumno).filter(Alumno.idAlumno == alumno_in.idAlumno).first():
        raise HTTPException(status_code=400, detail=f"El idAlumno '{alumno_in.idAlumno}' ya está registrado.")

    if db.query(Alumno).filter(Alumno.NIF == dni_clean).first():
        raise HTTPException(status_code=400, detail=f"El DNI/NIF '{dni_clean}' ya pertenece a otro alumno.")
        
    if db.query(Alumno).filter(Alumno.email == email_clean).first():
        raise HTTPException(status_code=400, detail=f"El email '{email_clean}' ya está registrado.")

    nuevo_alumno = Alumno(
        idAlumno=alumno_in.idAlumno,
        NIF=dni_clean,
        nombre=alumno_in.nombre.strip(),
        apellido1=alumno_in.apellido1.strip(),
        apellido2=alumno_in.apellido2.strip() if alumno_in.apellido2 else None,
        email=email_clean,
        direccion=alumno_in.direccion,
        codigoPostal=alumno_in.codigoPostal,
        municipio=alumno_in.municipio,  
        provincia=alumno_in.provincia,  
        beca=alumno_in.beca              
    )
    
    try:
        db.add(nuevo_alumno)
        db.commit()
        db.refresh(nuevo_alumno)
    except Exception as e:
        db.rollback()
        print(f"❌ ERROR REAL EN DB: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno en la base de datos.")

    return {
        "mensaje": "Alumno registrado exitosamente.",
        "idAlumno": nuevo_alumno.idAlumno,
        "nombre_completo": f"{nuevo_alumno.nombre} {nuevo_alumno.apellido1} {nuevo_alumno.apellido2 or ''}".strip()
    }