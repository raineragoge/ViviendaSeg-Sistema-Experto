# ViviendaSeg — Resumen final de la versión 1.1

**Objetivo:** demostrar un sistema experto educativo que permite a un propietario responder a un cuestionario adaptativo y obtener una evaluación **orientativa**, explicable y jerárquica del riesgo de su vivienda: **bajo, medio o alto**. No se utiliza aprendizaje automático ni puntuación.

## Entregables

- `static/index.html`, `style.css`, `main.js`: web adaptable con preguntas condicionales, escenarios de ejemplo e informe imprimible.
- `app.py`: API local con servidor Python sin dependencias externas.
- `knowledge.json`: **19 preguntas potenciales y 16 reglas** (5 reglas altas y 11 medias).
- `engine.py`: evaluación de reglas y gestión de información desconocida.
- `rules.pl`: representación alternativa de reglas en Prolog. La web **no ejecuta Prolog**.
- `ejemplos/`: casos de vivienda baja, alta, provisional, y tres casos centrados en madera.
- `tests/test_engine.py`: **40 pruebas automáticas superadas**, incluidas pruebas de las ramas condicionales, reglas prioritarias y coherencia de IDs entre Python y Prolog.

## Cambio principal acordado por el usuario: regla de madera

La madera **ya no significa automáticamente riesgo alto**. Se pregunta por las **medidas de protección** y por **documentación técnica sobre la resistencia al fuego** del elemento estructural.

| Datos declarados | Resultado sobre el factor madera |
|---|---|
| Informe técnico favorable | No activa regla de riesgo por madera; el resultado global puede ser bajo |
| Informe técnico desfavorable | Alto (R01 o R02) |
| Ausencia de informe o dato desconocido | Medio provisional si no existe otro riesgo alto |
| Sin protección declarada + sin documentación técnica favorable | Se activa además R16 (medio), sin asumir incumplimiento |
| Estructura mixta sin madera como elemento principal | No aparecen las preguntas de resistencia al fuego de madera |

El sistema **no inspecciona la vivienda ni verifica la documentación**. La protección no implica por sí sola una resistencia al fuego válida y una madera expuesta podría cumplir requisitos de resistencia. Es una simplificación académica sin validación de especialistas.

## Política de inferencia

1. La presencia de cualquier **riesgo alto confirmado** prevalece sobre los medios y los datos pendientes.
2. Si no hay alto y faltan datos indispensables, el resultado será **medio provisional**.
3. Si no faltan datos y hay alguna regla media activada, será **medio**.
4. Solo se obtiene **bajo** con todas las respuestas indispensables disponibles y ninguna regla de riesgo activada.
5. El informe expone reglas activadas, faltantes y recomendaciones específicas; un alto confirmado puede coexistir con datos pendientes.

## Alcance

**Incluye:** viviendas propias habituales, segundas residencias y viviendas propias sin ocupar; anexos únicamente integrados en la vivienda.

**Excluye:** inmuebles destinados al alquiler, oficinas, locales o establecimientos comerciales.

**Funcionalidad futura no implementada:** consulta por referencia catastral, mapas oficiales, persistencia de expedientes, autenticación, verificación de certificados e integración real de SWI-Prolog en el backend.

## Verificación y límites

- Las **40 pruebas del motor Python** pasan; ver ejecución local con `py -m unittest discover -s tests -v`.
- API local probada mediante solicitudes reales a `GET /api/schema` y `POST /api/evaluate` con tres escenarios de madera.
- Interfaz renderizada y recorrida en Chromium con API simulada conectada al motor Python; se verificaron el flujo condicional, resultados y ancho móvil sin errores JavaScript. La política del navegador de pruebas impidió abrir directamente el servidor local desde Chromium, por lo que la prueba de extremo a extremo sobre HTTP y navegador juntos queda pendiente.
- Puedes ejecutar la web sin instalar Prolog con `py app.py` y `http://127.0.0.1:8000/`.
- `rules.pl` es una versión independiente y **no se ha ejecutado con SWI-Prolog** porque no estaba instalado en este entorno. Se ha comprobado la coincidencia de identificadores de reglas, no su equivalencia funcional completa.
- Las reglas no están validadas por aseguradoras, técnicos ni autoridades; no sirven para tomar decisiones de aseguramiento o seguridad real.
- Siguen pendientes la comprobación de los cinco componentes **exactos** de la rúbrica del profesor y la validación técnica.

**Fuentes:** [CTE — Seguridad en caso de incendio (anejo E)](https://www.codigotecnico.org/DocumentosCTE/SeguridadEnCasoDeIncendio.html) y [RD 314/2006, BOE](https://www.boe.es/eli/es/rd/2006/03/17/314/con).
