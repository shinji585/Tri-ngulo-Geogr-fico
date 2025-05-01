# Triángulo Geográfico

Una herramienta para crear, visualizar y analizar triángulos utilizando coordenadas geográficas de lugares reales. Este programa permite calcular distancias, áreas y clasificar puntos adicionales con respecto al triángulo formado.

## Características

- Creación de triángulos a partir de lugares reales utilizando geocodificación
- Cálculo preciso de distancias geodésicas entre puntos
- Transformación de coordenadas geográficas a coordenadas cartesianas para visualización
- Cálculo del área utilizando dos métodos diferentes (fórmula de Herón y determinantes)
- Clasificación de puntos adicionales como interiores, en la frontera o exteriores al triángulo
- Visualización gráfica del triángulo con información detallada
- Exportación de datos a formato JSON para análisis posteriores

## Requisitos del sistema

- Python 3.6 o superior
- Conexión a internet (para la geocodificación)

## Instalación

1. Clone este repositorio o descargue el archivo de código fuente

2. Instale las dependencias necesarias:

```bash
pip install numpy matplotlib geopy geographiclib pandas
```

Alternativamente, puede usar el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Dependencias

El programa utiliza las siguientes bibliotecas de Python:

- **numpy**: Para operaciones matemáticas y manejo de matrices
- **matplotlib**: Para la visualización gráfica del triángulo
- **geopy**: Para la geocodificación de lugares
- **geographiclib**: Para cálculos geodésicos precisos
- **pandas**: Para manipulación y análisis de datos

## Uso

Para ejecutar el programa:

```bash
python triangulo_geografico.py
```

### Flujo de trabajo

1. El programa solicitará tres ubicaciones para formar el triángulo (puede ser el nombre de cualquier lugar, ciudad, dirección, etc.)
2. Se calcularán automáticamente las distancias entre puntos y se verificará si forman un triángulo válido
3. Se calculará el área del triángulo utilizando dos métodos diferentes
4. Se mostrará una visualización gráfica del triángulo con toda la información relevante
5. Opcionalmente, puede clasificar puntos adicionales con respecto al triángulo
6. Finalmente, los datos se pueden exportar a un archivo JSON

### Ejemplo de uso

```
Geolocalizador inicializado correctamente
Ingrese el lugar 1: Madrid
El lugar ingresado es: Madrid
Las coordenadas de Madrid son: 40.4167047, -3.7035825
Ingrese el lugar 2: Barcelona
El lugar ingresado es: Barcelona
Las coordenadas de Barcelona son: 41.3828939, 2.1774322
Ingrese el lugar 3: Valencia
El lugar ingresado es: Valencia
Las coordenadas de Valencia son: 39.4697065, -0.3763353

Distancias entre puntos:
Distancia de Madrid a Barcelona: 504064.23 metros
Distancia de Barcelona a Valencia: 303065.83 metros
Distancia de Valencia a Madrid: 301839.85 metros

Área del triángulo (fórmula de Herón): 37893068471.67 metros cuadrados
Área del triángulo (determinante): 37893068432.86 metros cuadrados
```

## Funcionalidades detalladas

### Transformación de coordenadas

El programa transforma coordenadas geográficas (latitud, longitud) en coordenadas cartesianas (x, y) para facilitar la visualización y los cálculos geométricos.

### Cálculo de áreas

El área del triángulo se calcula utilizando dos métodos diferentes:
- **Fórmula de Herón**: Utilizando las longitudes de los lados
- **Método del determinante**: Utilizando las coordenadas cartesianas transformadas

### Clasificación de puntos

Permite clasificar puntos adicionales como:
- **Interior**: El punto está dentro del triángulo
- **Frontera**: El punto está en uno de los lados del triángulo
- **Exterior**: El punto está fuera del triángulo

### Exportación de datos

Todos los datos del triángulo y los puntos clasificados se pueden exportar a un archivo JSON para análisis posteriores o integración con otros sistemas.

## Limitaciones

- La transformación de coordenadas utiliza una aproximación simple basada en la proyección de Mercator, que puede tener imprecisiones para distancias muy grandes
- La geocodificación depende de la disponibilidad y precisión de los datos en los servicios utilizados
- El programa no está optimizado para triángulos extremadamente grandes (que abarquen grandes porciones del globo terrestre)

## Autores

- shinji585
- willsepulvedam