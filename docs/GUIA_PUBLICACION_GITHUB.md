# Paso 13 · Publicar ReviewPulse-Agent en GitHub

## A. Preparación

1. **No trabajes sobre la copia anterior**. Extrae `ReviewPulse_Paso13_Listo_Para_GitHub.zip` y abre la carpeta interna `ReviewPulse-Agent` en VS Code. Este paquete no contiene `.venv`, bases SQLite ni archivos de las pruebas de usuarios.
2. Revisa `README.md`, `docs/RESULTADOS_SMART_AGREGADOS.md` y `docs/PROCEDENCIA_Y_LICENCIAS.md`. El corpus Trip-MAML no se redistribuye; **revisa los derechos de publicación del modelo `.joblib` antes de seleccionar visibilidad pública**.
3. Ejecuta `git --version` en la terminal de VS Code. Si Git no está instalado, utiliza la extensión/Git de VS Code cuando esté disponible o instala Git for Windows desde su sitio oficial; comprueba luego el comando.
4. Puedes ejecutar nuevamente la verificación y pruebas, pero **no es obligatorio recrear `.venv` en esta nueva carpeta solo para subirla**: la versión original ya fue verificada.

## B. Crear repositorio en GitHub

1. Abre [GitHub: crear repositorio](https://github.com/new) e inicia sesión.
2. Nombre sugerido: `ReviewPulse-Agent`. Descripción sugerida: `Agente académico para análisis de reseñas hoteleras en español, memoria histórica y alertas semanales reproducibles.`
3. Decide con las integrantes y el docente la visibilidad **Private/Public** tras comprobar las condiciones del modelo y los datos. Si el profesor requiere acceso, este tiene que poder visitar el enlace; un repositorio privado exige invitarlo.
4. No actives las casillas que agregan README, `.gitignore` o licencia desde GitHub. Ya existen README y `.gitignore` locales; la licencia se acordará por separado.
5. Pulsa **Create repository**. Copia la URL remota HTTPS **real**, por ejemplo la que se muestre en su pantalla, sin sustituirla por un usuario inventado.

## C. Subir por PowerShell (carpeta raíz `ReviewPulse-Agent`)

```powershell
git --version
git init
git branch -M main
git status --short
git add .
git status --short
```

**Detente aquí y revisa** que NO aparezcan `.venv`, `salida_app`, `.sqlite3`, `.jsonl`, `.env`, `Evidencia_Paso6.zip`, `trip-maml-main.zip` ni ningún archivo de huéspedes. Si ves algo sensible, no hagas `commit`. Ajusta `.gitignore` y retira el archivo del índice con `git restore --staged "ruta"` antes de continuar.

```powershell
git commit -m "Version academica reproducible ReviewPulse-Agent"
git remote add origin URL_REAL_COPIADA_DE_GITHUB
git push -u origin main
```

Sustituye únicamente `URL_REAL_COPIADA_DE_GITHUB` por la URL HTTPS real del repositorio. Si Git solicita identidad, establece `git config user.name "Nombre que decidas usar"` y `git config user.email "correo de GitHub"`, **sin compartir aquí claves o contraseñas**. Si solicita autenticación, sigue el inicio de sesión oficial de GitHub; no introduzcas tu contraseña de cuenta como token.

### Alternativa con interfaz de VS Code

Usa la pestaña **Control de código fuente**: *Initialize Repository*, revisa archivos que cambiarán, escribe un mensaje de commit y luego *Publish to GitHub*. Concede permisos en el navegador cuando GitHub los solicite. Confirma si la publicación será privada o pública. Los nombres exactos de las opciones pueden variar según versión.

## D. Comprobación después de publicar

1. Abre en ventana privada el enlace del repo si debe ser público. Confirma que README aparece y existe el archivo `modelos/modelos_multiaspecto.joblib` (si su distribución ha sido autorizada).
2. Verifica que están `app.py`, `requirements.txt`, `src/`, `tests/`, `experimentos/` y `docs/uml/`; que **no** están `.venv` ni `salida_app`.
3. En la pestaña **Actions**, revisa que el flujo `Pruebas ReviewPulse` se ejecutó correctamente. Si falla, comparte el error para corregirlo; todavía no hemos validado ese flujo en GitHub.
4. Clona el repo en una carpeta nueva (o descarga el ZIP desde **Code > Download ZIP**) y sigue el README. Si no tienes datos del corpus, las pruebas automáticas y demo sintética pueden ejecutarse de todas formas.
5. Copia el enlace del repositorio en el documento de diseño, portada de entrega y guion del video. Mándame la **URL real** para verificar públicamente la estructura y preparar el Paso 14.

## E. Si aparece algún error

- `git is not recognized`: instala Git for Windows, cierra/reabre VS Code, repite `git --version`.
- `remote origin already exists`: ejecuta `git remote -v` y revisa si apunta a tu repo; solo entonces usa `git remote set-url origin TU_URL`.
- `src refspec main does not match any`: falta el primer commit o branch; revisa `git log -1` y `git branch`.
- `failed to push some refs`: si creaste README remoto sin querer, no ejecutes `git push --force` a ciegas. Pide ayuda y concilia los cambios.
- Acceso denegado: verifica si estás autenticada en la cuenta correcta y tienes permiso de escritura.

No se publicó ningún repositorio remoto durante la preparación del paquete. **La creación del enlace y la autenticación son acciones de quien administra la cuenta GitHub.**
