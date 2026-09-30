# Generador de datos de ejemplo

> Este documento tiene el detalle técnico. Para hacer la práctica alcanza con el [README principal](../README.md).

Los CSV de [`raw/`](../raw) simulan una **extracción del sistema transaccional (OLTP) de EcoBottle AR** con fecha de corte **2025-09-30 23:59:59**. Contienen los pedidos del 01/01/2024 al 30/09/2025 y todo lo que ocurrió hasta el corte (pagos, envíos, encuestas y sesiones web). Todos los horarios están en hora local de Argentina.

Los datos no se generan tabla por tabla. Se simula el negocio de punta a punta (clientes que se registran, compran, pagan, reciben el envío, navegan la web y responden la encuesta) y cada tabla sale de esa simulación. Así, fechas, montos y estados son coherentes entre sí.

## Uso

```bash
python generator/generate_raw.py     # regenera raw/ (semilla 42)
python generator/validate_raw.py     # valida las reglas y muestra los KPIs mensuales esperados
```

- Solo usan la biblioteca estándar de Python (3.9+), no hace falta instalar nada.
- Con la misma semilla se obtienen exactamente los mismos archivos.
- `--seed N` genera otra variante del dataset; `--out carpeta` / `--dir carpeta` cambian la ubicación.
- `validate_raw.py` sale con código 1 si alguna regla falla. El resumen de KPIs sirve para contrastar los números del dashboard.

## Volumen aproximado

| Tabla | Filas | Tabla | Filas |
|---|---:|---|---:|
| customer | ~3.500 | payment | ~12.000 |
| address | ~3.800 | shipment | ~7.000 |
| sales_order | ~12.000 | web_session | ~100.000 |
| sales_order_item | ~14.500 | nps_response | ~3.000 |

## Reglas del sistema de origen

### Clientes y direcciones
- Los IDs son autoincrementales: se asignan en orden cronológico de alta, pedido, sesión, etc.
- Hay una base de clientes registrada antes de 2024. El resto se registra al comprar: en la web, al iniciar la sesión en la que compra; en la tienda, en la caja. Algunos solo se suscriben al newsletter y nunca compran: no tienen dirección cargada.
- Cada cliente tiene de 1 a 3 direcciones propias. La principal se carga en el alta y las demás durante el checkout. **Una dirección nunca se comparte entre clientes.**
- `status = 'I'`: clientes que pidieron la baja. Ninguno compró en los últimos 120 días.
- Los emails son ficticios (dominios `example.*`). Los teléfonos usan la característica de la ciudad del cliente.
- CABA no forma parte del catálogo: las ciudades de Buenos Aires son del interior de la provincia (La Plata, Mar del Plata, Quilmes, San Isidro, Bahía Blanca).

### Pedidos e ítems
- Los precios de lista **no incluyen IVA** y son constantes (sin inflación). `unit_price = list_price`; las promociones se registran en `discount_amount`.
- Cada pedido tiene **una línea por producto**.
- `subtotal = Σ line_total`, `tax_amount = 21 % del subtotal` y `total_amount = subtotal + tax_amount + shipping_fee`.
- El envío es gratis con subtotal desde $45.000 o durante Hot Sale / CyberMonday. Si no, la tarifa depende de la provincia destino: BA $1.200, CBA y SF $1.500, MZA $1.800.
- **ONLINE:** `store_id` es NULL. La facturación suele coincidir con la dirección principal (5 % NULL).
- **OFFLINE:**
  - Horario: lunes a sábado de 10 a 21 h; cerrado el 1/1, el 1/5 y el 25/12.
  - `shipping_address_id` es la dirección de la tienda (el cliente se lleva el producto).
  - La facturación es opcional (consumidor final).
  - El 5 % de las ventas se envía a domicilio desde la tienda.

### Ciclo de vida del pedido

| sales_order.status | payment.status | shipment.status | Significado |
|---|---|---|---|
| CREATED | PENDING | — | Esperando el pago (ej. cupón de efectivo de Mercado Pago) |
| CANCELLED | FAILED | — | Pago rechazado o cupón vencido (72 h) |
| CANCELLED | REFUNDED | CANCELLED | El cliente canceló después de pagar, antes del despacho |
| PAID | PAID | READY / SHIPPED | Pagado, en preparación o en viaje |
| FULFILLED | PAID | DELIVERED | Entregado (online o envío desde tienda) |
| FULFILLED | PAID | — | Venta en tienda |
| REFUNDED | REFUNDED | DELIVERED / — | Devolución posterior a la entrega o a la compra en tienda |

- **Pagos online:** con tarjeta se acreditan en segundos; con Mercado Pago (`GATEWAY`), en minutos. Los cupones de efectivo pueden tardar hasta 72 h.
- **Pagos en tienda:** son inmediatos (`CASH`, `CARD`, `TRANSFER`).
- `paid_at` y `transaction_ref` solo existen si el pago se concretó. El efectivo no tiene referencia.
- **Envíos (Correo Argentino):**
  - El envío se crea cuando se confirma el pago (`READY`).
  - Se despacha entre las 16 y las 19 h: el mismo día hábil si el pago entró antes de las 13 h, si no el día hábil siguiente.
  - Tarda de 1 a 5 días hábiles según el destino.
  - El tracking se asigna al despachar.
- El estado refleja la situación a la fecha de corte, así que solo los pedidos de los últimos días pueden seguir en `CREATED` o `PAID`.

### Encuesta NPS
- Se envía a las 10 h, 7 días después de la entrega. En compras en tienda, al día siguiente.
- Responde ~30 % en online y ~24 % en tienda. El 4 % de las respuestas es anónima (`customer_id` NULL).
- El puntaje depende de la experiencia (demora de la entrega, devolución) y el comentario es acorde al puntaje.
- `nps_response` no tiene `order_id`: se relaciona con el cliente y el canal.

### Sesiones web
- `source`:
  - `ads`: campañas pagas en redes.
  - `direct` y `referral`: incluyen el tráfico que genera el newsletter por email.
  - `organic`: búsquedas.
- Cada compra online ocurre dentro de una sesión del cliente. Las sesiones con `customer_id` NULL son de visitantes no logueados, incluidas las previas a registrarse.
- `ended_at` es NULL cuando la sesión no registró evento de cierre o seguía abierta al corte.
