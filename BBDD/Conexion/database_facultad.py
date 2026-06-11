import os 
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import and_, create_engine, Column, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload, Session
from dotenv import load_dotenv

# 1. CONEXIÓN A BASE DE DATOS
load_dotenv()

USER = os.getenv('USER_DB')
PASSWORD = os.getenv('PASSWORD_DB')
HOST = os.getenv('HOST_DB')
PORT = os.getenv('PORT_DB')
NAME = os.getenv('NAME_DB')

DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 2. MODELOS (Idénticos a los tuyos)
class Alumno(Base):
    __tablename__ = 'alumno'
    
    idAlumno = Column(String(5), primary_key=True)
    NIF = Column(String(9), unique=True, nullable=True)
    nombre = Column(String)
    apellido1 = Column(String, nullable=False)
    apellido2 = Column(String, nullable=True)
    email = Column(String(50), unique=True, nullable=True)
    
    matriculas = relationship("Matricula", back_populates="alumno")


class Asignatura(Base):
    __tablename__ = 'asignatura'
    
    idAsignatura = Column(String(5), primary_key=True)
    nombre = Column(String(150), unique=True, nullable=True)
    creditos = Column(Float, nullable=False)


class Matricula(Base):
    __tablename__ = 'matricula'
    
    idAlumno = Column(String(5), ForeignKey('alumno.idAlumno'), primary_key=True)
    idAsignatura = Column(String(5), ForeignKey('asignatura.idAsignatura'), primary_key=True)
    nota = Column(Float, nullable=False)
    
    alumno = relationship("Alumno", back_populates="matriculas")
    asignatura = relationship("Asignatura")


# 3. INSTANCIA DE FASTAPI Y DEPENDENCIA DE BD
app = FastAPI(title="Consulta de Facultad - Buscadores Independientes")

# Dependencia para manejar la sesión de la BD de forma automática y segura
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FUNCIÓN AUXILIAR PARA DAR FORMATO LIMPIO AL JSON
def estructurar_respuesta(alumnos: List[Alumno]):
    resultado = []
    for alu in alumnos:
        asignaturas_alumno = []
        for mat in alu.matriculas:
            # Evitamos errores si alguna relación viene vacía por error en BD
            if mat.asignatura:
                asignaturas_alumno.append({
                    "idAsignatura": mat.asignatura.idAsignatura,
                    "nombre": mat.asignatura.nombre,
                    "creditos": mat.asignatura.creditos,
                    "nota_obtenida": mat.nota
                })
            
        resultado.append({
            "alumno": f"{alu.nombre} {alu.apellido1} {alu.apellido2 or ''}".strip(),
            "NIF": alu.NIF,
            "email": alu.email,
            "asignaturas_matriculadas": asignaturas_alumno
        })
    return resultado


# 4. BUSCADORES OPTIMIZADOS (Usando joinedload para rendimiento)

@app.get("/buscar/por-dni/{dni}")
def buscar_por_dni(dni: str, db: Session = Depends(get_db)):
    # joinedload carga el alumno, sus matriculas y las asignaturas en UNA SOLA consulta SQL
    alumno = db.query(Alumno)\
               .options(joinedload(Alumno.matriculas).joinedload(Matricula.asignatura))\
               .filter(Alumno.NIF == dni)\
               .first()
               
    if not alumno:
        raise HTTPException(status_code=404, detail="No se encontró ningún alumno con ese DNI/NIF.")
    return estructurar_respuesta([alumno])


@app.get("/buscar/por-email/{email}")
def buscar_por_email(email: str, db: Session = Depends(get_db)):
    alumno = db.query(Alumno)\
               .options(joinedload(Alumno.matriculas).joinedload(Matricula.asignatura))\
               .filter(Alumno.email == email)\
               .first()
               
    if not alumno:
        raise HTTPException(status_code=404, detail="No se encontró ningún alumno con ese Email.")
    return estructurar_respuesta([alumno])


@app.get("/buscar/por-nombre-y-apellido")
def buscar_por_nombre_y_apellido(nombre: str, apellido: str, db: Session = Depends(get_db)):
    alumnos = db.query(Alumno)\
                .options(joinedload(Alumno.matriculas).joinedload(Matricula.asignatura))\
                .filter(
                    and_(
                        Alumno.nombre.like(f"%{nombre}%"),
                        (Alumno.apellido1.like(f"%{apellido}%")) | (Alumno.apellido2.like(f"%{apellido}%"))
                    )
                ).all()
        
    if not alumnos:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontró ningún alumno llamado '{nombre}' con el apellido '{apellido}'."
        )
        
    return estructurar_respuesta(alumnos)