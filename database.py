import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "wallet.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # filas accesibles como diccionario
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_db():
    """Crea todas las tablas si no existen."""
    with get_connection() as conn:
        conn.executescript("""
            -- Sitios / bancos / billeteras
            CREATE TABLE IF NOT EXISTS sitios (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre     TEXT    NOT NULL UNIQUE,
                tipo       TEXT    NOT NULL CHECK(tipo IN ('banco','billetera','efectivo','otro')),
                notas      TEXT    DEFAULT '',
                created_at TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            );

            -- Cuentas paraguas (agrupador)
            CREATE TABLE IF NOT EXISTS cuentas (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre     TEXT    NOT NULL,
                proposito  TEXT    NOT NULL DEFAULT '',
                created_at TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            );

            -- Subcuentas (cuenta + sitio = instancia independiente)
            CREATE TABLE IF NOT EXISTS subcuentas (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                cuenta_id     INTEGER NOT NULL REFERENCES cuentas(id) ON DELETE CASCADE,
                sitio_id      INTEGER NOT NULL REFERENCES sitios(id) ON DELETE CASCADE,
                tipo          TEXT    NOT NULL CHECK(tipo IN ('debito','credito','ahorros','efectivo','otro')),
                color         TEXT    NOT NULL DEFAULT '#888780',
                saldo_inicial REAL    NOT NULL DEFAULT 0.0,
                activa        INTEGER NOT NULL DEFAULT 1,
                created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
                UNIQUE(cuenta_id, sitio_id)
            );

            -- Categorías de movimientos
            CREATE TABLE IF NOT EXISTS categorias (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre  TEXT NOT NULL UNIQUE,
                tipo    TEXT NOT NULL CHECK(tipo IN ('ingreso','gasto','ambos'))
            );

            -- Movimientos (apuntan a subcuenta)
            CREATE TABLE IF NOT EXISTS movimientos (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                subcuenta_id INTEGER NOT NULL REFERENCES subcuentas(id) ON DELETE CASCADE,
                tipo         TEXT    NOT NULL CHECK(tipo IN ('ingreso','gasto')),
                monto        REAL    NOT NULL CHECK(monto > 0),
                descripcion  TEXT    NOT NULL,
                categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
                fecha        TEXT    NOT NULL,
                referencia   TEXT    DEFAULT '',
                notas        TEXT    DEFAULT '',
                created_at   TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            );

            -- Índices
            CREATE INDEX IF NOT EXISTS idx_mov_subcuenta ON movimientos(subcuenta_id);
            CREATE INDEX IF NOT EXISTS idx_mov_fecha     ON movimientos(fecha);
            CREATE INDEX IF NOT EXISTS idx_mov_tipo      ON movimientos(tipo);
            CREATE INDEX IF NOT EXISTS idx_sub_cuenta    ON subcuentas(cuenta_id);
            CREATE INDEX IF NOT EXISTS idx_sub_sitio     ON subcuentas(sitio_id);
        """)
        _insertar_datos_iniciales(conn)

def _insertar_datos_iniciales(conn):
    """Inserta datos iniciales si la DB está vacía."""
    if conn.execute("SELECT COUNT(*) FROM sitios").fetchone()[0] > 0:
        return

    # Sitios
    conn.executemany(
        "INSERT INTO sitios (nombre, tipo, notas) VALUES (?,?,?)",
        [
            ("Nu",        "billetera", "Billetera digital"),
            ("Físico",    "efectivo",  "Dinero en efectivo"),
            ("Santander", "banco",     "Banco Santander"),
        ]
    )

    # Cuentas paraguas
    conn.executemany(
        "INSERT INTO cuentas (nombre, proposito) VALUES (?,?)",
        [
            ("Negocio",   "Ingresos y gastos del negocio"),
            ("Personal",  "Gastos personales"),
            ("Ahorros",   "Fondo de reserva"),
        ]
    )

    # Subcuentas (cuenta_id, sitio_id, tipo, color, saldo_inicial)
    conn.executemany(
        "INSERT INTO subcuentas (cuenta_id, sitio_id, tipo, color, saldo_inicial) VALUES (?,?,?,?,?)",
        [
            (1, 1, "debito",   "#378ADD", 0.0),  # Negocio en Nu
            (1, 2, "efectivo", "#378ADD", 0.0),  # Negocio en Físico
            (1, 3, "debito",   "#378ADD", 0.0),  # Negocio en Santander
            (2, 1, "debito",   "#1D9E75", 0.0),  # Personal en Nu
            (3, 1, "ahorros",  "#BA7517", 0.0),  # Ahorros en Nu
            (3, 2, "ahorros",  "#BA7517", 0.0),  # Ahorros en Físico
        ]
    )

    # Categorías
    conn.executemany(
        "INSERT INTO categorias (nombre, tipo) VALUES (?,?)",
        [
            ("Venta",                "ingreso"),
            ("Transferencia recibida","ingreso"),
            ("Devolución",           "ingreso"),
            ("Otro ingreso",         "ingreso"),
            ("Compras",              "gasto"),
            ("Servicios",            "gasto"),
            ("Alimentación",         "gasto"),
            ("Transporte",           "gasto"),
            ("Proveedor",            "gasto"),
            ("Renta",                "gasto"),
            ("Suscripción",          "gasto"),
            ("Otro gasto",           "gasto"),
        ]
    )

# ─────────────────────────────────────────────
# SITIOS
# ─────────────────────────────────────────────

def obtener_sitios():
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM sitios ORDER BY nombre"
        ).fetchall()]

def agregar_sitio(nombre, tipo, notas=""):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO sitios (nombre, tipo, notas) VALUES (?,?,?)",
            (nombre, tipo, notas)
        )
        return cur.lastrowid

def editar_sitio(sitio_id, nombre, tipo, notas):
    with get_connection() as conn:
        conn.execute(
            "UPDATE sitios SET nombre=?, tipo=?, notas=? WHERE id=?",
            (nombre, tipo, notas, sitio_id)
        )

def eliminar_sitio(sitio_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM sitios WHERE id=?", (sitio_id,))


# ─────────────────────────────────────────────
# CUENTAS
# ─────────────────────────────────────────────

def obtener_cuentas():
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM cuentas ORDER BY nombre"
        ).fetchall()]

def agregar_cuenta(nombre, proposito=""):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO cuentas (nombre, proposito) VALUES (?,?)",
            (nombre, proposito)
        )
        return cur.lastrowid

def editar_cuenta(cuenta_id, nombre, proposito):
    with get_connection() as conn:
        conn.execute(
            "UPDATE cuentas SET nombre=?, proposito=? WHERE id=?",
            (nombre, proposito, cuenta_id)
        )

def eliminar_cuenta(cuenta_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM cuentas WHERE id=?", (cuenta_id,))


# ─────────────────────────────────────────────
# SUBCUENTAS
# ─────────────────────────────────────────────

def obtener_subcuentas(cuenta_id=None, sitio_id=None, solo_activas=True):
    query = """
        SELECT sc.*, c.nombre AS cuenta_nombre, c.proposito,
               s.nombre AS sitio_nombre, s.tipo AS sitio_tipo
        FROM subcuentas sc
        JOIN cuentas c ON c.id = sc.cuenta_id
        JOIN sitios s  ON s.id = sc.sitio_id
        WHERE 1=1
    """
    params = []
    if solo_activas:
        query += " AND sc.activa = 1"
    if cuenta_id:
        query += " AND sc.cuenta_id = ?"
        params.append(cuenta_id)
    if sitio_id:
        query += " AND sc.sitio_id = ?"
        params.append(sitio_id)
    query += " ORDER BY c.nombre, s.nombre"

    with get_connection() as conn:
        return [dict(r) for r in conn.execute(query, params).fetchall()]

def agregar_subcuenta(cuenta_id, sitio_id, tipo, color, saldo_inicial=0.0):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO subcuentas
               (cuenta_id, sitio_id, tipo, color, saldo_inicial)
               VALUES (?,?,?,?,?)""",
            (cuenta_id, sitio_id, tipo, color, saldo_inicial)
        )
        return cur.lastrowid

def editar_subcuenta(subcuenta_id, tipo, color):
    with get_connection() as conn:
        conn.execute(
            "UPDATE subcuentas SET tipo=?, color=? WHERE id=?",
            (tipo, color, subcuenta_id)
        )

def archivar_subcuenta(subcuenta_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE subcuentas SET activa=0 WHERE id=?", (subcuenta_id,))

def reactivar_subcuenta(subcuenta_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE subcuentas SET activa=1 WHERE id=?", (subcuenta_id,))


# ─────────────────────────────────────────────
# MOVIMIENTOS
# ─────────────────────────────────────────────

def agregar_movimiento(subcuenta_id, tipo, monto, descripcion,
                       fecha, categoria_id=None, referencia="", notas=""):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO movimientos
               (subcuenta_id, tipo, monto, descripcion,
                categoria_id, fecha, referencia, notas)
               VALUES (?,?,?,?,?,?,?,?)""",
            (subcuenta_id, tipo, monto, descripcion,
             categoria_id, fecha, referencia, notas)
        )
        return cur.lastrowid

def obtener_movimientos(subcuenta_id=None, cuenta_id=None, sitio_id=None,
                        tipo=None, fecha_desde=None, fecha_hasta=None, limite=100):
    query = """
        SELECT m.*, sc.color AS subcuenta_color,
               c.nombre AS cuenta_nombre,
               s.nombre AS sitio_nombre,
               cat.nombre AS categoria_nombre
        FROM movimientos m
        JOIN subcuentas sc ON sc.id = m.subcuenta_id
        JOIN cuentas c     ON c.id  = sc.cuenta_id
        JOIN sitios s      ON s.id  = sc.sitio_id
        LEFT JOIN categorias cat ON cat.id = m.categoria_id
        WHERE 1=1
    """
    params = []
    if subcuenta_id:
        query += " AND m.subcuenta_id = ?"
        params.append(subcuenta_id)
    if cuenta_id:
        query += " AND sc.cuenta_id = ?"
        params.append(cuenta_id)
    if sitio_id:
        query += " AND sc.sitio_id = ?"
        params.append(sitio_id)
    if tipo:
        query += " AND m.tipo = ?"
        params.append(tipo)
    if fecha_desde:
        query += " AND m.fecha >= ?"
        params.append(fecha_desde)
    if fecha_hasta:
        query += " AND m.fecha <= ?"
        params.append(fecha_hasta)
    query += " ORDER BY m.fecha DESC, m.id DESC LIMIT ?"
    params.append(limite)

    with get_connection() as conn:
        return [dict(r) for r in conn.execute(query, params).fetchall()]

def obtener_movimientos_completos():
    """Trae todos los movimientos con cuenta, sitio y categoría para exportar."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT m.fecha, m.tipo, m.monto, m.descripcion,
                   cat.nombre  AS categoria,
                   c.nombre    AS cuenta,
                   s.nombre    AS sitio,
                   sc.tipo     AS cuenta_tipo,
                   m.referencia, m.notas, m.created_at
            FROM movimientos m
            JOIN subcuentas sc  ON sc.id  = m.subcuenta_id
            JOIN cuentas c      ON c.id   = sc.cuenta_id
            JOIN sitios s       ON s.id   = sc.sitio_id
            LEFT JOIN categorias cat ON cat.id = m.categoria_id
            ORDER BY m.fecha DESC, m.id DESC
        """).fetchall()
        return [dict(r) for r in rows]

def eliminar_movimiento(mov_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM movimientos WHERE id=?", (mov_id,))


# ─────────────────────────────────────────────
# CATEGORÍAS
# ─────────────────────────────────────────────

def obtener_categorias(tipo=None):
    with get_connection() as conn:
        if tipo:
            rows = conn.execute(
                "SELECT * FROM categorias WHERE tipo=? OR tipo='ambos' ORDER BY nombre",
                (tipo,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM categorias ORDER BY nombre"
            ).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# SALDOS Y RESÚMENES
# ─────────────────────────────────────────────

def calcular_saldo_subcuenta(subcuenta_id):
    """Saldo de una subcuenta específica."""
    with get_connection() as conn:
        sc = conn.execute(
            "SELECT saldo_inicial FROM subcuentas WHERE id=?",
            (subcuenta_id,)
        ).fetchone()
        if not sc:
            return 0.0
        ingresos = conn.execute(
            "SELECT COALESCE(SUM(monto),0) FROM movimientos WHERE subcuenta_id=? AND tipo='ingreso'",
            (subcuenta_id,)
        ).fetchone()[0]
        gastos = conn.execute(
            "SELECT COALESCE(SUM(monto),0) FROM movimientos WHERE subcuenta_id=? AND tipo='gasto'",
            (subcuenta_id,)
        ).fetchone()[0]
        return sc["saldo_inicial"] + ingresos - gastos

def calcular_saldo_cuenta(cuenta_id):
    """Saldo total de todas las subcuentas de una cuenta."""
    with get_connection() as conn:
        subcuentas = conn.execute(
            "SELECT id FROM subcuentas WHERE cuenta_id=? AND activa=1",
            (cuenta_id,)
        ).fetchall()
        return sum(calcular_saldo_subcuenta(sc["id"]) for sc in subcuentas)

def resumen_mes(año, mes):
    """Ingresos y gastos del mes agrupados por cuenta."""
    fecha_desde = f"{año}-{mes:02d}-01"
    fecha_hasta = f"{año}-{mes:02d}-31"
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT c.id, c.nombre,
                   COALESCE(SUM(CASE WHEN m.tipo='ingreso' THEN m.monto ELSE 0 END),0) AS total_ingresos,
                   COALESCE(SUM(CASE WHEN m.tipo='gasto'   THEN m.monto ELSE 0 END),0) AS total_gastos
            FROM cuentas c
            LEFT JOIN subcuentas sc ON sc.cuenta_id = c.id AND sc.activa=1
            LEFT JOIN movimientos m ON m.subcuenta_id = sc.id
                AND m.fecha BETWEEN ? AND ?
            GROUP BY c.id
            ORDER BY c.nombre
        """, (fecha_desde, fecha_hasta)).fetchall()
        return [dict(r) for r in rows]

def gastos_ultimos_meses(n_meses=6):
    """Ingresos y gastos de los últimos n meses."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT strftime('%Y-%m', fecha) AS mes,
                   SUM(CASE WHEN tipo='ingreso' THEN monto ELSE 0 END) AS ingresos,
                   SUM(CASE WHEN tipo='gasto'   THEN monto ELSE 0 END) AS gastos
            FROM movimientos
            GROUP BY mes
            ORDER BY mes DESC
            LIMIT ?
        """, (n_meses,)).fetchall()
        return [dict(r) for r in reversed(rows)]

if __name__ == "__main__":
    inicializar_db()
    print("✅ Base de datos inicializada en:", DB_PATH)

    print("\nSitios:")
    for s in obtener_sitios():
        print(f"  [{s['id']}] {s['nombre']} ({s['tipo']})")

    print("\nCuentas:")
    for c in obtener_cuentas():
        print(f"  [{c['id']}] {c['nombre']} — {c['proposito']}")

    print("\nSubcuentas:")
    for sc in obtener_subcuentas():
        print(f"  [{sc['id']}] {sc['cuenta_nombre']} en {sc['sitio_nombre']} ({sc['tipo']}) — color: {sc['color']}")

    print("\nCategorías:")
    for cat in obtener_categorias():
        print(f"  {cat['tipo']:8s} | {cat['nombre']}")