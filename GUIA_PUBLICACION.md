# Publicar ViviendaSeg: GitHub → Cloudflare Pages

### 1. GitHub

Entra a https://github.com/new y crea el repositorio **ViviendaSeg-Sistema-Experto** en la cuenta `raineragoge`. Público. Sin README ni .gitignore iniciales.

Descomprime el ZIP y abre PowerShell desde la carpeta principal (debe contener `knowledge.json`, `public/`, `functions/` y `README.md`). Ejecuta:

```powershell
git init
git add .
git commit -m "Publicar ViviendaSeg 1.2"
git branch -M main
git remote add origin https://github.com/raineragoge/ViviendaSeg-Sistema-Experto.git
git push -u origin main
```

### 2. Cloudflare

Entra a https://dash.cloudflare.com/ → Workers & Pages → Crear aplicación → Pages → Conectar GitHub → seleccionar `raineragoge/ViviendaSeg-Sistema-Experto`.

- Framework: **None**
- Rama: **main**
- Comando de compilación: **vacío** (o `exit 0`)
- Directorio de salida: **public**
- Directorio raíz: **/**

Publicar. El proyecto usa **Pages Functions**, así que no elijas «Drag & drop».

### 3. Comprobación en la dirección que te asigne Cloudflare

1. Acceder a la página de inicio.
2. Abrir `/api/schema` en el mismo dominio; debe devolver JSON y 19 preguntas.
3. En el cuestionario, cargar el escenario «Alto» y verificar el resultado y las reglas.
4. Cargar «Datos desconocidos» y verificar «medio provisional».

Si `/api/schema` devuelve 404, verificar que `functions/` esté en la raíz del repositorio y que se haya creado una aplicación **Cloudflare Pages** conectada a Git.

### 4. ¿Qué necesito para completar la publicación contigo?

Por aquí no dispongo de la acción para crear un repositorio GitHub nuevo ni de acceso de publicación a tu cuenta Cloudflare. En cuanto tengas creado el repositorio y me indiques su URL, podemos verificarlo y continuar con el despliegue, aunque la conexión de Cloudflare en el navegador deberás completarla tú.
