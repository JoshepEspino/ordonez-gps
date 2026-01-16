"""
Script para probar las credenciales de TrackSolidPro
Lee las credenciales desde el archivo .env
"""

import os
from dotenv import load_dotenv
from main import TrackSolidAPI

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales desde .env
APP_KEY = os.getenv("TRACKSOLID_APP_KEY")
APP_SECRET = os.getenv("TRACKSOLID_APP_SECRET")
USER_EMAIL = os.getenv("TRACKSOLID_EMAIL")
USER_PASSWORD = os.getenv("TRACKSOLID_PASSWORD")

# Verificar que todas las credenciales estén configuradas
if not all([APP_KEY, APP_SECRET, USER_EMAIL, USER_PASSWORD]):
    print("❌ ERROR: Faltan credenciales en el archivo .env")
    print("\nPor favor, crea un archivo .env con:")
    print("TRACKSOLID_APP_KEY=tu_app_key")
    print("TRACKSOLID_APP_SECRET=tu_app_secret")
    print("TRACKSOLID_EMAIL=tu_email")
    print("TRACKSOLID_PASSWORD=tu_password")
    exit(1)

print("🔐 Probando credenciales desde .env...")
print(f"   Email: {USER_EMAIL}")

# Prueba las credenciales
api = TrackSolidAPI(APP_KEY, APP_SECRET, USER_EMAIL, USER_PASSWORD)

if api.obtener_token():
    print("✅ Credenciales correctas")
else:
    print("❌ Credenciales incorrectas")