"""Pruebas automatizadas de la aplicación (cliente de pruebas de Flask).

Ejecutar:  python -m unittest -v test_app
"""
import unittest
from decimal import Decimal

from main import (app, cantidad_letras, esta_aprobado, parse_numero, promedio_notas,
                  unir_nombres)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def ejercicio1(self, n1, n2, n3, asistencia):
        return self.client.post('/ejercicio1', data={
            'nota1': n1, 'nota2': n2, 'nota3': n3, 'asistencia': asistencia})

    def ejercicio2(self, a, b, c):
        return self.client.post('/ejercicio2', data={'nombre1': a, 'nombre2': b, 'nombre3': c})


class RutasTest(BaseTest):
    def test_paginas_get(self):
        for ruta in ('/', '/ejercicio1', '/ejercicio2'):
            self.assertEqual(self.client.get(ruta).status_code, 200, ruta)

    def test_menu_tiene_dos_botones(self):
        html = self.client.get('/').get_data(as_text=True)
        self.assertIn('href="/ejercicio1"', html)
        self.assertIn('href="/ejercicio2"', html)

    def test_formularios_tienen_boton_volver_y_enviar(self):
        for ruta in ('/ejercicio1', '/ejercicio2'):
            html = self.client.get(ruta).get_data(as_text=True)
            self.assertIn('href="/"', html)
            self.assertIn('method="post"', html)
            self.assertIn('type="submit"', html)

    def test_css_se_carga_desde_static(self):
        self.assertIn('/static/styles.css', self.client.get('/').get_data(as_text=True))
        resp = self.client.get('/static/styles.css')
        self.assertEqual(resp.status_code, 200)
        resp.close()

    def test_ruta_inexistente_404(self):
        resp = self.client.get('/no-existe')
        self.assertEqual(resp.status_code, 404)
        self.assertIn('Página no encontrada', resp.get_data(as_text=True))

    def test_metodo_no_permitido_405(self):
        self.assertEqual(self.client.post('/').status_code, 405)
        self.assertEqual(self.client.put('/ejercicio1').status_code, 405)


class Ejercicio1Test(BaseTest):
    def assertAprobado(self, resp):
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('APROBADO', html)
        self.assertNotIn('REPROBADO', html)

    def assertReprobado(self, resp):
        self.assertEqual(resp.status_code, 200)
        self.assertIn('REPROBADO', resp.get_data(as_text=True))

    def assertInvalido(self, resp, texto=None):
        self.assertEqual(resp.status_code, 400)
        html = resp.get_data(as_text=True)
        self.assertIn('role="alert"', html)
        self.assertNotIn('APROBADO', html)
        if texto:
            self.assertIn(texto, html)

    def test_aprobado_en_el_limite(self):
        resp = self.ejercicio1('40', '40', '40', '75')
        self.assertAprobado(resp)
        self.assertIn('40,00', resp.get_data(as_text=True))

    def test_reprobado_por_notas(self):
        self.assertReprobado(self.ejercicio1('39', '39', '39', '100'))

    def test_reprobado_por_asistencia(self):
        self.assertReprobado(self.ejercicio1('70', '70', '70', '74'))

    def test_reprobado_por_asistencia_decimal(self):
        self.assertReprobado(self.ejercicio1('70', '70', '70', '74,9'))

    def test_reprobado_por_ambos(self):
        self.assertReprobado(self.ejercicio1('10', '10', '10', '0'))

    def test_aprobado_con_notas_distintas(self):
        resp = self.ejercicio1('55', '65', '45', '86')   # ejemplo del enunciado
        self.assertAprobado(resp)
        self.assertIn('55,00', resp.get_data(as_text=True))

    def test_promedio_sobre_40_con_una_nota_baja(self):
        self.assertAprobado(self.ejercicio1('70', '70', '10', '80'))   # promedio 50

    def test_limites_validos(self):
        self.assertReprobado(self.ejercicio1('10', '10', '10', '100'))
        self.assertAprobado(self.ejercicio1('70', '70', '70', '100'))
        self.assertReprobado(self.ejercicio1('70', '70', '70', '0'))

    def test_decimales_con_coma_y_punto(self):
        self.assertAprobado(self.ejercicio1('40,5', '40.5', '39,5', '75,0'))

    def test_promedio_justo_bajo_40_no_se_redondea_a_aprobado(self):
        resp = self.ejercicio1('39,99', '40', '40', '100')   # promedio real 39,9966...
        self.assertReprobado(resp)
        self.assertIn('39,99', resp.get_data(as_text=True))
        self.assertNotIn('40,00', resp.get_data(as_text=True))

    def test_notas_fuera_de_rango(self):
        for nota in ('9', '9,99', '71', '70,01', '0', '100'):
            self.assertInvalido(self.ejercicio1(nota, '50', '50', '80'), 'entre 10 y 70')

    def test_asistencia_fuera_de_rango(self):
        for asistencia in ('101', '100,5', '-1'):
            self.assertInvalido(self.ejercicio1('50', '50', '50', asistencia))
        self.assertInvalido(self.ejercicio1('50', '50', '50', '101'), 'entre 0 y 100')

    def test_campos_vacios(self):
        self.assertInvalido(self.ejercicio1('', '50', '50', '80'), 'Completa todos los campos')
        self.assertInvalido(self.ejercicio1('50', '50', '50', ''), 'Completa todos los campos')
        self.assertInvalido(self.ejercicio1('   ', '50', '50', '80'), 'Completa todos los campos')

    def test_formulario_sin_campos(self):
        self.assertInvalido(self.client.post('/ejercicio1', data={}), 'Completa todos los campos')

    def test_entradas_no_numericas(self):
        for texto in ('abc', '5a', '1e1', 'nan', 'inf', '4 0', '--5', '50.', '.5', '1,2,3', '٤٠', '+50'):
            self.assertInvalido(self.ejercicio1(texto, '50', '50', '80'), 'número válido')

    def test_se_conservan_los_datos_al_fallar(self):
        html = self.ejercicio1('9', '55', '60', '88').get_data(as_text=True)
        for valor in ('value="9"', 'value="55"', 'value="60"', 'value="88"'):
            self.assertIn(valor, html)

    def test_no_ejecuta_html_en_los_errores(self):
        html = self.ejercicio1('<script>alert(1)</script>', '50', '50', '80').get_data(as_text=True)
        self.assertNotIn('<script>alert(1)</script>', html)

    def test_funciones_puras(self):
        self.assertEqual(promedio_notas([Decimal('40'), Decimal('40'), Decimal('41')]), Decimal('40.33'))
        self.assertEqual(promedio_notas([Decimal('39.99'), Decimal('40'), Decimal('40')]), Decimal('39.99'))
        self.assertTrue(esta_aprobado([Decimal(40)] * 3, Decimal(75)))
        self.assertFalse(esta_aprobado([Decimal(40)] * 3, Decimal('74.99')))
        self.assertFalse(esta_aprobado([Decimal('39.99'), Decimal(40), Decimal(40)], Decimal(100)))
        self.assertEqual(parse_numero(' 55,5 '), Decimal('55.5'))
        self.assertIsNone(parse_numero(None))


class Ejercicio2Test(BaseTest):
    def assertInvalido(self, resp, texto=None):
        self.assertEqual(resp.status_code, 400)
        html = resp.get_data(as_text=True)
        self.assertIn('role="alert"', html)
        if texto:
            self.assertIn(texto, html)

    def test_ejemplo_del_enunciado(self):
        resp = self.ejercicio2('Felipe', 'Juan', 'Gustavo')
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<strong>Gustavo</strong>', html)
        self.assertIn('<strong>7</strong>', html)

    def test_nombre_corto_y_largo(self):
        html = self.ejercicio2('Al', 'Bo', 'Maximiliano').get_data(as_text=True)
        self.assertIn('<strong>Maximiliano</strong>', html)
        self.assertIn('<strong>11</strong>', html)

    def test_tildes_y_enie(self):
        html = self.ejercicio2('Ana', 'Íñigo', 'Raúl').get_data(as_text=True)
        self.assertIn('<strong>Íñigo</strong>', html)
        self.assertIn('<strong>5</strong>', html)

    def test_espacios_no_cuentan(self):
        # 'María José' tiene 9 letras (10 caracteres con el espacio) y supera a 'Catalina' (8)
        html = self.ejercicio2('María José', 'Catalina', 'Ana').get_data(as_text=True)
        self.assertIn('<strong>María José</strong>', html)
        self.assertIn('<strong>9</strong>', html)

    def test_espacios_extra_se_normalizan(self):
        html = self.ejercicio2('   Pedro   ', 'Ana', 'Luis').get_data(as_text=True)
        self.assertIn('<strong>Pedro</strong>', html)
        self.assertIn('<strong>5</strong>', html)

    def test_caracteres_especiales_no_cuentan(self):
        # 'O'Higgins' = 8 letras; 'Ana-María' = 8 letras; 'Pedro' = 5. Empate entre los dos primeros.
        html = self.ejercicio2("O'Higgins", 'Ana-María', 'Pedro').get_data(as_text=True)
        self.assertIn('Hay un empate', html)
        self.assertIn('<strong>8</strong>', html)

    def test_empate_muestra_ambos(self):
        html = self.ejercicio2('Pedro', 'Maria', 'Ana').get_data(as_text=True)
        self.assertIn('Pedro y Maria', html)
        self.assertIn('Hay un empate', html)

    def test_empate_de_los_tres_no_es_posible_si_son_distintos_pero_si_mismo_largo(self):
        html = self.ejercicio2('Ana', 'Eva', 'Ida').get_data(as_text=True)
        self.assertIn('Ana, Eva y Ida', html)

    def test_nombres_repetidos_se_rechazan(self):
        self.assertInvalido(self.ejercicio2('Juan', 'juan ', 'Ana'), 'diferentes')
        self.assertInvalido(self.ejercicio2('Juan', 'Ana', 'JUAN'), 'diferentes')
        self.assertInvalido(self.ejercicio2('Ana', 'Ana', 'Ana'), 'diferentes')
        self.assertInvalido(self.ejercicio2('Ana María', 'AnaMaría', 'Luis'), 'diferentes')

    def test_entradas_vacias(self):
        self.assertInvalido(self.ejercicio2('', 'Ana', 'Luis'), 'Completa los tres nombres')
        self.assertInvalido(self.ejercicio2('Ana', '   ', 'Luis'), 'Completa los tres nombres')
        self.assertInvalido(self.client.post('/ejercicio2', data={}), 'Completa los tres nombres')

    def test_nombre_sin_letras(self):
        self.assertInvalido(self.ejercicio2('1234', 'Ana', 'Luis'), 'al menos una letra')
        self.assertInvalido(self.ejercicio2('Ana', '!!!', 'Luis'), 'al menos una letra')

    def test_nombre_demasiado_largo(self):
        self.assertInvalido(self.ejercicio2('a' * 81, 'Ana', 'Luis'), 'máximo 80')

    def test_se_conservan_los_datos_al_fallar(self):
        html = self.ejercicio2('Ana', 'Ana', 'Luis').get_data(as_text=True)
        self.assertIn('value="Ana"', html)
        self.assertIn('value="Luis"', html)

    def test_xss_se_escapa(self):
        resp = self.ejercicio2('<script>alert(1)</script>', 'Ana', 'Luis')
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_comillas_no_rompen_el_formulario(self):
        html = self.ejercicio2('"><b>x', 'Ana', 'Ana').get_data(as_text=True)
        self.assertNotIn('"><b>x', html)

    def test_funciones_puras(self):
        self.assertEqual(cantidad_letras('María José'), 9)
        self.assertEqual(cantidad_letras('Ñandú-2'), 5)
        self.assertEqual(cantidad_letras('   '), 0)
        self.assertEqual(unir_nombres(['A']), 'A')
        self.assertEqual(unir_nombres(['A', 'B']), 'A y B')
        self.assertEqual(unir_nombres(['A', 'B', 'C']), 'A, B y C')


if __name__ == '__main__':
    unittest.main()
