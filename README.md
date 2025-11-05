# Sistema de Gestión de Quejas

Aplicación web construida con **FastAPI**, **Jinja2** y **SQLite** para gestionar reclamaciones de clientes. El sistema usa un modelo de clasificación de Hugging Face (zero-shot) que asigna automáticamente cada queja al área responsable en función del producto y la descripción ingresada.

## Características principales

- Autenticación con alta/baja de usuarios (hash de contraseñas con `bcrypt`).
- Registro de quejas ligado a productos y usuarios.
- Clasificación automática con el modelo `facebook/bart-large-mnli` (puedes cambiarlo desde `.env`).
- Asignación de áreas con registro del puntaje de confianza del modelo.
- Plantillas HTML que replican las pantallas solicitadas.
- Datos iniciales para productos, áreas y un usuario administrador.

## Requisitos

- Python 3.10 o superior.
- Acceso a internet para descargar el modelo de Hugging Face la primera vez.
- Token personal de Hugging Face con permisos para usar la API (no lo compartas públicamente).

## Instalación paso a paso (modo "para dummies")

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <URL_DEL_REPO>
   cd Desarrollo_Software
   ```

2. **Crear y activar un entorno virtual (opcional, pero recomendado)**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # En Windows usa: .venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   > La primera vez que ejecutes la app, `transformers` descargará automáticamente el modelo; puede tardar unos minutos.

4. **Configurar variables de entorno**
   - Copia el archivo `.env.example` a `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edita `.env` y reemplaza los valores:
     - `SECRET_KEY`: escribe cualquier cadena larga y aleatoria (por ejemplo, usa [https://djecrety.ir/](https://djecrety.ir/)).
     - `HUGGINGFACE_TOKEN`: pega tu token personal. Nunca lo publiques ni lo subas al repositorio.
     - Si quieres cambiar el modelo o la base de datos, ajusta `HUGGINGFACE_MODEL` y `DATABASE_URL`.

5. **Inicializar la base de datos y ejecutar el servidor**
   ```bash
   uvicorn app.main:app --reload
   ```
   - Al arrancar la aplicación se crearán automáticamente las tablas en `complaints.db`, se cargarán los catálogos de productos/áreas y se generará un usuario administrador (`admin@example.com` / `admin123`). Cambia esta contraseña después del primer ingreso.

6. **Abrir la aplicación**
   - Visita [http://localhost:8000](http://localhost:8000) en tu navegador.
   - Verás la pantalla de inicio de sesión. Puedes:
     - Entrar con el usuario administrador por defecto.
     - Crear un nuevo usuario desde "Crear Usuario".
   - Una vez autenticado, accederás al formulario "Levantar Queja" donde podrás registrar reclamaciones y revisar el historial propio.

## Arquitectura del proyecto

```
app/
├── __init__.py
├── auth.py              # Utilidades de autenticación y hashing
├── config.py            # Configuración centralizada con Pydantic
├── database.py          # Conexión y helpers de SQLAlchemy
├── main.py              # Creación del FastAPI app + bootstrap de datos
├── ml.py                # Carga y uso del modelo de Hugging Face
├── models.py            # Modelos ORM (áreas, productos, usuarios, quejas)
├── routers/
│   └── web.py           # Rutas HTML (login, registro, formulario)
├── static/
│   └── style.css        # Estilos para las vistas
└── templates/
    ├── base.html        # Layout base (header, mensajes flash)
    ├── complaint_form.html
    ├── login.html
    └── register.html
```

- **Base de datos**: SQLite por defecto (`complaints.db`), fácilmente reemplazable por PostgreSQL/MySQL cambiando `DATABASE_URL`.
- **Modelos principales**:
  - `Area`: áreas responsables con correo y tipo de atención.
  - `Product`: catálogo de productos.
  - `User`: usuarios con roles básicos.
  - `Complaint`: quejas con folio automático, asignación de área y puntaje del modelo.
- **Clasificación automática**: `app/ml.py` usa `transformers.pipeline` con zero-shot classification. El texto enviado combina el nombre del producto y la descripción, y se evalúa contra los nombres de las áreas registradas.

## Uso del modelo de Hugging Face

- El archivo `.env` define `HUGGINGFACE_TOKEN` y `HUGGINGFACE_MODEL`.
- La primera llamada a `classify_area` inicializa el pipeline y reutiliza la instancia (`lru_cache`).
- Puedes reemplazar `facebook/bart-large-mnli` por un modelo propio en Hugging Face que soporte clasificación zero-shot o `text-classification` con etiquetas personalizadas.

## Comandos útiles

- **Ejecución en modo producción simple (sin recarga):**
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
- **Recrear base de datos desde cero:**
  ```bash
  rm complaints.db
  uvicorn app.main:app --reload
  ```
- **Actualizar dependencias:**
  ```bash
  pip install --upgrade -r requirements.txt
  ```

## Seguridad y buenas prácticas

- Nunca publiques tu token real de Hugging Face (mantenlo en `.env`, que debe estar excluido de Git).
- Cambia el `SECRET_KEY` y la contraseña del administrador en el entorno productivo.
- Configura HTTPS y un reverse proxy (Nginx, Traefik) para despliegues en producción.
- Si decides usar una base de datos distinta a SQLite, asegúrate de crearla previamente y actualizar `DATABASE_URL` con las credenciales correctas.

## Licencia

Este proyecto se entrega como ejemplo educativo. Adáptalo libremente a tus necesidades.
