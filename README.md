# ViviendaSeg · Sistema experto de riesgos en viviendas

**Versión de distribución 1.2 · Octubre de 2026** — Prototipo académico, no producto asegurador. Motor de inferencia jerárquico, 19 preguntas potenciales, 16 reglas, conclusiones explicables y avisos para información desconocida.

**Uso exclusivamente educativo:** las reglas no están validadas por peritos, aseguradoras ni equipos de emergencias. No tomar decisiones de aseguramiento, seguridad o habitabilidad con el resultado.

## Arquitectura

```
public/                  HTML, CSS y JavaScript del cuestionario
functions/api/           API de Cloudflare Pages Functions (JavaScript)
functions/_shared/       Motor JS y copia generada de la base de conocimiento
knowledge.json           Fuente de verdad de preguntas y reglas
engine.py                Motor Python para uso local y comparación académica
app.py                   Servidor local Python opcional
rules.pl                 Representación educativa independiente en Prolog
tests/                   Tests Python y JS
scripts/                 Sincronización y verificación de paridad Python ↔ JS
docs/                    Capturas y resumen de la versión anterior
```

**Cómo funciona publicado:** Cloudflare Pages sirve los archivos de `public/` y ejecuta `functions/api/schema.js` y `functions/api/evaluate.js`. Las respuestas se envían temporalmente a la API y se evalúan en Cloudflare mediante reglas JavaScript. No hay base de datos ni registro de usuarios; este proyecto no persiste las respuestas. Los motores Python y Prolog se mantienen para uso local y demostración académica; **Cloudflare no ejecuta Prolog ni Python en este despliegue**.

## Publicar con GitHub + Cloudflare Pages

1. Crea en tu cuenta GitHub un repositorio **público** llamado `ViviendaSeg-Sistema-Experto`, vacío (no marques README inicial, ya viene incluido).
2. En tu equipo, descomprime el ZIP y abre PowerShell **dentro de la carpeta que contiene este README y `public/`**.
3. Ejecuta los comandos siguientes:

```powershell
git init
git add .
git commit -m "ViviendaSeg v1.2: sistema experto listo para Cloudflare"
git branch -M main
git remote add origin https://github.com/raineragoge/ViviendaSeg-Sistema-Experto.git
git push -u origin main
```

Si Git requiere autenticación, sigue el inicio de sesión de GitHub. No compartas contraseñas ni tokens aquí.

4. En [Cloudflare](https://dash.cloudflare.com/) entra a **Workers & Pages**, crea una aplicación de **Pages** conectando el repositorio de GitHub (Git integration, no Direct Upload).
5. Configura exactamente:

| Opción | Valor |
|---|---|
| Repositorio | `raineragoge/ViviendaSeg-Sistema-Experto` |
| Rama de producción | `main` |
| Preset/Framework | `None` |
| Build command | Dejar vacío (si lo exige: `exit 0`) |
| Build output directory | `public` |
| Root directory | raíz del repositorio (por defecto) |

6. Publica y prueba la dirección `https://NOMBRE-DEL-PROYECTO.pages.dev`. La dirección real depende del nombre concedido por Cloudflare; **no está publicada ni verificada todavía**.
7. Comprueba estas URLs ya bajo el dominio real:

- `/` — cuestionario.
- `/api/schema` — JSON de preguntas y versión.
- Completa el escenario de riesgo alto y verifica que el informe muestre sus reglas. Para probar POST automáticamente en tu equipo, consulta las pruebas JS.

**Importante:** conecta GitHub desde Pages. Subir `public/` mediante arrastrar y soltar en el panel de Cloudflare **no publica estas Pages Functions**, por lo que fallaría el cuestionario.

Cada nuevo commit en `main` desencadenará un despliegue de Pages, si mantienes activado el despliegue automático.

## Usar localmente sin instalar Prolog

PowerShell, desde la carpeta del proyecto:

```powershell
py app.py
```

Visita http://127.0.0.1:8000/. También puedes ejecutar `INICIAR_WINDOWS.bat`.

## Pruebas

Requiere Python 3.9+ y Node 22+ **solo para probar**; el despliegue a Cloudflare Pages no requiere que instales Node localmente.

```powershell
py -m unittest discover -s tests -v
node --test tests/test_cloudflare.mjs
py scripts/test_parity.py
py scripts/sync_knowledge.py --check
```

- 40 pruebas Python (motor original).
- 14 pruebas de Pages Functions y JS.
- 507 escenarios comparados Python ↔ JS en el script de paridad.
- Las funciones de Pages no se han probado aún en el entorno real de Cloudflare; esa prueba queda pendiente tras publicar.

## Editar reglas

Editar **solo** `knowledge.json`. Después ejecutar:

```powershell
py scripts/sync_knowledge.py
py scripts/test_parity.py
```

Se actualiza el archivo generado `functions/_shared/knowledge.js`. Subir ambos cambios a GitHub. Las pruebas CI verifican que los archivos están sincronizados.

## Protección y limitaciones

- La aplicación no utiliza cookies de cuenta, base de datos ni almacenamiento persistente de respuestas. La infraestructura de Cloudflare puede tener registros técnicos de las solicitudes; no se ha auditado su configuración.
- No se solicita información personal identificativa ni dirección o referencia catastral.
- Los resultados son **orientativos y provisionales** cuando faltan datos.
- Un factor alto confirmado prevalece sobre otras respuestas desconocidas.
- El año de construcción no se usa como criterio automático de seguridad.
- Las estructuras de madera con informe favorable no son automáticamente de riesgo alto; las afirmaciones del usuario no equivalen a certificación documental.
- Rúbrica exacta de los cinco componentes de Sistemas Expertos pendiente de comparar con la documentación del profesor.
- La lógica JS es una adaptación comprobada contra Python, pero no se ha realizado auditoría externa.

## Fuentes de referencia

- CTE / RD 314/2006: https://www.boe.es/eli/es/rd/2006/03/17/314/con
- DB-SI (resistencia al fuego, madera): https://www.codigotecnico.org/DocumentosCTE/SeguridadEnCasoDeIncendio.html
- Cloudflare Pages Functions: https://developers.cloudflare.com/pages/functions/get-started/
- Git Integration: https://developers.cloudflare.com/pages/configuration/git-integration/
