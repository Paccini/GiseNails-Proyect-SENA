# Gise-Nails Web App

Aplicativo web para **Gise-Nails**, empresa de uñas ubicada en Ibagué, Colombia. Permite gestionar reservas, clientes, servicios y productos, facilitando la administración y experiencia de los usuarios.

## Estructura del Proyecto

```
proyecto Gise-Nails/
│
├── backend/        # Backend Django: lógica, modelos, vistas, urls
│   ├── clientes/   # Gestión de clientes y panel de usuario
│   ├── gisenails/  # Configuración principal Django
│   ├── inicio/     # Página principal
│   ├── login/      # Autenticación de usuarios
│   ├── nosotros/   # Información de la empresa
│   ├── reserva/    # Gestión de reservas y lógica de citas
│   ├── empleados/  # Gestión de empleados
│   ├── productos/  # Gestión de productos
│   ├── servicio/   # Gestión de servicios
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

## Uso

- Accede a la aplicación en [http://localhost:8000](http://localhost:8000).
- Regístrate, inicia sesión, realiza reservas y navega por la información de la empresa.

## Funcionalidades

- **Gestión de clientes:** Registro, edición y panel de usuario con historial de reservas.
- **Reservas inteligentes:** Si el usuario agenda una cita y no está registrado, los datos de la reserva se guardan y se autocompletan en el formulario de registro. Al registrarse o iniciar sesión, la cita queda asociada automáticamente al usuario y se muestra en su panel.
- **Autenticación:** Inicio de sesión y registro seguro, con autocompletado de datos desde la reserva.
- **Gestión de empleados, servicios y productos:** Administración completa desde el panel.
- **Panel administrativo:** Gestión interna para el equipo Gise-Nails.
- **Frontend atractivo:** Interfaz visual con imágenes, videos y estilos personalizados.
- **Notificaciones y experiencia mejorada:** Mensajes y redirecciones automáticas según el flujo de usuario.

## Tecnologías

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Base de datos:** SQLite (por defecto Django)

## Novedades recientes

- **Reserva asociada automáticamente al usuario tras registro/login.**
- **Autocompletado de nombre, correo y teléfono en el registro si la cita fue agendada antes de crear la cuenta.**
- **Panel de usuario muestra todas las reservas asociadas al cliente autenticado.**
- **Mejoras en la gestión de rutas y redirecciones para un flujo de usuario más intuitivo.**
- **Validación para evitar duplicidad de reservas y correos.**

## Estructura de carpetas principales

- `backend/`: Código fuente del servidor y lógica de negocio.
- `frontend/static/`: Recursos estáticos (CSS, JS, imágenes, videos).
- `frontend/templates/`: Plantillas HTML para cada módulo.

## Contacto

Para dudas o soporte, contacta a cualquiera de los autores.

---

¡Gracias por usar Gise-Nails!