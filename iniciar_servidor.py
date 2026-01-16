"""
Script mejorado para iniciar el servidor con manejo de errores
"""

import time
import sys

print("="*80)
print("🛰️ GPS TRACKER - INICIANDO SERVIDOR")
print("="*80)
print("\n⏳ Esperando para evitar límite de frecuencia de la API...")
print("   (Esto es normal después de varias pruebas)\n")

# Esperar 15 segundos para evitar límite de frecuencia
for i in range(15, 0, -1):
    print(f"\r   Iniciando en {i} segundos...", end="", flush=True)
    time.sleep(1)

print("\n\n🚀 Iniciando servidor...\n")

# Importar y ejecutar app
try:
    import app
except KeyboardInterrupt:
    print("\n\n🛑 Servidor detenido por el usuario")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
