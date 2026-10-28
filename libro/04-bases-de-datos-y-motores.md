# Capítulo 4. Sistemas de bases de datos y sus motores

## 4.1. Definición académica

Una base de datos es una colección organizada de datos, diseñada para facilitar almacenamiento, consulta y actualización. Un sistema gestor de bases de datos (DBMS o SGBD) es el software que administra ese conjunto: interpreta consultas, controla acceso, integridad, concurrencia, transacciones y persistencia. «Base de datos» designa los datos organizados; «motor» suele referirse al software que los gestiona o ejecuta consultas.

## 4.2. Explicación sencilla

La base de datos sería una biblioteca ordenada, y el motor el equipo y los procedimientos que permiten encontrar, prestar, incorporar y proteger los libros. El archivo CSV es comparable con una lista impresa: contiene información tabular, pero por sí solo no aporta todas las capacidades de un SGBD.

## 4.3. Familias de almacenamiento

Los sistemas relacionales almacenan datos en tablas con relaciones y suelen consultarse mediante SQL. Los sistemas documentales organizan objetos como documentos JSON. Los de clave-valor permiten recuperar un valor por una clave. Los orientados a grafos enfatizan nodos y relaciones; los columnares priorizan ciertas cargas analíticas. Se elige tecnología según tipo de dato, volumen, patrón de uso, consistencia, complejidad y costo.

PostgreSQL, MySQL, SQL Server y Oracle son ejemplos de gestores relacionales que suelen utilizarse para operación empresarial. DuckDB es un motor analítico embebido que permite realizar consultas SQL sobre archivos y tablas sin desplegar un servidor; en la práctica lo controlamos con Python. BigQuery y Snowflake son soluciones habituales de analítica y almacenamiento en la nube. Un mismo producto puede soportar más de un tipo de carga: OLTP y OLAP describen principalmente patrones de trabajo y diseño, no etiquetas comerciales exclusivas.

## 4.4. Criterios para elegir

Antes de seleccionar un motor, definir: quién consultará, cuántos registros se generan, cuántos usuarios escribirán simultáneamente, qué latencia se requiere, qué disponibilidad es necesaria, quién administrará el sistema y cómo se factura. Un motor adecuado para registrar pagos no tiene necesariamente que ser el óptimo para analizar series históricas.

## 4.5. Ejercicios propuestos

- **Ejercicio conceptual.** Comparar un CSV, un gestor relacional transaccional y un motor analítico en una matriz con lectura, escritura, control de integridad y uso típico.
- **Ejercicio aplicado.** Justificar por qué DuckDB es conveniente para un laboratorio local con CSV y consultas SQL.
- **Ejercicio de razonamiento.** Definir un caso donde se preferiría un servidor PostgreSQL, uno donde sería útil DuckDB y uno que exigiría evaluar una arquitectura distribuida.

**Evidencia:** ficha de decisión tecnológica de una página.

---

[← Capítulo 3](03-dato-informacion-conocimiento.md) · [Índice](README.md) · [Capítulo 5 →](05-modelo-relacional-y-sql.md)
