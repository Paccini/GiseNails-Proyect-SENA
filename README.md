# Gise-Nails Web App

Aplicativo web para **Gise-Nails**, empresa de uñas ubicada en Ibagué, Colombia. Permite gestionar reservas, clientes, información de servicios y más, facilitando la administración y experiencia de los usuarios.

## Autores

- Santiago Paccini
- Juan Arcila
- Sarai Prada
- Luis Niño
- Yohan Mahecha

## Estructura del Proyecto

```
proyecto Gise-Nails/
│
├── backend/        # Backend Django: lógica, modelos, vistas, urls
│   ├── clientes/   # Gestión de clientes
│   ├── gisenails/  # Configuración principal Django
│   ├── inicio/     # Página principal
│   ├── login/      # Autenticación de usuarios
│   ├── nosotros/   # Información de la empresa
│   ├── reserva/    # Gestión de reservas
│   └── manage.py   # Script de administración Django
│
├── frontend/       # Recursos estáticos y plantillas
│   ├── static/
│   │   ├── css/    # Hojas de estilo
│   │   ├── img/    # Imágenes
│   │   ├── js/     # Scripts JS
│   │   └── video/  # Videos
│   └── templates/  # Plantillas HTML organizadas por módulo
│
└── README.md       # Este archivo
```

## Instalación

1. **Clona el repositorio:**
   ```
   git clone <URL-del-repositorio>
   cd proyecto Gise-Nails
   ```

2. **Crea y activa un entorno virtual:**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```
   pip install -r requirements.txt
   ```

4. **Ejecuta migraciones de Django:**
   ```
   python manage.py migrate
   ```

5. **Inicia el servidor de desarrollo:**
   ```
   python manage.py runserver
   ```

6. **(Opcional) Instala dependencias del frontend si las hay.**

## Uso

- Accede a la aplicación en [http://localhost:8000](http://localhost:8000).
- Regístrate, inicia sesión, realiza reservas y navega por la información de la empresa.

## Funcionalidades

- **Gestión de clientes:** Registro y administración de usuarios.
- **Reservas:** Solicitud y gestión de citas.
- **Autenticación:** Inicio de sesión y registro seguro.
- **Información de servicios:** Detalles sobre los servicios ofrecidos.
- **Panel administrativo:** Gestión interna para el equipo Gise-Nails.
- **Frontend atractivo:** Interfaz visual con imágenes, videos y estilos personalizados.

## Tecnologías

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Base de datos:** SQLite (por defecto Django)

## Estructura de carpetas principales

- `backend/`: Código fuente del servidor y lógica de negocio.
- `frontend/static/`: Recursos estáticos (CSS, JS, imágenes, videos).
- `frontend/templates/`: Plantillas HTML para cada módulo.

## Contacto

Para dudas o soporte, contacta a cualquiera de los autores.

---

¡Gracias por usar Gise-Nails!