"""
APLICACIÓN GPS SIMPLIFICADA
===========================
Muestra el último estado GPS actualizado automáticamente
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import os
import time
import threading
from datetime import datetime, UTC
from main import TrackSolidAPI

app = Flask(__name__)
CORS(app)

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv()

# Configuración desde variables de entorno
CONFIG = {
    "APP_KEY": os.getenv("TRACKSOLID_APP_KEY"),
    "APP_SECRET": os.getenv("TRACKSOLID_APP_SECRET"),
    "USER_EMAIL": os.getenv("TRACKSOLID_EMAIL"),
    "USER_PASSWORD": os.getenv("TRACKSOLID_PASSWORD"),
    "INTERVALO": int(os.getenv("INTERVALO_ACTUALIZACION", "30"))  # segundos
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

# Variables globales
api_gps = None
ubicaciones_actuales = []
ultima_actualizacion = None

def inicializar_api():
    """Inicializa la API"""
    global api_gps
    
    print("\n🔑 Inicializando API TrackSolidPro...")
    print(f"   Email: {CONFIG['USER_EMAIL']}")
    print(f"   APP_KEY configurado: {bool(CONFIG['APP_KEY'])}")
    print(f"   APP_SECRET configurado: {bool(CONFIG['APP_SECRET'])}")
    print(f"   PASSWORD configurado: {bool(CONFIG['USER_PASSWORD'])}")
    
    try:
        api_gps = TrackSolidAPI(
            CONFIG["APP_KEY"],
            CONFIG["APP_SECRET"], 
            CONFIG["USER_EMAIL"],
            CONFIG["USER_PASSWORD"]
        )
        
        print("   Solicitando token de acceso...")
        if api_gps.obtener_token():
            print(f"   ✅ Token obtenido: {api_gps.access_token[:20]}...")
            print(f"   ✅ API inicializada correctamente")
            return True
        else:
            print("   ❌ Error al obtener token")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def actualizar_ubicaciones():
    """Actualiza las ubicaciones de todos los dispositivos"""
    global ubicaciones_actuales, ultima_actualizacion
    
    if not api_gps or not api_gps.access_token:
        print("⚠️ API no inicializada o sin token")
        return
    
    try:
        print("📱 Solicitando lista de dispositivos...")
        dispositivos = api_gps.listar_dispositivos()
        
        if not dispositivos:
            print("⚠️ No se obtuvieron dispositivos de la API")
            return
        
        print(f"✅ Se encontraron {len(dispositivos)} dispositivos")
        
        nuevas_ubicaciones = []
        
        for disp in dispositivos:
            imei = disp.get('imei')
            nombre = disp.get('deviceName', 'Sin nombre')
            print(f"📍 Obteniendo ubicación de {nombre} ({imei})...")
            
            try:
                ubicacion = api_gps.obtener_ubicacion(imei)
                if ubicacion:
                    ubicacion['deviceName'] = nombre
                    ubicacion['imei'] = imei
                    nuevas_ubicaciones.append(ubicacion)
                    print(f"   ✅ Ubicación obtenida: {ubicacion.get('lat')}, {ubicacion.get('lng')}")
                else:
                    print(f"   ⚠️ No se obtuvo ubicación para {nombre}")
            except Exception as e:
                print(f"   ❌ Error obteniendo ubicación {imei}: {str(e)}")
        
        ubicaciones_actuales = nuevas_ubicaciones
        ultima_actualizacion = datetime.now()
        
        print(f"📡 Actualizado: {len(nuevas_ubicaciones)} dispositivos con ubicación")
        
    except Exception as e:
        print(f"❌ Error actualizando: {str(e)}")
        import traceback
        traceback.print_exc()

def bucle_actualizacion():
    print(f"🔄 Iniciando actualización automática cada {CONFIG['INTERVALO']} segundos")
    
    while True:
        try:
            actualizar_ubicaciones()
            time.sleep(CONFIG["INTERVALO"])
        except Exception as e:
            print(f"❌ Error en bucle: {str(e)}")
            time.sleep(CONFIG["INTERVALO"])

# Template HTML simplificado
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
    <title>GPS Tracker - Estado Actual</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
        }
        .card {
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        .device-card {
            transition: transform 0.2s;
        }
        .device-card:hover {
            transform: translateY(-5px);
        }
        .status-badge {
            font-size: 0.9rem;
            padding: 5px 10px;
        }
        .update-time {
            font-size: 0.85rem;
            color: #6c757d;
        }
        .metric {
            font-size: 1.5rem;
            font-weight: bold;
        }
        .loading {
            text-align: center;
            padding: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="card mb-4">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h1 class="mb-0">🛰️ GPS Tracker</h1>
                        <p class="mb-0 text-muted">Estado actual de dispositivos</p>
                    </div>
                    <div class="col-md-4 text-end">
                        <div id="ultimaActualizacion" class="update-time">
                            Cargando...
                        </div>
                        <span class="badge bg-success status-badge">
                            <span id="estadoConexion">🔄 Actualizando</span>
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Dispositivos -->
        <div id="dispositivosContainer" class="row">
            <div class="col-12 loading">
                <div class="spinner-border text-light" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="text-light mt-3">Cargando dispositivos...</p>
            </div>
        </div>
    </div>

    <script>
        let intervaloActualizacion = {{ intervalo }} * 1000;

        function formatearFecha(fecha) {
            if (!fecha) return 'N/A';
            const d = new Date(fecha);
            return d.toLocaleString('es-PE', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }

        function crearTarjetaDispositivo(dispositivo) {
            const estado = dispositivo.status === '1' ? 'Online' : 'Offline';
            const colorEstado = dispositivo.status === '1' ? 'success' : 'danger';
            const acc = dispositivo.accStatus === '1' ? 'Encendido' : 'Apagado';
            const colorAcc = dispositivo.accStatus === '1' ? 'success' : 'secondary';

            return `
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card device-card h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <h5 class="card-title mb-0">${dispositivo.deviceName}</h5>
                                <span class="badge bg-${colorEstado}">${estado}</span>
                            </div>
                            
                            <div class="mb-3">
                                <small class="text-muted">IMEI: ${dispositivo.imei}</small>
                            </div>

                            <div class="row text-center mb-3">
                                <div class="col-6">
                                    <div class="metric text-primary">${dispositivo.speed || 0}</div>
                                    <small class="text-muted">km/h</small>
                                </div>
                                <div class="col-6">
                                    <div class="metric text-info">${dispositivo.direction || 0}°</div>
                                    <small class="text-muted">Dirección</small>
                                </div>
                            </div>

                            <div class="mb-2">
                                <strong>📍 Coordenadas:</strong><br>
                                <small>Lat: ${dispositivo.lat || 'N/A'}</small><br>
                                <small>Lng: ${dispositivo.lng || 'N/A'}</small>
                            </div>

                            <div class="mb-2">
                                <strong>🕒 Fecha GPS:</strong><br>
                                <small>${dispositivo.gpsTime || 'N/A'}</small>
                            </div>

                            <div class="mb-2">
                                <strong>🔑 ACC:</strong>
                                <span class="badge bg-${colorAcc} ms-2">${acc}</span>
                            </div>

                            <div class="mb-2">
                                <strong>🛰️ Satélites:</strong>
                                <span class="ms-2">${dispositivo.gpsNum || 'N/A'}</span>
                            </div>

                            <div>
                                <strong>🔋 Batería:</strong>
                                <span class="ms-2">${dispositivo.powerValue || 'N/A'}%</span>
                            </div>

                            ${dispositivo.locDesc ? `
                                <div class="mt-3">
                                    <small class="text-muted">📍 ${dispositivo.locDesc}</small>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }

        function actualizarDispositivos() {
            fetch('/api/ubicaciones')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const container = document.getElementById('dispositivosContainer');
                        
                        if (data.ubicaciones.length === 0) {
                            container.innerHTML = `
                                <div class="col-12">
                                    <div class="alert alert-warning">
                                        ⚠️ No se encontraron dispositivos
                                    </div>
                                </div>
                            `;
                        } else {
                            container.innerHTML = data.ubicaciones
                                .map(disp => crearTarjetaDispositivo(disp))
                                .join('');
                        }

                        // Actualizar tiempo
                        document.getElementById('ultimaActualizacion').textContent = 
                            'Última actualización: ' + formatearFecha(data.ultima_actualizacion);
                        
                        document.getElementById('estadoConexion').textContent = 
                            '✅ Conectado';
                    } else {
                        document.getElementById('estadoConexion').textContent = 
                            '❌ Error';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('estadoConexion').textContent = 
                        '⚠️ Sin conexión';
                });
        }

        // Actualizar inmediatamente al cargar
        actualizarDispositivos();

        // Actualizar automáticamente
        setInterval(actualizarDispositivos, intervaloActualizacion);

        // Mostrar siguiente actualización
        setInterval(() => {
            const badge = document.querySelector('.status-badge');
            badge.classList.add('pulse');
            setTimeout(() => badge.classList.remove('pulse'), 300);
        }, intervaloActualizacion);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal"""
    return render_template_string(HTML_TEMPLATE, intervalo=CONFIG["INTERVALO"])

@app.route('/api/ubicaciones')
def api_ubicaciones():
    """API: Obtiene las ubicaciones actuales"""
    try:
        return jsonify({
            "success": True,
            "ubicaciones": ubicaciones_actuales,
            "total": len(ubicaciones_actuales),
            "ultima_actualizacion": ultima_actualizacion.isoformat() if ultima_actualizacion else None
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/estado')
def api_estado():
    """API: Estado del sistema"""
    return jsonify({
        "status": "online",
        "dispositivos": len(ubicaciones_actuales),
        "intervalo": CONFIG["INTERVALO"],
        "ultima_actualizacion": ultima_actualizacion.isoformat() if ultima_actualizacion else None
    })

@app.route('/api/diagnostico')
def api_diagnostico():
    """API: Diagnóstico del sistema para debugging"""
    try:
        diagnostico = {
            "servidor": {
                "status": "online",
                "timestamp": datetime.now(UTC).isoformat()
            },
            "configuracion": {
                "intervalo": CONFIG["INTERVALO"],
                "app_key_configurado": bool(CONFIG["APP_KEY"]),
                "app_secret_configurado": bool(CONFIG["APP_SECRET"]),
                "email_configurado": bool(CONFIG["USER_EMAIL"]),
                "password_configurado": bool(CONFIG["USER_PASSWORD"]),
                "email": CONFIG["USER_EMAIL"] if CONFIG["USER_EMAIL"] else "NO CONFIGURADO"
            },
            "api": {
                "inicializada": api_gps is not None,
                "token_activo": api_gps.access_token is not None if api_gps else False,
                "token_preview": api_gps.access_token[:20] + "..." if api_gps and api_gps.access_token else "NO TOKEN",
                "token_expira_en": int((api_gps.token_expiration - time.time()) / 60) if api_gps and api_gps.token_expiration else None,
                "token_expira_timestamp": datetime.fromtimestamp(api_gps.token_expiration).isoformat() if api_gps and api_gps.token_expiration else None
            },
            "datos": {
                "ubicaciones_actuales": len(ubicaciones_actuales),
                "ultima_actualizacion": ultima_actualizacion.isoformat() if ultima_actualizacion else None,
                "dispositivos": [
                    {
                        "deviceName": u.get('deviceName'),
                        "imei": u.get('imei'),
                        "status": u.get('status')
                    } for u in ubicaciones_actuales
                ]
            }
        }
        
        # Intentar obtener dispositivos en tiempo real
        if api_gps and api_gps.access_token:
            try:
                dispositivos_raw = api_gps.listar_dispositivos()
                diagnostico["test_api"] = {
                    "success": True,
                    "total_dispositivos": len(dispositivos_raw) if dispositivos_raw else 0,
                    "dispositivos": dispositivos_raw if dispositivos_raw else []
                }
            except Exception as e:
                diagnostico["test_api"] = {
                    "success": False,
                    "error": str(e)
                }
        else:
            diagnostico["test_api"] = {
                "success": False,
                "error": "API no inicializada o sin token"
            }
        
        return jsonify(diagnostico)
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "tipo": type(e).__name__
        }), 500

@app.route('/api/forzar-actualizacion')
def api_forzar_actualizacion():
    """API: Fuerza una actualización inmediata de los dispositivos"""
    try:
        if not api_gps or not api_gps.access_token:
            return jsonify({
                "success": False,
                "error": "API no inicializada o sin token"
            }), 500
        
        print("\n🔄 Forzando actualización manual...")
        actualizar_ubicaciones()
        
        return jsonify({
            "success": True,
            "mensaje": "Actualización forzada completada",
            "dispositivos": len(ubicaciones_actuales),
            "ultima_actualizacion": ultima_actualizacion.isoformat() if ultima_actualizacion else None
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/geojson')
def api_geojson():
    """API: Devuelve las ubicaciones en formato GeoJSON"""
    try:
        features = []
        
        for ubicacion in ubicaciones_actuales:
            # Crear feature GeoJSON para cada dispositivo
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
        
        # Crear FeatureCollection GeoJSON
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total": len(features),
                "ultima_actualizacion": ultima_actualizacion.isoformat() if ultima_actualizacion else None,
                "generado": datetime.now(UTC).isoformat()
            }
        }
        
        return jsonify(geojson)
        
    except Exception as e:
        return jsonify({
            "type": "FeatureCollection",
            "features": [],
            "error": str(e)
        }), 500

# Inicializar la API al importar el módulo (para Gunicorn/Render)
def inicializar_aplicacion():
    """Inicializa la aplicación al arrancar"""
    global api_gps, ubicaciones_actuales, ultima_actualizacion
    
    print("="*80)
    print("🛰️ GPS TRACKER - INICIALIZANDO")
    print("="*80)
    
    if inicializar_api():
        print("✅ API inicializada, obteniendo primera actualización...")
        actualizar_ubicaciones()
        
        # Iniciar bucle de actualización en segundo plano
        hilo = threading.Thread(target=bucle_actualizacion, daemon=True)
        hilo.start()
        print("✅ Bucle de actualización iniciado")
    else:
        print("❌ No se pudo inicializar la API")

# Inicializar automáticamente cuando se importa el módulo
inicializar_aplicacion()

if __name__ == '__main__':
    # Iniciar servidor Flask directamente (para desarrollo local)
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🌐 Servidor iniciando en puerto {port}")
    print(f"📱 Accede a: http://localhost:{port}")
    print(f"🔄 Actualización automática: cada {CONFIG['INTERVALO']} segundos\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)


