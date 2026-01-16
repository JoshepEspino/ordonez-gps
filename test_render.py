"""
Script de prueba para verificar la conexión en Render
"""

import os
from dotenv import load_dotenv
from main import TrackSolidAPI

print("="*80)
print("TEST DE CONEXIÓN - RENDER")
print("="*80)

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales
APP_KEY = os.getenv("TRACKSOLID_APP_KEY")
APP_SECRET = os.getenv("TRACKSOLID_APP_SECRET")
USER_EMAIL = os.getenv("TRACKSOLID_EMAIL")
USER_PASSWORD = os.getenv("TRACKSOLID_PASSWORD")

print("\n📋 VERIFICACIÓN DE VARIABLES DE ENTORNO:")
print(f"   APP_KEY: {'✅ Configurado' if APP_KEY else '❌ NO configurado'}")
print(f"   APP_SECRET: {'✅ Configurado' if APP_SECRET else '❌ NO configurado'}")
print(f"   USER_EMAIL: {USER_EMAIL if USER_EMAIL else '❌ NO configurado'}")
print(f"   USER_PASSWORD: {'✅ Configurado' if USER_PASSWORD else '❌ NO configurado'}")

if not all([APP_KEY, APP_SECRET, USER_EMAIL, USER_PASSWORD]):
    print("\n❌ ERROR: Faltan credenciales")
    print("\nEn Render, configura las variables de entorno:")
    print("   Environment → Add Environment Variable")
    print("   - TRACKSOLID_APP_KEY")
    print("   - TRACKSOLID_APP_SECRET")
    print("   - TRACKSOLID_EMAIL")
    print("   - TRACKSOLID_PASSWORD")
    exit(1)

print("\n🔑 PROBANDO CONEXIÓN A LA API...")

try:
    api = TrackSolidAPI(APP_KEY, APP_SECRET, USER_EMAIL, USER_PASSWORD)
    
    print("   Solicitando token...")
    if api.obtener_token():
        print(f"   ✅ Token obtenido: {api.access_token[:20]}...")
        
        print("\n📱 OBTENIENDO DISPOSITIVOS...")
        dispositivos = api.listar_dispositivos()
        
        if dispositivos:
            print(f"   ✅ Se encontraron {len(dispositivos)} dispositivos:")
            for i, disp in enumerate(dispositivos, 1):
                print(f"\n   {i}. {disp.get('deviceName', 'Sin nombre')}")
                print(f"      IMEI: {disp.get('imei')}")
                print(f"      Modelo: {disp.get('mcType')}")
                print(f"      Estado: {'Activo' if disp.get('enabledFlag') == 1 else 'Inactivo'}")
                
                # Intentar obtener ubicación
                print(f"      Obteniendo ubicación...")
                try:
                    ubicacion = api.obtener_ubicacion(disp.get('imei'))
                    if ubicacion:
                        print(f"      ✅ Ubicación: {ubicacion.get('lat')}, {ubicacion.get('lng')}")
                        print(f"      Velocidad: {ubicacion.get('speed')} km/h")
                        print(f"      Estado GPS: {ubicacion.get('status')}")
                    else:
                        print(f"      ⚠️ No se obtuvo ubicación")
                except Exception as e:
                    print(f"      ❌ Error: {str(e)}")
        else:
            print("   ⚠️ No se encontraron dispositivos")
            print("\n   Posibles causas:")
            print("   - No hay dispositivos asociados a esta cuenta")
            print("   - Las credenciales son de otra cuenta")
            print("   - Problema de permisos en la API")
    else:
        print("   ❌ No se pudo obtener token")
        print("\n   Verifica:")
        print("   - Que las credenciales sean correctas")
        print("   - Que la cuenta esté activa")
        print("   - Que no haya problemas de red")
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("FIN DEL TEST")
print("="*80)
