# 🛰️ GPS Tracker Web Service

Aplicación web para exportar datos GPS históricos de dispositivos TrackSolidPro en formato GeoJSON con actualización automática.

## 🚀 Características

- ✅ **Actualización automática** cada 30 segundos
- ✅ **Interfaz web moderna** con Bootstrap 5
- ✅ **Exportación de historial diario** en formato GeoJSON
- ✅ **Ubicaciones en tiempo real**
- ✅ **API REST completa**
- ✅ **Despliegue en Render/Heroku**

## 🌐 Demo en Vivo

**URL de producción:** [Se configurará después del despliegue]

## 🔧 Despliegue en Render

### 1. Subir a GitHub:
```bash
git init
git add .
git commit -m "Initial commit: GPS Tracker Web Service"
git remote add origin https://github.com/TU-USUARIO/gps-tracker-web.git
git push -u origin main
```

### 2. Configurar en Render:
1. Ve a [render.com](https://render.com)
2. Conecta tu repositorio de GitHub
3. Crear **Web Service**
4. Configuración:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3

### 3. Variables de Entorno en Render:
```
TRACKSOLID_APP_KEY=8FB345B8693CCD00E1DFFF7BA374386E339A22A4105B6558
TRACKSOLID_APP_SECRET=e87788d85cc548808a8a6c1eb66554c0
TRACKSOLID_EMAIL=ce.especialistasig@gmail.com
TRACKSOLID_PASSWORD=CorporacionOrdoñez2026*
ENABLE_AUTO_UPDATE=true
AUTO_UPDATE_INTERVAL=30
```

## 🔧 Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python app.py
```

Accede a: http://localhost:5000

## 📡 API Endpoints

- `GET /` - Interfaz web principal
- `GET /api/dispositivos` - Lista de dispositivos
- `GET /api/ubicaciones/actuales` - Ubicaciones en tiempo real
- `GET /api/exportar/actuales/geojson` - Exportar ubicaciones actuales
- `GET /api/exportar/historial/{imei}/geojson` - Exportar historial
- `POST /api/auto-update/start` - Iniciar actualización automática
- `POST /api/auto-update/stop` - Detener actualización automática

## 🗺️ Formato GeoJSON

Los archivos exportados siguen el estándar GeoJSON compatible con:
- QGIS
- ArcGIS  
- Google Earth (convertir a KML)
- Aplicaciones web (Leaflet, OpenLayers)

## 📱 Uso

1. **Acceder a la aplicación web**
2. **Hacer clic en "Iniciar"** para activar actualización automática
3. **Ver ubicaciones en tiempo real** con badge "En Vivo"
4. **Exportar datos:**
   - "Exportar Actuales": Ubicaciones del momento
   - "Exportar Historial": Datos de fecha específica
   - "Exportar Todos": Datos masivos

## 🔄 Actualización Automática

- ✅ Ubicaciones actualizadas cada 30 segundos
- ✅ Archivos GeoJSON generados automáticamente
- ✅ Interfaz web en tiempo real
- ✅ Control manual (iniciar/detener)
- ✅ Funciona 24/7

## 🛠️ Tecnologías

- **Backend:** Flask + Python 3.11
- **Frontend:** Bootstrap 5 + JavaScript
- **API:** TrackSolidPro REST API
- **Despliegue:** Render/Heroku compatible
- **Formatos:** GeoJSON, CSV, KML

## 📞 Soporte

- **Repositorio:** [GitHub Issues](https://github.com/TU-USUARIO/gps-tracker-web/issues)
- **Documentación:** Ver archivos en el repositorio

---

⭐ **¡Dale una estrella si te resulta útil!**

Creado el 2026-01-13