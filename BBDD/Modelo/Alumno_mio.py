from datetime import date
from sqlmodel import SQLModel, Field
from pydantic import field_validator

class Alumno(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=255)
    fechaNacimiento: date = Field(nullable=False,index=True)
    NIF: str = Field(max_length=9, unique=True, nullable=False)  # 8 dígitos + letra, único y no nulo
    apellido1: str = Field(max_length=255, nullable=False)
    apellido2: str = Field(max_length=255, nullable=True)  # Puede ser nulo si el alumno no tiene segundo apellido
    email: str = Field(max_length=255, nullable=False, unique=True)  # Correo electrónico único y no nulo
    direccion: str = Field(max_length=255)
    codigoPostal: str = Field(max_length=10)
    municipio: str = Field(max_length=255)
    provincia: str = Field(max_length=255)
    beca: bool = Field(default=False)  # Indica si el alumno tiene beca, por defecto es False
    
    def __str__(self):
        return f"Alumno(id={self.id}, nombre='{self.nombre}', fechaNacimiento={self.fechaNacimiento}, NIF='{self.NIF}', apellido1='{self.apellido1}', apellido2='{self.apellido2}', email='{self.email}', direccion='{self.direccion}', codigoPostal='{self.codigoPostal}', municipio='{self.municipio}', provincia='{self.provincia}', beca={self.beca})"
    def __repr__(self):
        return self.__str__()
    

    @field_validator("NIF") # Valida el campo NIF cada vez que se asigna un valor, se invoca automáticamente al crear o modificar el campo NIF del modelo Alumno    
    @classmethod
    def validar_NIF(clase, valor: str) -> bool:
    # Secuencia oficial de letras (índices del 0 al 22)
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    # Asegurarse de que el número es entero y calcular el resto
        resto = int(valor[:-1]) % 23
    # Retornar la letra correspondiente
        if letras[resto]!=valor[-1].upper():
            raise ValueError(f"NIF inválido: la letra no coincide con el número. Se esperaba '{letras[resto]}', pero se recibió '{valor[-1]}'")
        else:
            print(f"NIF válido: {valor[-1]} coincide con la letra '{letras[resto]}'")
            return True
    # valorar incluir validaciones para cada campo, como por ejemplo:
    # def __init__(self, id: int, nombre: str, fechaNacimiento: date, NIF: str, apellido1: str, apellido2: str, email: str, direccion: str, codigoPostal: str, municipio: str, provincia: str, beca: bool):