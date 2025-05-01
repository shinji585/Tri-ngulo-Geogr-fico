import numpy as np
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from geographiclib.geodesic import Geodesic
import pandas as pd
import json
import os
from datetime import datetime

# Función para transformar coordenadas geográficas (lat, lon) a coordenadas planas (x, y)
def transformacion_coordenada(p, p0):
    """
    Transforma coordenadas geográficas a coordenadas cartesianas relativas a un punto de origen.
    Utiliza una aproximación simple basada en la proyección de Mercator.
    
    Args:
        p: Tupla (latitud, longitud) del punto a transformar
        p0: Tupla (latitud, longitud) del punto de origen
        
    Returns:
        Tupla (x, y) en metros desde el punto de origen
    """
    # Radio de la Tierra en metros
    R = 6371000
    
    # Convertir grados a radianes
    lat1, lon1 = np.radians(p[0]), np.radians(p[1])
    lat0, lon0 = np.radians(p0[0]), np.radians(p0[1])
    
    # Calcular diferencias
    dlat = lat1 - lat0
    dlon = lon1 - lon0
    
    # Aproximación para distancias relativamente pequeñas
    x = R * dlon * np.cos((lat0 + lat1) / 2)
    y = R * dlat
    
    return (x, y)

# Función para calcular el área de un triángulo usando coordenadas
def area_triangulo(p1, p2, p3):
    """
    Calcula el área de un triángulo usando el determinante.
    
    Args:
        p1, p2, p3: Tuplas (x, y) de los vértices del triángulo
        
    Returns:
        Área del triángulo en unidades cuadradas
    """
    mat = np.array([
        [p1[0], p2[0], p3[0]],
        [p1[1], p2[1], p3[1]],
        [   1 ,    1 ,    1 ]
    ])
    return 0.5 * np.abs(np.linalg.det(mat))

# Función para clasificar un punto respecto a un triángulo
def clasificar_punto(p, a, b, c):
    """
    Clasifica un punto como interior, en la frontera o exterior a un triángulo.
    
    Args:
        p: Tupla (x, y) del punto a clasificar
        a, b, c: Tuplas (x, y) de los vértices del triángulo
        
    Returns:
        String: "Interior", "Frontera" o "Exterior"
    """
    A = area_triangulo(a, b, c)
    A1 = area_triangulo(p, b, c)
    A2 = area_triangulo(a, p, c)
    A3 = area_triangulo(a, b, p)
    suma = A1 + A2 + A3
    
    # Tolerancia para comparaciones de punto flotante
    epsilon = 1e-10
    
    if np.isclose(A1, 0, atol=epsilon) or np.isclose(A2, 0, atol=epsilon) or np.isclose(A3, 0, atol=epsilon):
        return "Frontera"
    elif np.isclose(suma, A, atol=epsilon):
        return "Interior"
    else:
        return "Exterior"

def dibujar_triangulo_con_datos(v0, v1, v2, distancias, area_heron, area_determinante, df_puntos, df_clasificados=None):
    """
    Dibuja el triángulo, las distancias entre puntos, áreas calculadas y los puntos clasificados si existen.
    
    Args:
        v0, v1, v2: Vértices del triángulo en coordenadas transformadas
        distancias: Tupla con las tres distancias (d1, d2, d3) en metros
        area_heron: Área calculada con la fórmula de Herón
        area_determinante: Área calculada con determinantes
        df_puntos: DataFrame con la información de los puntos del triángulo
        df_clasificados: DataFrame con puntos clasificados (opcional)
    """
    d1, d2, d3 = distancias
    
    # Crear figura con tres subplots: el triángulo, la información y los datos
    fig = plt.figure(figsize=(18, 10))
    
    # Subplot para el triángulo (ocupa 6/10 del espacio)
    ax1 = plt.subplot2grid((10, 10), (0, 0), colspan=6, rowspan=10)
    
    # Coordenadas del triángulo
    x_coords = [v0[0], v1[0], v2[0], v0[0]]
    y_coords = [v0[1], v1[1], v2[1], v0[1]]
    
    # Definir colores distintos para cada punto
    colores_vertices = ['#1f77b4', '#ff7f0e', '#2ca02c']  # azul, naranja, verde
    
    # Dibujar el triángulo
    ax1.plot(x_coords, y_coords, 'k-', linewidth=2, label='Triángulo')
    
    # Marcar los vértices con diferentes marcadores y colores
    marcadores = ['o', 's', '^']  # círculo, cuadrado, triángulo
    for i, (x, y, color, marker) in enumerate(zip([v0[0], v1[0], v2[0]], 
                                               [v0[1], v1[1], v2[1]], 
                                               colores_vertices, 
                                               marcadores)):
        ax1.plot(x, y, marker=marker, color=color, markersize=10, label=f'Punto {i+1}')
    
    # Añadir etiquetas con las distancias en cada línea del triángulo
    # Punto medio entre v0 y v1
    mid_x01, mid_y01 = (v0[0] + v1[0]) / 2, (v0[1] + v1[1]) / 2
    ax1.text(mid_x01, mid_y01, f"{d1:.2f} m", fontsize=9, 
             bbox=dict(facecolor='white', alpha=0.7), ha='center', va='center')
    
    # Punto medio entre v1 y v2
    mid_x12, mid_y12 = (v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2
    ax1.text(mid_x12, mid_y12, f"{d2:.2f} m", fontsize=9, 
             bbox=dict(facecolor='white', alpha=0.7), ha='center', va='center')
    
    # Punto medio entre v2 y v0
    mid_x20, mid_y20 = (v2[0] + v0[0]) / 2, (v2[1] + v0[1]) / 2
    ax1.text(mid_x20, mid_y20, f"{d3:.2f} m", fontsize=9, 
             bbox=dict(facecolor='white', alpha=0.7), ha='center', va='center')
    
    # Si hay puntos clasificados, dibujarlos
    if df_clasificados is not None and not df_clasificados.empty:
        # Definir colores para cada tipo de clasificación
        color_map = {
            "Interior": '#00cc00',  # Verde intenso
            "Frontera": '#ffcc00',  # Amarillo
            "Exterior": '#cc0000'   # Rojo intenso
        }
        
        for idx, row in df_clasificados.iterrows():
            x, y = row['x_transf'], row['y_transf']
            clasificacion = row['clasificacion']
            ax1.plot(x, y, marker='*', color=color_map[clasificacion], 
                    markersize=12, label=f"{row['nombre']} ({clasificacion})" if idx == 0 else "")
            # Añadir etiqueta con el nombre del punto
            ax1.text(x+50, y+50, row['nombre'], fontsize=8, 
                    bbox=dict(facecolor='white', alpha=0.7), ha='center', va='center')
    
    ax1.set_xlabel("X (metros)", fontsize=12)
    ax1.set_ylabel("Y (metros)", fontsize=12)
    ax1.set_title("Triángulo Geográfico", fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True)
    ax1.axis('equal')
    
    # Segundo subplot para la información (ocupa 4/10 del espacio de la derecha, mitad superior)
    ax2 = plt.subplot2grid((10, 10), (0, 6), colspan=4, rowspan=5)
    ax2.axis('off')  # Sin ejes
    
    # Crear tabla informativa
    info_text = f"""
    INFORMACIÓN DEL TRIÁNGULO
    
    DISTANCIAS:
    • Punto 1 a Punto 2: {d1:.2f} m
    • Punto 2 a Punto 3: {d2:.2f} m
    • Punto 3 a Punto 1: {d3:.2f} m
    
    PERÍMETRO:
    • Total: {d1 + d2 + d3:.2f} m
    
    ÁREAS:
    • Método de Herón: {area_heron:.2f} m²
    • Método Determinante: {area_determinante:.2f} m²
    
    DETERMINANTES:
    • Det principal: {np.linalg.det(np.array([[v0[0], v1[0], v2[0]], [v0[1], v1[1], v2[1]], [1, 1, 1]])):.2f}
    • Det/2 (área): {area_determinante:.2f}
    """
    
    ax2.text(0, 0.95, info_text, fontsize=11, va='top', fontfamily='monospace')
    
    # Tercer subplot para los datos de pandas (ocupa 4/10 del espacio de la derecha, mitad inferior)
    ax3 = plt.subplot2grid((10, 10), (5, 6), colspan=4, rowspan=5)
    ax3.axis('off')
    
    # Crear tabla de datos del triángulo
    table_data = []
    for idx, row in df_puntos.iterrows():
        table_data.append([
            f"Punto {idx+1}",
            row['nombre'],
            f"{row['latitud']:.6f}",
            f"{row['longitud']:.6f}",
            f"{row['x_transf']:.2f}",
            f"{row['y_transf']:.2f}"
        ])
    
    col_labels = ['Punto', 'Nombre', 'Latitud', 'Longitud', 'X (m)', 'Y (m)']
    tabla = ax3.table(cellText=table_data, colLabels=col_labels, loc='center', 
                      cellLoc='center', colColours=['#f0f0f0']*len(col_labels))
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9)
    tabla.scale(1, 1.5)
    
    # Si hay puntos clasificados, mostrar una tabla adicional
    if df_clasificados is not None and not df_clasificados.empty:
        ax3.text(0, 0.9, "PUNTOS CLASIFICADOS:", fontsize=11, fontweight='bold', va='top')
        
        # Crear datos para la tabla de puntos clasificados
        class_data = []
        for idx, row in df_clasificados.iterrows():
            class_data.append([
                row['nombre'],
                f"{row['latitud']:.6f}",
                f"{row['longitud']:.6f}",
                row['clasificacion']
            ])
        
        col_class = ['Nombre', 'Latitud', 'Longitud', 'Clasificación']
        tabla_class = ax3.table(cellText=class_data, colLabels=col_class, loc='bottom', 
                          cellLoc='center', colColours=['#f0f0f0']*len(col_class))
        tabla_class.auto_set_font_size(False)
        tabla_class.set_fontsize(9)
        tabla_class.scale(1, 1.5)
    
    plt.tight_layout()
    plt.show()

def crear_dataframes(locations, location_names, distances):
    """
    Crea un DataFrame con la información de los puntos del triángulo.
    
    Args:
        locations: Lista de tuplas (latitud, longitud)
        location_names: Lista con los nombres de las ubicaciones
        distances: Tupla con las tres distancias (d1, d2, d3) en metros
        
    Returns:
        DataFrame con la información de los puntos
    """
    # Origen para la transformación de coordenadas
    p0 = locations[0]
    
    # Transformar coordenadas
    coords_transf = [transformacion_coordenada(p, p0) for p in locations]
    
    # Crear DataFrame
    df = pd.DataFrame({
        'nombre': location_names,
        'latitud': [p[0] for p in locations],
        'longitud': [p[1] for p in locations],
        'x_transf': [c[0] for c in coords_transf],
        'y_transf': [c[1] for c in coords_transf]
    })
    
    # Añadir columnas adicionales para análisis
    df['distancia_desde_origen'] = [0, distances[0], distances[2]]
    
    return df

def exportar_a_json(df_puntos, df_clasificados, datos_triangulo, nombre_archivo="datos_triangulo.json"):
    """
    Exporta los datos a un archivo JSON.
    
    Args:
        df_puntos: DataFrame con la información de los puntos del triángulo
        df_clasificados: DataFrame con puntos clasificados (puede ser None)
        datos_triangulo: Diccionario con información del triángulo
        nombre_archivo: Nombre del archivo JSON a crear
    """
    # Crear diccionario para exportar
    datos_json = {
        'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'triangulo': {
            'puntos': df_puntos.to_dict(orient='records'),
            'distancias': {
                'punto1_punto2': datos_triangulo['distancias'][0],
                'punto2_punto3': datos_triangulo['distancias'][1],
                'punto3_punto1': datos_triangulo['distancias'][2]
            },
            'perimetro': sum(datos_triangulo['distancias']),
            'area_heron': datos_triangulo['area_heron'],
            'area_determinante': datos_triangulo['area_determinante']
        }
    }
    
    # Añadir puntos clasificados si existen
    if df_clasificados is not None and not df_clasificados.empty:
        datos_json['puntos_clasificados'] = df_clasificados.to_dict(orient='records')
    
    # Exportar a JSON
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos_json, f, ensure_ascii=False, indent=4)
    
    print(f"\nDatos exportados correctamente a {nombre_archivo}")
    return datos_json

def main():
    try:
        # Crear un objecto de tipo geolocalizador
        geolocator = Nominatim(user_agent="proyecto_feria")
        print("Geolocalizador inicializado correctamente")
        
        # Lista para almacenar las ubicaciones
        locations = []
        location_names = []
        
        # Solicitar tres ubicaciones
        for i in range(1, 4):
            while True:
                try:
                    coordenada = input(f"Ingrese el lugar {i}: ")
                    if coordenada == "":
                        print("La cadena está vacía, por favor ingrese un lugar válido.")
                        continue
                    
                    print(f"El lugar ingresado es: {coordenada}")
                    location = geolocator.geocode(coordenada)
                    
                    if location:
                        print(f"Las coordenadas de {coordenada} son: {location.latitude}, {location.longitude}")
                        locations.append((location.latitude, location.longitude))
                        location_names.append(coordenada)
                        break
                    else:
                        print(f"No se encontraron las coordenadas para {coordenada}. Intente con otro lugar.")
                except Exception as e:
                    print(f"Error de tipo: {e}")
        
        # Extraer puntos
        p0, p1, p2 = locations
        
        # Inicializar el objeto Geodesic
        geod = Geodesic.WGS84
        
        # Calcular las distancias
        g1 = geod.Inverse(p0[0], p0[1], p1[0], p1[1])
        g2 = geod.Inverse(p1[0], p1[1], p2[0], p2[1])
        g3 = geod.Inverse(p2[0], p2[1], p0[0], p0[1])
        
        # Obtener las distancias (en metros)
        d1 = g1['s12']
        d2 = g2['s12']
        d3 = g3['s12']
        
        print(f"\nDistancias entre puntos:")
        print(f"Distancia de {location_names[0]} a {location_names[1]}: {d1:.2f} metros")
        print(f"Distancia de {location_names[1]} a {location_names[2]}: {d2:.2f} metros")
        print(f"Distancia de {location_names[2]} a {location_names[0]}: {d3:.2f} metros")
        
        # Verificar si los puntos forman un triángulo válido
        if d1 + d2 <= d3 or d2 + d3 <= d1 or d3 + d1 <= d2:
            print("\n¡Error! Los puntos seleccionados no forman un triángulo válido (la suma de dos lados debe ser mayor que el tercer lado).")
            return
        
        # Usar la fórmula de Herón para calcular el área
        s = (d1 + d2 + d3) / 2  # Semi-perímetro
        area_heron = (s * (s - d1) * (s - d2) * (s - d3)) ** 0.5  # Área por la fórmula de Herón
        print(f"\nÁrea del triángulo (fórmula de Herón): {area_heron:.2f} metros cuadrados")
        
        # Transformar coordenadas geográficas a coordenadas cartesianas para visualización
        v0 = transformacion_coordenada(p0, p0)  # El origen es (0,0)
        v1 = transformacion_coordenada(p1, p0)
        v2 = transformacion_coordenada(p2, p0)
        
        # Calcular área usando el método del determinante con coordenadas cartesianas
        area_determinante = area_triangulo(v0, v1, v2)
        print(f"Área del triángulo (determinante): {area_determinante:.2f} metros cuadrados")
        
        # Crear DataFrame con los datos del triángulo
        df_puntos = crear_dataframes(locations, location_names, (d1, d2, d3))
        print("\nDatos del triángulo:")
        print(df_puntos)
        
        # Crear DataFrame para puntos clasificados
        df_clasificados = pd.DataFrame(columns=['nombre', 'latitud', 'longitud', 'x_transf', 'y_transf', 'clasificacion'])
        
        # Datos del triángulo para exportar
        datos_triangulo = {
            'distancias': (d1, d2, d3),
            'area_heron': area_heron,
            'area_determinante': area_determinante
        }
        
        # Mostrar el triángulo con la información de distancias y áreas
        dibujar_triangulo_con_datos(v0, v1, v2, (d1, d2, d3), area_heron, area_determinante, df_puntos)
        
        # Solicitar un punto para clasificar
        while True:
            try:
                respuesta = input("\n¿Desea clasificar un punto respecto al triángulo? (s/n): ").lower()
                if respuesta != 's':
                    break
                    
                punto_nombre = input("Ingrese el lugar para clasificar: ")
                if punto_nombre == "":
                    print("La cadena está vacía")
                    continue
                    
                location_punto = geolocator.geocode(punto_nombre)
                
                if location_punto:
                    print(f"Las coordenadas de {punto_nombre} son: {location_punto.latitude}, {location_punto.longitude}")
                    p_clasificar = (location_punto.latitude, location_punto.longitude)
                    
                    # Transformar coordenadas
                    v_clasificar = transformacion_coordenada(p_clasificar, p0)
                    
                    # Clasificar punto
                    resultado = clasificar_punto(v_clasificar, v0, v1, v2)
                    print(f"El punto está {resultado} del triángulo")
                    
                    # Añadir al DataFrame de puntos clasificados
                    nuevo_punto = pd.DataFrame({
                        'nombre': [punto_nombre],
                        'latitud': [p_clasificar[0]],
                        'longitud': [p_clasificar[1]],
                        'x_transf': [v_clasificar[0]],
                        'y_transf': [v_clasificar[1]],
                        'clasificacion': [resultado]
                    })
                    df_clasificados = pd.concat([df_clasificados, nuevo_punto], ignore_index=True)
                    
                    # Actualizar gráfico con todos los puntos clasificados
                    dibujar_triangulo_con_datos(v0, v1, v2, (d1, d2, d3), area_heron, area_determinante, 
                                               df_puntos, df_clasificados)
                else:
                    print(f"No se encontraron las coordenadas para {punto_nombre}")
            except Exception as e:
                print(f"Error de tipo: {e}")
        
        # Exportar datos a JSON
        nombre_archivo = input("\nIngrese nombre para el archivo JSON (o presione Enter para usar el predeterminado): ")
        if nombre_archivo == "":
            nombre_archivo = "datos_triangulo.json"
        else:
            if not nombre_archivo.endswith('.json'):
                nombre_archivo += '.json'
        
        datos_json = exportar_a_json(df_puntos, df_clasificados, datos_triangulo, nombre_archivo)
        
        # Análisis estadístico básico
        print("\nAnálisis estadístico del triángulo:")
        print(f"- Perímetro total: {sum(datos_triangulo['distancias']):.2f} metros")
        print(f"- Distancia media entre puntos: {sum(datos_triangulo['distancias'])/3:.2f} metros")
        print(f"- Distancia máxima: {max(datos_triangulo['distancias']):.2f} metros")
        print(f"- Distancia mínima: {min(datos_triangulo['distancias']):.2f} metros")
        
        if not df_clasificados.empty:
            print("\nAnálisis de puntos clasificados:")
            print(f"- Total de puntos clasificados: {len(df_clasificados)}")
            conteo = df_clasificados['clasificacion'].value_counts()
            for categoria, cantidad in conteo.items():
                print(f"- Puntos {categoria}: {cantidad} ({cantidad/len(df_clasificados)*100:.1f}%)")
    
    except Exception as e:
        print(f"Ocurrió un error en el programa principal: {e}")

if __name__ == "__main__":
    main()