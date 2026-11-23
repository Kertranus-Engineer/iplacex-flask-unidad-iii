"""Unidad III - Flask.

Ejercicio 1: promedio de tres notas (10 a 70) y asistencia (0 a 100).
Ejercicio 2: nombre con más letras entre tres nombres distintos.
"""
import re
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from flask import Flask, render_template, request

app = Flask(__name__)

NOTA_MIN, NOTA_MAX = 10, 70
PROMEDIO_APROBACION = 40
ASISTENCIA_APROBACION = 75
LARGO_MAXIMO_NOMBRE = 80

# Números con coma o punto decimal (hasta 2 decimales). No acepta signos ni notación científica.
PATRON_NUMERO = re.compile(r'[0-9]{1,3}([.,][0-9]{1,2})?')

CAMPOS_NOTAS = (('nota1', 'Nota 1'), ('nota2', 'Nota 2'), ('nota3', 'Nota 3'))
CAMPOS_NOMBRES = (('nombre1', 'Nombre 1'), ('nombre2', 'Nombre 2'), ('nombre3', 'Nombre 3'))


# ---------------------------------------------------------------- lógica
def parse_numero(texto):
    """Convierte '55', '55,5' o '55.5' en Decimal. Devuelve None si no es un número válido."""
    texto = (texto or '').strip()
    if not PATRON_NUMERO.fullmatch(texto):
        return None
    return Decimal(texto.replace(',', '.'))


def promedio_notas(notas):
    """Promedio con 2 decimales para mostrar.

    Nunca muestra 40,00 si el promedio real es menor que 40 (por ejemplo 39,999).
    """
    exacto = sum(notas) / Decimal(3)
    centesimas = Decimal('0.01')
    mostrado = exacto.quantize(centesimas, rounding=ROUND_HALF_UP)
    if exacto < PROMEDIO_APROBACION <= mostrado:
        mostrado = exacto.quantize(centesimas, rounding=ROUND_DOWN)
    return mostrado


def esta_aprobado(notas, asistencia):
    """Aprobado solo si promedio >= 40 Y asistencia >= 75 (comparación exacta, sin redondeos)."""
    promedio_suficiente = sum(notas) >= PROMEDIO_APROBACION * 3
    return promedio_suficiente and asistencia >= ASISTENCIA_APROBACION


def cantidad_letras(nombre):
    """Cuenta solo letras (con tildes y ñ); no cuenta espacios, guiones, apóstrofes ni números."""
    return sum(caracter.isalpha() for caracter in nombre)


def normalizar_nombre(texto):
    """Quita espacios al inicio y al final y reduce los espacios repetidos a uno solo."""
    return ' '.join((texto or '').split())


def clave_comparacion(nombre):
    """Dos nombres son el mismo si solo difieren en mayúsculas o espacios ('Juan' = 'JUAN ' = 'ju an')."""
    return ''.join(nombre.split()).casefold()


def unir_nombres(nombres):
    """['A', 'B', 'C'] -> 'A, B y C'."""
    if len(nombres) <= 1:
        return ''.join(nombres)
    return ', '.join(nombres[:-1]) + ' y ' + nombres[-1]


def formatear(numero):
    """Muestra el número con coma decimal, como se escribe en Chile."""
    return str(numero).replace('.', ',')


# ---------------------------------------------------------------- rutas
@app.route('/')
def inicio():
    return render_template('index.html')


@app.route('/ejercicio1', methods=['GET', 'POST'])
def ejercicio1():
    if request.method == 'GET':
        return render_template('ejercicio1.html', datos={}, error=None, campo_error=None)

    campos = CAMPOS_NOTAS + (('asistencia', 'Asistencia'),)
    datos = {campo: request.form.get(campo, '').strip() for campo, _ in campos}

    valores = {}
    for campo, etiqueta in campos:
        texto = datos[campo]
        minimo, maximo = (0, 100) if campo == 'asistencia' else (NOTA_MIN, NOTA_MAX)
        numero = parse_numero(texto)
        if not texto:
            error = 'Completa todos los campos.'
        elif numero is None:
            error = f'{etiqueta}: escribe un número válido, por ejemplo 55 o 55,5.'
        elif not minimo <= numero <= maximo:
            error = f'{etiqueta} debe estar entre {minimo} y {maximo}.'
        else:
            valores[campo] = numero
            continue
        return render_template('ejercicio1.html', datos=datos, error=error, campo_error=campo), 400

    notas = [valores[campo] for campo, _ in CAMPOS_NOTAS]
    asistencia = valores['asistencia']
    return render_template(
        'resultado.html', tipo='notas',
        promedio=formatear(promedio_notas(notas)),
        asistencia=formatear(asistencia),
        aprobado=esta_aprobado(notas, asistencia),
    )


@app.route('/ejercicio2', methods=['GET', 'POST'])
def ejercicio2():
    if request.method == 'GET':
        return render_template('ejercicio2.html', datos={}, error=None, campo_error=None)

    datos = {campo: normalizar_nombre(request.form.get(campo)) for campo, _ in CAMPOS_NOMBRES}

    for campo, etiqueta in CAMPOS_NOMBRES:
        nombre = datos[campo]
        if not nombre:
            error = 'Completa los tres nombres.'
        elif cantidad_letras(nombre) == 0:
            error = f'{etiqueta} debe tener al menos una letra.'
        elif len(nombre) > LARGO_MAXIMO_NOMBRE:
            error = f'{etiqueta} puede tener como máximo {LARGO_MAXIMO_NOMBRE} caracteres.'
        else:
            continue
        return render_template('ejercicio2.html', datos=datos, error=error, campo_error=campo), 400

    nombres = [datos[campo] for campo, _ in CAMPOS_NOMBRES]
    if len({clave_comparacion(nombre) for nombre in nombres}) != 3:
        return render_template('ejercicio2.html', datos=datos, campo_error=None,
                               error='Los tres nombres deben ser diferentes.'), 400

    letras = [cantidad_letras(nombre) for nombre in nombres]
    maximo = max(letras)
    ganadores = [nombre for nombre, cantidad in zip(nombres, letras) if cantidad == maximo]
    return render_template(
        'resultado.html', tipo='nombres',
        ganadores=unir_nombres(ganadores), hay_empate=len(ganadores) > 1,
        max_letras=maximo, detalle=list(zip(nombres, letras)),
    )


@app.errorhandler(404)
@app.errorhandler(405)
def pagina_no_disponible(error):
    return render_template('error.html', codigo=error.code), error.code


if __name__ == '__main__':
    # Servidor de desarrollo, solo para uso local.
    app.run(host='127.0.0.1', port=5000, debug=False)
