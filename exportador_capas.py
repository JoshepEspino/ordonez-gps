"""
EXPORTADOR DE CAPAS GEOESPACIALES
=================================
Exporta datos GPS a diferentes formatos compatibles con SIG

Formatos soportados:
- CSV (Comma Separated Values)
- GeoJSON (Geographic JSON)
- KML (Keyhole Markup Language)
- GeoRSS (Geographic RSS)
- WFS-compatible JSON
"""

import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
import os

class ExportadorCapas:
    """Clase para exportar datos GPS a diferentes formatos geoespaciales"""
    
    def __init__(self):
        self.formatos_soportados = [
            'csv', 'geojson', 'kml', 'georss', 'wfs_json'
        ]
    
    def exportar_csv(self, datos: List[Dict], archivo: str) -> bool:
        """
        Exporta datos GPS a formato CSV
        
        Args:
            datos: Lista de ubicaciones GPS
            archivo: Nombre del archivo de salida
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if not datos:
                print("⚠️ No hay datos para exportar")
                return False
            
            # Obtener todas las claves únicas
            campos = set()
            for dato in datos:
                campos.update(dato.keys())
            
            # Campos específicos para GPS en orden
            campos_gps = [
                'deviceName', 'imei', 'lat', 'lng', 'speed', 'direction',
                'gpsTime', 'accStatus', 'status', 'gpsNum', 'powerValue',
                'locDesc', 'posType'
            ]
            
            # Organizar campos: GPS primero, luego el resto
            campos_ordenados = []
            for campo in campos_gps:
                if campo in campos:
                    campos_ordenados.append(campo)
                    campos.remove(campo)
            campos_ordenados.extend(sorted(campos))
            
            with open(archivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=campos_ordenados)
                writer.writeheader()
                writer.writerows(datos)
            
            print(f"✅ CSV exportado: {archivo} ({len(datos)} registros)")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando CSV: {str(e)}")
            return False
    
    def exportar_geojson(self, datos: List[Dict], archivo: str) -> bool:
        """
        Exporta datos GPS a formato GeoJSON
        
        Args:
            datos: Lista de ubicaciones GPS
            archivo: Nombre del archivo de salida
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if not datos:
                print("⚠️ No hay datos para exportar")
                return False
            
            features = []
            
            for dato in datos:
                # Verificar que tenga coordenadas válidas
                lat = dato.get('lat')
                lng = dato.get('lng')
                
                if lat is None or lng is None:
                    continue
                
                try:
                    lat = float(lat)
                    lng = float(lng)
                except (ValueError, TypeError):
                    continue
                
                # Crear propiedades (todos los campos excepto coordenadas)
                propiedades = {k: v for k, v in dato.items() if k not in ['lat', 'lng']}
                
                # Crear feature GeoJSON
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]  # GeoJSON usa [lng, lat]
                    },
                    "properties": propiedades
                }
                
                features.append(feature)
            
            # Crear FeatureCollection
            geojson = {
                "type": "FeatureCollection",
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": "EPSG:4326"
                    }
                },
                "features": features,
                "metadata": {
                    "generated": datetime.now().isoformat(),
                    "source": "TrackSolidPro GPS Tracker",
                    "total_features": len(features)
                }
            }
            
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, indent=2, ensure_ascii=False)
            
            print(f"✅ GeoJSON exportado: {archivo} ({len(features)} features)")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando GeoJSON: {str(e)}")
            return False
    
    def exportar_kml(self, datos: List[Dict], archivo: str) -> bool:
        """
        Exporta datos GPS a formato KML
        
        Args:
            datos: Lista de ubicaciones GPS
            archivo: Nombre del archivo de salida
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if not datos:
                print("⚠️ No hay datos para exportar")
                return False
            
            # Crear elemento raíz KML
            kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
            document = ET.SubElement(kml, "Document")
            
            # Metadatos del documento
            name = ET.SubElement(document, "name")
            name.text = "GPS Tracking Data - TrackSolidPro"
            
            description = ET.SubElement(document, "description")
            description.text = f"Datos GPS exportados el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Estilo para los puntos
            style = ET.SubElement(document, "Style", id="gpsPoint")
            icon_style = ET.SubElement(style, "IconStyle")
            icon = ET.SubElement(icon_style, "Icon")
            href = ET.SubElement(icon, "href")
            href.text = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
            
            # Crear placemarks para cada punto
            for i, dato in enumerate(datos):
                lat = dato.get('lat')
                lng = dato.get('lng')
                
                if lat is None or lng is None:
                    continue
                
                try:
                    lat = float(lat)
                    lng = float(lng)
                except (ValueError, TypeError):
                    continue
                
                placemark = ET.SubElement(document, "Placemark")
                
                # Nombre del placemark
                name_elem = ET.SubElement(placemark, "name")
                device_name = dato.get('deviceName', f'Dispositivo {i+1}')
                name_elem.text = f"{device_name} - {dato.get('gpsTime', 'Sin fecha')}"
                
                # Descripción con detalles
                desc = ET.SubElement(placemark, "description")
                desc_text = f"""
                <![CDATA[
                <table border="1" style="border-collapse: collapse;">
                    <tr><td><b>Dispositivo:</b></td><td>{dato.get('deviceName', 'N/A')}</td></tr>
                    <tr><td><b>IMEI:</b></td><td>{dato.get('imei', 'N/A')}</td></tr>
                    <tr><td><b>Velocidad:</b></td><td>{dato.get('speed', 'N/A')} km/h</td></tr>
                    <tr><td><b>Dirección:</b></td><td>{dato.get('direction', 'N/A')}°</td></tr>
                    <tr><td><b>Fecha GPS:</b></td><td>{dato.get('gpsTime', 'N/A')}</td></tr>
                    <tr><td><b>Estado ACC:</b></td><td>{'Encendido' if dato.get('accStatus') == '1' else 'Apagado'}</td></tr>
                    <tr><td><b>Estado:</b></td><td>{'Online' if dato.get('status') == '1' else 'Offline'}</td></tr>
                    <tr><td><b>Satélites:</b></td><td>{dato.get('gpsNum', 'N/A')}</td></tr>
                    <tr><td><b>Batería:</b></td><td>{dato.get('powerValue', 'N/A')}%</td></tr>
                </table>
                ]]>
                """
                desc.text = desc_text
                
                # Referencia al estilo
                style_url = ET.SubElement(placemark, "styleUrl")
                style_url.text = "#gpsPoint"
                
                # Coordenadas
                point = ET.SubElement(placemark, "Point")
                coordinates = ET.SubElement(point, "coordinates")
                coordinates.text = f"{lng},{lat},0"  # KML usa lng,lat,altitude
            
            # Escribir archivo KML
            tree = ET.ElementTree(kml)
            ET.indent(tree, space="  ", level=0)  # Formatear XML
            tree.write(archivo, encoding='utf-8', xml_declaration=True)
            
            print(f"✅ KML exportado: {archivo} ({len([d for d in datos if d.get('lat') and d.get('lng')])} placemarks)")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando KML: {str(e)}")
            return False
    
    def exportar_georss(self, datos: List[Dict], archivo: str) -> bool:
        """
        Exporta datos GPS a formato GeoRSS
        
        Args:
            datos: Lista de ubicaciones GPS
            archivo: Nombre del archivo de salida
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if not datos:
                print("⚠️ No hay datos para exportar")
                return False
            
            # Crear elemento raíz RSS
            rss = ET.Element("rss", version="2.0")
            rss.set("xmlns:georss", "http://www.georss.org/georss")
            rss.set("xmlns:gml", "http://www.opengis.net/gml")
            
            channel = ET.SubElement(rss, "channel")
            
            # Metadatos del canal
            title = ET.SubElement(channel, "title")
            title.text = "GPS Tracking Feed - TrackSolidPro"
            
            description = ET.SubElement(channel, "description")
            description.text = "Feed de datos GPS en tiempo real"
            
            link = ET.SubElement(channel, "link")
            link.text = "http://localhost:8000"
            
            # Crear items para cada punto GPS
            for dato in datos:
                lat = dato.get('lat')
                lng = dato.get('lng')
                
                if lat is None or lng is None:
                    continue
                
                try:
                    lat = float(lat)
                    lng = float(lng)
                except (ValueError, TypeError):
                    continue
                
                item = ET.SubElement(channel, "item")
                
                # Título del item
                item_title = ET.SubElement(item, "title")
                device_name = dato.get('deviceName', 'Dispositivo GPS')
                item_title.text = f"{device_name} - {dato.get('gpsTime', 'Sin fecha')}"
                
                # Descripción
                item_desc = ET.SubElement(item, "description")
                item_desc.text = f"Velocidad: {dato.get('speed', 'N/A')} km/h, Estado: {'Online' if dato.get('status') == '1' else 'Offline'}"
                
                # Coordenadas GeoRSS
                georss_point = ET.SubElement(item, "georss:point")
                georss_point.text = f"{lat} {lng}"
                
                # GUID único
                guid = ET.SubElement(item, "guid")
                guid.text = f"{dato.get('imei', 'unknown')}_{dato.get('gpsTime', datetime.now().isoformat())}"
                
                # Fecha de publicación
                pub_date = ET.SubElement(item, "pubDate")
                try:
                    # Intentar convertir fecha GPS a formato RSS
                    gps_time = dato.get('gpsTime', '')
                    if gps_time:
                        dt = datetime.strptime(gps_time, '%Y-%m-%d %H:%M:%S')
                        pub_date.text = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
                    else:
                        pub_date.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
                except:
                    pub_date.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # Escribir archivo GeoRSS
            tree = ET.ElementTree(rss)
            ET.indent(tree, space="  ", level=0)
            tree.write(archivo, encoding='utf-8', xml_declaration=True)
            
            print(f"✅ GeoRSS exportado: {archivo} ({len([d for d in datos if d.get('lat') and d.get('lng')])} items)")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando GeoRSS: {str(e)}")
            return False
    
    def exportar_wfs_json(self, datos: List[Dict], archivo: str) -> bool:
        """
        Exporta datos GPS a formato JSON compatible con WFS
        
        Args:
            datos: Lista de ubicaciones GPS
            archivo: Nombre del archivo de salida
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if not datos:
                print("⚠️ No hay datos para exportar")
                return False
            
            features = []
            
            for dato in datos:
                lat = dato.get('lat')
                lng = dato.get('lng')
                
                if lat is None or lng is None:
                    continue
                
                try:
                    lat = float(lat)
                    lng = float(lng)
                except (ValueError, TypeError):
                    continue
                
                # Crear feature compatible con WFS
                feature = {
                    "type": "Feature",
                    "id": f"gps.{dato.get('imei', 'unknown')}.{len(features) + 1}",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    },
                    "geometry_name": "geom",
                    "properties": {
                        "device_name": dato.get('deviceName'),
                        "imei": dato.get('imei'),
                        "speed": dato.get('speed'),
                        "direction": dato.get('direction'),
                        "gps_time": dato.get('gpsTime'),
                        "acc_status": dato.get('accStatus'),
                        "status": dato.get('status'),
                        "gps_num": dato.get('gpsNum'),
                        "power_value": dato.get('powerValue'),
                        "location_desc": dato.get('locDesc'),
                        "pos_type": dato.get('posType')
                    }
                }
                
                features.append(feature)
            
            # Crear respuesta WFS
            wfs_response = {
                "type": "FeatureCollection",
                "totalFeatures": len(features),
                "features": features,
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": "EPSG:4326"
                    }
                },
                "bbox": self._calcular_bbox(features) if features else None
            }
            
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(wfs_response, f, indent=2, ensure_ascii=False)
            
            print(f"✅ WFS JSON exportado: {archivo} ({len(features)} features)")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando WFS JSON: {str(e)}")
            return False
    
    def _calcular_bbox(self, features: List[Dict]) -> List[float]:
        """Calcula el bounding box de las features"""
        if not features:
            return None
        
        lngs = []
        lats = []
        
        for feature in features:
            coords = feature.get('geometry', {}).get('coordinates', [])
            if len(coords) >= 2:
                lngs.append(coords[0])
                lats.append(coords[1])
        
        if not lngs or not lats:
            return None
        
        return [min(lngs), min(lats), max(lngs), max(lats)]
    
    def exportar_multiples_formatos(self, datos: List[Dict], nombre_base: str, formatos: List[str] = None) -> Dict[str, bool]:
        """
        Exporta datos a múltiples formatos
        
        Args:
            datos: Lista de ubicaciones GPS
            nombre_base: Nombre base para los archivos (sin extensión)
            formatos: Lista de formatos a exportar (None = todos)
            
        Returns:
            Diccionario con el resultado de cada exportación
        """
        if formatos is None:
            formatos = self.formatos_soportados
        
        resultados = {}
        
        for formato in formatos:
            if formato not in self.formatos_soportados:
                print(f"⚠️ Formato no soportado: {formato}")
                resultados[formato] = False
                continue
            
            archivo = f"{nombre_base}.{formato.replace('_', '.')}"
            
            if formato == 'csv':
                resultados[formato] = self.exportar_csv(datos, archivo)
            elif formato == 'geojson':
                resultados[formato] = self.exportar_geojson(datos, archivo)
            elif formato == 'kml':
                resultados[formato] = self.exportar_kml(datos, archivo)
            elif formato == 'georss':
                resultados[formato] = self.exportar_georss(datos, archivo)
            elif formato == 'wfs_json':
                resultados[formato] = self.exportar_wfs_json(datos, archivo)
        
        return resultados


def crear_capa_teselas_config(datos: List[Dict], nombre: str = "gps_tracking") -> Dict:
    """
    Crea configuración para servicio de teselas
    
    Args:
        datos: Lista de ubicaciones GPS
        nombre: Nombre de la capa
        
    Returns:
        Configuración para servicio de teselas
    """
    if not datos:
        return {}
    
    # Calcular extent de los datos
    lats = [float(d.get('lat', 0)) for d in datos if d.get('lat')]
    lngs = [float(d.get('lng', 0)) for d in datos if d.get('lng')]
    
    if not lats or not lngs:
        return {}
    
    config = {
        "name": nombre,
        "title": "GPS Tracking Layer",
        "description": "Capa de seguimiento GPS en tiempo real",
        "type": "vector",
        "format": "pbf",
        "extent": [min(lngs), min(lats), max(lngs), max(lats)],
        "center": [sum(lngs)/len(lngs), sum(lats)/len(lats)],
        "minzoom": 0,
        "maxzoom": 18,
        "attribution": "TrackSolidPro GPS Data",
        "properties": {
            "device_name": "string",
            "imei": "string", 
            "speed": "number",
            "direction": "number",
            "gps_time": "string",
            "status": "string"
        }
    }
    
    return config


# Función de utilidad para uso directo
def exportar_datos_gps(datos: List[Dict], nombre_archivo: str, formato: str = 'geojson') -> bool:
    """
    Función de utilidad para exportar datos GPS
    
    Args:
        datos: Lista de ubicaciones GPS
        nombre_archivo: Nombre del archivo (con o sin extensión)
        formato: Formato de exportación
        
    Returns:
        True si se exportó correctamente
    """
    exportador = ExportadorCapas()
    
    # Asegurar extensión correcta
    if not nombre_archivo.endswith(f'.{formato}'):
        nombre_archivo = f"{nombre_archivo}.{formato}"
    
    if formato == 'csv':
        return exportador.exportar_csv(datos, nombre_archivo)
    elif formato == 'geojson':
        return exportador.exportar_geojson(datos, nombre_archivo)
    elif formato == 'kml':
        return exportador.exportar_kml(datos, nombre_archivo)
    elif formato == 'georss':
        return exportador.exportar_georss(datos, nombre_archivo)
    elif formato == 'wfs_json':
        return exportador.exportar_wfs_json(datos, nombre_archivo)
    else:
        print(f"❌ Formato no soportado: {formato}")
        return False


if __name__ == "__main__":
    # Ejemplo de uso
    datos_ejemplo = [
        {
            "deviceName": "Vehículo 001",
            "imei": "869066063791553",
            "lat": -2.1234567,
            "lng": -79.9876543,
            "speed": 45,
            "direction": 180,
            "gpsTime": "2025-01-13 10:30:00",
            "accStatus": "1",
            "status": "1",
            "gpsNum": 8,
            "powerValue": 85
        }
    ]
    
    exportador = ExportadorCapas()
    
    print("🗺️ Exportando datos de ejemplo...")
    resultados = exportador.exportar_multiples_formatos(datos_ejemplo, "ejemplo_gps")
    
    print(f"\n📊 Resultados:")
    for formato, exito in resultados.items():
        estado = "✅" if exito else "❌"
        print(f"   {estado} {formato.upper()}")