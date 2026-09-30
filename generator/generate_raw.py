#!/usr/bin/env python3
"""Generador reproducible de los datos de ejemplo de EcoBottle AR (carpeta raw/).

Simula el sistema transaccional (OLTP) de EcoBottle: clientes que se registran,
compran online o en tienda, pagan, reciben envíos, navegan la web y responden la
encuesta NPS. Todas las tablas se derivan de esa simulación, por lo que fechas,
montos y estados son coherentes entre sí.

Uso:
    python generator/generate_raw.py                     # semilla 42, escribe en raw/
    python generator/generate_raw.py --seed 7 --out tmp/  # otra semilla / carpeta

Solo usa la biblioteca estándar (Python 3.9+). Las reglas de negocio simuladas
están documentadas en generator/README.md.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import string
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Parámetros generales
# ---------------------------------------------------------------------------
START = date(2024, 1, 1)                      # primer día con pedidos
END = date(2025, 9, 30)                       # último día con pedidos
START_DT = datetime.combine(START, time())
SNAPSHOT = datetime(2025, 9, 30, 23, 59, 59)  # momento de la extracción

TARGET_ONLINE_ORDERS = 7300
TARGET_OFFLINE_ORDERS = 4700
TARGET_SESSIONS = 100_000
PRE_EXISTING_CUSTOMERS = 650       # clientes registrados antes de 2024
NEWSLETTER_ONLY_CUSTOMERS = 180    # se registran en la web pero nunca compran
P_NEW_CUSTOMER = {1: 0.24, 2: 0.20}  # prob. de que un pedido sea de un cliente nuevo

TAX_RATE = 0.21                    # IVA sobre el subtotal (los precios de lista no incluyen IVA)
FREE_SHIPPING_FROM = 45000.00      # subtotal desde el cual el envío es gratis
SHIPPING_FEE = {1: 1200.00, 2: 1500.00, 3: 1500.00, 4: 1800.00}  # por provincia destino

# ---------------------------------------------------------------------------
# Catálogos
# ---------------------------------------------------------------------------
CHANNELS = [(1, "ONLINE", "Tienda Online"), (2, "OFFLINE", "Tiendas Físicas")]
PROVINCES = [(1, "Buenos Aires", "BA"), (2, "Córdoba", "CBA"), (3, "Santa Fe", "SF"), (4, "Mendoza", "MZA")]
PROVINCE_WEIGHTS = {1: 0.44, 2: 0.22, 3: 0.21, 4: 0.13}
CATEGORIES = [(1, "Bottles", None), (2, "Classic", 1), (3, "Sport", 1)]
PRODUCT_LAUNCH = datetime(2023, 3, 1)
PRODUCTS = [
    (1, "ECO-CLASSIC-A", "Classic A Bottle", 2, 12000.00),
    (2, "ECO-SPORT-B", "Sport B Bottle", 3, 15000.00),
]
LIST_PRICE = {p[0]: p[4] for p in PRODUCTS}

# provincia -> [(ciudad, código postal, característica telefónica, peso)]
CITIES = {
    1: [("La Plata", "1900", "221", 0.30), ("Mar del Plata", "7600", "223", 0.22),
        ("Quilmes", "1878", "11", 0.20), ("San Isidro", "1642", "11", 0.16),
        ("Bahía Blanca", "8000", "291", 0.12)],
    2: [("Córdoba", "5000", "351", 0.62), ("Río Cuarto", "5800", "358", 0.20),
        ("Villa Carlos Paz", "5152", "3541", 0.18)],
    3: [("Rosario", "2000", "341", 0.55), ("Santa Fe", "3000", "342", 0.30),
        ("Rafaela", "2300", "3492", 0.15)],
    4: [("Mendoza", "5500", "261", 0.50), ("Godoy Cruz", "5501", "261", 0.30),
        ("San Rafael", "5600", "260", 0.20)],
}
FAST_CITIES = {"La Plata", "Quilmes", "San Isidro"}  # cerca del depósito online
BIG_CITIES = {"Córdoba", "Rosario", "Santa Fe", "Mendoza", "Godoy Cruz"}

# store_id -> (nombre, provincia, calle, ciudad, cp, apertura). address_id = store_id
STORES = {
    1: ("Tienda BA", 1, "Av. 7 1045", "La Plata", "1900", datetime(2023, 3, 15, 10, 0)),
    2: ("Tienda CBA", 2, "Av. Colón 480", "Córdoba", "5000", datetime(2023, 5, 10, 10, 0)),
    3: ("Tienda SF", 3, "San Martín 850", "Rosario", "2000", datetime(2023, 7, 3, 10, 0)),
    4: ("Tienda MZA", 4, "Av. San Martín 1150", "Mendoza", "5500", datetime(2023, 9, 1, 10, 0)),
}
STORE_WEIGHTS = {1: 0.30, 2: 0.26, 3: 0.25, 4: 0.19}

FIRST_NAMES = [
    "María", "Juan", "Sofía", "Mateo", "Valentina", "Santiago", "Camila", "Benjamín", "Martina",
    "Lucas", "Lucía", "Joaquín", "Julieta", "Tomás", "Catalina", "Nicolás", "Agustina", "Facundo",
    "Florencia", "Franco", "Micaela", "Ignacio", "Carolina", "Gonzalo", "Paula", "Federico",
    "Victoria", "Martín", "Rocío", "Diego", "Milagros", "Pablo", "Antonella", "Emiliano", "Brenda",
    "Matías", "Daniela", "Leandro", "Luciana", "Gabriel", "Ana", "Sebastián", "Belén", "Alejandro",
    "Natalia", "Ezequiel", "Romina", "Hernán", "Silvina", "Ramiro",
]
LAST_NAMES = [
    "González", "Rodríguez", "Gómez", "Fernández", "López", "Díaz", "Martínez", "Pérez", "García",
    "Sánchez", "Romero", "Sosa", "Álvarez", "Torres", "Ruiz", "Ramírez", "Flores", "Acosta",
    "Benítez", "Medina", "Suárez", "Herrera", "Aguirre", "Pereyra", "Gutiérrez", "Giménez",
    "Molina", "Silva", "Castro", "Rojas", "Ortiz", "Núñez", "Luna", "Juárez", "Cabrera", "Ríos",
    "Ferreyra", "Godoy", "Morales", "Domínguez", "Moreno", "Peralta", "Vega", "Carrizo", "Quiroga",
    "Castillo", "Ledesma", "Muñoz", "Ojeda", "Ponce",
]
STREETS = [
    "Av. San Martín", "Belgrano", "Rivadavia", "Sarmiento", "Mitre", "Moreno", "25 de Mayo",
    "9 de Julio", "Av. Colón", "Urquiza", "Independencia", "Italia", "España", "Lavalle", "Tucumán",
    "Salta", "Entre Ríos", "Maipú", "Brown", "Alem", "Av. Pellegrini", "Laprida", "Chacabuco",
    "Güemes", "Dorrego", "Balcarce", "Las Heras", "Pueyrredón", "Castelli", "Alsina",
]
EMAIL_DOMAINS = ["example.com", "example.net", "example.org"]

NPS_COMMENTS = {
    "promoter": ["Todo perfecto", "Volvería a comprar", "Muy conforme con la calidad",
                 "Excelente botella, mantiene la temperatura"],
    "promoter_online": ["Entrega rápida y producto excelente"],
    "promoter_offline": ["Muy buena atención en la tienda"],
    "passive": ["Buen producto, un poco caro", "Podría mejorar el empaque",
                "Correcto, sin sorpresas", "Me gustaría más variedad de colores"],
    "passive_online": ["La entrega podría ser más rápida"],
    "detractor": ["La tapa pierde líquido", "No cumplió mis expectativas"],
    "detractor_online": ["Llegó con la caja dañada"],
    "detractor_late": ["Tardó mucho más de lo esperado", "El envío demoró y nadie me avisó"],
    "detractor_offline": ["Tuve que esperar mucho en la caja", "Poco stock en la tienda"],
    "detractor_refund": ["Tuve que devolverlo"],
}

# Tiendas cerradas y sin despachos del correo
HOLIDAYS = {date(2024, 1, 1), date(2024, 5, 1), date(2024, 12, 25),
            date(2025, 1, 1), date(2025, 5, 1), date(2025, 12, 25)}

ONLINE_HOURS = [3, 2, 1.2, 0.8, 0.6, 0.7, 1.2, 2, 3, 4, 5, 5.5,
                6, 6, 5.5, 5.5, 5.5, 6, 7, 8, 9, 9.5, 8, 5]
STORE_HOURS = {  # horario de atención: lunes a sábado de 10 a 21
    "weekday": {10: 4, 11: 6, 12: 7, 13: 6, 14: 5, 15: 5, 16: 6, 17: 8, 18: 9, 19: 8, 20: 5},
    "saturday": {10: 5, 11: 8, 12: 9, 13: 9, 14: 8, 15: 8, 16: 8, 17: 8, 18: 7, 19: 6, 20: 4},
}

MONTH_SEASON = {1: 1.15, 2: 1.10, 3: 1.05, 4: 0.95, 5: 0.95, 6: 0.92,
                7: 0.85, 8: 0.88, 9: 0.95, 10: 1.00, 11: 1.05, 12: 1.15}
SPORT_SHARE = {1: 0.60, 2: 0.55, 3: 0.42, 4: 0.40, 5: 0.42, 6: 0.52,
               7: 0.32, 8: 0.34, 9: 0.40, 10: 0.42, 11: 0.50, 12: 0.58}
ONLINE_WEEKDAY = [1.10, 1.05, 1.00, 1.00, 0.95, 0.85, 1.05]
OFFLINE_WEEKDAY = [0.85, 0.85, 0.90, 0.95, 1.15, 1.60, 0.00]  # domingo cerrado


# ---------------------------------------------------------------------------
# Calendario comercial
# ---------------------------------------------------------------------------
@dataclass
class DayInfo:
    online: float = 1.0          # multiplicador de pedidos online
    offline: float = 1.0         # multiplicador de ventas en tienda
    traffic: float = 1.0         # multiplicador de tráfico web
    promo_discount: float = 0.0  # descuento de campaña (Hot Sale, Cyber, Black Friday)
    free_shipping: bool = False
    campaign: bool = False       # campaña paga en redes -> más tráfico "ads"
    email_day: bool = False      # envío de newsletter -> más tráfico "direct"/"referral"
    sport_share: float = 0.45    # prob. de que un pedido de un solo producto sea Sport B
    extra_transit: tuple = (0, 0)  # días hábiles extra de demora del correo


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def in_range(d: date, start: date, end: date) -> bool:
    return start <= d <= end


def build_day_info(d: date) -> DayInfo:
    progress = (d - START).days / (END - START).days
    season = MONTH_SEASON[d.month]
    info = DayInfo(
        online=season * ONLINE_WEEKDAY[d.weekday()] * (1 + 0.45 * progress),
        offline=season * OFFLINE_WEEKDAY[d.weekday()] * (1 + 0.08 * progress),
        traffic=season * (1 + 0.35 * progress),
        sport_share=SPORT_SHARE[d.month],
    )
    y = d.year
    hot_sale = {2024: (date(2024, 5, 13), date(2024, 5, 15)), 2025: (date(2025, 5, 12), date(2025, 5, 14))}
    if y in hot_sale and in_range(d, *hot_sale[y]):
        info.online *= 3.2
        info.traffic *= 2.4
        info.promo_discount, info.free_shipping, info.campaign = 0.20, True, True
        info.extra_transit = (1, 2)
    if in_range(d, date(2024, 11, 4), date(2024, 11, 6)):  # CyberMonday
        info.online *= 2.6
        info.traffic *= 2.0
        info.promo_discount, info.free_shipping, info.campaign = 0.15, True, True
        info.extra_transit = (1, 2)
    if in_range(d, date(2024, 11, 29), date(2024, 12, 1)):  # Black Friday
        info.online *= 2.0
        info.offline *= 1.3
        info.traffic *= 1.7
        info.promo_discount, info.campaign = 0.15, True
    fathers_day = nth_weekday(y, 6, 6, 3)
    if in_range(d, fathers_day - timedelta(days=10), fathers_day):
        info.online *= 1.6
        info.offline *= 1.8
        info.traffic *= 1.3
        info.sport_share = 0.65
    mothers_day = nth_weekday(y, 10, 6, 3)
    if in_range(d, mothers_day - timedelta(days=10), mothers_day):
        info.online *= 1.35
        info.offline *= 1.4
    childrens_day = nth_weekday(y, 8, 6, 3)
    if in_range(d, childrens_day - timedelta(days=7), childrens_day):
        info.online *= 1.25
        info.offline *= 1.3
        info.sport_share = 0.30
    if in_range(d, date(y, 2, 15), date(y, 3, 10)):  # vuelta a clases
        info.online *= 1.3
        info.offline *= 1.35
        info.sport_share = 0.35
    if in_range(d, date(y, 12, 10), date(y, 12, 24)):  # fiestas
        info.online *= 1.8
        info.offline *= 2.0
        info.traffic *= 1.5
        info.extra_transit = (1, 2)
    if in_range(d, date(y, 12, 26), date(y, 12, 31)):
        info.online *= 0.8
        info.offline *= 0.8
    if d.weekday() == 1 and (d.day - 1) // 7 in (1, 3):  # newsletter: 2.º y 4.º martes
        info.online *= 1.25
        info.traffic *= 1.3
        info.email_day = True
    if in_range(d, date(2024, 7, 1), date(2024, 8, 31)):  # demoras del correo
        info.extra_transit = (2, 5)
    if d in HOLIDAYS:
        info.offline = 0.0
    return info


def is_business_day(d: date) -> bool:
    return d.weekday() < 5 and d not in HOLIDAYS


def add_business_days(d: date, n: int) -> date:
    while n > 0:
        d += timedelta(days=1)
        if is_business_day(d):
            n -= 1
    return d


# ---------------------------------------------------------------------------
# Entidades de la simulación
# ---------------------------------------------------------------------------
@dataclass
class Address:
    province_id: int
    city: str
    postal_code: str
    line1: str
    line2: str | None
    created_at: datetime
    address_id: int | None = None


@dataclass
class Customer:
    first_name: str
    last_name: str
    email: str
    phone: str | None
    created_at: datetime
    province_id: int
    city: tuple
    pref: str                    # ONLINE / OFFLINE / OMNI
    propensity: float            # qué tan seguido compra
    active_until: datetime       # a partir de acá deja de comprar (churn)
    addresses: list = field(default_factory=list)
    status: str = "A"
    deactivated_at: datetime | None = None
    last_order_at: datetime | None = None
    next_order_at: datetime | None = None  # no vuelve a comprar antes de esta fecha
    last_activity: datetime | None = None
    customer_id: int | None = None

    def touch(self, t: datetime) -> None:
        if self.last_activity is None or t > self.last_activity:
            self.last_activity = t


@dataclass
class Order:
    channel_id: int
    order_date: datetime
    customer: Customer
    store_id: int | None
    shipping_address: Address
    billing_address: Address | None
    lines: list                  # [(product_id, qty, unit_price, discount, line_total)]
    subtotal: float
    tax: float
    shipping_fee: float
    total: float
    ships: bool                  # tiene envío (online o envío desde tienda)
    session_start: datetime | None = None
    method: str = ""
    paid_at: datetime | None = None
    failed_at: datetime | None = None
    cancelled_at: datetime | None = None  # cancelación después del pago
    refunded_at: datetime | None = None
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    transaction_ref: str | None = None
    tracking: str | None = None
    order_id: int | None = None


@dataclass
class Session:
    started_at: datetime
    ended_at: datetime | None
    customer: Customer | None
    source: str
    device: str


# ---------------------------------------------------------------------------
# Simulación
# ---------------------------------------------------------------------------
class Simulation:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.days = [START + timedelta(days=n) for n in range((END - START).days + 1)]
        self.info = {d: build_day_info(d) for d in self.days}
        self.customers: list[Customer] = []
        self.orders: list[Order] = []
        self.sessions: list[Session] = []
        self.nps: list[tuple] = []
        self.used_emails: set[str] = set()
        self.used_refs: set[str] = set()
        self.pool_online: list[Customer] = []
        self.w_online: list[float] = []
        self.pool_offline: dict[int, list[Customer]] = {p[0]: [] for p in PROVINCES}
        self.w_offline: dict[int, list[float]] = {p[0]: [] for p in PROVINCES}
        self.store_addresses = {
            sid: Address(prov, city, cp, street, None, opened, address_id=sid)
            for sid, (_, prov, street, city, cp, opened) in STORES.items()
        }

    # -- utilidades ---------------------------------------------------------
    def pick(self, weights: dict):
        return self.rng.choices(list(weights), weights=list(weights.values()))[0]

    def seconds(self, lo: float, hi: float) -> timedelta:
        return timedelta(seconds=round(self.rng.uniform(lo, hi)))

    def poisson(self, lam: float) -> int:
        if lam <= 0:
            return 0
        if lam > 50:
            return max(0, round(self.rng.gauss(lam, math.sqrt(lam))))
        limit, k, p = math.exp(-lam), 0, 1.0
        while True:
            p *= self.rng.random()
            if p <= limit:
                return k
            k += 1

    def online_time(self, d: date) -> datetime:
        hour = self.rng.choices(range(24), weights=ONLINE_HOURS)[0]
        return datetime.combine(d, time(hour)) + timedelta(seconds=self.rng.randrange(3600))

    def store_time(self, d: date) -> datetime:
        hours = STORE_HOURS["saturday" if d.weekday() == 5 else "weekday"]
        hour = self.pick(hours)
        return datetime.combine(d, time(hour)) + timedelta(seconds=self.rng.randrange(3600))

    def unique(self, used: set, make) -> str:
        while True:
            value = make()
            if value not in used:
                used.add(value)
                return value

    # -- clientes y direcciones ---------------------------------------------
    def make_email(self, first: str, last: str) -> str:
        def ascii_lower(s: str) -> str:
            return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()

        f, l = ascii_lower(first), ascii_lower(last)

        def make() -> str:
            base = self.rng.choice([f"{f}.{l}", f"{f}{l}", f"{f[0]}{l}", f"{f}_{l}", f"{l}.{f}"])
            r = self.rng.random()
            if r < 0.35:
                base += str(self.rng.randint(1, 99))
            elif r < 0.65:
                base += str(self.rng.randint(1965, 2006))
            return f"{base}@{self.rng.choice(EMAIL_DOMAINS)}"

        return self.unique(self.used_emails, make)

    def make_phone(self, area: str) -> str:
        digits = "".join(str(self.rng.randint(0, 9)) for _ in range(10 - len(area) - 1))
        digits = str(self.rng.randint(3, 6)) + digits
        split = {2: 4, 3: 3, 4: 2}[len(area)]
        return f"+54 9 {area} {digits[:split]}-{digits[split:]}"

    def new_address(self, province_id: int, city: tuple, created_at: datetime) -> Address:
        line1 = f"{self.rng.choice(STREETS)} {self.rng.randint(100, 4999)}"
        line2 = None
        if self.rng.random() < 0.45:
            line2 = f"Piso {self.rng.randint(1, 12)} Dto {self.rng.choice('ABCDEF')}"
        return Address(province_id, city[0], city[1], line1, line2, created_at)

    def random_city(self, province_id: int) -> tuple:
        options = CITIES[province_id]
        return self.rng.choices(options, weights=[c[3] for c in options])[0]

    def new_customer(self, created_at: datetime, pref: str, province_id: int | None = None,
                     with_address: bool = True) -> Customer:
        if province_id is None:
            province_id = self.pick(PROVINCE_WEIGHTS)
        city = self.random_city(province_id)
        first, last = self.rng.choice(FIRST_NAMES), self.rng.choice(LAST_NAMES)
        lifetime = timedelta(days=self.rng.expovariate(1 / 520))
        c = Customer(
            first_name=first,
            last_name=last,
            email=self.make_email(first, last),
            phone=None if self.rng.random() < 0.08 else self.make_phone(city[2]),
            created_at=created_at,
            province_id=province_id,
            city=city,
            pref=pref,
            propensity=min(self.rng.lognormvariate(0, 0.7), 5.0),
            active_until=max(created_at, START_DT) + lifetime,
        )
        c.touch(created_at)
        if with_address:
            c.addresses.append(self.new_address(province_id, city, created_at))
        self.customers.append(c)
        if pref in ("ONLINE", "OMNI"):
            self.pool_online.append(c)
            self.w_online.append(c.propensity)
        if pref in ("OFFLINE", "OMNI"):
            self.pool_offline[province_id].append(c)
            self.w_offline[province_id].append(c.propensity)
        return c

    def random_pref(self, main: str) -> str:
        return "OMNI" if self.rng.random() < 0.12 else main

    def create_initial_customers(self) -> None:
        for _ in range(PRE_EXISTING_CUSTOMERS):
            pref = self.pick({"ONLINE": 0.50, "OFFLINE": 0.38, "OMNI": 0.12})
            if pref == "ONLINE":
                province, earliest = self.pick(PROVINCE_WEIGHTS), PRODUCT_LAUNCH
            else:
                store = self.pick(STORE_WEIGHTS)
                province, earliest = STORES[store][1], STORES[store][5]
            span = (START_DT - earliest).total_seconds()
            created = earliest + timedelta(seconds=span * self.rng.random() ** 0.8)
            self.new_customer(created, pref, province)
        # Registrados en la web (newsletter) que nunca compran
        span = (SNAPSHOT - START_DT).total_seconds()
        for _ in range(NEWSLETTER_ONLY_CUSTOMERS):
            created = START_DT + timedelta(seconds=self.rng.uniform(0, span))
            self.new_customer(created, "ONLINE", with_address=False)
            self.pool_online.pop()  # no participan de la elección de compradores
            self.w_online.pop()

    def pick_active(self, pool: list, weights: list, t: datetime) -> Customer | None:
        for _ in range(30):
            if not pool:
                return None
            c = self.rng.choices(pool, weights=weights)[0]
            if c.next_order_at and c.next_order_at > t:
                continue
            if c.active_until > t:
                return c
            i = pool.index(c)  # abandonó: no vuelve a comprar
            pool.pop(i)
            weights.pop(i)
        return None

    # -- pedidos ------------------------------------------------------------
    def simulate_orders(self) -> None:
        online_base = TARGET_ONLINE_ORDERS / sum(i.online for i in self.info.values())
        offline_base = TARGET_OFFLINE_ORDERS / sum(i.offline for i in self.info.values())
        for d in self.days:
            info = self.info[d]
            events = [(self.online_time(d), 1, None) for _ in range(self.poisson(online_base * info.online))]
            for _ in range(self.poisson(offline_base * info.offline)):
                events.append((self.store_time(d), 2, self.pick(STORE_WEIGHTS)))
            events.sort(key=lambda e: (e[0], e[1]))
            for t, channel, store in events:
                self.create_order(t, channel, store, info)

    def create_order(self, t: datetime, channel: int, store: int | None, info: DayInfo) -> None:
        rng = self.rng
        if channel == 1:
            session_start = t - self.seconds(4 * 60, 35 * 60)
            c = None
            if rng.random() >= P_NEW_CUSTOMER[1]:
                if rng.random() < 0.06:  # cliente de tienda que prueba la web
                    p = self.pick(PROVINCE_WEIGHTS)
                    c = self.pick_active(self.pool_offline[p], self.w_offline[p], t)
                else:
                    c = self.pick_active(self.pool_online, self.w_online, t)
            if c is None:  # se registra al iniciar la sesión en la que compra
                c = self.new_customer(session_start, self.random_pref("ONLINE"))
            session_start = max(session_start, c.created_at)
            shipping = self.choose_shipping_address(c, session_start, t)
            billing = c.addresses[0] if rng.random() < 0.95 else None
            ships = True
        else:
            session_start = None
            province = STORES[store][1]
            c = None
            if rng.random() >= P_NEW_CUSTOMER[2]:
                c = self.pick_active(self.pool_offline[province], self.w_offline[province], t)
            if c is None:  # se registra en la caja
                home = province if rng.random() < 0.97 else self.pick(PROVINCE_WEIGHTS)
                c = self.new_customer(t - self.seconds(60, 240), self.random_pref("OFFLINE"), home)
            ships = rng.random() < 0.05  # envío a domicilio desde la tienda
            shipping = c.addresses[0] if ships else self.store_addresses[store]
            billing = c.addresses[0] if rng.random() < 0.65 else None

        lines = self.make_lines(channel, info)
        subtotal = round(sum(line[4] for line in lines), 2)
        tax = round(subtotal * TAX_RATE, 2)
        fee = 0.0
        if ships and not (channel == 1 and info.free_shipping) and subtotal < FREE_SHIPPING_FROM:
            fee = SHIPPING_FEE[shipping.province_id]
        order = Order(
            channel_id=channel, order_date=t, customer=c, store_id=store,
            shipping_address=shipping, billing_address=billing, lines=lines,
            subtotal=subtotal, tax=tax, shipping_fee=fee, total=round(subtotal + tax + fee, 2),
            ships=ships, session_start=session_start,
        )
        c.last_order_at = t
        c.next_order_at = t + timedelta(days=7 + min(self.rng.expovariate(1 / 30), 150))
        c.touch(t)
        self.orders.append(order)

    def choose_shipping_address(self, c: Customer, session_start: datetime, t: datetime) -> Address:
        if len(c.addresses) < 3 and self.rng.random() < 0.07:  # carga una dirección nueva en el checkout
            province = c.province_id if self.rng.random() < 0.8 else self.pick(PROVINCE_WEIGHTS)
            created = session_start + (t - session_start) * self.rng.uniform(0.2, 0.9)
            address = self.new_address(province, self.random_city(province), created)
            c.addresses.append(address)
            return address
        if len(c.addresses) > 1 and self.rng.random() < 0.25:
            return self.rng.choice(c.addresses[1:])
        return c.addresses[0]

    def make_lines(self, channel: int, info: DayInfo) -> list:
        rng = self.rng
        if rng.random() < 0.22:
            products = [1, 2]
        else:
            products = [2] if rng.random() < info.sport_share else [1]
        bulk = rng.random() < 0.008  # compras corporativas / regalos
        if bulk:
            pct = 0.15
        elif channel == 1:
            if info.promo_discount:
                pct = info.promo_discount
            elif info.email_day and rng.random() < 0.30:
                pct = 0.10  # cupón del newsletter
            else:
                pct = 0.05 if rng.random() < 0.04 else 0.0
        else:
            if info.promo_discount and rng.random() < 0.5:
                pct = 0.10
            else:
                pct = 0.10 if rng.random() < 0.06 else 0.0  # promo bancaria
        lines = []
        for pid in products:
            qty = rng.randint(6, 15) if bulk else self.pick({1: 0.56, 2: 0.27, 3: 0.11, 4: 0.06})
            price = LIST_PRICE[pid]
            discount = round(qty * price * pct, 2)
            lines.append((pid, qty, price, discount, round(qty * price - discount, 2)))
        return lines

    # -- pagos y envíos -----------------------------------------------------
    def make_ref(self, o: Order) -> str | None:
        rng = self.rng
        alnum = string.ascii_uppercase + string.digits
        if o.method == "CASH":
            return None
        if o.method == "GATEWAY":
            make = lambda: "MP-" + "".join(rng.choices(string.digits, k=11))
        elif o.method == "TRANSFER":
            make = lambda: "TRF-" + "".join(rng.choices(string.digits, k=10))
        elif o.channel_id == 2:
            make = lambda: "POS-" + "".join(rng.choices(alnum, k=10))
        else:
            make = lambda: "CARD-" + "".join(rng.choices(alnum, k=10))
        return self.unique(self.used_refs, make)

    def dispatch_time(self, paid_at: datetime) -> datetime:
        """Pagos confirmados antes de las 13 h de un día hábil salen ese día; si no, el siguiente."""
        d = paid_at.date()
        if not (is_business_day(d) and paid_at.hour < 13):
            d = add_business_days(d, 1)
        return datetime.combine(d, time(16)) + self.seconds(0, 3 * 3600 - 1)

    def delivery_time(self, o: Order) -> datetime:
        address = o.shipping_address
        if o.channel_id == 2:
            lo, hi = (1, 2) if address.province_id == STORES[o.store_id][1] else (2, 4)
        elif address.city in FAST_CITIES:
            lo, hi = 1, 2
        elif address.province_id == 1:
            lo, hi = 2, 3
        elif address.city in BIG_CITIES:
            lo, hi = 2, 4
        else:
            lo, hi = 3, 5
        days = self.rng.randint(lo, hi)
        extra = self.info.get(o.shipped_at.date(), DayInfo()).extra_transit
        if extra != (0, 0):
            days += self.rng.randint(*extra)
        day = add_business_days(o.shipped_at.date(), days)
        return datetime.combine(day, time(9)) + self.seconds(0, 11 * 3600 - 1)

    def simulate_lifecycle(self, o: Order) -> None:
        rng, t0 = self.rng, o.order_date
        if o.channel_id == 1:
            o.method = "CARD" if rng.random() < 0.58 else "GATEWAY"
            if o.method == "CARD":
                if rng.random() < 0.05:
                    o.failed_at = t0 + self.seconds(20, 180)
                else:
                    o.paid_at = t0 + self.seconds(15, 240)
            else:
                x = rng.random()
                if x < 0.22:  # cupón de pago en efectivo (Rapipago / Pago Fácil), vence a las 72 h
                    if rng.random() < 0.25:
                        o.failed_at = t0 + timedelta(hours=72)
                    else:
                        o.paid_at = t0 + timedelta(seconds=round(min(rng.expovariate(1 / 18), 70) * 3600 + 1800))
                elif x < 0.26:
                    o.failed_at = t0 + self.seconds(60, 600)
                else:
                    o.paid_at = t0 + self.seconds(30, 720)
        else:
            o.method = self.pick({"CASH": 0.38, "CARD": 0.50, "TRANSFER": 0.12})
            if o.method == "CARD" and rng.random() < 0.025:  # tarjeta rechazada, se anula la venta
                o.failed_at = t0 + self.seconds(30, 120)
            else:
                o.paid_at = t0 + self.seconds(10, 180)
        if o.paid_at is None:
            return
        o.transaction_ref = self.make_ref(o)
        if not o.ships:
            if rng.random() < 0.02:  # devolución en tienda
                o.refunded_at = o.paid_at + timedelta(days=rng.uniform(1, 25))
            return
        dispatch = self.dispatch_time(o.paid_at)
        if o.channel_id == 1 and rng.random() < 0.015:  # el cliente cancela antes del despacho
            o.cancelled_at = o.paid_at + (dispatch - o.paid_at) * rng.uniform(0.1, 0.9)
            return
        o.shipped_at = dispatch
        o.tracking = f"CA{rng.randrange(10**9):09d}AR"
        o.delivered_at = self.delivery_time(o)
        days = (o.delivered_at - t0).total_seconds() / 86400
        if rng.random() < (0.08 if days > 8 else 0.03):
            o.refunded_at = o.delivered_at + timedelta(days=rng.uniform(2, 15))

    # -- NPS ----------------------------------------------------------------
    def nps_answer(self, o: Order) -> tuple:
        rng = self.rng
        late = False
        if o.ships:
            days = (o.delivered_at - o.order_date).total_seconds() / 86400
            late = days > 7
            mu = 8.7 - 0.5 * max(0.0, days - 5)
        else:
            mu = 8.7
        if o.refunded_at:
            mu -= 3.8
        if any(line[3] > 0 for line in o.lines):
            mu += 0.2
        score = min(10, max(0, round(rng.gauss(mu, 1.7))))
        online = o.channel_id == 1
        if score >= 9:
            bucket, null_p = ["promoter", "promoter_online" if online else "promoter_offline"], 0.35
        elif score >= 7:
            bucket, null_p = ["passive"] + (["passive_online"] if o.ships else []), 0.45
        else:
            bucket = ["detractor"]
            if o.refunded_at:
                bucket = ["detractor_refund"] * 3 + bucket
            if late:
                bucket = ["detractor_late"] * 3 + bucket
            bucket.append("detractor_online" if o.ships else "detractor_offline")
            null_p = 0.15
        comment = None
        if rng.random() >= null_p:
            comment = rng.choice(NPS_COMMENTS[rng.choice(bucket)])
        return score, comment

    def simulate_nps(self) -> None:
        """Encuesta 7 días después de la entrega (compras en tienda: al día siguiente)."""
        rng = self.rng
        for o in self.orders:
            if o.paid_at is None or o.cancelled_at:
                continue
            if o.ships:
                if o.delivered_at is None:
                    continue
                survey = datetime.combine(o.delivered_at.date() + timedelta(days=7), time(10))
                rate, max_hours = 0.30, 72
            else:
                survey = datetime.combine(o.order_date.date() + timedelta(days=1), time(10))
                rate, max_hours = 0.24, 48
            if rng.random() >= rate:
                continue
            responded = survey + timedelta(seconds=round(min(rng.expovariate(1 / 10), max_hours) * 3600))
            if responded > SNAPSHOT:
                continue
            score, comment = self.nps_answer(o)
            customer = None if rng.random() < 0.04 else o.customer  # respuesta anónima
            if customer:
                customer.touch(responded)
            self.nps.append((responded, customer, o.channel_id, score, comment))

    # -- sesiones web -------------------------------------------------------
    def session_source(self, d: date, identified: bool) -> str:
        info = self.info.get(d, DayInfo())
        if info.campaign:
            weights = {"ads": 0.45, "direct": 0.20, "referral": 0.17, "organic": 0.18}
        elif info.email_day:
            weights = {"direct": 0.38, "referral": 0.27, "ads": 0.17, "organic": 0.18}
        else:
            weights = {"direct": 0.28, "organic": 0.28, "ads": 0.26, "referral": 0.18}
        if identified:
            weights["direct"] += 0.10
        return self.pick(weights)

    def session_device(self, source: str, t: datetime) -> str:
        if source == "ads":
            return self.pick({"mobile": 0.80, "desktop": 0.15, "tablet": 0.05})
        desktop = 0.34 + (0.12 if t.weekday() < 5 and 9 <= t.hour < 18 else 0)
        return self.pick({"mobile": 0.94 - desktop, "desktop": desktop, "tablet": 0.06})

    def add_session(self, start: datetime, customer: Customer | None, end: datetime | None = None) -> None:
        if start < START_DT or start > SNAPSHOT:
            return
        if end is None:
            if self.rng.random() < 0.30:  # rebote
                end = start + self.seconds(5, 60)
            else:
                end = start + timedelta(seconds=round(min(self.rng.lognormvariate(math.log(360), 0.8), 4500)))
        if end > SNAPSHOT or self.rng.random() < 0.03:  # sesión abierta o sin evento de cierre
            end = None
        source = self.session_source(start.date(), customer is not None)
        self.sessions.append(Session(start, end, customer, source, self.session_device(source, start)))
        if customer:
            customer.touch(start)

    def simulate_order_sessions(self) -> None:
        rng = self.rng
        for o in self.orders:
            if o.channel_id != 1:
                continue
            c = o.customer
            self.add_session(o.session_start, c, o.order_date + self.seconds(30, 480))
            for _ in range(self.pick({0: 0.45, 1: 0.30, 2: 0.17, 3: 0.08})):  # sesiones de búsqueda previas
                start = o.order_date - self.seconds(3 * 3600, 10 * 86400)
                identified = start >= c.created_at and rng.random() < 0.6
                self.add_session(start, c if identified else None)

    def mark_inactive(self) -> None:
        """Algunos clientes sin compras recientes piden la baja (status = 'I')."""
        for c in self.customers:
            if c.last_order_at is None:
                eligible = c.created_at < SNAPSHOT - timedelta(days=180)
            else:
                eligible = c.last_order_at < SNAPSHOT - timedelta(days=120)
            if eligible and self.rng.random() < 0.15:
                deactivated = c.last_activity + timedelta(days=self.rng.uniform(10, 60))
                if deactivated < SNAPSHOT:
                    c.status, c.deactivated_at = "I", deactivated

    def simulate_browsing_sessions(self) -> None:
        rate = {"ONLINE": 0.9, "OMNI": 0.7, "OFFLINE": 0.15}  # sesiones logueadas por mes
        max_weight = max(ONLINE_HOURS)
        for c in self.customers:
            start = max(c.created_at, START_DT)
            end = min(c.active_until + timedelta(days=30), c.deactivated_at or SNAPSHOT, SNAPSHOT)
            if end <= start:
                continue
            span = (end - start).total_seconds()
            n = self.poisson(span / (30 * 86400) * rate[c.pref] * math.sqrt(c.propensity))
            for _ in range(n):
                while True:
                    t = start + timedelta(seconds=round(self.rng.uniform(0, span)))
                    if self.rng.random() < ONLINE_HOURS[t.hour] / max_weight:
                        break
                self.add_session(t, c)

    def simulate_anonymous_sessions(self) -> None:
        remaining = max(0, TARGET_SESSIONS - len(self.sessions))
        base = remaining / sum(i.traffic for i in self.info.values())
        for d in self.days:
            for _ in range(self.poisson(base * self.info[d].traffic)):
                self.add_session(self.online_time(d), None)

    # -- ejecución y salida -------------------------------------------------
    def run(self) -> None:
        self.create_initial_customers()
        self.simulate_orders()
        for o in self.orders:
            self.simulate_lifecycle(o)
        self.simulate_nps()
        self.simulate_order_sessions()
        self.mark_inactive()
        self.simulate_browsing_sessions()
        self.simulate_anonymous_sessions()
        self.assign_ids()

    def assign_ids(self) -> None:
        """IDs autoincrementales en orden cronológico, como en una base real."""
        self.customers.sort(key=lambda c: c.created_at)
        for i, c in enumerate(self.customers, start=1):
            c.customer_id = i
        addresses = sorted((a for c in self.customers for a in c.addresses), key=lambda a: a.created_at)
        for i, a in enumerate(addresses, start=1001):
            a.address_id = i
        self.addresses = addresses
        self.orders.sort(key=lambda o: o.order_date)
        for i, o in enumerate(self.orders):
            o.order_id = 1_000_000_000 + i
        self.sessions.sort(key=lambda s: s.started_at)
        self.nps.sort(key=lambda n: n[0])

    def write(self, out: Path) -> dict:
        out.mkdir(parents=True, exist_ok=True)
        S = SNAPSHOT
        visible = lambda t: t is not None and t <= S

        def money(x: float) -> str:
            return f"{x:.2f}"

        def ts(t: datetime | None) -> str:
            return t.strftime("%Y-%m-%d %H:%M:%S") if t else ""

        tables: dict[str, tuple[list, list]] = {}
        tables["channel"] = (["channel_id", "code", "name"], CHANNELS)
        tables["province"] = (["province_id", "name", "code"], PROVINCES)
        tables["product_category"] = (["category_id", "name", "parent_id"], CATEGORIES)
        tables["product"] = (
            ["product_id", "sku", "name", "category_id", "list_price", "status", "created_at"],
            [(pid, sku, name, cat, money(price), "A", ts(PRODUCT_LAUNCH)) for pid, sku, name, cat, price in PRODUCTS],
        )
        tables["store"] = (["store_id", "name", "address_id"], [(sid, s[0], sid) for sid, s in STORES.items()])
        tables["customer"] = (
            ["customer_id", "email", "first_name", "last_name", "phone", "status", "created_at"],
            [(c.customer_id, c.email, c.first_name, c.last_name, c.phone, c.status, ts(c.created_at))
             for c in self.customers],
        )
        address_rows = [(a.address_id, a.line1, a.line2, a.city, a.province_id, a.postal_code, "AR", ts(a.created_at))
                        for a in list(self.store_addresses.values()) + self.addresses]
        tables["address"] = (
            ["address_id", "line1", "line2", "city", "province_id", "postal_code", "country_code", "created_at"],
            address_rows,
        )

        order_rows, item_rows, payment_rows, shipment_rows = [], [], [], []
        item_id, shipment_id = 5_000_000_000, 9_000_000_000
        for i, o in enumerate(self.orders):
            paid = visible(o.paid_at)
            if visible(o.failed_at):
                status, pay_status = "CANCELLED", "FAILED"
            elif not paid:
                status, pay_status = "CREATED", "PENDING"
            elif visible(o.cancelled_at):
                status, pay_status = "CANCELLED", "REFUNDED"
            elif visible(o.refunded_at):
                status, pay_status = "REFUNDED", "REFUNDED"
            elif not o.ships or visible(o.delivered_at):
                status, pay_status = "FULFILLED", "PAID"
            else:
                status, pay_status = "PAID", "PAID"
            order_rows.append((
                o.order_id, o.customer.customer_id, o.channel_id, o.store_id, ts(o.order_date),
                o.billing_address.address_id if o.billing_address else None,
                o.shipping_address.address_id, status, "ARS",
                money(o.subtotal), money(o.tax), money(o.shipping_fee), money(o.total),
            ))
            for pid, qty, price, discount, line_total in o.lines:
                item_rows.append((item_id, o.order_id, pid, qty, money(price), money(discount), money(line_total)))
                item_id += 1
            payment_rows.append((
                7_000_000_000 + i, o.order_id, o.method, pay_status, money(o.total),
                ts(o.paid_at) if paid else None, o.transaction_ref if paid else None,
            ))
            if o.ships and paid:  # el envío se crea al confirmarse el pago
                if visible(o.cancelled_at):
                    ship_status = "CANCELLED"
                elif visible(o.delivered_at):
                    ship_status = "DELIVERED"
                elif visible(o.shipped_at):
                    ship_status = "SHIPPED"
                else:
                    ship_status = "READY"
                shipped = visible(o.shipped_at)
                shipment_rows.append((
                    shipment_id, o.order_id, "Correo Argentino", o.tracking if shipped else None, ship_status,
                    ts(o.shipped_at) if shipped else None,
                    ts(o.delivered_at) if visible(o.delivered_at) else None,
                ))
                shipment_id += 1

        tables["sales_order"] = (
            ["order_id", "customer_id", "channel_id", "store_id", "order_date", "billing_address_id",
             "shipping_address_id", "status", "currency_code", "subtotal", "tax_amount", "shipping_fee",
             "total_amount"],
            order_rows,
        )
        tables["sales_order_item"] = (
            ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_amount", "line_total"],
            item_rows,
        )
        tables["payment"] = (
            ["payment_id", "order_id", "method", "status", "amount", "paid_at", "transaction_ref"],
            payment_rows,
        )
        tables["shipment"] = (
            ["shipment_id", "order_id", "carrier", "tracking_number", "status", "shipped_at", "delivered_at"],
            shipment_rows,
        )
        tables["web_session"] = (
            ["session_id", "customer_id", "started_at", "ended_at", "source", "device"],
            [(11_000_000_000 + i, s.customer.customer_id if s.customer else None, ts(s.started_at),
              ts(s.ended_at), s.source, s.device) for i, s in enumerate(self.sessions)],
        )
        tables["nps_response"] = (
            ["nps_id", "customer_id", "channel_id", "score", "comment", "responded_at"],
            [(13_000_000_000 + i, c.customer_id if c else None, ch, score, comment, ts(t))
             for i, (t, c, ch, score, comment) in enumerate(self.nps)],
        )

        for name, (header, rows) in tables.items():
            with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow(header)
                writer.writerows(["" if v is None else v for v in row] for row in rows)
        return {name: len(rows) for name, (_, rows) in tables.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=42, help="semilla aleatoria (default: 42)")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "raw",
                        help="carpeta de salida (default: raw/)")
    args = parser.parse_args()
    sim = Simulation(args.seed)
    sim.run()
    counts = sim.write(args.out)
    print(f"Datos generados en {args.out} (semilla {args.seed}, corte {SNAPSHOT:%Y-%m-%d %H:%M:%S})")
    for name, n in counts.items():
        print(f"  {name + '.csv':<22}{n:>8} filas")


if __name__ == "__main__":
    main()
