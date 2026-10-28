# Capítulo 3. Dato, información y conocimiento

## 3.1. Definición académica

Un dato es una representación registrada de un hecho o una observación. La información surge al organizar e interpretar datos en un contexto. El conocimiento aparece cuando una persona u organización puede relacionar esa información con reglas, experiencia y objetivos para fundamentar decisiones. Esta secuencia es la base de las organizaciones orientadas a datos (*data-driven*).

## 3.2. Explicación para principiantes

«25000» aislado es un dato. «La compra 815 costó ARS 25.000 el 12 de septiembre» es información. «Las compras del canal web tienen mayor ticket en determinada campaña, por lo que conviene evaluar una inversión» es una hipótesis de conocimiento; necesita contraste antes de transformarse en decisión. Tener más datos no implica automáticamente decidir mejor.

## 3.3. Tipos, fuentes y calidad

Los datos pueden ser estructurados (filas y columnas), semiestructurados (JSON, XML) y no estructurados (texto libre, audio, imágenes). También pueden ser primarios, si se recolectan para un estudio específico, o secundarios, si se reutilizan desde otra fuente. Los sistemas digitales generan datos transaccionales (pedidos, pagos), conductuales (sesiones), maestros (clientes y productos) y de percepción (encuestas).

La calidad puede examinarse mediante completitud, unicidad, validez, consistencia, exactitud y oportunidad. Un campo `NULL` no significa cero: puede representar que un valor se desconoce o no aplica. El significado debe constar en un diccionario de datos. Para trabajar con personas, recopilar solamente lo necesario para un propósito legítimo y claro.

## 3.4. Aplicación a EcoBottle

El repositorio contiene 13 archivos CSV de origen: `channel`, `province`, `product_category`, `product`, `store`, `customer`, `address`, `sales_order`, `sales_order_item`, `payment`, `shipment`, `web_session` y `nps_response`. Hay dos canales, cuatro provincias, dos productos y registros de órdenes, visitas y encuestas. Los datos son ficticios y representan una fotografía del negocio con corte al 30/09/2025, con pedidos desde el 01/01/2024. Los montos se expresan en pesos argentinos. El detalle de cada tabla está en el [README de la práctica](../README.md#las-tablas).

## 3.5. Ejercicios propuestos

- **Ejercicio inicial.** Para «cliente 17», «compra del producto A» y «9 puntos NPS», indicar qué contexto falta para producir información.
- **Ejercicio guiado.** Clasificar las 13 fuentes de EcoBottle en catálogos, maestros, transaccionales, actividad digital y encuestas.
- **Ejercicio de análisis.** Formular cinco preguntas que un gerente puede responder con estas fuentes y dos que no puede responder sin datos adicionales.

**Evidencia:** glosario con al menos 20 términos y catálogo de fuentes.

---

[← Capítulo 2](02-git-github.md) · [Índice](README.md) · [Capítulo 4 →](04-bases-de-datos-y-motores.md)
