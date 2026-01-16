"""
Script de diagnóstico para verificar credenciales
Lee las credenciales desde el archivo .env
"""

import hashlib
import requests
import os
from datetime import datetime, UTC
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Credenciales desde .env
APP_KEY = os.getenv("TRACKSOLID_APP_KEY")
APP_SECRET = os.getenv("TRACKSOLID_APP_SECRET")
USER_EMAIL = os.getenv("TRACKSOLID_EMAIL")
BASE_PASSWORD = os.getenv("TRACKSOLID_PASSWORD")

# Verificar que las credenciales estén configuradas
if not all([APP_KEY, APP_SECRET, USER_EMAIL, BASE_PASSWORD]):
    print("❌ ERROR: Faltan credenciales en el archivo .env")
    print("\nPor favor, crea un archivo .env con:")
    print("TRACKSOLID_APP_KEY=tu_app_key")
    print("TRACKSOLID_APP_SECRET=tu_app_secret")
    print("TRACKSOLID_EMAIL=tu_email")
    print("TRACKSOLID_PASSWORD=tu_password")
    exit(1)

# Probar diferentes variaciones de la contraseña
passwords_to_test = [
    BASE_PASSWORD,  # La contraseña del .env
    BASE_PASSWORD.replace("ó", "o"),  # Sin tildes
    BASE_PASSWORD.replace("ñ", "n"),  # Sin ñ
]

def md5_hash(text):
    """Convierte un texto a hash MD5"""
    return hashlib.md5(text.encode('utf-8')).hexdigest().lower()

def generate_signature(params, app_secret):
    """Genera la firma MD5"""
    sorted_items = sorted(params.items())
    base = "".join([f"{k}{v}" for k, v in sorted_items])
    sign_str = f"{app_secret}{base}{app_secret}"
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

def test_credentials(password):
    """Prueba las credenciales"""
    endpoint = "https://us-open.tracksolidpro.com/route/rest"
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    password_md5 = md5_hash(password)
    
    params = {
        "app_key": APP_KEY,
        "expires_in": "3600",
        "format": "json",
        "method": "jimi.oauth.token.get",
        "sign_method": "md5",
        "timestamp": timestamp,
        "user_id": USER_EMAIL,
        "user_pwd_md5": password_md5,
        "v": "1.0"
    }
    
    params["sign"] = generate_signature(params, APP_SECRET)
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(endpoint, data=params, headers=headers)
        result = response.json()
        return result
    except Exception as e:
        return {"error": str(e)}

print("="*80)
print("DIAGNÓSTICO DE CREDENCIALES")
print("="*80)
print(f"\nAPP_KEY: {APP_KEY}")
print(f"USER_EMAIL: {USER_EMAIL}")
print("\nProbando diferentes variaciones de contraseña...\n")

for i, password in enumerate(passwords_to_test, 1):
    print(f"{i}. Probando: {password}")
    print(f"   MD5: {md5_hash(password)}")
    
    result = test_credentials(password)
    
    if result.get('code') == 0:
        print(f"   ✅ ¡ÉXITO! Esta contraseña funciona")
        print(f"   Token: {result['result']['accessToken'][:20]}...")
        print(f"\n{'='*80}")
        print("CONTRASEÑA CORRECTA ENCONTRADA:")
        print(f"   {password}")
        print(f"{'='*80}")
        break
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    print()
else:
    print("="*80)
    print("❌ Ninguna contraseña funcionó")
    print("\n💡 Sugerencias:")
    print("   1. Verifica que el email sea correcto")
    print("   2. Intenta resetear la contraseña en TrackSolidPro")
    print("   3. Verifica que la cuenta esté activa")
    print("   4. Contacta al soporte de TrackSolidPro")
    print("="*80)
