# Instalación del proyecto

1. Clona el repositorio:
   ```
   git clone <URL-del-repositorio>
   cd PROYECTO-GISE-NAILS
   ```

2. Crea y activa un entorno virtual:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Ejecuta migraciones de Django:
   ```
   python manage.py migrate
   ```

5. Inicia el servidor de desarrollo:
   ```
   python manage.py runserver
   ```

6. (Opcional) Instala dependencias del frontend si las hay.