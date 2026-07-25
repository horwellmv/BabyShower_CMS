# 👶 BabyShower CMS

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1+-green?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-316192?logo=postgresql&logoColor=white)
![Railway](https://img.shields.io/badge/Deploy-Railway-purple?logo=railway&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-CDN-06B6D4?logo=tailwindcss&logoColor=white)

Sistema de gestión de invitaciones para un Baby Shower. Permite a los invitados confirmar asistencia (RSVP), ver una galería de fotos y reservar regalos de una lista curada por los organizadores.

## ✨ Funcionalidades

- 🔐 **Autenticación por teléfono** — Los invitados acceden con su número registrado
- 📱 **Diseño mobile-first** — Optimizado para celulares con diseño watercolor premium
- 📋 **RSVP** — Confirmar o declinar asistencia
- 🎁 **Lista de Regalos** — Reservar regalos (stock único o ilimitado)
- 🖼️ **Galería** — Visualizar fotos del evento
- 📝 **Mis Reservas** — Ver regalos reservados
- ⚙️ **Panel Admin** — Gestión completa con Django Jazzmin

## 🛠️ Tecnologías

| Tecnología | Uso |
|---|---|
| **Django 5.1+** | Backend, ORM, admin |
| **PostgreSQL** | Base de datos en producción |
| **SQLite** | Base de datos en desarrollo local |
| **Supabase Storage** | Almacenamiento de imágenes (producción) |
| **TailwindCSS (CDN)** | Estilos del frontend |
| **WhiteNoise** | Servir archivos estáticos |
| **Gunicorn** | Servidor WSGI de producción |
| **Jazzmin** | Tema premium para Django Admin |
| **Railway** | Plataforma de deploy |

## 📁 Estructura del Proyecto

```
BabyShower_CMS/
├── backend/
│   ├── apps/
│   │   └── invitations/        # App principal
│   │       ├── admin.py        # Config del admin
│   │       ├── middleware.py   # Autenticación por sesión
│   │       ├── models.py       # Guest, Gift, GiftReservation, GalleryImage
│   │       ├── views.py        # Vistas y API endpoints
│   │       ├── urls.py         # Rutas de la app
│   │       └── tests.py        # Tests automatizados
│   ├── core/
│   │   ├── settings.py         # Configuración Django
│   │   ├── storage_backends.py # Backend Supabase Storage
│   │   ├── urls.py             # Rutas principales
│   │   └── wsgi.py             # Punto de entrada WSGI
│   ├── manage.py
│   ├── export_data.py          # Script migración SQLite → PostgreSQL
│   └── requirements.txt
├── frontend/
│   ├── assets/
│   │   ├── css/custom.css      # Estilos personalizados
│   │   ├── js/app.js           # JavaScript global
│   │   └── images/             # Imágenes estáticas
│   └── templates/
│       ├── base.html           # Template base
│       ├── home.html           # Página principal + RSVP
│       ├── login.html          # Login por teléfono
│       ├── gifts.html          # Lista de regalos
│       ├── gallery.html        # Galería de fotos
│       ├── my_reservations.html # Mis reservas
│       └── components/         # Componentes reutilizables
├── media/                      # Archivos subidos (solo desarrollo local)
├── .env                        # Variables de entorno (NO se sube a Git)
├── .env.example                # Ejemplo de variables de entorno
├── .gitignore
├── Procfile                    # Comando de inicio para Railway
├── railway.json                # Configuración de Railway
├── nixpacks.toml               # Config de build para Railway
└── README.md
```

## 🚀 Instalación Local

### Requisitos previos

- Python 3.11+
- pip
- Git

### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/BabyShower_CMS.git
   cd BabyShower_CMS
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   # Copiar el archivo de ejemplo
   cp .env.example .env
   
   # Editar .env con tus valores (en desarrollo, los defaults funcionan)
   ```

5. **Ejecutar migraciones**
   ```bash
   cd backend
   python manage.py migrate
   ```

6. **Crear superusuario (admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Iniciar servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

8. **Acceder a la app**
   - Frontend: http://localhost:8000/login/
   - Admin: http://localhost:8000/admin/

## 🔐 Variables de Entorno

| Variable | Requerida | Descripción | Ejemplo |
|---|:---:|---|---|
| `SECRET_KEY` | ✅ | Clave secreta de Django | `django-insecure-...` (dev) |
| `DEBUG` | ❌ | Modo debug | `True` (dev) / `False` (prod) |
| `ALLOWED_HOSTS` | ❌ | Hosts permitidos | `localhost,127.0.0.1` |
| `DATABASE_URL` | ❌ | URL de PostgreSQL | `postgresql://user:pass@host/db` |
| `SUPABASE_URL` | ❌ | URL del proyecto Supabase | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | ❌ | API key de Supabase (service role) | `eyJhbGci...` |
| `SUPABASE_BUCKET` | ❌ | Nombre del bucket de storage | `media` |

> **Nota**: En desarrollo local, solo `SECRET_KEY` es necesaria (y tiene un fallback automático). Las demás variables usan valores por defecto para desarrollo.

## 🚂 Deploy en Railway

### Pasos

1. **Crear proyecto en Railway**
   - Ir a [railway.app](https://railway.app)
   - Conectar tu repositorio de GitHub
   - Seleccionar la rama `main` para deploy automático

2. **Agregar PostgreSQL**
   - En el proyecto de Railway, click en "New" → "Database" → "PostgreSQL"
   - Railway inyecta automáticamente `DATABASE_URL`

3. **Configurar variables de entorno en Railway**
   - `SECRET_KEY`: Generar con:
     ```bash
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.railway.app`
   - `SUPABASE_URL`: URL de tu proyecto Supabase
   - `SUPABASE_KEY`: API key de Supabase
   - `SUPABASE_BUCKET`: `media`

4. **Deploy automático**
   - Cada push a `main` dispara un deploy automático
   - Railway ejecuta migraciones y collectstatic automáticamente (ver `Procfile`)

5. **Crear superusuario en producción**
   - En Railway, abrir la consola del servicio
   - Ejecutar:
     ```bash
     cd backend
     python manage.py createsuperuser
     ```

## 📦 Migración de Datos (SQLite → PostgreSQL)

Si tienes datos en desarrollo local que quieres llevar a producción:

1. **Exportar datos locales**
   ```bash
   cd backend
   python export_data.py
   ```
   Esto genera `data_fixture.json` en la raíz del proyecto.

2. **Importar en producción**
   - Subir `data_fixture.json` al repo o copiarlo a Railway
   - En la consola de Railway:
     ```bash
     cd backend
     python manage.py loaddata ../data_fixture.json
     ```

3. **Migrar imágenes**
   - Subir manualmente las imágenes de `media/gifts/` y `media/gallery/` a Supabase Storage
   - Mantener la misma estructura de carpetas

## 🧪 Tests

```bash
cd backend
python manage.py test apps.invitations --verbosity=2
```

## 👥 Créditos

Desarrollado por [Muval.net](https://muval.net)