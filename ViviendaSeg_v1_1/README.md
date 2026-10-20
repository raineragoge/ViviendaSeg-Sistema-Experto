# ViviendaSeg · Sistema experto de riesgo de viviendas

Prototipo académico **funcional** de clasificación orientativa del riesgo de una vivienda: bajo, medio y alto, utilizando reglas jerárquicas explicables. Está diseñado como trabajo de Sistemas Expertos. No sirve para fijar primas, aprobar seguros, certificar seguridad ni sustituir a profesionales.

## Inicio rápido · Windows PowerShell

Desde la carpeta del proyecto:

```powershell
py app.py
```

Abre **http://127.0.0.1:8000/** en el navegador. Si `py` no está disponible, prueba `python app.py`.

No necesitas instalar Prolog, ni paquetes de Python, ni una base de datos. No abras `static/index.html` directamente: el cuestionario consulta una API local de Python.

En la página encontrarás ejemplos de **riesgo bajo, medio, alto y provisional**, y un botón para imprimir el informe.

Detén el servidor con `Ctrl+C`.

## Cambios de v1.0 a v1.1

- 19 preguntas potenciales (antes 17), con 2 nuevas preguntas condicionadas al uso de madera estructural.
- 16 reglas (antes 15). R01 y R02 ahora requieren un informe desfavorable; R16 añade una alerta preventiva cuando no hay protecciones declaradas ni documentación favorable.
- Condiciones compuestas **AND/OR** para mostrar preguntas solo cuando corresponde.
- Nuevas pruebas de condiciones, prioridad y coherencia básica de identificadores Python–Prolog.

## Pruebas automatizadas

```powershell
py -m unittest discover -s tests -v
```

También puedes probar el motor sin usar el navegador:

```powershell
Get-Content -Raw ejemplos/vivienda_alta.json | py engine.py
```

## Componentes y arquitectura

- **Interfaz de usuario:** `static/index.html`, `style.css`, `main.js`. Cuestionario adaptativo y explicación de la conclusión.
- **Base de conocimiento:** `knowledge.json`. Reglas R01-R16, preguntas, condiciones, medidas y referencias.
- **Motor de inferencia:** `engine.py`. Encadenamiento hacia adelante mediante evaluación de reglas `if`/`then` y resolución jerárquica.
- **Memoria de trabajo:** objeto `answers` (navegador) y diccionario `facts` (evaluación) con las respuestas aportadas; no persiste en disco.
- **Módulo de explicación:** `triggered_rules`, `trace`, `missing` y `recommendations` devueltos por la API y mostrados al usuario.
- **Servidor local:** `app.py` (biblioteca estándar `http.server`). Exposición de `GET /api/schema` y `POST /api/evaluate`.
- **Representación Prolog:** `rules.pl`, con las mismas 16 reglas y jerarquía, para estudiar y ejecutar opcionalmente con SWI-Prolog.

**Pendiente de cotejar con la rúbrica:** el profesor exige cinco componentes del sistema experto. Hemos construido interfaz, base, inferencia, memoria de trabajo y módulo explicativo como cinco subsistemas habituales, pero deben contrastarse sus nombres exactos con el material de clase.

### Nota sobre Prolog

El prototipo web funciona en **Python**, no ejecuta directamente Prolog. `rules.pl` es una versión independiente demostrativa. Para ejecutarlo manualmente, SWI-Prolog es opcional:

```text
swipl -q -s rules.pl -g "ejemplo_alto,imprimir_resultado,halt"
```

Esta decisión permite abrir la web sin instalar Prolog y mantiene reglas explícitas en Prolog para el trabajo. Integrar SWI-Prolog en la ejecución web real requeriría disponer de su motor (instalado o alojado remotamente); **no se afirma que esa integración ya exista**.

## Razonamiento de las reglas

1. Se validan todas las respuestas y se descartan respuestas que quedaron ocultas al cambiar de rama.
2. Se activan las reglas cuyas condiciones se cumplen.
3. Si se activa alguna de nivel **alto**, el resultado es **alto**, incluso si falta otra información; se listan datos pendientes.
4. Si no hay alto y faltan respuestas, el resultado es **medio provisional**, aunque existan otros factores medios ya confirmados.
5. Si no falta información solicitada, pero hay reglas de nivel medio, el resultado es **medio**.
6. Solo sin reglas activadas y con respuestas completas se obtiene **bajo**.

La **antigüedad (año 2006)** solo activa la pregunta sobre reformas; no asigna riesgo. El CTE entró en vigor en 2006 con periodos transitorios y no supone que edificios posteriores estén construidos íntegramente con materiales incombustibles.

### Tratamiento de madera estructural (mejora v1.1)

El sistema **ya no califica automáticamente una estructura de madera como riesgo alto**. Si la estructura principal es de madera (o mixta con madera principal), plantea dos preguntas adicionales:

1. Si conoce medidas de protección contra incendios de esos elementos constructivos.
2. Si dispone de proyecto, memoria o informe técnico sobre la resistencia al fuego de la estructura.

Resultados en ausencia de otros factores:

- **Informe técnico favorable declarado:** no se activa un riesgo por madera; puede resultar bajo si todo lo demás está completo y sin factores detectados. Se trata de una declaración del usuario, **no de una validación de documentos**.
- **Informe técnico desfavorable declarado:** se activa **alto** (R01 o R02), exista o no protección declarada.
- **Sin documentación o respuesta desconocida:** resulta **medio provisional**. No se equipara la falta de papeles con incumplimiento.
- **Sin protección declarada y sin informe favorable:** adicionalmente se dispara **R16, medio** como señal preventiva; sigue siendo provisional por la documentación faltante.
- **Protección desconocida con informe técnico favorable:** la protección se considera información no indispensable para la clasificación académica, pues existe un informe técnico que justifica la resistencia al fuego.

Las estructuras de madera pueden cumplir las exigencias pertinentes por dimensionado o soluciones constructivas sin que exista necesariamente un revestimiento añadido. CTE DB-SI anejo E contempla su resistencia al fuego. Estas preguntas solo recogen **afirmaciones del propietario**, no comprueban certificaciones ni la autenticidad o suficiencia técnica de documentos. El resultado global nunca sustituye una valoración pericial.


La **ubicación geográfica** no se deduce: preguntar antecedentes de inundación no constituye una evaluación hidrológica real.

## Verificación de v1.1

Se han superado 40 pruebas del motor, comprobado los endpoints de la API real mediante HTTP y recorrido la interfaz en Chromium con respuestas del motor Python inyectadas en un contexto de navegador aislado. La política del navegador de prueba bloqueó localhost, así que la navegación completa sobre el servidor HTTP real deberá repetirse en el ordenador de entrega. No se ha ejecutado SWI-Prolog en este entorno.

## Alcance y limitaciones

**Dentro:** viviendas propias de uso habitual, segundas viviendas y viviendas propias desocupadas, en su uso residencial; garajes y trasteros solo integrados con la vivienda.

**Fuera:** alquileres como objeto del análisis, oficinas, negocios y otros usos no residenciales.

**No implementado:** integración catastral, GIS/mapas oficiales de peligrosidad, documentos adjuntos, gestión de usuarios, persistencia o autenticación, una suscripción de seguros real, validación pericial, motor Prolog embebido en la web o despliegue en internet.

**Seguridad:** los resultados son educativos; situaciones de fuga de gas o posible inestabilidad estructural requieren atención urgente de profesionales y, cuando corresponda, emergencias. No utilizar `http.server` como servidor público de producción.

## Próxima iteración

1. Validar reglas con profesorado y, si el uso dejara de ser exclusivamente académico, profesionales de edificación y aseguramiento.
2. Completar la rúbrica exacta de cinco componentes.
3. Validar con un técnico las reglas de instalaciones, protección, madera, antigüedad y periodos sin ocupación; siguen siendo hipótesis académicas.
4. Integrar Prolog como motor real si se decide hacer obligatoria esa parte.
5. Posteriormente: referencia catastral y datos oficiales, manteniendo transparencia de procedencia, permisos y cobertura.

## Fuentes para el apartado normativo

- [BOE: Real Decreto 314/2006, CTE](https://www.boe.es/eli/es/rd/2006/03/17/314/con)
- [CTE: DB SI, Seguridad en caso de incendio (anejo E, madera estructural)](https://www.codigotecnico.org/DocumentosCTE/SeguridadEnCasoDeIncendio.html)
- [Donostia: recomendaciones de emergencias](https://www.donostia.eus/es/seguridad-ciudadana-emergencias/emergencias/consejos-recomendaciones)
