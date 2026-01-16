"""
Genera archivos GeoJSON estáticos que puedes compartir o subir a servicios web
Lee las credenciales desde el archivo .env
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
from main import TrackSolidAPI

# Cargar variables de entorno
load_dotenv()

# Configuración desde .env
CONFIG = {
    "APP_KEY": os.getenv("TRACKSOLID_APP_KEY"),
    "APP_SECRET": os.getenv("TRACKSOLID_APP_SECRET"),
    "USER_EMAIL": os.getenv("TRACKSOLID_EMAIL"),
    "USER_PASSWORD": os.getenv("TRACKSOLID_PASSWORD")
}

# Verificar que todas las credenciales estén configuradas
if not all([CONFIG["APP_KEY"], CONFIG["APP_SECRET"], CONFIG["USER_EMAIL"], CONFIG["USER_PASSWORD"]]):
    print("❌ ERROR: Faltan credenciales en el archivo .env")
    print("Por favor, configura las siguientes variables en .env:")
    print("  - TRACKSOLID_APP_KEY")
    print("  - TRACKSOLID_APP_SECRET")
    print("  - TRACKSOLID_EMAIL")
    print("  - TRACKSOLID_PASSWORD")
    exit(1)

def crear_geojson(ubicaciones):
    """Crea un GeoJSON a partir de las ubicaciones"""
    features = []
    
    for ubicacion in ubicaciones:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(ubicacion.get('lng', 0)),
                    float(ubicacion.get('lat', 0))
                ]
            },
            "properties": {
                "deviceName": ubicacion.get('deviceName', 'Sin nombre'),
                "imei": ubicacion.get('imei'),
                "speed": ubicacion.get('speed', 0),
                "direction": ubicacion.get('direction', 0),
                "accStatus": ubicacion.get('accStatus'),
                "gpsTime": ubicacion.get('gpsTime'),
                "status": ubicacion.get('status'),
                "powerValue": ubicacion.get('powerValue'),
                "gpsNum": ubicacion.get('gpsNum'),
                "locDesc": ubicacion.get('locDesc', '')
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "total": len(features),
            "generado": datetime.now().isoformat(),
            "fuente": "TrackSolidPro GPS Tracker"
        }
    }
    
    return geojson

def guardar_geojson(geojson, nombre_archivo):
    """Guarda el GeoJSON en un archivo"""
    carpeta = "geojson_publicos"
    
    # Crear carpeta si no existe
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    ruta_completa = os.path.join(carpeta, nombre_archivo)
    
    with open(ruta_completa, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Guardado: {ruta_completa}")
    return ruta_completa

def main():
    print("="*70)
    print("GENERADOR DE GEOJSON ESTÁTICO")
    print("="*70)
    
    # Inicializar API
    print("\n🔑 Conectando a TrackSolidPro...")
    api = TrackSolidAPI(
        CONFIG["APP_KEY"],
        CONFIG["APP_SECRET"],
        CONFIG["USER_EMAIL"],
        CONFIG["USER_PASSWORD"]
    )
    
    if not api.obtener_token():
        print("❌ Error al conectar")
        return
    
    # Obtener dispositivos
    print("📱 Obteniendo dispositivos...")
    dispositivos = api.listar_dispositivos()
    
    if not dispositivos:
        print("⚠️ No se encontraron dispositivos")
        return
    
    print(f"✅ Se encontraron {len(dispositivos)} dispositivos")
    
    # Obtener ubicaciones
    print("\n📍 Obteniendo ubicaciones...")
    ubicaciones = []
    
    for disp in dispositivos:
        imei = disp.get('imei')
        nombre = disp.get('deviceName', 'Sin nombre')
        
        try:
            ubicacion = api.obtener_ubicacion(imei)
            if ubicacion:
                ubicacion['deviceName'] = nombre
                ubicacion['imei'] = imei
                ubicaciones.append(ubicacion)
                print(f"   ✅ {nombre}")
        except Exception as e:
            print(f"   ❌ {nombre}: {str(e)}")
    
    if not ubicaciones:
        print("\n⚠️ No se pudieron obtener ubicaciones")
        return
    
    print(f"\n✅ Se obtuvieron {len(ubicaciones)} ubicaciones")
    
    # Crear GeoJSON
    print("\n🗺️ Generando GeoJSON...")
    geojson = crear_geojson(ubicaciones)
    
    # Guardar archivos
    print("\n💾 Guardando archivos...")
    
    # Archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    guardar_geojson(geojson, f"ubicaciones_{timestamp}.geojson")
    
    # Archivo actual (siempre actualizado)
    guardar_geojson(geojson, "ubicaciones_actual.geojson")
    
    # Archivo por dispositivo
    for ubicacion in ubicaciones:
        nombre_dispositivo = ubicacion.get('deviceName', 'sin_nombre').replace(' ', '_')
        geojson_individual = crear_geojson([ubicacion])
        guardar_geojson(geojson_individual, f"{nombre_dispositivo}.geojson")
    
    print("\n" + "="*70)
    print("✅ PROCESO COMPLETADO")
    print("="*70)
    print(f"\nArchivos generados en la carpeta: geojson_publicos/")
    print(f"Total de dispositivos: {len(ubicaciones)}")
    print("\n💡 Puedes:")
    print("   - Subir estos archivos a GitHub Pages")
    print("   - Compartirlos en Google Drive")
    print("   - Usarlos en QGIS, ArcGIS, etc.")
    print("   - Incrustarlos en sitios web")
    
    # Mostrar URL de ejemplo para GitHub Pages
    print("\n📌 Ejemplo de URL pública (GitHub Pages):")
    print("   https://tu-usuario.github.io/tu-repo/geojson_publicos/ubicaciones_actual.geojson")

if __name__ == "__main__":
    main()
