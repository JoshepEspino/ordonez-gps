"""
EXTRACTOR DE DATOS GPS - TRACKSOLIDPRO
======================================
Script para extraer coordenadas, velocidad y datos de dispositivos GPS

Autor: Asistente de programación
Fecha: 2025-01-13
"""

import hashlib
import requests
import json
import time
import threading
from datetime import datetime, UTC
from typing import Dict, List, Optional
from config_endpoints import obtener_endpoint, listar_endpoints


class TrackSolidAPI:
    """
    Clase principal para interactuar con la API de TrackSolidPro
    """
    
    def __init__(self, app_key: str, app_secret: str, user_email: str, user_password: str):
        """
        Inicializa la conexión con TrackSolidPro
        
        Args:
            app_key: Clave de aplicación
            app_secret: Secreto de aplicación
            user_email: Email del usuario
            user_password: Contraseña del usuario (se convertirá a MD5)
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.user_email = user_email
        self.user_password_md5 = self._md5_hash(user_password)
        self.endpoint = "https://us-open.tracksolidpro.com/route/rest"
        self.access_token = None
        
    def _md5_hash(self, text: str) -> str:
        """Convierte un texto a hash MD5"""
        return hashlib.md5(text.encode('utf-8')).hexdigest().lower()
    
    def _generate_signature(self, params: dict) -> str:
        """
        Genera la firma MD5 requerida por la API
        
        Args:
            params: Diccionario con los parámetros de la petición
            
        Returns:
            Firma MD5 en mayúsculas
        """
        # Ordenar parámetros alfabéticamente
        sorted_items = sorted(params.items())
        
        # Crear cadena concatenada
        base = "".join([f"{k}{v}" for k, v in sorted_items])
        
        # Agregar secret al inicio y al final
        sign_str = f"{self.app_secret}{base}{self.app_secret}"
        
        # Calcular MD5 y convertir a mayúsculas
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()
    
    def _make_request(self, params: dict) -> Optional[dict]:
        """
        Realiza una petición POST a la API
        
        Args:
            params: Parámetros de la petición
            
        Returns:
            Respuesta JSON o None si hay error
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.post(self.endpoint, data=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la petición: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Respuesta del servidor: {e.response.text}")
            return None
    
    def obtener_token(self) -> bool:
        """
        Obtiene el token de acceso de la API
        
        Returns:
            True si se obtuvo el token, False si hubo error
        """
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        
        params = {
            "app_key": self.app_key,
            "expires_in": "3600",
            "format": "json",
            "method": "jimi.oauth.token.get",
            "sign_method": "md5",
            "timestamp": timestamp,
            "user_id": self.user_email,
            "user_pwd_md5": self.user_password_md5,
            "v": "1.0"
        }
        
        # Generar firma
        params["sign"] = self._generate_signature(params)
        
        print("🔑 Solicitando token de acceso...")
        response = self._make_request(params)
        
        if response and response.get('code') == 0:
            self.access_token = response['result']['accessToken']
            print(f"✅ Token obtenido: {self.access_token[:20]}...")
            return True
        else:
            print(f"❌ Error al obtener token: {response}")
            return False
    
    def listar_dispositivos(self) -> Optional[List[dict]]:
        """
        Lista todos los dispositivos de la cuenta
        
        Returns:
            Lista de dispositivos o None si hay error
        """
        if not self.access_token:
            print("⚠️ Primero debes obtener un token")
            return None
        
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        
        params = {
            "access_token": self.access_token,
            "app_key": self.app_key,
            "format": "json",
            "method": "jimi.user.device.list",
            "sign_method": "md5",
            "target": self.user_email,
            "timestamp": timestamp,
            "v": "1.0"
        }
        
        params["sign"] = self._generate_signature(params)
        
        print("📱 Obteniendo lista de dispositivos...")
        response = self._make_request(params)
        
        if response and response.get('code') == 0:
            dispositivos = response.get('result', [])
            print(f"✅ Se encontraron {len(dispositivos)} dispositivos")
            return dispositivos
        else:
            print(f"❌ Error al listar dispositivos: {response}")
            return None
    
    def obtener_ubicacion(self, imei: str) -> Optional[dict]:
        """
        Obtiene la ubicación actual de un dispositivo
        
        Args:
            imei: IMEI del dispositivo
            
        Returns:
            Datos de ubicación o None si hay error
        """
        if not self.access_token:
            print("⚠️ Primero debes obtener un token")
            return None
        
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        
        params = {
            "access_token": self.access_token,
            "app_key": self.app_key,
            "format": "json",
            "imeis": imei,
            "method": "jimi.device.location.get",
            "sign_method": "md5",
            "timestamp": timestamp,
            "v": "1.0"
        }
        
        params["sign"] = self._generate_signature(params)
        
        print(f"📍 Obteniendo ubicación del dispositivo {imei}...")
        response = self._make_request(params)
        
        if response and response.get('code') == 0:
            ubicaciones = response.get('result', [])
            if ubicaciones:
                return ubicaciones[0]
            else:
                print("⚠️ No se encontraron datos de ubicación")
                return None
        else:
            print(f"❌ Error al obtener ubicación: {response}")
            return None
    
    def obtener_historial_ruta(self, imei: str, fecha_inicio: str, fecha_fin: str) -> Optional[List[dict]]:
        """
        Obtiene el historial de ruta de un dispositivo
        
        Args:
            imei: IMEI del dispositivo
            fecha_inicio: Fecha inicio (formato: YYYY-MM-DD HH:MM:SS)
            fecha_fin: Fecha fin (formato: YYYY-MM-DD HH:MM:SS)
            
        Returns:
            Lista de puntos de ruta o None si hay error
        """
        if not self.access_token:
            print("⚠️ Primero debes obtener un token")
            return None
        
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        
        params = {
            "access_token": self.access_token,
            "app_key": self.app_key,
            "begin_time": fecha_inicio,
            "end_time": fecha_fin,
            "format": "json",
            "imei": imei,
            "method": "jimi.device.track.list",
            "sign_method": "md5",
            "timestamp": timestamp,
            "v": "1.0"
        }
        
        params["sign"] = self._generate_signature(params)
        
        print(f"🛣️ Obteniendo historial de ruta...")
        response = self._make_request(params)
        
        if response and response.get('code') == 0:
            ruta = response.get('result', [])
            print(f"✅ Se encontraron {len(ruta)} puntos en la ruta")
            return ruta
        else:
            print(f"❌ Error al obtener historial: {response}")
            return None
    
    def enviar_datos_a_endpoint(self, endpoint_url: str, datos: dict, headers: Optional[dict] = None) -> bool:
        """
        Envía los datos del dispositivo a un endpoint externo
        
        Args:
            endpoint_url: URL del endpoint destino
            datos: Datos a enviar (ubicación, dispositivo, etc.)
            headers: Headers adicionales para la petición
            
        Returns:
            True si se envió correctamente, False si hubo error
        """
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        try:
            print(f"📤 Enviando datos a: {endpoint_url}")
            
            # Agregar timestamp y metadata
            payload = {
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "TrackSolidPro",
                "data": datos
            }
            
            response = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Datos enviados exitosamente")
            print(f"   Status: {response.status_code}")
            if response.text:
                print(f"   Respuesta: {response.text[:100]}...")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al enviar datos: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Status: {e.response.status_code}")
                print(f"   Respuesta: {e.response.text}")
            return False
    
    def enviar_ubicacion_a_endpoint(self, imei: str, endpoint_url: str, headers: Optional[dict] = None) -> bool:
        """
        Obtiene la ubicación de un dispositivo y la envía a un endpoint
        
        Args:
            imei: IMEI del dispositivo
            endpoint_url: URL del endpoint destino
            headers: Headers adicionales para la petición
            
        Returns:
            True si se envió correctamente, False si hubo error
        """
        # Obtener ubicación actual
        ubicacion = self.obtener_ubicacion(imei)
        
        if not ubicacion:
            print("❌ No se pudo obtener la ubicación del dispositivo")
            return False
        
        # Enviar datos al endpoint
        return self.enviar_datos_a_endpoint(endpoint_url, ubicacion, headers)


class MonitorAutomatico:
    """
    Clase para manejar el monitoreo automático de dispositivos
    """
    
    def __init__(self, api: TrackSolidAPI):
        self.api = api
        self.activo = False
        self.hilo_monitor = None
        self.intervalo = 30  # segundos por defecto
        self.endpoint_url = None
        self.headers = None
        self.dispositivos_monitoreados = []
        self.estadisticas = {
            'total_envios': 0,
            'envios_exitosos': 0,
            'errores': 0,
            'inicio': None
        }
    
    def configurar(self, intervalo: int, endpoint_url: str, headers: Optional[dict] = None, dispositivos: Optional[List[str]] = None):
        """
        Configura el monitoreo automático
        
        Args:
            intervalo: Intervalo en segundos (5, 10, 30, 60)
            endpoint_url: URL del endpoint destino
            headers: Headers HTTP opcionales
            dispositivos: Lista de IMEIs a monitorear (None = todos)
        """
        if intervalo not in [5, 10, 30, 60]:
            print("⚠️ Intervalo debe ser 5, 10, 30 o 60 segundos")
            return False
        
        self.intervalo = intervalo
        self.endpoint_url = endpoint_url
        self.headers = headers
        self.dispositivos_monitoreados = dispositivos or []
        
        print(f"✅ Monitoreo configurado:")
        print(f"   Intervalo: {intervalo} segundos")
        print(f"   Endpoint: {endpoint_url}")
        print(f"   Dispositivos: {'Todos' if not dispositivos else len(dispositivos)}")
        
        return True
    
    def _monitorear(self):
        """Función interna que ejecuta el monitoreo en bucle"""
        self.estadisticas['inicio'] = datetime.now()
        print(f"\n🚀 Iniciando monitoreo automático cada {self.intervalo} segundos...")
        print("Presiona Ctrl+C para detener\n")
        
        while self.activo:
            try:
                # Obtener lista de dispositivos a monitorear
                if self.dispositivos_monitoreados:
                    # Monitorear solo dispositivos específicos
                    dispositivos_a_procesar = []
                    todos_dispositivos = self.api.listar_dispositivos()
                    if todos_dispositivos:
                        for disp in todos_dispositivos:
                            if disp.get('imei') in self.dispositivos_monitoreados:
                                dispositivos_a_procesar.append(disp)
                else:
                    # Monitorear todos los dispositivos
                    dispositivos_a_procesar = self.api.listar_dispositivos()
                
                if not dispositivos_a_procesar:
                    print("⚠️ No hay dispositivos para monitorear")
                    time.sleep(self.intervalo)
                    continue
                
                # Procesar cada dispositivo
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"🔄 [{timestamp}] Procesando {len(dispositivos_a_procesar)} dispositivos...")
                
                for dispositivo in dispositivos_a_procesar:
                    if not self.activo:  # Verificar si se debe detener
                        break
                    
                    imei = dispositivo.get('imei')
                    nombre = dispositivo.get('deviceName', 'Sin nombre')
                    
                    self.estadisticas['total_envios'] += 1
                    
                    # Enviar datos
                    if self.api.enviar_ubicacion_a_endpoint(imei, self.endpoint_url, self.headers):
                        self.estadisticas['envios_exitosos'] += 1
                        print(f"   ✅ {nombre} ({imei})")
                    else:
                        self.estadisticas['errores'] += 1
                        print(f"   ❌ {nombre} ({imei})")
                
                # Mostrar estadísticas
                if self.estadisticas['total_envios'] > 0:
                    tasa_exito = (self.estadisticas['envios_exitosos'] / self.estadisticas['total_envios']) * 100
                    print(f"📊 Estadísticas: {self.estadisticas['envios_exitosos']}/{self.estadisticas['total_envios']} exitosos ({tasa_exito:.1f}%)")
                
                # Esperar hasta el siguiente ciclo
                if self.activo:
                    print(f"⏳ Esperando {self.intervalo} segundos...\n")
                    time.sleep(self.intervalo)
                
            except KeyboardInterrupt:
                print("\n🛑 Deteniendo monitoreo...")
                self.detener()
                break
            except Exception as e:
                print(f"❌ Error en monitoreo: {str(e)}")
                self.estadisticas['errores'] += 1
                if self.activo:
                    time.sleep(self.intervalo)
    
    def iniciar(self):
        """Inicia el monitoreo automático en un hilo separado"""
        if self.activo:
            print("⚠️ El monitoreo ya está activo")
            return False
        
        if not self.endpoint_url:
            print("❌ Debes configurar el monitoreo primero")
            return False
        
        self.activo = True
        self.hilo_monitor = threading.Thread(target=self._monitorear, daemon=True)
        self.hilo_monitor.start()
        return True
    
    def detener(self):
        """Detiene el monitoreo automático"""
        if not self.activo:
            print("⚠️ El monitoreo no está activo")
            return False
        
        self.activo = False
        if self.hilo_monitor and self.hilo_monitor.is_alive():
            self.hilo_monitor.join(timeout=2)
        
        # Mostrar estadísticas finales
        if self.estadisticas['inicio']:
            duracion = datetime.now() - self.estadisticas['inicio']
            print(f"\n📊 ESTADÍSTICAS FINALES:")
            print(f"   Duración: {duracion}")
            print(f"   Total envíos: {self.estadisticas['total_envios']}")
            print(f"   Exitosos: {self.estadisticas['envios_exitosos']}")
            print(f"   Errores: {self.estadisticas['errores']}")
            if self.estadisticas['total_envios'] > 0:
                tasa_exito = (self.estadisticas['envios_exitosos'] / self.estadisticas['total_envios']) * 100
                print(f"   Tasa de éxito: {tasa_exito:.1f}%")
        
        print("✅ Monitoreo detenido")
        return True
    
    def estado(self):
        """Muestra el estado actual del monitoreo"""
        if self.activo:
            duracion = datetime.now() - self.estadisticas['inicio'] if self.estadisticas['inicio'] else "N/A"
            print(f"\n🟢 MONITOREO ACTIVO")
            print(f"   Intervalo: {self.intervalo} segundos")
            print(f"   Endpoint: {self.endpoint_url}")
            print(f"   Duración: {duracion}")
            print(f"   Envíos: {self.estadisticas['envios_exitosos']}/{self.estadisticas['total_envios']}")
        else:
            print("\n🔴 MONITOREO INACTIVO")


def configurar_monitoreo_automatico(api: TrackSolidAPI, dispositivos: List[dict]) -> MonitorAutomatico:
    """
    Configura el monitoreo automático de forma interactiva
    
    Args:
        api: Instancia de la API
        dispositivos: Lista de dispositivos disponibles
        
    Returns:
        Instancia configurada de MonitorAutomatico
    """
    monitor = MonitorAutomatico(api)
    
    print("\n" + "="*80)
    print("CONFIGURACIÓN DE MONITOREO AUTOMÁTICO")
    print("="*80)
    
    # Seleccionar intervalo
    print("\nIntervalos disponibles:")
    print("1. 5 segundos (muy frecuente)")
    print("2. 10 segundos (frecuente)")
    print("3. 30 segundos (normal)")
    print("4. 60 segundos (lento)")
    
    while True:
        try:
            opcion_intervalo = input("\nSelecciona intervalo (1-4): ")
            intervalos = {'1': 5, '2': 10, '3': 30, '4': 60}
            if opcion_intervalo in intervalos:
                intervalo = intervalos[opcion_intervalo]
                break
            else:
                print("⚠️ Opción no válida")
        except KeyboardInterrupt:
            print("\n❌ Configuración cancelada")
            return None
    
    # Seleccionar endpoint
    print("\n¿Usar endpoint predefinido?")
    listar_endpoints()
    
    usar_predefinido = input("\n¿Usar endpoint predefinido? (s/n): ")
    
    if usar_predefinido.lower() == 's':
        nombre_endpoint = input("Nombre del endpoint: ")
        config = obtener_endpoint(nombre_endpoint)
        
        if config:
            endpoint_url = config['url']
            headers = config['headers']
            print(f"✅ Usando endpoint: {config['descripcion']}")
        else:
            print("❌ Endpoint no encontrado")
            return None
    else:
        endpoint_url = input("Ingresa la URL del endpoint: ")
        
        # Headers personalizados
        usar_headers = input("¿Agregar headers personalizados? (s/n): ")
        headers = None
        if usar_headers.lower() == 's':
            headers = {}
            while True:
                header = input("\nHeader (formato 'clave: valor' o 'enter' para terminar): ")
                if not header.strip():
                    break
                try:
                    key, value = header.split(':', 1)
                    headers[key.strip()] = value.strip()
                except ValueError:
                    print("⚠️ Formato incorrecto. Usa 'clave: valor'")
    
    # Seleccionar dispositivos
    print(f"\n¿Monitorear todos los dispositivos ({len(dispositivos)})?")
    monitorear_todos = input("(s/n): ")
    
    dispositivos_seleccionados = None
    if monitorear_todos.lower() != 's':
        print("\nSelecciona dispositivos a monitorear:")
        mostrar_dispositivos(dispositivos)
        
        dispositivos_seleccionados = []
        while True:
            imei = input("\nIMEI del dispositivo (o 'enter' para terminar): ")
            if not imei.strip():
                break
            
            # Verificar que el IMEI existe
            encontrado = False
            for disp in dispositivos:
                if disp.get('imei') == imei:
                    dispositivos_seleccionados.append(imei)
                    print(f"✅ Agregado: {disp.get('deviceName')} ({imei})")
                    encontrado = True
                    break
            
            if not encontrado:
                print("⚠️ IMEI no encontrado")
    
    # Configurar monitor
    if monitor.configurar(intervalo, endpoint_url, headers, dispositivos_seleccionados):
        return monitor
    else:
        return None


def mostrar_dispositivos(dispositivos: List[dict]):
    """Muestra la lista de dispositivos de forma legible"""
    print("\n" + "="*80)
    print("DISPOSITIVOS DISPONIBLES")
    print("="*80)
    
    for i, disp in enumerate(dispositivos, 1):
        print(f"\n{i}. {disp.get('deviceName', 'Sin nombre')}")
        print(f"   IMEI: {disp.get('imei')}")
        print(f"   Modelo: {disp.get('mcType')}")
        print(f"   Número de placa: {disp.get('vehicleNumber', 'N/A')}")
        print(f"   Estado: {'Activo' if disp.get('enabledFlag') == 1 else 'Inactivo'}")


def mostrar_ubicacion(ubicacion: dict):
    """Muestra los datos de ubicación de forma legible"""
    print("\n" + "="*80)
    print("DATOS DE UBICACIÓN")
    print("="*80)
    
    print(f"\n📱 Dispositivo: {ubicacion.get('deviceName')}")
    print(f"📍 Coordenadas:")
    print(f"   Latitud:  {ubicacion.get('lat')}")
    print(f"   Longitud: {ubicacion.get('lng')}")
    print(f"\n🚗 Datos del vehículo:")
    print(f"   Velocidad: {ubicacion.get('speed')} km/h")
    print(f"   Dirección: {ubicacion.get('direction')}°")
    print(f"   ACC: {'Encendido' if ubicacion.get('accStatus') == '1' else 'Apagado'}")
    print(f"\n🛰️ Datos GPS:")
    print(f"   Satélites: {ubicacion.get('gpsNum')}")
    print(f"   Tipo posición: {ubicacion.get('posType')}")
    print(f"   Fecha GPS: {ubicacion.get('gpsTime')}")
    print(f"\n🔋 Batería:")
    print(f"   Externa: {ubicacion.get('powerValue')}%")
    print(f"   Estado: {'Online' if ubicacion.get('status') == '1' else 'Offline'}")
    
    if ubicacion.get('locDesc'):
        print(f"\n📍 Ubicación: {ubicacion.get('locDesc')}")


def guardar_a_json(datos: dict, nombre_archivo: str):
    """Guarda los datos en un archivo JSON"""
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Datos guardados en: {nombre_archivo}")


def guardar_a_csv(puntos_ruta: List[dict], nombre_archivo: str):
    """Guarda los puntos de ruta en un archivo CSV"""
    import csv
    
    if not puntos_ruta:
        print("⚠️ No hay datos para guardar")
        return
    
    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
        # Obtener todas las claves únicas
        campos = set()
        for punto in puntos_ruta:
            campos.update(punto.keys())
        
        writer = csv.DictWriter(f, fieldnames=sorted(campos))
        writer.writeheader()
        writer.writerows(puntos_ruta)
    
    print(f"\n💾 Ruta guardada en: {nombre_archivo}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal del programa"""
    
    print("="*80)
    print("EXTRACTOR DE DATOS GPS - TRACKSOLIDPRO")
    print("="*80)
    
    # CONFIGURACIÓN desde variables de entorno
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    APP_KEY = os.getenv("TRACKSOLID_APP_KEY")
    APP_SECRET = os.getenv("TRACKSOLID_APP_SECRET")
    USER_EMAIL = os.getenv("TRACKSOLID_EMAIL")
    USER_PASSWORD = os.getenv("TRACKSOLID_PASSWORD")
    
    # Verificar que todas las credenciales estén configuradas
    if not all([APP_KEY, APP_SECRET, USER_EMAIL, USER_PASSWORD]):
        print("\n❌ ERROR: Faltan credenciales en el archivo .env")
        print("Por favor, configura las siguientes variables en .env:")
        print("  - TRACKSOLID_APP_KEY")
        print("  - TRACKSOLID_APP_SECRET")
        print("  - TRACKSOLID_EMAIL")
        print("  - TRACKSOLID_PASSWORD")
        return
    
    # Crear instancia de la API
    api = TrackSolidAPI(APP_KEY, APP_SECRET, USER_EMAIL, USER_PASSWORD)
    
    # Obtener token
    if not api.obtener_token():
        print("\n❌ No se pudo conectar a la API. Verifica tus credenciales.")
        return
    
    # Listar dispositivos
    dispositivos = api.listar_dispositivos()
    
    if not dispositivos:
        print("\n⚠️ No se encontraron dispositivos en tu cuenta")
        return
    
    mostrar_dispositivos(dispositivos)
    
    # Crear instancia del monitor automático
    monitor = None
    
    # Menú de opciones
    while True:
        print("\n" + "="*80)
        print("MENÚ DE OPCIONES")
        print("="*80)
        print("1. Ver ubicación actual de un dispositivo")
        print("2. Ver historial de ruta de un dispositivo")
        print("3. Guardar datos de ubicación en JSON")
        print("4. Enviar datos de ubicación a endpoint")
        print("5. Enviar datos de todos los dispositivos a endpoint")
        print("6. 🔄 Configurar monitoreo automático")
        print("7. 🚀 Iniciar monitoreo automático")
        print("8. 🛑 Detener monitoreo automático")
        print("9. 📊 Estado del monitoreo")
        print("10. Salir")
        
        opcion = input("\nSelecciona una opción (1-10): ")
        
        if opcion == "1":
            imei = input("\nIngresa el IMEI del dispositivo: ")
            ubicacion = api.obtener_ubicacion(imei)
            if ubicacion:
                mostrar_ubicacion(ubicacion)
        
        elif opcion == "2":
            imei = input("\nIngresa el IMEI del dispositivo: ")
            print("\nFormato de fecha: YYYY-MM-DD HH:MM:SS")
            print("Ejemplo: 2025-01-13 08:00:00")
            fecha_inicio = input("Fecha inicio: ")
            fecha_fin = input("Fecha fin: ")
            
            ruta = api.obtener_historial_ruta(imei, fecha_inicio, fecha_fin)
            if ruta:
                print(f"\n✅ Se encontraron {len(ruta)} puntos")
                print("\nPrimeros 3 puntos:")
                for i, punto in enumerate(ruta[:3], 1):
                    print(f"\n{i}. Lat: {punto.get('lat')}, Lng: {punto.get('lng')}")
                    print(f"   Velocidad: {punto.get('gpsSpeed')} km/h")
                    print(f"   Fecha: {punto.get('gpsTime')}")
                
                guardar = input("\n¿Guardar toda la ruta en CSV? (s/n): ")
                if guardar.lower() == 's':
                    guardar_a_csv(ruta, f"ruta_{imei}.csv")
        
        elif opcion == "3":
            imei = input("\nIngresa el IMEI del dispositivo: ")
            ubicacion = api.obtener_ubicacion(imei)
            if ubicacion:
                guardar_a_json(ubicacion, f"ubicacion_{imei}.json")
        
        elif opcion == "4":
            imei = input("\nIngresa el IMEI del dispositivo: ")
            
            # Mostrar endpoints predefinidos
            print("\n¿Usar endpoint predefinido?")
            listar_endpoints()
            
            usar_predefinido = input("\n¿Usar endpoint predefinido? (s/n): ")
            
            if usar_predefinido.lower() == 's':
                nombre_endpoint = input("Nombre del endpoint: ")
                config = obtener_endpoint(nombre_endpoint)
                
                if config:
                    endpoint_url = config['url']
                    headers = config['headers']
                    print(f"✅ Usando endpoint: {config['descripcion']}")
                else:
                    print("❌ Endpoint no encontrado")
                    continue
            else:
                endpoint_url = input("Ingresa la URL del endpoint: ")
                
                # Opción para headers personalizados
                usar_headers = input("¿Agregar headers personalizados? (s/n): ")
                headers = None
                if usar_headers.lower() == 's':
                    print("\nEjemplos de headers:")
                    print("Authorization: Bearer tu_token")
                    print("X-API-Key: tu_api_key")
                    print("Content-Type: application/json")
                    
                    headers = {}
                    while True:
                        header = input("\nHeader (formato 'clave: valor' o 'enter' para terminar): ")
                        if not header.strip():
                            break
                        try:
                            key, value = header.split(':', 1)
                            headers[key.strip()] = value.strip()
                        except ValueError:
                            print("⚠️ Formato incorrecto. Usa 'clave: valor'")
            
            api.enviar_ubicacion_a_endpoint(imei, endpoint_url, headers)
        
        elif opcion == "5":
            # Mostrar endpoints predefinidos
            print("\n¿Usar endpoint predefinido?")
            listar_endpoints()
            
            usar_predefinido = input("\n¿Usar endpoint predefinido? (s/n): ")
            
            if usar_predefinido.lower() == 's':
                nombre_endpoint = input("Nombre del endpoint: ")
                config = obtener_endpoint(nombre_endpoint)
                
                if config:
                    endpoint_url = config['url']
                    headers = config['headers']
                    print(f"✅ Usando endpoint: {config['descripcion']}")
                else:
                    print("❌ Endpoint no encontrado")
                    continue
            else:
                endpoint_url = input("\nIngresa la URL del endpoint: ")
                
                # Opción para headers personalizados
                usar_headers = input("¿Agregar headers personalizados? (s/n): ")
                headers = None
                if usar_headers.lower() == 's':
                    headers = {}
                    while True:
                        header = input("\nHeader (formato 'clave: valor' o 'enter' para terminar): ")
                        if not header.strip():
                            break
                        try:
                            key, value = header.split(':', 1)
                            headers[key.strip()] = value.strip()
                        except ValueError:
                            print("⚠️ Formato incorrecto. Usa 'clave: valor'")
            
            print(f"\n📤 Enviando datos de {len(dispositivos)} dispositivos...")
            exitosos = 0
            
            for dispositivo in dispositivos:
                imei = dispositivo.get('imei')
                print(f"\n📱 Procesando {dispositivo.get('deviceName')} ({imei})")
                
                if api.enviar_ubicacion_a_endpoint(imei, endpoint_url, headers):
                    exitosos += 1
            
            print(f"\n✅ Proceso completado: {exitosos}/{len(dispositivos)} dispositivos enviados")
        
        elif opcion == "6":
            monitor = configurar_monitoreo_automatico(api, dispositivos)
            if monitor:
                print("✅ Monitoreo configurado correctamente")
            else:
                print("❌ Error al configurar monitoreo")
        
        elif opcion == "7":
            if not monitor:
                print("❌ Primero debes configurar el monitoreo (opción 6)")
            else:
                if monitor.iniciar():
                    print("🚀 Monitoreo iniciado")
                    print("💡 Tip: Usa la opción 9 para ver el estado")
                    print("⚠️ Para detener, usa la opción 8")
        
        elif opcion == "8":
            if not monitor:
                print("❌ No hay monitoreo configurado")
            else:
                monitor.detener()
        
        elif opcion == "9":
            if not monitor:
                print("❌ No hay monitoreo configurado")
            else:
                monitor.estado()
        
        elif opcion == "10":
            # Detener monitoreo si está activo
            if monitor and monitor.activo:
                print("🛑 Deteniendo monitoreo antes de salir...")
                monitor.detener()
            
            print("\n👋 ¡Hasta pronto!")
            break
        
        else:
            print("\n⚠️ Opción no válida")


if __name__ == "__main__":
    main()