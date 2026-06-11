import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class AlumnoCreate(BaseModel):
    idAlumno: str = Field(..., min_length=1, max_length=5, description="Código de 5 caracteres")
    NIF: str = Field(..., min_length=9, max_length=9, description="DNI/NIF con formato de 8 números y letra")
    nombre: str = Field(..., min_length=1, max_length=50)
    apellido1: str = Field(..., min_length=1, max_length=50)
    apellido2: Optional[str] = Field(None, max_length=50)
    email: EmailStr = Field(..., description="Email válido del alumno")
    direccion: str = Field(..., min_length=5, max_length=100) 
    codigoPostal: int = Field(..., ge=1000, le=99999, description="Código postal de 5 dígitos") 
    municipio: str = Field(..., min_length=1, max_length=50) 
    provincia: str = Field(..., min_length=1, max_length=50) 
    beca: str = Field(..., min_length=2, max_length=2, description="Código de beca, ej: SI o NO") 

    @field_validator('NIF')
    @classmethod
    def validar_dni_espanol(cls, v: str) -> str:
        dni = v.upper().strip()
        regex = r'^[0-9]{8}[A-Z]$'
        if not re.match(regex, dni):
            raise ValueError("El formato del DNI debe ser de 8 números seguidos de una letra (ej: 12345678Z).")
        
        letras_validas = "TRWAGMYFPDXBNJZSQVHLCKE"
        numero = int(dni[:-1])
        letra_esperada = letras_validas[numero % 23]
        
        if dni[-1] != letra_esperada:
            raise ValueError(f"La letra del DNI no es correcta. Para el número {numero} corresponde la letra '{letra_esperada}'.")
            
        return dni

    @field_validator('email')
    @classmethod
    def validar_email_ucm(cls, v: str) -> str:
        email = v.lower().strip()
        if not email.endswith("@ucm.com"):
            raise ValueError("El correo electrónico debe pertenecer obligatoriamente al dominio '@ucm.com'.")
        return email