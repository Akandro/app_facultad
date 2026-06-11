import enum
from sqlalchemy import Column, String, ForeignKey, Float, Integer, Enum, CHAR, Numeric
from sqlalchemy.orm import relationship
from database import Base


class Alumno(Base):
    __tablename__ = 'alumno'

    idAlumno = Column(String(5), primary_key=True)
    NIF = Column(String(9), unique=True)
    nombre = Column(String(255), nullable=False)
    apellido1 = Column(String(255), nullable=False)
    apellido2 = Column(String(255))
    email = Column(String(50), unique=True)
    direccion = Column(String(100), nullable=False)
    codigoPostal = Column(Integer, nullable=False)
    municipio = Column(String(255), nullable=False)
    provincia = Column(String(255), nullable=False)
    beca = Column(String(2), nullable=False)

    matriculas = relationship("Matricula", back_populates="alumno")


class Asignatura(Base):
    __tablename__ = 'asignatura'

    curso = Column(Numeric(2, 0), nullable=False)
    idAsignatura = Column(CHAR(5), primary_key=True)
    nombre = Column(String(150), unique=True)
    cuatrimestre = Column(Enum('1', '2'))
    creditos = Column(Float, nullable=False)
    caracter = Column(Enum('obligatoria', 'optativa'), nullable=False)
    coordinador = Column(CHAR(5), nullable=False)

    matriculas = relationship("Matricula", back_populates="asignatura")


class Matricula(Base):
    __tablename__ = 'matricula'

    idAlumno = Column(String(5), ForeignKey('alumno.idAlumno'), primary_key=True)
    idAsignatura = Column(CHAR(5), ForeignKey('asignatura.idAsignatura'), primary_key=True)
    nota = Column(Float, nullable=False)

    alumno = relationship("Alumno", back_populates="matriculas")
    asignatura = relationship("Asignatura", back_populates="matriculas")