# ViviendaSeg — Evidencias de validación Prolog

**Fecha:** 23 de octubre de 2026  
**Método:** consultas manuales ejecutadas en SWISH (SWI-Prolog online) sobre `rules.pl`.  
**Fuente de las salidas:** resultados copiados por el estudiante en la conversación.

## Comprobaciones manuales terminadas (16/16)

| N.º | Escenario | Resultado observado | Estado |
|---:|---|---|---|
| 1 | Madera desfavorable y electricidad defectuosa | Alto; R01, R03; faltantes permitidos | Coincide |
| 2 | Uso destinado al alquiler | Estado `excluded` | Coincide, confirmado manualmente |
| 3 | Electricidad desconocida con datos incompletos | Medio provisional; electricidad pendiente | Coincide |
| 4 | Vivienda completa sin riesgo | Bajo, no provisional, sin reglas | Coincide |
| 5 | Electricidad sin revisión | Medio confirmado; R06 | Coincide |
| 6 | Fuga de gas | Alto; R04 | Coincide |
| 7 | Mantenimiento de caldera pendiente | Medio confirmado; R07 | Coincide |
| 8 | Estado de caldera desconocido | Medio provisional; caldera pendiente | Coincide |
| 9 | Madera con informe favorable | Bajo; sin reglas | Coincide |
| 10 | Madera con informe desfavorable | Alto; R01 | Coincide |
| 11 | Madera sin informe | Medio provisional; informe_madera pendiente | Coincide |
| 12 | Estructura mixta con madera e informe desfavorable | Alto; R02 | Coincide |
| 13 | Electricidad defectuosa y detectores desconocidos | Alto; R03; detectores pendiente | Coincide |
| 14 | Vivienda de 1980, reformas sin responder | Medio provisional; reforma pendiente | Coincide |
| 15 | Madera sin protección y sin informe | Medio provisional; R16; informe_madera pendiente | Coincide |
| 16 | Calefacción eléctrica y dato irrelevante de caldera con fuga | Bajo; R04 no se activa | Coincide |

**Nota de rigor:** la primera ejecución del escenario 12 devolvió la salida del escenario previo; después se volvió a ejecutar con una consulta completa y la salida coincidió. Se contabiliza una sola comprobación superada.

## Comprobación automática independiente

Se han preparado:
- `tests/test_rules.pl` — 16 pruebas unitarias directas.
- `scripts/prolog_json.pl` — adaptador entre los hechos Python y el motor Prolog.
- `scripts/test_prolog_parity.py` — 514 escenarios de comparación Python–Prolog (14 dirigidos + 500 aleatorios reproducibles).
- `notebooks/validacion_python_prolog.ipynb` — ejecución en Google Colab sin instalación local.

**Estado: EJECUTADO Y SUPERADO EN GOOGLE COLAB (23/10/2026).**

El estudiante ha compartido la salida completa de la segunda ejecución corregida:

```text
1/2 — Comprobando las 16 pruebas unitarias de Prolog
DETALLE PROLOG:
................
Código de salida de las pruebas Prolog: 0

2/2 — Comparando 514 escenarios Python–Prolog
OK: paridad Python / Prolog comprobada en 514 escenarios
ERRORES DEL COMPARADOR:
(sin errores impresos)
Código de salida del comparador: 0

VALIDACIÓN PYTHON–PROLOG SUPERADA: 16 pruebas y 514 escenarios coincidentes.
```

**Interpretación:** las 16 pruebas unitarias de Prolog y los 514 casos de comparación Python–Prolog (14 dirigidos y 500 aleatorios reproducibles) han superado esta ejecución. Se ha comparado estado, nivel, provisionalidad, reglas activadas y datos pendientes. Son evidencias del prototipo educativo; no equivalen a una verificación formal de todos los casos posibles.

**Incidencia resuelta:** la primera ejecución del comparador se detuvo antes de comparar porque un caso de prueba fijaba `uso="unknown"`, valor no admitido por el validador Python en ese campo. Se sustituyó por un caso con uso omitido y la segunda ejecución se completó sin diferencias. Esto fue un error en los datos de prueba y no demuestra un fallo de las reglas.

## Alcance y limitaciones

La web pública se ejecuta con JavaScript; Python sirve para evaluación local y Prolog contiene las reglas simbólicas del prototipo. Ejecutar los tres motores por separado **no significa** que la web use Prolog en producción.

La propuesta es educativa y no está validada para decisiones reales sobre seguros, seguridad, construcción o habitabilidad.
