import customtkinter as ctk
import database as db
from config import FUENTE, COLOR_BG, COLOR_CARD, COLOR_TEXTO, COLOR_MUTED


# ── Formulario de cuenta paraguas ─────────────────────────────────────────────

class FormularioCuenta(ctk.CTkToplevel):
    def __init__(self, padre, cuenta=None, on_guardado=None):
        super().__init__(padre)
        self.cuenta      = cuenta
        self.on_guardado = on_guardado
        self.title("Nueva cuenta" if not cuenta else "Editar cuenta")
        self.geometry("400x280")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self.grab_set()
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Nombre *", font=(FUENTE, 11),
                     text_color=COLOR_MUTED, anchor="w"
                     ).pack(fill="x", pady=(0, 4))
        self.entryNombre = ctk.CTkEntry(
            scroll, font=(FUENTE, 13), height=36,
            placeholder_text="Ej: Negocio, Ahorros, Personal...")
        self.entryNombre.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(scroll, text="Propósito", font=(FUENTE, 11),
                     text_color=COLOR_MUTED, anchor="w"
                     ).pack(fill="x", pady=(0, 4))
        self.entryProposito = ctk.CTkEntry(
            scroll, font=(FUENTE, 13), height=36,
            placeholder_text="Ej: Ingresos del negocio...")
        self.entryProposito.pack(fill="x", pady=(0, 16))

        frameBotones = ctk.CTkFrame(scroll, fg_color="transparent")
        frameBotones.pack(fill="x")
        frameBotones.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            frameBotones, text="Cancelar", font=(FUENTE, 13),
            height=36, width=100, fg_color="transparent",
            border_width=1, border_color="#E0DED6",
            text_color=COLOR_MUTED, hover_color="#E8E6DF",
            command=self.destroy
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            frameBotones, text="Guardar", font=(FUENTE, 13, "bold"),
            height=36, command=self._guardar
        ).grid(row=0, column=1, sticky="ew")

        self.lblError = ctk.CTkLabel(
            scroll, text="", font=(FUENTE, 12),
            text_color="#D85A30", anchor="w")
        self.lblError.pack(fill="x", pady=(8, 0))

        if self.cuenta:
            self.entryNombre.insert(0, self.cuenta["nombre"])
            if self.cuenta.get("proposito"):
                self.entryProposito.insert(0, self.cuenta["proposito"])

    def _guardar(self):
        nombre = self.entryNombre.get().strip()
        if not nombre:
            self.lblError.configure(text="⚠ El nombre es obligatorio")
            return
        proposito = self.entryProposito.get().strip()
        if self.cuenta:
            db.editar_cuenta(self.cuenta["id"], nombre, proposito)
        else:
            db.agregar_cuenta(nombre, proposito)
        if self.on_guardado:
            self.on_guardado()
        self.destroy()


# ── Formulario de subcuenta ───────────────────────────────────────────────────

class FormularioSubcuenta(ctk.CTkToplevel):
    def __init__(self, padre, cuenta_id, on_guardado=None):
        super().__init__(padre)
        self.cuenta_id   = cuenta_id
        self.on_guardado = on_guardado
        self.title("Agregar sitio a cuenta")
        self.geometry("400x320")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self.grab_set()
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Sitio
        ctk.CTkLabel(scroll, text="Sitio *", font=(FUENTE, 11),
                     text_color=COLOR_MUTED, anchor="w"
                     ).pack(fill="x", pady=(0, 4))
        sitios = db.obtener_sitios()
        self.sitiosMap = {s["nombre"]: s["id"] for s in sitios}
        self.comboSitio = ctk.CTkComboBox(
            scroll, values=list(self.sitiosMap.keys()),
            font=(FUENTE, 13), height=36, state="readonly")
        if sitios:
            self.comboSitio.set(sitios[0]["nombre"])
        self.comboSitio.pack(fill="x", pady=(0, 12))

        # Tipo
        ctk.CTkLabel(scroll, text="Tipo *", font=(FUENTE, 11),
                     text_color=COLOR_MUTED, anchor="w"
                     ).pack(fill="x", pady=(0, 4))
        self.comboTipo = ctk.CTkComboBox(
            scroll, font=(FUENTE, 13), height=36,
            values=["debito", "credito", "ahorros", "efectivo", "otro"],
            state="readonly")
        self.comboTipo.set("debito")
        self.comboTipo.pack(fill="x", pady=(0, 12))

        # Color
        ctk.CTkLabel(scroll, text="Color", font=(FUENTE, 11),
                     text_color=COLOR_MUTED, anchor="w"
                     ).pack(fill="x", pady=(0, 4))
        self.colores = {
            "Azul"   : "#378ADD",
            "Verde"  : "#1D9E75",
            "Naranja": "#BA7517",
            "Rojo"   : "#D85A30",
            "Morado" : "#7F77DD",
            "Gris"   : "#888780",
        }
        self.comboColor = ctk.CTkComboBox(
            scroll, values=list(self.colores.keys()),
            font=(FUENTE, 13), height=36, state="readonly")
        self.comboColor.set("Azul")
        self.comboColor.pack(fill="x", pady=(0, 12))

        # Saldo inicial
        ctk.CTkLabel(scroll, text="Saldo inicial", font=(FUENTE, 11),
                     text_color=COLOR_MUTED, anchor="w"
                     ).pack(fill="x", pady=(0, 4))
        self.entrySaldo = ctk.CTkEntry(
            scroll, font=(FUENTE, 13), height=36,
            placeholder_text="0.00")
        self.entrySaldo.pack(fill="x", pady=(0, 16))

        frameBotones = ctk.CTkFrame(scroll, fg_color="transparent")
        frameBotones.pack(fill="x")
        frameBotones.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            frameBotones, text="Cancelar", font=(FUENTE, 13),
            height=36, width=100, fg_color="transparent",
            border_width=1, border_color="#E0DED6",
            text_color=COLOR_MUTED, hover_color="#E8E6DF",
            command=self.destroy
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            frameBotones, text="Agregar", font=(FUENTE, 13, "bold"),
            height=36, command=self._guardar
        ).grid(row=0, column=1, sticky="ew")

        self.lblError = ctk.CTkLabel(
            scroll, text="", font=(FUENTE, 12),
            text_color="#D85A30", anchor="w")
        self.lblError.pack(fill="x", pady=(8, 0))

    def _guardar(self):
        sitioNombre = self.comboSitio.get()
        sitioId     = self.sitiosMap.get(sitioNombre)
        if not sitioId:
            self.lblError.configure(text="⚠ Selecciona un sitio")
            return
        tipo  = self.comboTipo.get()
        color = self.colores[self.comboColor.get()]
        try:
            saldo = float(self.entrySaldo.get().replace(",", "."))
        except ValueError:
            saldo = 0.0
        try:
            db.agregar_subcuenta(self.cuenta_id, sitioId, tipo, color, saldo)
        except Exception:
            self.lblError.configure(
                text="⚠ Esta cuenta ya existe en ese sitio")
            return
        if self.on_guardado:
            self.on_guardado()
        self.destroy()


# ── Gestión de cuentas ────────────────────────────────────────────────────────

class GestionCuentas(ctk.CTkToplevel):
    def __init__(self, padre):
        super().__init__(padre)
        self.title("Gestión de cuentas")
        self.geometry("540x600")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self._construir()

    def _construir(self):
        ctk.CTkLabel(
            self, text="Cuentas",
            font=(FUENTE, 18, "bold"), text_color=COLOR_TEXTO, anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 12))

        ctk.CTkButton(
            self, text="+ Agregar cuenta",
            font=(FUENTE, 13), height=36,
            command=self._abrirFormularioCuenta
        ).pack(fill="x", padx=20, pady=(0, 12))

        self.frameLista = ctk.CTkScrollableFrame(
            self, fg_color="transparent")
        self.frameLista.pack(fill="both", expand=True,
                             padx=20, pady=(0, 16))

        self._refrescarLista()

    def _abrirFormularioCuenta(self, cuenta=None):
        FormularioCuenta(self, cuenta=cuenta,
                         on_guardado=self._refrescarLista)

    def _abrirFormularioSubcuenta(self, cuenta_id):
        FormularioSubcuenta(self, cuenta_id=cuenta_id,
                            on_guardado=self._refrescarLista)

    def _refrescarLista(self):
        for widget in self.frameLista.winfo_children():
            widget.destroy()

        cuentas = db.obtener_cuentas()
        tipos   = {"debito": "Débito", "credito": "Crédito",
                   "ahorros": "Ahorros", "efectivo": "Efectivo",
                   "otro": "Otro"}

        if not cuentas:
            ctk.CTkLabel(self.frameLista,
                         text="No hay cuentas registradas",
                         font=(FUENTE, 13), text_color=COLOR_MUTED
                         ).pack(pady=40)
            return

        for cuenta in cuentas:
            # Card de cuenta paraguas
            card = ctk.CTkFrame(self.frameLista, fg_color=COLOR_CARD,
                                corner_radius=10)
            card.pack(fill="x", pady=(0, 10))

            # Cabecera
            cab = ctk.CTkFrame(card, fg_color="transparent")
            cab.pack(fill="x", padx=14, pady=(10, 6))
            cab.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                cab, text=cuenta["nombre"],
                font=(FUENTE, 14, "bold"), text_color=COLOR_TEXTO,
                anchor="w"
            ).grid(row=0, column=0, sticky="w")

            if cuenta.get("proposito"):
                ctk.CTkLabel(
                    cab, text=cuenta["proposito"],
                    font=(FUENTE, 11), text_color=COLOR_MUTED, anchor="w"
                ).grid(row=1, column=0, sticky="w")

            # Botones de cuenta
            frameBtns = ctk.CTkFrame(cab, fg_color="transparent")
            frameBtns.grid(row=0, column=1, rowspan=2, sticky="e")

            ctk.CTkButton(
                frameBtns, text="Editar", font=(FUENTE, 11),
                height=26, width=60, fg_color="transparent",
                border_width=1, border_color="#E0DED6",
                text_color=COLOR_MUTED, hover_color="#E8E6DF",
                command=lambda c=cuenta: self._abrirFormularioCuenta(c)
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                frameBtns, text="Eliminar", font=(FUENTE, 11),
                height=26, width=70, fg_color="transparent",
                border_width=1, border_color="#E0DED6",
                text_color="#D85A30", hover_color="#FDECEA",
                command=lambda c=cuenta: self._eliminarCuenta(c)
            ).pack(side="left")

            # Separador
            ctk.CTkFrame(card, height=1,
                         fg_color="#E0DED6").pack(fill="x", padx=14)

            # Subcuentas
            subcuentas = db.obtener_subcuentas(
                cuenta_id=cuenta["id"], solo_activas=False)

            for sc in subcuentas:
                saldo = db.calcular_saldo_subcuenta(sc["id"])
                fila  = ctk.CTkFrame(card, fg_color="transparent")
                fila.pack(fill="x", padx=14, pady=3)
                fila.grid_columnconfigure(2, weight=1)

                # Dot de color
                ctk.CTkFrame(fila, width=8, height=8,
                             fg_color=sc["color"],
                             corner_radius=4
                             ).grid(row=0, column=0, padx=(0, 8))

                # Sitio y tipo
                ctk.CTkLabel(
                    fila,
                    text=f"{sc['sitio_nombre']} · {tipos.get(sc['tipo'], '')}",
                    font=(FUENTE, 12), text_color=COLOR_TEXTO, anchor="w"
                ).grid(row=0, column=1, sticky="w")

                # Saldo
                ctk.CTkLabel(
                    fila,
                    text=f"${saldo:,.2f}",
                    font=(FUENTE, 12, "bold"),
                    text_color="#D85A30" if saldo < 0 else COLOR_TEXTO
                ).grid(row=0, column=2, sticky="e")

                # Archivar / Reactivar
                if sc["activa"]:
                    ctk.CTkButton(
                        fila, text="Archivar", font=(FUENTE, 10),
                        height=24, width=70, fg_color="transparent",
                        border_width=1, border_color="#E0DED6",
                        text_color=COLOR_MUTED, hover_color="#E8E6DF",
                        command=lambda sid=sc["id"]: self._archivarSubcuenta(sid)
                    ).grid(row=0, column=3, padx=(8, 0))
                else:
                    ctk.CTkLabel(
                        fila, text="Archivada",
                        font=(FUENTE, 10), text_color=COLOR_MUTED
                    ).grid(row=0, column=3, padx=(8, 0))
                    ctk.CTkButton(
                        fila, text="Reactivar", font=(FUENTE, 10),
                        height=24, width=70, fg_color="transparent",
                        border_width=1, border_color="#E0DED6",
                        text_color="#1D9E75", hover_color="#E8F5F0",
                        command=lambda sid=sc["id"]: self._reactivarSubcuenta(sid)
                    ).grid(row=0, column=4, padx=(4, 0))

            # Botón agregar sitio
            ctk.CTkButton(
                card, text="+ Agregar sitio",
                font=(FUENTE, 11), height=28,
                fg_color="transparent", border_width=1,
                border_color="#E0DED6", text_color=COLOR_MUTED,
                hover_color="#E8E6DF",
                command=lambda c=cuenta: self._abrirFormularioSubcuenta(c["id"])
            ).pack(fill="x", padx=14, pady=(6, 10))

    def _eliminarCuenta(self, cuenta):
        db.eliminar_cuenta(cuenta["id"])
        self._refrescarLista()

    def _archivarSubcuenta(self, subcuenta_id):
        db.archivar_subcuenta(subcuenta_id)
        self._refrescarLista()

    def _reactivarSubcuenta(self, subcuenta_id):
        db.reactivar_subcuenta(subcuenta_id)
        self._refrescarLista()


if __name__ == "__main__":
    db.inicializar_db()
    raiz = ctk.CTk()
    raiz.withdraw()
    app = GestionCuentas(raiz)
    app.mainloop()