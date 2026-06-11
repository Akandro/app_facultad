from datetime import date
from sqlmodel import SQLModel, Field
from pydantic import field_validator
import re


# -------------------------
# MODELO DE BASE DE DATOS
# -------------------------
class Alumno(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    nombre: str
    NIF: str
    apellido1: str
    apellido2: str | None = None
    email: str

    direccion: str | None = None
    codigoPostal: str | None = None
    municipio: str | None = None
    provincia: str | None = None

    beca: bool = False
    fechaNacimiento: date

    # -------- VALIDADORES --------
    @field_validator("NIF")
    @classmethod
    def validar_dni(cls, value: str) -> str:
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"

        if not re.match(r"^\d{7,8}[A-Z]$", value):
            raise ValueError("Formato de DNI inválido")

        numero = int(value[:-1])
        if letras[numero % 23] != value[-1]:
            raise ValueError("DNI inválido")

        return value

    @field_validator("email")
    @classmethod
    def validar_email(cls, value: str) -> str:
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron, value):
            raise ValueError("Email inválido")
        return value


# -------------------------
# MODELO DE ENTRADA (POST)
# -------------------------
class AlumnoCreate(SQLModel):
    nombre: str
    NIF: str
    apellido1: str
    apellido2: str | None = None
    email: str

    direccion: str | None = None
    codigoPostal: str | None = None
    municipio: str | None = None
    provincia: str | None = None

    beca: bool = False
    fechaNacimiento: date

