from datetime import date
from formularioMovimiento import FormularioMovimiento as FormMov
import customtkinter as ctk
import database as db
from exportar import exportar_excel as exportar
from gestionSitios import GestionSitios as GesSitios
from graficas import VentanaGraficas as Graficas
from config import FUENTE, COLOR_BG, COLOR_CARD, COLOR_TEXTO, COLOR_MUTED

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLOR_TEXT = COLOR_TEXTO  # alias para compatibilidad


# ── Tarjeta de cuenta paraguas ─────────────────────────────────────────────────

class TarjetaCuenta(ctk.CTkFrame):
    def __init__(self, padre, cuenta, subcuentas, on_click_sub=None):
        super().__init__(padre, fg_color=COLOR_CARD, corner_radius=12)
        self.cuenta       = cuenta
        self.subcuentas   = subcuentas
        self.on_click_sub = on_click_sub
        self._construir()

    def _construir(self):
        # Barra de color — usa el color de la primera subcuenta
        color = self.subcuentas[0]["color"] if self.subcuentas else "#888780"
        ctk.CTkFrame(self, height=4, fg_color=color,
                     corner_radius=0).pack(fill="x")

        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.pack(fill="both", padx=14, pady=10)

        # Nombre de la cuenta paraguas
        ctk.CTkLabel(
            contenido, text=self.cuenta["nombre"],
            font=(FUENTE, 13, "bold"), text_color=COLOR_TEXTO,
            anchor="w"
        ).pack(fill="x")

        # Total de todas las subcuentas
        total = db.calcular_saldo_cuenta(self.cuenta["id"])
        color_total = "#D85A30" if total < 0 else COLOR_TEXTO
        ctk.CTkLabel(
            contenido, text=f"${total:,.2f}",
            font=(FUENTE, 18, "bold"), text_color=color_total,
            anchor="w"
        ).pack(fill="x")

        # Separador
        ctk.CTkFrame(contenido, height=1,
                     fg_color="#E0DED6").pack(fill="x", pady=(8, 6))

        # Subcuentas individuales
        for sc in self.subcuentas:
            saldo = db.calcular_saldo_subcuenta(sc["id"])
            fila  = ctk.CTkFrame(contenido, fg_color="transparent",
                                 cursor="hand2")
            fila.pack(fill="x", pady=2)
            fila.grid_columnconfigure(1, weight=1)

            ctk.CTkFrame(fila, width=8, height=8,
                         fg_color=sc["color"],
                         corner_radius=4).grid(row=0, column=0, padx=(0, 8))

            ctk.CTkLabel(fila, text=sc["sitio_nombre"],
                         font=(FUENTE, 11), text_color=COLOR_MUTED,
                         anchor="w").grid(row=0, column=1, sticky="w")

            ctk.CTkLabel(
                fila,
                text=f"${saldo:,.2f}",
                font=(FUENTE, 11, "bold"),
                text_color="#D85A30" if saldo < 0 else COLOR_TEXTO
            ).grid(row=0, column=2, padx=(8, 0))

            # Clic en la subcuenta filtra movimientos
            sc_id = sc["id"]
            fila.bind("<Button-1>",
                      lambda e, sid=sc_id: self.on_click_sub(sid)
                      if self.on_click_sub else None)


# ── Fila de movimiento ─────────────────────────────────────────────────────────

class FilaMovimiento(ctk.CTkFrame):
    def __init__(self, padre, mov, on_eliminar=None):
        super().__init__(padre, fg_color="transparent")
        self.on_eliminar = on_eliminar
        self._construir(mov)

    def _construir(self, mov):
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(
            self, width=10, height=10,
            fg_color=mov["subcuenta_color"], corner_radius=5
        ).grid(row=0, column=0, rowspan=2, padx=(6, 10), pady=6)

        ctk.CTkLabel(
            self, text=mov["descripcion"],
            font=(FUENTE, 13), text_color=COLOR_TEXTO, anchor="w"
        ).grid(row=0, column=1, sticky="w")

        detalle = f"{mov['cuenta_nombre']} · {mov['sitio_nombre']}"
        if mov.get("categoria_nombre"):
            detalle += f" · {mov['categoria_nombre']}"
        detalle += f" · {mov['fecha']}"

        ctk.CTkLabel(
            self, text=detalle,
            font=(FUENTE, 11), text_color=COLOR_MUTED, anchor="w"
        ).grid(row=1, column=1, sticky="w")

        signo = "+" if mov["tipo"] == "ingreso" else "−"
        color = "#1D9E75" if mov["tipo"] == "ingreso" else "#D85A30"
        ctk.CTkLabel(
            self, text=f"{signo}${mov['monto']:,.2f}",
            font=(FUENTE, 13, "bold"), text_color=color
        ).grid(row=0, column=2, rowspan=2, padx=12)

        ctk.CTkButton(
            self, text="Eliminar", font=(FUENTE, 11), height=28,
            fg_color="transparent", border_width=1, border_color="#E0DED6",
            text_color="#D85A30", hover_color="#FDECEA",
            command=lambda: self.on_eliminar(mov["id"]) if self.on_eliminar else None
        ).grid(row=0, column=3, rowspan=2, padx=12)

        ctk.CTkFrame(self, height=1, fg_color="#E0DED6").grid(
            row=2, column=0, columnspan=4, sticky="ew", padx=4)


# ── Ventana principal ──────────────────────────────────────────────────────────

class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mis Cuentas")
        self.geometry("960x700")
        self.configure(fg_color=COLOR_BG)
        self.subcuentaActivaId = None
        self.sitioActivoId     = None
        self.listaMov          = None
        self.fechaDesde        = None
        self.fechaHasta        = None
        self.modoOscuro        = False
        self.construirUI()

    def construirUI(self):

        # ── Barra superior ──────────────────────────
        barra = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=0)
        barra.pack(fill="x")

        ctk.CTkLabel(
            barra, text="Mis Cuentas",
            font=(FUENTE, 20, "bold"), text_color=COLOR_TEXTO
        ).pack(side="left", padx=20, pady=14)

        ctk.CTkButton(
            barra, text="+ Nuevo Movimiento",
            font=(FUENTE, 13), height=34,
            command=self._abrirFormulario
        ).pack(side="right", padx=(0, 16), pady=10)

        ctk.CTkButton(
            barra, text="Sitios", font=(FUENTE, 13), height=34,
            fg_color="transparent", border_width=1,
            border_color="#E0DED6", text_color=COLOR_MUTED,
            hover_color="#E8E6DF", command=self._abrirSitios
        ).pack(side="right", padx=(0, 8), pady=10)

        ctk.CTkButton(
            barra, text="Exportar", font=(FUENTE, 13), height=34,
            fg_color="transparent", border_width=1,
            border_color="#E0DED6", text_color=COLOR_MUTED,
            hover_color="#E8E6DF", command=self._exportar
        ).pack(side="right", padx=(0, 8), pady=10)

        ctk.CTkButton(
            barra, text="Gráficas", font=(FUENTE, 13), height=34,
            fg_color="transparent", border_width=1,
            border_color="#E0DED6", text_color=COLOR_MUTED,
            hover_color="#E8E6DF", command=self._abrirGraficas
        ).pack(side="right", padx=(0, 8), pady=10)

        ctk.CTkButton(
            barra, text="🌙", font=(FUENTE, 16), height=34, width=40,
            fg_color="transparent", border_width=1,
            border_color="#E0DED6", text_color=COLOR_MUTED,
            hover_color="#E8E6DF", command=self._toggleModo
        ).pack(side="right", padx=(0, 8), pady=10)

        # ── Resumen ─────────────────────────────────
        frameResumen = ctk.CTkFrame(self, fg_color="transparent")
        frameResumen.pack(fill="x", padx=16, pady=(16, 0))
        frameResumen.grid_columnconfigure((0, 1, 2), weight=1)

        hoy     = date.today()
        resumen = db.resumen_mes(hoy.year, hoy.month)
        cuentas = db.obtener_cuentas()

        totalDisponible = sum(db.calcular_saldo_cuenta(c["id"]) for c in cuentas)
        totalGastos     = sum(r["total_gastos"]   for r in resumen)
        totalIngresos   = sum(r["total_ingresos"] for r in resumen)

        for i, (etiqueta, valor, color) in enumerate([
            ("Total disponible",  f"${totalDisponible:,.2f}", COLOR_TEXTO),
            ("Gastos este mes",   f"${totalGastos:,.2f}",     "#D85A30"),
            ("Ingresos este mes", f"${totalIngresos:,.2f}",   "#1D9E75"),
        ]):
            card = ctk.CTkFrame(frameResumen, fg_color=COLOR_CARD,
                                corner_radius=10)
            card.grid(row=0, column=i, sticky="ew",
                      padx=(0 if i == 0 else 6, 0))
            ctk.CTkLabel(card, text=etiqueta, font=(FUENTE, 11),
                         text_color=COLOR_MUTED, anchor="w"
                         ).pack(fill="x", padx=14, pady=(10, 0))
            ctk.CTkLabel(card, text=valor, font=(FUENTE, 22, "bold"),
                         text_color=color, anchor="w"
                         ).pack(fill="x", padx=14, pady=(0, 10))

        # ── Tabs de sitios ──────────────────────────
        frameSitios = ctk.CTkFrame(self, fg_color="transparent")
        frameSitios.pack(fill="x", padx=16, pady=(12, 6))

        sitios = db.obtener_sitios()

        ctk.CTkButton(
            frameSitios, text="Todos", font=(FUENTE, 12),
            height=30, width=70,
            fg_color="#378ADD" if self.sitioActivoId is None else "transparent",
            text_color="white" if self.sitioActivoId is None else COLOR_MUTED,
            border_width=1, border_color="#E0DED6",
            command=lambda: self._seleccionarSitio(None)
        ).pack(side="left", padx=(0, 6))

        for sitio in sitios:
            activo = self.sitioActivoId == sitio["id"]
            ctk.CTkButton(
                frameSitios, text=sitio["nombre"], font=(FUENTE, 12),
                height=30,
                fg_color="#378ADD" if activo else "transparent",
                text_color="white" if activo else COLOR_MUTED,
                border_width=1, border_color="#E0DED6",
                command=lambda s=sitio: self._seleccionarSitio(s["id"])
            ).pack(side="left", padx=(0, 6))

        # ── Tarjetas de cuentas ─────────────────────
        frameCuentas = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=200)
        frameCuentas.pack(fill="x", padx=16, pady=(0, 8))

        for i, cuenta in enumerate(cuentas):
            subcuentas = db.obtener_subcuentas(
                cuenta_id=cuenta["id"],
                sitio_id=self.sitioActivoId)
            if not subcuentas:
                continue
            tarjeta = TarjetaCuenta(
                frameCuentas, cuenta, subcuentas,
                on_click_sub=self._filtrarPorSubcuenta)
            tarjeta.grid(row=0, column=i, sticky="nsew",
                         padx=(0 if i == 0 else 8, 0))
            frameCuentas.grid_columnconfigure(i, weight=1)

        # ── Filtro por fechas ───────────────────────
        frameFiltro = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=10)
        frameFiltro.pack(fill="x", padx=16, pady=(0, 8))
        frameFiltro.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(frameFiltro, text="Desde:", font=(FUENTE, 12),
                     text_color=COLOR_MUTED
                     ).grid(row=0, column=0, padx=(14, 6), pady=10)
        self.entryDesde = ctk.CTkEntry(
            frameFiltro, font=(FUENTE, 12), height=32,
            placeholder_text="YYYY-MM-DD")
        self.entryDesde.grid(row=0, column=1, sticky="ew", pady=10)

        ctk.CTkLabel(frameFiltro, text="Hasta:", font=(FUENTE, 12),
                     text_color=COLOR_MUTED
                     ).grid(row=0, column=2, padx=(14, 6), pady=10)
        self.entryHasta = ctk.CTkEntry(
            frameFiltro, font=(FUENTE, 12), height=32,
            placeholder_text="YYYY-MM-DD")
        self.entryHasta.grid(row=0, column=3, sticky="ew", pady=10)

        ctk.CTkButton(
            frameFiltro, text="Filtrar", font=(FUENTE, 12),
            height=32, width=80, command=self._aplicarFiltro
        ).grid(row=0, column=4, padx=(10, 6), pady=10)

        ctk.CTkButton(
            frameFiltro, text="Limpiar", font=(FUENTE, 12),
            height=32, width=80, fg_color="transparent",
            border_width=1, border_color="#E0DED6",
            text_color=COLOR_MUTED, hover_color="#E8E6DF",
            command=self._limpiarFiltro
        ).grid(row=0, column=5, padx=(0, 14), pady=10)

        # ── Movimientos ─────────────────────────────
        panel_movs = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=12)
        panel_movs.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        ctk.CTkLabel(
            panel_movs, text="Movimientos recientes",
            font=(FUENTE, 14, "bold"), text_color=COLOR_TEXTO, anchor="w"
        ).pack(fill="x", padx=16, pady=(12, 8))

        self.listaMov = ctk.CTkScrollableFrame(
            panel_movs, fg_color="transparent")
        self.listaMov.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        self._refrescarLista()

    # ── Métodos ────────────────────────────────────

    def _seleccionarSitio(self, sitio_id):
        self.sitioActivoId     = sitio_id
        self.subcuentaActivaId = None
        self._refrescar()

    def _filtrarPorSubcuenta(self, subcuenta_id):
        if self.subcuentaActivaId == subcuenta_id:
            self.subcuentaActivaId = None
        else:
            self.subcuentaActivaId = subcuenta_id
        self._refrescarLista()

    def _aplicarFiltro(self):
        self.fechaDesde = self.entryDesde.get().strip() or None
        self.fechaHasta = self.entryHasta.get().strip() or None
        self._refrescarLista()

    def _limpiarFiltro(self):
        self.fechaDesde = None
        self.fechaHasta = None
        self.entryDesde.delete(0, "end")
        self.entryHasta.delete(0, "end")
        self._refrescarLista()

    def _refrescarLista(self):
        for widget in self.listaMov.winfo_children():
            widget.destroy()

        movimientos = db.obtener_movimientos(
            subcuenta_id=self.subcuentaActivaId,
            sitio_id=self.sitioActivoId,
            fecha_desde=self.fechaDesde,
            fecha_hasta=self.fechaHasta,
            limite=50
        )

        if not movimientos:
            ctk.CTkLabel(
                self.listaMov,
                text="Sin movimientos registrados",
                font=(FUENTE, 13), text_color=COLOR_MUTED
            ).pack(pady=40)
        else:
            for mov in movimientos:
                FilaMovimiento(
                    self.listaMov, mov,
                    on_eliminar=self._eliminarMovimiento
                ).pack(fill="x")

    def _eliminarMovimiento(self, mov_id):
        db.eliminar_movimiento(mov_id)
        self._refrescar()

    def _refrescar(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.construirUI()

    def _toggleModo(self):
        if self.modoOscuro:
            ctk.set_appearance_mode("light")
            self.modoOscuro = False
        else:
            ctk.set_appearance_mode("dark")
            self.modoOscuro = True
        self._refrescar()

    def _abrirFormulario(self):
        formulario = FormMov(self)
        formulario.grab_set()
        self.wait_window(formulario)
        self._refrescar()

    def _abrirSitios(self):
        ventana = GesSitios(self)
        ventana.grab_set()
        self.wait_window(ventana)

    def _exportar(self):
        import os
        ruta = exportar()
        os.startfile(ruta)

    def _abrirGraficas(self):
        ventana = Graficas(self)
        ventana.grab_set()


# ── Arrancar ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    db.inicializar_db()
    app = VentanaPrincipal()
    app.mainloop()