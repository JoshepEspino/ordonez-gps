"""
Script para probar y guardar el GeoJSON generado
"""

import requests
import json
from datetime import datetime

# URL del servidor (ajusta si es necesario)
BASE_URL = "http://localhost:5000"

def obtener_geojson():
    """Obtiene el GeoJSON del servidor"""
    try:
        print("📡 Obteniendo GeoJSON...")
        response = requests.get(f"{BASE_URL}/api/geojson")
        response.raise_for_status()
        
        geojson = response.json()
        
        print(f"✅ GeoJSON obtenido correctamente")
        print(f"   Total de dispositivos: {geojson.get('metadata', {}).get('total', 0)}")
        
        return geojson
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        return None

def guardar_geojson(geojson, carpeta="geojson_publicos"):
    """Guarda el GeoJSON en un archivo"""
    import os
    
    # Crear carpeta si no existe
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    # Nombre del archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{carpeta}/ubicaciones_{timestamp}.geojson"
    
    # Guardar
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    
    print(f"💾 GeoJSON guardado en: {nombre_archivo}")
    return nombre_archivo

def guardar_geojson_actual(geojson, carpeta="geojson_publicos"):
    """Guarda el GeoJSON con nombre fijo (siempre actualizado)"""
    import os
    
    # Crear carpeta si no existe
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    nombre_archivo = f"{carpeta}/ubicaciones_actual.geojson"
    
    # Guardar
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    
    print(f"💾 GeoJSON actual guardado en: {nombre_archivo}")
    return nombre_archivo

def mostrar_info_geojson(geojson):
    """Muestra información del GeoJSON"""
    print("\n" + "="*60)
    print("INFORMACIÓN DEL GEOJSON")
    print("="*60)
    
    metadata = geojson.get('metadata', {})
    features = geojson.get('features', [])
    
    print(f"\nTotal de dispositivos: {metadata.get('total', 0)}")
    print(f"Última actualización: {metadata.get('ultima_actualizacion', 'N/A')}")
    print(f"Generado: {metadata.get('generado', 'N/A')}")
    
    if features:
        print(f"\nDispositivos:")
        for i, feature in enumerate(features, 1):
            props = feature.get('properties', {})
            coords = feature.get('geometry', {}).get('coordinates', [0, 0])
            
            print(f"\n{i}. {props.get('deviceName', 'Sin nombre')}")
            print(f"   IMEI: {props.get('imei')}")
            print(f"   Coordenadas: {coords[1]}, {coords[0]}")
            print(f"   Velocidad: {props.get('speed', 0)} km/h")
            print(f"   Estado: {'Online' if props.get('status') == '1' else 'Offline'}")

if __name__ == "__main__":
    print("="*60)
    print("TEST GEOJSON - GPS TRACKER")
    print("="*60)
    print(f"\nAsegúrate de que el servidor esté corriendo en {BASE_URL}")
    print("Ejecuta: python app.py\n")
    
    # Obtener GeoJSON
    geojson = obtener_geojson()
    
    if geojson:
        # Mostrar información
        mostrar_info_geojson(geojson)
        
        # Guardar archivos
        print("\n" + "="*60)
        guardar_geojson(geojson)
        guardar_geojson_actual(geojson)
        
        print("\n✅ Proceso completado")
        print("\n💡 Puedes usar estos archivos en:")
        print("   - QGIS")
        print("   - ArcGIS")
        print("   - Leaflet")
        print("   - Google Maps")
        print("   - Cualquier aplicación que soporte GeoJSON")
