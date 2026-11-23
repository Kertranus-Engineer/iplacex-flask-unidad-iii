# Evaluación Unidad III — Programación Web con Flask

Aplicación web con Flask que tiene un menú principal con dos botones. Cada botón lleva a un formulario distinto:

- **Ejercicio 1:** recibe tres notas (10 a 70) y la asistencia (0 a 100 %), muestra el promedio y si el estudiante está **aprobado** (promedio ≥ 40 **y** asistencia ≥ 75 %) o **reprobado**.
- **Ejercicio 2:** recibe tres nombres diferentes y muestra el que tiene **más letras** y cuántas son.

## Cómo ejecutarla (Windows, PowerShell)

Requiere Python 3.10 o superior.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Luego abrir <http://127.0.0.1:5000/> en el navegador. Para detener el servidor: `Ctrl + C`.

## Pruebas automáticas

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_app
```

## Criterios usados cuando el enunciado no dice nada

- **Decimales:** las notas y la asistencia aceptan coma o punto (por ejemplo `55,5` o `55.5`), con hasta 2 decimales. No se aceptan letras, signos ni notación científica.
- **Aprobación:** se compara con el promedio exacto, no con el redondeado. El promedio se muestra con 2 decimales (si el promedio real es menor que 40, nunca se muestra como 40,00).
- **Campos vacíos o inválidos:** se muestra un mensaje de error en el mismo formulario y se conservan los datos escritos.
- **Ejercicio 2:** solo se cuentan **letras** (con tildes y ñ). No se cuentan espacios, guiones, apóstrofes ni números. Los espacios repetidos o al borde se limpian.
- **Nombres repetidos:** deben ser diferentes; `Juan` y `juan ` se consideran el mismo nombre y se rechazan.
- **Empate:** si dos o tres nombres tienen la misma cantidad máxima de letras, se muestran todos.
- Cada nombre debe tener al menos una letra y como máximo 80 caracteres.

## Estructura

```
main.py                  rutas y lógica en Python
templates/               base.html (bloques), index.html, ejercicio1.html,
                         ejercicio2.html, resultado.html, error.html
static/styles.css        estilos (se carga desde base.html)
test_app.py              pruebas automáticas
requirements.txt         dependencias (Flask)
```

Rutas: `/` (menú), `/ejercicio1` y `/ejercicio2` (GET muestra el formulario, POST procesa los datos). Una dirección inexistente muestra una página de error 404.
