# Capítulo 14. Laboratorio paso a paso

## 14.1. Qué se entrega

Un repositorio derivado por fork del [repositorio de la materia](../README.md), con transformaciones SQL en `sql/`, dimensiones y hechos correctamente conectados, consultas para seis indicadores, archivos de `dw/` generados por el programa, documentación y una visualización legible. EcoBottle AR es una empresa ficticia que vende dos modelos de botellas reutilizables en línea y en cuatro tiendas físicas.

## 14.2. Preparación del ambiente

Instalar Git y Python 3.9 o posterior. Realizar un fork propio del repositorio y clonarlo; sustituir `URL_DEL_FORK` por la URL real. La carpeta que se crea lleva el nombre del fork.

```bash
git clone URL_DEL_FORK
cd NOMBRE_DE_LA_CARPETA
python -m venv .venv
```

Activar el entorno virtual:

- macOS/Linux: `source .venv/bin/activate`
- Windows (PowerShell): `.venv\Scripts\activate`

Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

El archivo `requirements.txt` especifica la dependencia de DuckDB. No es necesario instalar un servidor de bases de datos. En Mac, si el comando `python` no existe, usar `python3`.

## 14.3. Inspección inicial

```bash
python run_sql.py --explorar
```

En la interfaz de DuckDB —o en la consola de respaldo— ejecutar:

```sql
SELECT * FROM raw.customer LIMIT 5;
DESCRIBE raw.sales_order;
SELECT COUNT(*) FROM raw.web_session;
```

Identificar tipos de dato, claves, nulos y magnitud. No modificar `raw/`: son archivos de origen. El modo exploración no ejecuta los archivos de transformación SQL.

## 14.4. Construcción

Primero estudiar `sql/01_dimensiones.sql`, que contiene una dimensión producto resuelta con clave subrogada. Completar las demás dimensiones de acuerdo con el modelo diseñado. Luego escribir `sql/02_hechos.sql` con su grano, restricciones y claves foráneas. Finalmente completar `sql/03_consultas.sql` con verificaciones y preguntas de negocio.

Ejecutar:

```bash
python run_sql.py
```

El programa reconstruye `warehouse.duckdb`, ejecuta cada archivo SQL por orden alfabético, exporta las tablas creadas a `dw/` y genera `dw/modelo_estrella.md`. Para inspeccionar el modelo final con la interfaz:

```bash
python run_sql.py --ui
```

## 14.5. Control de calidad obligatorio

- Conciliar importes de `sales_order` con los KPIs, respetando los estados válidos.
- Comprobar PK únicas y no nulas en cada dimensión y tabla de hechos.
- Comprobar que las FK de hechos encuentran su dimensión.
- Verificar que el número de filas se corresponda con el grano declarado.
- Validar la fórmula NPS y la población de respuestas.
- Evaluar si los cortes por provincia representan correctamente la dirección de envío y el canal offline.
- Asegurar que las consultas mensuales usen fechas comparables.
- Comprobar que el resultado se reconstruye desde cero en otra computadora.

## 14.6. Visualización y relato ejecutivo

Proponer como mínimo: un encabezado con período y filtros; tarjetas de ventas, ticket promedio, actividad y NPS; serie mensual de ventas; comparación de provincias; ranking de producto; tendencia de NPS. Incorporar fuente, período de corte y definiciones accesibles. Usar la herramienta de visualización que indique la cátedra; el producto SQL y los CSV quedan desacoplados del software de BI.

## 14.7. Documentación

El README del fork debe explicar propósito, requisitos, pasos reproducibles, diseño del modelo, grano, relaciones, convenciones de cálculo, capturas del tablero, supuestos, limitaciones y hallazgos. Los commits deben comunicar avances comprensibles. Es preferible un proyecto pequeño que pueda reconstruirse y explicarse a un conjunto de scripts que solo funcionan en la computadora de quien lo hizo.

## 14.8. Criterios de evaluación

| Criterio | Peso |
|---|---|
| Modelo dimensional, SQL y calidad de datos | 40 % |
| Dashboard, claridad visual e interpretación | 30 % |
| Reproducibilidad, uso de consola/Git y documentación | 20 % |
| Argumentación, ética y recomendaciones | 10 % |

---

[← Capítulo 13](13-ux-e-investigacion-de-usuarios.md) · [Índice](README.md) · [Apéndice A →](apendice-a-planificacion.md)
