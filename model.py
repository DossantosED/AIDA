import json
import re
from collections import Counter

def cargar_preguntas_respuestas():
    with open('dataset.json', 'r') as archivo:
        data = json.load(archivo)
        return data['patrones']

def palabras_clave(texto):
    palabras = re.findall(r'\w+', texto.lower())
    return Counter(palabras)

def similitud(palabras_entrada, palabras_pregunta):
    puntuacion = sum((palabras_entrada & palabras_pregunta).values())
    return puntuacion

def encontrar_respuesta_mas_probable(preguntas, entrada_usuario):
    palabras_entrada = palabras_clave(entrada_usuario)
    pregunta_mas_probable = None
    puntuacion_maxima = 0

    for pregunta in preguntas:
        palabras_pregunta = palabras_clave(pregunta['pregunta'])
        puntuacion = similitud(palabras_entrada, palabras_pregunta)

        if puntuacion > puntuacion_maxima:
            puntuacion_maxima = puntuacion
            pregunta_mas_probable = pregunta

    if puntuacion_maxima > 0:
        return pregunta_mas_probable['respuesta']
    else:
        return "Lo siento, no entiendo la pregunta. Por favor intenta con otra."
