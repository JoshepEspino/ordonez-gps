"""
APLICACIÓN WEB GPS PARA GITHUB
==============================
Aplicación web Flask para exportar datos GPS históricos del día

Características:
- Interfaz web moderna
- Exportación de historial del día en GeoJSON
- Compatible con despliegue en Heroku/Railway
- API REST para integración

Ejecutar localmente: python app_web.py
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import tempfile
import threading
import time
from datetime import datetime, timedelta, UTC
from main import TrackSolidAPI
from exportador_capas import ExportadorCapas
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuración desde variables de entorno (para GitHub/Heroku)
CONFIG = {
    "APP_KEY": os.getenv("TRACKSOLID_APP_KEY", "8FB345B8693CCD00E1DFFF7BA374386E339A22A4105B6558"),
    "APP_SECRET": os.getenv("TRACKSOLID_APP_SECRET", "e87788d85cc548808a8a6c1eb66554c0"),
    "USER_EMAIL": os.getenv("TRACKSOLID_EMAIL", "ce.especialistasig@gmail.com"),
    "USER_PASSWORD": os.getenv("TRACKSOLID_PASSWORD", "CorporacionOrdoñez2026*"),
    "AUTO_UPDATE_INTERVAL": int(os.getenv("AUTO_UPDATE_INTERVAL", "30")),  # segundos
    "ENABLE_AUTO_UPDATE": os.getenv("ENABLE_AUTO_UPDATE", "true").lower() == "true"
}

# Variables globales
api_gps = None
dispositivos_cache = []
ubicaciones_cache = {}
ultima_actualizacion = None
auto_update_thread = None
auto_update_active = False

def inicializar_api():
    """Inicializa la conexión con TrackSolidPro"""
    global api_gps, dispositivos_cache, ultima_actualizacion
    
    try:
        api_gps = TrackSolidAPI(
            CONFIG["APP_KEY"],
            CONFIG["APP_SECRET"], 
            CONFIG["USER_EMAIL"],
            CONFIG["USER_PASSWORD"]
        )
        
        if api_gps.obtener_token():
            dispositivos_cache = api_gps.listar_dispositivos() or []
            ultima_actualizacion = datetime.now()
            logger.info(f"API inicializada con {len(dispositivos_cache)} dispositivos")
            
            # Iniciar actualización automática si está habilitada
            if CONFIG["ENABLE_AUTO_UPDATE"]:
                iniciar_actualizacion_automatica()
            
            return True
        else:
            logger.error("Error al obtener token de TrackSolidPro")
            return False
    except Exception as e:
        logger.error(f"Error al inicializar API: {str(e)}")
        return False

def actualizar_ubicaciones_cache():
    """Actualiza el cache de ubicaciones de todos los dispositivos"""
    global ubicaciones_cache, ultima_actualizacion
    
    if not api_gps or not api_gps.access_token:
        return False
    
    try:
        nuevas_ubicaciones = {}
        
        for dispositivo in dispositivos_cache:
            imei = dispositivo.get('imei')
            try:
                ubicacion = api_gps.obtener_ubicacion(imei)
                if ubicacion:
                    nuevas_ubicaciones[imei] = {
                        'ubicacion': ubicacion,
                        'dispositivo': dispositivo,
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                logger.error(f"Error obteniendo ubicación {imei}: {str(e)}")
        
        ubicaciones_cache = nuevas_ubicaciones
        ultima_actualizacion = datetime.now()
        
        logger.info(f"Cache actualizado: {len(nuevas_ubicaciones)} ubicaciones")
        return True
        
    except Exception as e:
        logger.error(f"Error actualizando cache: {str(e)}")
        return False

def actualizacion_automatica():
    """Función que ejecuta la actualización automática en bucle"""
    global auto_update_active
    
    logger.info(f"Iniciando actualización automática cada {CONFIG['AUTO_UPDATE_INTERVAL']} segundos")
    
    while auto_update_active:
        try:
            actualizar_ubicaciones_cache()
            
            # Generar archivo GeoJSON actualizado automáticamente
            if ubicaciones_cache:
                generar_geojson_automatico()
            
            time.sleep(CONFIG["AUTO_UPDATE_INTERVAL"])
            
        except Exception as e:
            logger.error(f"Error en actualización automática: {str(e)}")
            time.sleep(CONFIG["AUTO_UPDATE_INTERVAL"])

def iniciar_actualizacion_automatica():
    """Inicia el hilo de actualización automática"""
    global auto_update_thread, auto_update_active
    
    if auto_update_active:
        return True
    
    auto_update_active = True
    auto_update_thread = threading.Thread(target=actualizacion_automatica, daemon=True)
    auto_update_thread.start()
    
    logger.info("Actualización automática iniciada")
    return True

def detener_actualizacion_automatica():
    """Detiene la actualización automática"""
    global auto_update_active
    
    auto_update_active = False
    logger.info("Actualización automática detenida")
    return True

def generar_geojson_automatico():
    """Genera archivo GeoJSON actualizado automáticamente"""
    try:
        if not ubicaciones_cache:
            return False
        
        # Preparar datos para exportación
        ubicaciones_para_exportar = []
        for imei, data in ubicaciones_cache.items():
            ubicacion = data['ubicacion']
            ubicacion['deviceName'] = data['dispositivo'].get('deviceName', 'Sin nombre')
            ubicacion['imei'] = imei
            ubicaciones_para_exportar.append(ubicacion)
        
        # Crear archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"ubicaciones_actuales_{timestamp}.geojson"
        
        # Exportar
        exportador = ExportadorCapas()
        if exportador.exportar_geojson(ubicaciones_para_exportar, nombre_archivo):
            logger.info(f"GeoJSON automático generado: {nombre_archivo}")
            
            # Mantener solo los últimos 5 archivos para no llenar el disco
            limpiar_archivos_antiguos()
            
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error generando GeoJSON automático: {str(e)}")
        return False

def limpiar_archivos_antiguos():
    """Limpia archivos GeoJSON antiguos, manteniendo solo los últimos 5"""
    try:
        import glob
        
        archivos = glob.glob("ubicaciones_actuales_*.geojson")
        archivos.sort(reverse=True)  # Más recientes primero
        
        # Eliminar archivos antiguos (mantener solo los últimos 5)
        for archivo in archivos[5:]:
            try:
                os.remove(archivo)
                logger.info(f"Archivo antiguo eliminado: {archivo}")
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error limpiando archivos antiguos: {str(e)}")

def obtener_historial_dia(imei, fecha=None):
    """Obtiene el historial completo de un día específico"""
    if not api_gps or not api_gps.access_token:
        return None
    
    if fecha is None:
        fecha = datetime.now().date()
    elif isinstance(fecha, str):
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
    
    # Definir inicio y fin del día
    inicio = datetime.combine(fecha, datetime.min.time())
    fin = datetime.combine(fecha, datetime.max.time())
    
    # Formatear fechas para la API
    fecha_inicio = inicio.strftime('%Y-%m-%d %H:%M:%S')
    fecha_fin = fin.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        historial = api_gps.obtener_historial_ruta(imei, fecha_inicio, fecha_fin)
        return historial
    except Exception as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        return None

# =============================================================================
# RUTAS WEB
# =============================================================================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/dispositivos')
def api_dispositivos():
    """API: Lista de dispositivos"""
    try:
        if not dispositivos_cache:
            if not inicializar_api():
                return jsonify({
                    "success": False,
                    "error": "No se pudo conectar con TrackSolidPro"
                }), 503
        
        return jsonify({
            "success": True,
            "dispositivos": dispositivos_cache,
            "total": len(dispositivos_cache),
            "ultima_actualizacion": ultima_actualizacion.isoformat() if ultima_actualizacion else None
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo dispositivos: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/historial/<imei>')
def api_historial(imei):
    """API: Historial de un dispositivo"""
    try:
        fecha = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        
        historial = obtener_historial_dia(imei, fecha)
        
        if historial is None:
            return jsonify({
                "success": False,
                "error": "No se pudo obtener historial"
            }), 404
        
        return jsonify({
            "success": True,
            "imei": imei,
            "fecha": fecha,
            "total_puntos": len(historial),
            "historial": historial
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/exportar/historial/<imei>/geojson')
def api_exportar_historial_geojson(imei):
    """API: Exportar historial del día en GeoJSON"""
    try:
        fecha = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        
        # Obtener historial
        historial = obtener_historial_dia(imei, fecha)
        
        if not historial:
            return jsonify({
                "success": False,
                "error": f"No se encontró historial para {imei} en {fecha}"
            }), 404
        
        # Crear archivo temporal
        exportador = ExportadorCapas()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.geojson', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Exportar a GeoJSON
        if not exportador.exportar_geojson(historial, temp_path):
            os.unlink(temp_path)
            return jsonify({
                "success": False,
                "error": "Error exportando a GeoJSON"
            }), 500
        
        # Nombre del archivo de descarga
        device_name = next((d.get('deviceName', imei) for d in dispositivos_cache if d.get('imei') == imei), imei)
        nombre_descarga = f"historial_{device_name}_{fecha}.geojson".replace(' ', '_')
        
        def cleanup():
            """Limpia el archivo temporal"""
            try:
                os.unlink(temp_path)
            except:
                pass
        
        # Programar limpieza después de 2 minutos
        threading.Timer(120.0, cleanup).start()
        
        return send_file(
            temp_path,
            mimetype='application/geo+json',
            as_attachment=True,
            download_name=nombre_descarga
        )
        
    except Exception as e:
        logger.error(f"Error exportando historial: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/exportar/todos/geojson')
def api_exportar_todos_geojson():
    """API: Exportar historial del día de todos los dispositivos"""
    try:
        fecha = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        
        if not dispositivos_cache:
            return jsonify({
                "success": False,
                "error": "No hay dispositivos disponibles"
            }), 404
        
        # Obtener historial de todos los dispositivos
        todos_historiales = []
        
        for dispositivo in dispositivos_cache:
            imei = dispositivo.get('imei')
            historial = obtener_historial_dia(imei, fecha)
            
            if historial:
                # Agregar información del dispositivo a cada punto
                for punto in historial:
                    punto['deviceName'] = dispositivo.get('deviceName', 'Sin nombre')
                    punto['imei'] = imei
                
                todos_historiales.extend(historial)
        
        if not todos_historiales:
            return jsonify({
                "success": False,
                "error": f"No se encontró historial para ningún dispositivo en {fecha}"
            }), 404
        
        # Crear archivo temporal
        exportador = ExportadorCapas()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.geojson', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Exportar a GeoJSON
        if not exportador.exportar_geojson(todos_historiales, temp_path):
            os.unlink(temp_path)
            return jsonify({
                "success": False,
                "error": "Error exportando a GeoJSON"
            }), 500
        
        # Nombre del archivo de descarga
        nombre_descarga = f"historial_completo_{fecha}.geojson"
        
        def cleanup():
            """Limpia el archivo temporal"""
            try:
                os.unlink(temp_path)
            except:
                pass
        
        # Programar limpieza después de 2 minutos
        threading.Timer(120.0, cleanup).start()
        
        return send_file(
            temp_path,
            mimetype='application/geo+json',
            as_attachment=True,
            download_name=nombre_descarga
        )
        
    except Exception as e:
        logger.error(f"Error exportando todos los historiales: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/ubicaciones/actuales')
def api_ubicaciones_actuales():
    """API: Ubicaciones actuales en cache"""
    try:
        if not ubicaciones_cache:
            # Si no hay cache, intentar actualizar
            actualizar_ubicaciones_cache()
        
        ubicaciones_lista = []
        for imei, data in ubicaciones_cache.items():
            ubicaciones_lista.append({
                "imei": imei,
                "nombre": data['dispositivo'].get('deviceName', 'Sin nombre'),
                "ubicacion": data['ubicacion'],
                "timestamp": data['timestamp']
            })
        
        return jsonify({
            "success": True,
            "ubicaciones": ubicaciones_lista,
            "total": len(ubicaciones_lista),
            "ultima_actualizacion": ultima_actualizacion.isoformat() if ultima_actualizacion else None,
            "auto_update_activo": auto_update_active,
            "intervalo_actualizacion": CONFIG["AUTO_UPDATE_INTERVAL"]
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo ubicaciones actuales: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/auto-update/start', methods=['POST'])
def api_iniciar_auto_update():
    """API: Iniciar actualización automática"""
    try:
        if iniciar_actualizacion_automatica():
            return jsonify({
                "success": True,
                "message": "Actualización automática iniciada",
                "intervalo": CONFIG["AUTO_UPDATE_INTERVAL"]
            })
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo iniciar la actualización automática"
            }), 500
    
    except Exception as e:
        logger.error(f"Error iniciando auto-update: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/auto-update/stop', methods=['POST'])
def api_detener_auto_update():
    """API: Detener actualización automática"""
    try:
        detener_actualizacion_automatica()
        return jsonify({
            "success": True,
            "message": "Actualización automática detenida"
        })
    
    except Exception as e:
        logger.error(f"Error deteniendo auto-update: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/auto-update/status')
def api_status_auto_update():
    """API: Estado de la actualización automática"""
    try:
        return jsonify({
            "success": True,
            "auto_update_activo": auto_update_active,
            "intervalo_segundos": CONFIG["AUTO_UPDATE_INTERVAL"],
            "ubicaciones_en_cache": len(ubicaciones_cache),
            "ultima_actualizacion": ultima_actualizacion.isoformat() if ultima_actualizacion else None
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo status auto-update: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/exportar/actuales/geojson')
def api_exportar_ubicaciones_actuales():
    """API: Exportar ubicaciones actuales del cache en GeoJSON"""
    try:
        if not ubicaciones_cache:
            return jsonify({
                "success": False,
                "error": "No hay ubicaciones en cache"
            }), 404
        
        # Preparar datos para exportación
        ubicaciones_para_exportar = []
        for imei, data in ubicaciones_cache.items():
            ubicacion = data['ubicacion']
            ubicacion['deviceName'] = data['dispositivo'].get('deviceName', 'Sin nombre')
            ubicacion['imei'] = imei
            ubicaciones_para_exportar.append(ubicacion)
        
        # Crear archivo temporal
        exportador = ExportadorCapas()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.geojson', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Exportar a GeoJSON
        if not exportador.exportar_geojson(ubicaciones_para_exportar, temp_path):
            os.unlink(temp_path)
            return jsonify({
                "success": False,
                "error": "Error exportando a GeoJSON"
            }), 500
        
        # Nombre del archivo de descarga
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_descarga = f"ubicaciones_actuales_{timestamp}.geojson"
        
        def cleanup():
            """Limpia el archivo temporal"""
            try:
                os.unlink(temp_path)
            except:
                pass
        
        # Programar limpieza después de 2 minutos
        threading.Timer(120.0, cleanup).start()
        
        return send_file(
            temp_path,
            mimetype='application/geo+json',
            as_attachment=True,
            download_name=nombre_descarga
        )
        
    except Exception as e:
        logger.error(f"Error exportando ubicaciones actuales: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/status')
def api_status():
    """API: Estado del sistema"""
    return jsonify({
        "status": "online",
        "api_inicializada": api_gps is not None and api_gps.access_token is not None,
        "dispositivos": len(dispositivos_cache),
        "ubicaciones_en_cache": len(ubicaciones_cache),
        "auto_update_activo": auto_update_active,
        "intervalo_actualizacion": CONFIG["AUTO_UPDATE_INTERVAL"],
        "ultima_actualizacion": ultima_actualizacion.isoformat() if ultima_actualizacion else None,
        "timestamp": datetime.now(UTC).isoformat()
    })

# =============================================================================
# INICIALIZACIÓN
# =============================================================================

if __name__ == '__main__':
    print("="*80)
    print("🛰️ APLICACIÓN WEB GPS - GITHUB READY")
    print("="*80)
    
    # Inicializar API
    print("🔑 Inicializando conexión con TrackSolidPro...")
    if inicializar_api():
        print(f"✅ API inicializada con {len(dispositivos_cache)} dispositivos")
    else:
        print("⚠️ API no inicializada, se intentará conectar en el primer uso")
    
    # Configuración del servidor
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"\n🌐 Servidor iniciando en puerto {port}")
    print(f"📱 Accede a: http://localhost:{port}")
    print(f"🔧 Modo debug: {debug}")
    
    if not debug:
        print(f"\n🚀 Listo para despliegue en:")
        print(f"   • Heroku")
        print(f"   • Railway") 
        print(f"   • Render")
        print(f"   • DigitalOcean App Platform")
    
    app.run(host='0.0.0.0', port=port, debug=debug)