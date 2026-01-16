"""
Script para iniciar el servidor con HTTPS usando ngrok
Esto te da una URL HTTPS pública instantáneamente
"""

import subprocess
import sys
import time
import requests
import json

def verificar_ngrok():
    """Verifica si ngrok está instalado"""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            print(f"✅ ngrok encontrado: {result.stdout.strip()}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("❌ ngrok no está instalado")
    print("\n📥 Para instalar ngrok:")
    print("   1. Ve a: https://ngrok.com/download")
    print("   2. Descarga ngrok para tu sistema")
    print("   3. Extrae el archivo y agrégalo al PATH")
    print("   4. (Opcional) Crea cuenta gratis en ngrok.com para más funciones")
    return False

def iniciar_servidor_flask():
    """Inicia el servidor Flask en segundo plano"""
    print("\n🚀 Iniciando servidor Flask...")
    
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar a que el servidor inicie
        print("⏳ Esperando a que el servidor inicie...")
        time.sleep(5)
        
        # Verificar que el servidor esté corriendo
        try:
            response = requests.get('http://localhost:5000/api/estado', timeout=5)
            if response.status_code == 200:
                print("✅ Servidor Flask iniciado correctamente")
                return proceso
        except requests.exceptions.RequestException:
            pass
        
        print("⚠️ El servidor puede estar iniciando, continuando...")
        return proceso
        
    except Exception as e:
        print(f"❌ Error al iniciar servidor: {e}")
        return None

def iniciar_ngrok():
    """Inicia ngrok para crear túnel HTTPS"""
    print("\n🌐 Iniciando túnel HTTPS con ngrok...")
    
    try:
        proceso = subprocess.Popen(
            ['ngrok', 'http', '5000', '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar a que ngrok inicie
        time.sleep(3)
        
        # Obtener la URL pública de ngrok
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        url_https = tunnel.get('public_url')
                        print(f"\n{'='*70}")
                        print("✅ TÚNEL HTTPS CREADO EXITOSAMENTE")
                        print(f"{'='*70}")
                        print(f"\n🌐 URL PÚBLICA HTTPS:")
                        print(f"   {url_https}")
                        print(f"\n📍 URL GEOJSON:")
                        print(f"   {url_https}/api/geojson")
                        print(f"\n🗺️ MAPA INTERACTIVO:")
                        print(f"   {url_https}/")
                        print(f"\n{'='*70}")
                        print("\n💡 Esta URL es pública y funciona desde cualquier lugar")
                        print("⚠️ La URL cambiará cada vez que reinicies ngrok")
                        print("💎 Crea cuenta gratis en ngrok.com para URLs fijas")
                        print(f"\n{'='*70}")
                        
                        return proceso, url_https
        except requests.exceptions.RequestException:
            print("⚠️ No se pudo obtener la URL de ngrok automáticamente")
            print("   Revisa la consola de ngrok para ver la URL")
        
        return proceso, None
        
    except Exception as e:
        print(f"❌ Error al iniciar ngrok: {e}")
        return None, None

def main():
    print("="*70)
    print("INICIAR SERVIDOR CON HTTPS (usando ngrok)")
    print("="*70)
    
    # Verificar ngrok
    if not verificar_ngrok():
        return
    
    # Iniciar servidor Flask
    proceso_flask = iniciar_servidor_flask()
    if not proceso_flask:
        print("❌ No se pudo iniciar el servidor Flask")
        return
    
    # Iniciar ngrok
    proceso_ngrok, url_https = iniciar_ngrok()
    if not proceso_ngrok:
        print("❌ No se pudo iniciar ngrok")
        proceso_flask.terminate()
        return
    
    # Mantener los procesos corriendo
    print("\n🟢 SERVIDOR ACTIVO")
    print("\nPresiona Ctrl+C para detener el servidor\n")
    
    try:
        # Esperar indefinidamente
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo servidor...")
        
        # Detener procesos
        if proceso_ngrok:
            proceso_ngrok.terminate()
            print("✅ ngrok detenido")
        
        if proceso_flask:
            proceso_flask.terminate()
            print("✅ Servidor Flask detenido")
        
        print("\n👋 ¡Hasta pronto!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
