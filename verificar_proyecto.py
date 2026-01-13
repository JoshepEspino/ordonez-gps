"""
VERIFICADOR DE PROYECTO WEB
===========================
Script para verificar que el proyecto esté listo para despliegue

Ejecutar con: python verificar_proyecto.py
"""

import os
import sys
from datetime import datetime

def verificar_archivos_principales():
    """Verifica que todos los archivos principales estén presentes"""
    
    archivos_requeridos = [
        "app.py",
        "main.py", 
        "exportador_capas.py",
        "config_endpoints.py",
        "requirements.txt",
        "Procfile",
        "runtime.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "render.yaml",
        "INSTRUCCIONES_DESPLIEGUE.md",
        "templates/index.html",
        ".github/workflows/deploy.yml"
    ]
    
    print("📁 Verificando archivos principales...")
    
    archivos_faltantes = []
    archivos_presentes = []
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            archivos_presentes.append(archivo)
            print(f"   ✅ {archivo}")
        else:
            archivos_faltantes.append(archivo)
            print(f"   ❌ {archivo} - FALTANTE")
    
    return len(archivos_faltantes) == 0, archivos_faltantes

def verificar_imports():
    """Verifica que los imports funcionen correctamente"""
    
    print(f"\n🐍 Verificando imports de Python...")
    
    modulos_a_probar = [
        ("app", "Aplicación principal"),
        ("main", "Conexión TrackSolidPro"),
        ("exportador_capas", "Exportador de capas"),
        ("config_endpoints", "Configuración de endpoints")
    ]
    
    imports_exitosos = 0
    
    for modulo, descripcion in modulos_a_probar:
        try:
            __import__(modulo)
            print(f"   ✅ {modulo} - {descripcion}")
            imports_exitosos += 1
        except ImportError as e:
            print(f"   ❌ {modulo} - Error: {str(e)}")
        except Exception as e:
            print(f"   ⚠️ {modulo} - Advertencia: {str(e)}")
    
    return imports_exitosos == len(modulos_a_probar)

def verificar_configuracion():
    """Verifica la configuración del proyecto"""
    
    print(f"\n⚙️ Verificando configuración...")
    
    # Verificar requirements.txt
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        dependencias_requeridas = ["flask", "flask-cors", "requests", "gunicorn"]
        dependencias_encontradas = []
        
        for dep in dependencias_requeridas:
            if dep in requirements.lower():
                dependencias_encontradas.append(dep)
                print(f"   ✅ Dependencia: {dep}")
            else:
                print(f"   ❌ Dependencia faltante: {dep}")
        
        config_ok = len(dependencias_encontradas) == len(dependencias_requeridas)
        
    except Exception as e:
        print(f"   ❌ Error leyendo requirements.txt: {str(e)}")
        config_ok = False
    
    # Verificar Procfile
    try:
        with open("Procfile", "r") as f:
            procfile = f.read().strip()
        
        if "gunicorn app:app" in procfile:
            print(f"   ✅ Procfile configurado correctamente")
        else:
            print(f"   ❌ Procfile mal configurado: {procfile}")
            config_ok = False
            
    except Exception as e:
        print(f"   ❌ Error leyendo Procfile: {str(e)}")
        config_ok = False
    
    return config_ok

def verificar_template():
    """Verifica que el template HTML esté completo"""
    
    print(f"\n🌐 Verificando template HTML...")
    
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        elementos_requeridos = [
            "GPS Tracker",
            "bootstrap",
            "cargarDispositivos",
            "exportarHistorial",
            "iniciarAutoUpdate",
            "detenerAutoUpdate"
        ]
        
        elementos_encontrados = 0
        
        for elemento in elementos_requeridos:
            if elemento in html_content:
                elementos_encontrados += 1
                print(f"   ✅ Elemento encontrado: {elemento}")
            else:
                print(f"   ❌ Elemento faltante: {elemento}")
        
        template_ok = elementos_encontrados == len(elementos_requeridos)
        
        # Verificar tamaño del archivo
        tamano_kb = len(html_content) / 1024
        print(f"   📊 Tamaño del template: {tamano_kb:.1f} KB")
        
        return template_ok
        
    except Exception as e:
        print(f"   ❌ Error leyendo template: {str(e)}")
        return False

def mostrar_resumen_final(archivos_ok, imports_ok, config_ok, template_ok):
    """Muestra el resumen final de la verificación"""
    
    print(f"\n" + "="*80)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*80)
    
    verificaciones = [
        ("Archivos principales", archivos_ok),
        ("Imports de Python", imports_ok),
        ("Configuración", config_ok),
        ("Template HTML", template_ok)
    ]
    
    total_verificaciones = len(verificaciones)
    verificaciones_exitosas = sum(1 for _, ok in verificaciones if ok)
    
    print(f"\n📈 Estadísticas:")
    print(f"   Total verificaciones: {total_verificaciones}")
    print(f"   Exitosas: {verificaciones_exitosas}")
    print(f"   Fallidas: {total_verificaciones - verificaciones_exitosas}")
    print(f"   Tasa de éxito: {(verificaciones_exitosas/total_verificaciones*100):.1f}%")
    
    print(f"\n📋 Detalle:")
    for nombre, ok in verificaciones:
        estado = "✅ PASS" if ok else "❌ FAIL"
        print(f"   {estado} {nombre}")
    
    if verificaciones_exitosas == total_verificaciones:
        print(f"\n🎉 ¡PROYECTO LISTO PARA DESPLIEGUE!")
        print(f"   ✅ Todos los archivos están presentes")
        print(f"   ✅ La configuración es correcta")
        print(f"   ✅ Los imports funcionan")
        print(f"   ✅ El template está completo")
        
        print(f"\n🚀 PRÓXIMOS PASOS:")
        print(f"   1. Seguir INSTRUCCIONES_DESPLIEGUE.md")
        print(f"   2. Subir a GitHub")
        print(f"   3. Desplegar en Render")
        
        return True
    else:
        print(f"\n⚠️ EL PROYECTO TIENE PROBLEMAS")
        print(f"   Revisa los errores mostrados arriba")
        print(f"   Corrige los problemas antes de desplegar")
        
        return False

def main():
    """Función principal"""
    
    print("="*80)
    print("🔍 VERIFICADOR DE PROYECTO WEB")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Directorio: {os.getcwd()}")
    
    # Ejecutar verificaciones
    archivos_ok, archivos_faltantes = verificar_archivos_principales()
    imports_ok = verificar_imports()
    config_ok = verificar_configuracion()
    template_ok = verificar_template()
    
    # Mostrar resumen
    proyecto_listo = mostrar_resumen_final(archivos_ok, imports_ok, config_ok, template_ok)
    
    # Código de salida
    sys.exit(0 if proyecto_listo else 1)

if __name__ == "__main__":
    main()