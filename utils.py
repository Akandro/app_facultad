from typing import List
from models import Alumno  # Importamos el modelo para el tipado

def estructurar_respuesta(alumnos: List[Alumno]):
    resultado = []
    for alu in alumnos:
        asignaturas_alumno = []
        for mat in alu.matriculas:
            if mat.assignatura:  
                asignaturas_alumno.append({
                    "idAsignatura": mat.assignatura.idAsignatura,
                    "nombre": mat.assignatura.nombre,
                    "creditos": mat.assignatura.creditos,
                    "nota_obtenida": mat.nota
                })
            
        resultado.append({
            "alumno": f"{alu.nombre} {alu.apellido1} {alu.apellido2 or ''}".strip(),
            "NIF": alu.NIF,
            "email": alu.email,
            "municipio": alu.municipio,
            "provincia": alu.provincia,
            "beca": alu.beca,
            "asignaturas_matriculadas": asignaturas_alumno
        })
    return resultado