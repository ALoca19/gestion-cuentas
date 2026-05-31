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
                           
            -- Cuentas / tarjetas / efectivo
            CREATE TABLE IF NOT EXISTS cuentas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT    NOT NULL,
                tipo        TEXT    NOT NULL CHECK(tipo IN ('debito','credito','ahorros','efectivo','otro')),
                proposito   TEXT    NOT NULL DEFAULT '',
                color       TEXT    NOT NULL DEFAULT '#888780',
                saldo_inicial REAL  NOT NULL DEFAULT 0.0,
                activa      INTEGER NOT NULL DEFAULT 1,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
                sitio_id    INTEGER REFERENCES sitios(id) ON DELETE SET NULL
            );

            -- Categorías de movimientos
            CREATE TABLE IF NOT EXISTS categorias (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre  TEXT NOT NULL UNIQUE,
                tipo    TEXT NOT NULL CHECK(tipo IN ('ingreso','gasto','ambos'))
            );

            -- Movimientos (ingresos y gastos)
            CREATE TABLE IF NOT EXISTS movimientos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                cuenta_id   INTEGER NOT NULL REFERENCES cuentas(id) ON DELETE CASCADE,
                tipo        TEXT    NOT NULL CHECK(tipo IN ('ingreso','gasto')),
                monto       REAL    NOT NULL CHECK(monto > 0),
                descripcion TEXT    NOT NULL,
                categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
                fecha       TEXT    NOT NULL,
                referencia  TEXT    DEFAULT '',
                notas       TEXT    DEFAULT '',
                created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            );

            -- Índices para búsqueda rápida
            CREATE INDEX IF NOT EXISTS idx_mov_cuenta ON movimientos(cuenta_id);
            CREATE INDEX IF NOT EXISTS idx_mov_fecha  ON movimientos(fecha);
            CREATE INDEX IF NOT EXISTS idx_mov_tipo   ON movimientos(tipo);
        """)
        _insertar_datos_iniciales(conn)


def _insertar_datos_iniciales(conn):
    """Inserta cuentas y categorías de ejemplo si la DB está vacía."""

    # Solo si no hay cuentas todavía
    if conn.execute("SELECT COUNT(*) FROM cuentas").fetchone()[0] > 0:
        return
    
    sitios = [
    ("Nu",        "billetera", "Billetera digital"),
    ("Santander", "banco",     "Banco Santander"),
    ("Físico",    "efectivo",  "Dinero en efectivo"),
    ]
    conn.executemany(
        "INSERT INTO sitios (nombre, tipo, notas) VALUES (?,?,?)",
        sitios
    )
    

    cuentas = [
    ("Transferencias", "debito",   "Ventas y compras de negocio", "#378ADD", 0.0, 1),
    ("Personal",       "debito",   "Gastos personales",           "#1D9E75", 0.0, 1),
    ("Ahorros",        "ahorros",  "Fondo de reserva",            "#BA7517", 0.0, 1),
    ("Crédito",        "credito",  "Tarjeta de crédito",          "#D85A30", 0.0, 2),
    ("Efectivo",       "efectivo", "Dinero físico",               "#888780", 0.0, 3),
    ]
    conn.executemany(
        "INSERT INTO cuentas (nombre, tipo, proposito, color, saldo_inicial, sitio_id) VALUES (?,?,?,?,?,?)",
        cuentas,
    )

    categorias = [
        ("Venta",               "ingreso"),
        ("Transferencia recibida", "ingreso"),
        ("Devolución",          "ingreso"),
        ("Otro ingreso",        "ingreso"),
        ("Compras",             "gasto"),
        ("Servicios",           "gasto"),
        ("Alimentación",        "gasto"),
        ("Transporte",          "gasto"),
        ("Proveedor",           "gasto"),
        ("Renta",               "gasto"),
        ("Suscripción",         "gasto"),
        ("Otro gasto",          "gasto"),
    ]
    conn.executemany(
        "INSERT INTO categorias (nombre, tipo) VALUES (?,?)",
        categorias,
    )


# ─────────────────────────────────────────────
# CUENTAS
# ─────────────────────────────────────────────

def obtener_cuentas(solo_activas=True):
    with get_connection() as conn:
        query = "SELECT * FROM cuentas"
        if solo_activas:
            query += " WHERE activa = 1"
        query += " ORDER BY nombre"
        return [dict(r) for r in conn.execute(query).fetchall()]


def obtener_cuenta(cuenta_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM cuentas WHERE id = ?", (cuenta_id,)).fetchone()
        return dict(row) if row else None


def agregar_cuenta(nombre, tipo, proposito, color, saldo_inicial=0.0, sitio_id=None):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO cuentas (nombre, tipo, proposito, color, saldo_inicial, sitio_id) VALUES (?,?,?,?,?,?)",
            (nombre, tipo, proposito, color, saldo_inicial, sitio_id),
        )
        return cur.lastrowid


def editar_cuenta(cuenta_id, nombre, tipo, proposito, color, sitio_id=None):
    with get_connection() as conn:
        conn.execute(
            "UPDATE cuentas SET nombre=?, tipo=?, proposito=?, color=?, sitio_id=? WHERE id=?",
            (nombre, tipo, proposito, color, sitio_id, cuenta_id),
        )


def archivar_cuenta(cuenta_id):
    with get_connection() as conn:
        conn.execute("UPDATE cuentas SET activa = 0 WHERE id = ?", (cuenta_id,))

def reactivar_cuenta(cuenta_id):
    with get_connection() as conn:
        conn.execute("UPDATE cuentas SET activa = 1 WHERE id = ?", (cuenta_id,))

# ─────────────────────────────────────────────
# MOVIMIENTOS
# ─────────────────────────────────────────────

def agregar_movimiento(cuenta_id, tipo, monto, descripcion,
                       fecha, categoria_id=None, referencia="", notas=""):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO movimientos
               (cuenta_id, tipo, monto, descripcion, categoria_id, fecha, referencia, notas)
               VALUES (?,?,?,?,?,?,?,?)""",
            (cuenta_id, tipo, monto, descripcion, categoria_id, fecha, referencia, notas),
        )
        return cur.lastrowid


def obtener_movimientos(cuenta_id=None, tipo=None, fecha_desde=None,
                        fecha_hasta=None, limite=100):
    query = """
        SELECT m.*, c.nombre AS cuenta_nombre, c.color AS cuenta_color,
               cat.nombre AS categoria_nombre
        FROM movimientos m
        JOIN cuentas c ON c.id = m.cuenta_id
        LEFT JOIN categorias cat ON cat.id = m.categoria_id
        WHERE 1=1
    """
    params = []
    if cuenta_id:
        query += " AND m.cuenta_id = ?"
        params.append(cuenta_id)
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


def eliminar_movimiento(mov_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM movimientos WHERE id = ?", (mov_id,))


# ─────────────────────────────────────────────
# CATEGORÍAS
# ─────────────────────────────────────────────

def obtener_categorias(tipo=None):
    with get_connection() as conn:
        if tipo:
            rows = conn.execute(
                "SELECT * FROM categorias WHERE tipo = ? OR tipo = 'ambos' ORDER BY nombre",
                (tipo,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM categorias ORDER BY nombre").fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# RESUMEN / SALDOS
# ─────────────────────────────────────────────

def calcular_saldo(cuenta_id):
    """Saldo = saldo_inicial + ingresos - gastos."""
    with get_connection() as conn:
        cuenta = conn.execute(
            "SELECT saldo_inicial FROM cuentas WHERE id = ?", (cuenta_id,)
        ).fetchone()
        if not cuenta:
            return 0.0

        ingresos = conn.execute(
            "SELECT COALESCE(SUM(monto),0) FROM movimientos WHERE cuenta_id=? AND tipo='ingreso'",
            (cuenta_id,),
        ).fetchone()[0]

        gastos = conn.execute(
            "SELECT COALESCE(SUM(monto),0) FROM movimientos WHERE cuenta_id=? AND tipo='gasto'",
            (cuenta_id,),
        ).fetchone()[0]

        return cuenta["saldo_inicial"] + ingresos - gastos


def resumen_mes(año, mes):
    """Ingresos y gastos totales del mes, agrupados por cuenta."""
    fecha_desde = f"{año}-{mes:02d}-01"
    fecha_hasta = f"{año}-{mes:02d}-31"
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.nombre, c.color,
                   COALESCE(SUM(CASE WHEN m.tipo='ingreso' THEN m.monto ELSE 0 END),0) AS total_ingresos,
                   COALESCE(SUM(CASE WHEN m.tipo='gasto'   THEN m.monto ELSE 0 END),0) AS total_gastos
            FROM cuentas c
            LEFT JOIN movimientos m ON m.cuenta_id = c.id
                AND m.fecha BETWEEN ? AND ?
            WHERE c.activa = 1
            GROUP BY c.id
            ORDER BY c.nombre
            """,
            (fecha_desde, fecha_hasta),
        ).fetchall()
        return [dict(r) for r in rows]
    
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

def gastos_ultimos_meses(n_meses=6):
    """Devuelve ingresos y gastos de los últimos n meses."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                strftime('%Y-%m', fecha) AS mes,
                SUM(CASE WHEN tipo='ingreso' THEN monto ELSE 0 END) AS ingresos,
                SUM(CASE WHEN tipo='gasto'   THEN monto ELSE 0 END) AS gastos
            FROM movimientos
            GROUP BY mes
            ORDER BY mes DESC
            LIMIT ?
        """, (n_meses,)).fetchall()
        return [dict(r) for r in reversed(rows)]
    
#------------------------------------
# Obtencion de movimientos
#------------------------------------
def obtener_movimientos_completos():
    """Trae todos los movimientos con cuenta, sitio y categoría para exportar."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                m.fecha,
                m.tipo,
                m.monto,
                m.descripcion,
                cat.nombre   AS categoria,
                c.nombre     AS cuenta,
                c.tipo       AS cuenta_tipo,
                s.nombre     AS sitio,
                m.referencia,
                m.notas,
                m.created_at
            FROM movimientos m
            JOIN cuentas c ON c.id = m.cuenta_id
            LEFT JOIN categorias cat ON cat.id = m.categoria_id
            LEFT JOIN sitios s ON s.id = c.sitio_id
            ORDER BY m.fecha DESC, m.id DESC
        """).fetchall()
        return [dict(r) for r in rows]

if __name__ == "__main__":
    inicializar_db()
    print("✅ Base de datos inicializada en:", DB_PATH)
    print("\nCuentas creadas:")
    for c in obtener_cuentas():
        print(f"  [{c['id']}] {c['nombre']} ({c['tipo']}) — color: {c['color']}")
    print("\nCategorías:")
    for cat in obtener_categorias():
        print(f"  {cat['tipo']:8s} | {cat['nombre']}")
    print("\nSitios:")