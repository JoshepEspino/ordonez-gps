"""
CONFIGURACIÓN DE ENDPOINTS
=========================
Archivo para configurar los endpoints donde enviar los datos GPS
"""

# Configuraciones de endpoints predefinidos
ENDPOINTS = {
    "local_test": {
        "url": "http://localhost:5000/gps-data",
        "headers": {
            "Content-Type": "application/json"
        },
        "descripcion": "Servidor de prueba local"
    },
    
    "webhook_example": {
        "url": "https://webhook.site/tu-webhook-id",
        "headers": {
            "Content-Type": "application/json",
            "X-API-Key": "tu_api_key_aqui"
        },
        "descripcion": "Webhook de prueba (reemplaza con tu URL)"
    },
    
    "api_custom": {
        "url": "https://tu-api.com/gps-data",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer tu_token_aqui"
        },
        "descripcion": "API personalizada (configura tu URL y token)"
    }
}

def obtener_endpoint(nombre: str):
    """
    Obtiene la configuración de un endpoint por nombre
    
    Args:
        nombre: Nombre del endpoint configurado
        
    Returns:
        Diccionario con url y headers, o None si no existe
    """
    return ENDPOINTS.get(nombre)

def listar_endpoints():
    """Lista todos los endpoints configurados"""
    print("\nEndpoints configurados:")
    print("="*50)
    for nombre, config in ENDPOINTS.items():
        print(f"\n{nombre}:")
        print(f"  URL: {config['url']}")
        print(f"  Descripción: {config['descripcion']}")

def agregar_endpoint(nombre: str, url: str, headers: dict = None, descripcion: str = ""):
    """
    Agrega un nuevo endpoint a la configuración
    
    Args:
        nombre: Nombre identificador del endpoint
        url: URL del endpoint
        headers: Headers HTTP opcionales
        descripcion: Descripción del endpoint
    """
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    ENDPOINTS[nombre] = {
        "url": url,
        "headers": headers,
        "descripcion": descripcion
    }
    
    print(f"✅ Endpoint '{nombre}' agregado correctamente")