# Trabajo Práctico Final — Introducción al Marketing Online y los Negocios Digitales

Repositorio del trabajo práctico final de la materia.

**Consigna y documento principal:** [Trabajo Práctico Final](https://docs.google.com/document/d/15RNP3FVqLjO4jzh80AAkK6mUR5DOLqPxLjQxqvdzrYg/edit?usp=sharing)
**Diagrama Entidad Relación:** [DER](./assets/DER.png)

## Estructura

```
raw/         datos de origen (CSV), uno por tabla del sistema transaccional
generator/   generador y validador de los datos de raw/
assets/      diagrama entidad relación
```

## Datos de origen

Los CSV de `raw/` representan una extracción del sistema transaccional de EcoBottle AR con fecha de corte **30/09/2025 23:59:59**. Incluyen los pedidos del 01/01/2024 al 30/09/2025. Las reglas de negocio que respetan los datos (estados, montos, envíos, NPS, sesiones) están descriptas en [`generator/README.md`](./generator/README.md).

Para regenerarlos o validarlos (no requiere dependencias):

```bash
python generator/generate_raw.py
python generator/validate_raw.py
```
