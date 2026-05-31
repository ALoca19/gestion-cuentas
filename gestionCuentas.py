import customtkinter as ctk
import database as db
from config import FUENTE, COLOR_BG, COLOR_CARD, COLOR_TEXTO, COLOR_MUTED



class FormularioCuenta(ctk.CTkToplevel):
    def __init__(self, padre, cuenta=None, on_guardado=None):
        super().__init__(padre)
        self.cuenta      = cuenta       # None = nueva, dict = editar
        self.on_guardado = on_guardado
        self.title("Nueva cuenta" if not cuenta else "Editar cuenta")
        self.geometry("420x520")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self.grab_set()
        self._construir()

    def _construir(self):
        ctk.CTkLabel(
            self,
            text="Nueva cuenta" if not self.cuenta else "Editar cuenta",
            font=(FUENTE, 18, "bold"),
            text_color=COLOR_TEXTO,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 16))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Nombre
        ctk.CTkLabel(scroll, text="Nombre *",
                     font=(FUENTE, 11), text_color=COLOR_MUTED,
                     anchor="w").pack(fill="x", pady=(0, 4))
        self.entryNombre = ctk.CTkEntry(
            scroll, font=(FUENTE, 13), height=36,
            placeholder_text="Ej: Transferencias, Ahorros...")
        self.entryNombre.pack(fill="x", pady=(0, 12))

        # Tipo
        ctk.CTkLabel(scroll, text="Tipo *",
                     font=(FUENTE, 11), text_color=COLOR_MUTED,
                     anchor="w").pack(fill="x", pady=(0, 4))
        self.comboTipo = ctk.CTkComboBox(
            scroll, font=(FUENTE, 13), height=36,
            values=["debito", "credito", "ahorros", "efectivo", "otro"],
            state="readonly")
        self.comboTipo.set("debito")
        self.comboTipo.pack(fill="x", pady=(0, 12))

        # Propósito
        ctk.CTkLabel(scroll, text="Propósito",
                     font=(FUENTE, 11), text_color=COLOR_MUTED,
                     anchor="w").pack(fill="x", pady=(0, 4))
        self.entryProposito = ctk.CTkEntry(
            scroll, font=(FUENTE, 13), height=36,
            placeholder_text="Ej: Gastos personales, Ventas...")
        self.entryProposito.pack(fill="x", pady=(0, 12))

        # Sitio
        ctk.CTkLabel(scroll, text="Sitio / Banco",
                     font=(FUENTE, 11), text_color=COLOR_MUTED,
                     anchor="w").pack(fill="x", pady=(0, 4))
        sitios = db.obtener_sitios()
        self.sitiosMap = {s["nombre"]: s["id"] for s in sitios}
        self.sitiosMap["Sin sitio"] = None
        opciones = ["Sin sitio"] + [s["nombre"] for s in sitios]
        self.comboSitio = ctk.CTkComboBox(
            scroll, font=(FUENTE, 13), height=36,
            values=opciones, state="readonly")
        self.comboSitio.set("Sin sitio")
        self.comboSitio.pack(fill="x", pady=(0, 12))

        # Color
        ctk.CTkLabel(scroll, text="Color",
                     font=(FUENTE, 11), text_color=COLOR_MUTED,
                     anchor="w").pack(fill="x", pady=(0, 4))
        self.colores = {
            "Azul"    : "#378ADD",
            "Verde"   : "#1D9E75",
            "Naranja" : "#BA7517",
            "Rojo"    : "#D85A30",
            "Morado"  : "#7F77DD",
            "Gris"    : "#888780",
        }
        self.comboColor = ctk.CTkComboBox(
            scroll, font=(FUENTE, 13), height=36,
            values=list(self.colores.keys()), state="readonly")
        self.comboColor.set("Azul")
        self.comboColor.pack(fill="x", pady=(0, 12))

        # Saldo inicial (solo al crear)
        if not self.cuenta:
            ctk.CTkLabel(scroll, text="Saldo inicial",
                         font=(FUENTE, 11), text_color=COLOR_MUTED,
                         anchor="w").pack(fill="x", pady=(0, 4))
            self.entrySaldo = ctk.CTkEntry(
                scroll, font=(FUENTE, 13), height=36,
                placeholder_text="0.00")
            self.entrySaldo.pack(fill="x", pady=(0, 12))

        # Botones
        frameBotones = ctk.CTkFrame(scroll, fg_color="transparent")
        frameBotones.pack(fill="x", pady=(4, 0))
        frameBotones.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            frameBotones, text="Cancelar",
            font=(FUENTE, 13), height=36, width=100,
            fg_color="transparent", border_width=1,
            border_color="#E0DED6", text_color=COLOR_MUTED,
            hover_color="#E8E6DF", command=self.destroy
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            frameBotones, text="Guardar",
            font=(FUENTE, 13, "bold"), height=36,
            command=self._guardar
        ).grid(row=0, column=1, sticky="ew")

        self.lblError = ctk.CTkLabel(
            scroll, text="", font=(FUENTE, 12),
            text_color="#D85A30", anchor="w")
        self.lblError.pack(fill="x", pady=(8, 0))

        # Si es edición, llenar campos
        if self.cuenta:
            self.entryNombre.insert(0, self.cuenta["nombre"])
            self.comboTipo.set(self.cuenta["tipo"])
            if self.cuenta.get("proposito"):
                self.entryProposito.insert(0, self.cuenta["proposito"])
            color_nombre = next(
                (k for k, v in self.colores.items() if v == self.cuenta["color"]), "Gris")
            self.comboColor.set(color_nombre)
            # Llenar sitio actual
            if self.cuenta.get("sitio_id"):
                sitio_nombre = next(
                    (k for k, v in self.sitiosMap.items() if v == self.cuenta["sitio_id"]),
                    "Sin sitio"
                )
                self.comboSitio.set(sitio_nombre)

    def _guardar(self):
        nombre = self.entryNombre.get().strip()
        if not nombre:
            self.lblError.configure(text="⚠ El nombre es obligatorio")
            return

        tipo      = self.comboTipo.get()
        proposito = self.entryProposito.get().strip()
        color     = self.colores[self.comboColor.get()]
        sitioId   = self.sitiosMap.get(self.comboSitio.get())

        if self.cuenta:
            # Editar cuenta existente
            db.editar_cuenta(
                self.cuenta["id"], nombre, tipo, proposito, color, sitioId
            )
        else:
            # Nueva cuenta
            try:
                saldo = float(self.entrySaldo.get().replace(",", "."))
            except ValueError:
                saldo = 0.0

            db.agregar_cuenta(nombre, tipo, proposito, color, saldo, sitioId)

        if self.on_guardado:
            self.on_guardado()

        self.destroy()


class GestionCuentas(ctk.CTkToplevel):
    def __init__(self, padre):
        super().__init__(padre)
        self.title("Gestión de cuentas")
        self.geometry("500x560")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self._construir()

    def _construir(self):
        ctk.CTkLabel(
            self,
            text="Cuentas",
            font=(FUENTE, 18, "bold"),
            text_color=COLOR_TEXTO,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 16))

        # Botón agregar
        ctk.CTkButton(
            self,
            text="+ Agregar cuenta",
            font=(FUENTE, 13),
            height=36,
            command=self._abrirFormulario
        ).pack(fill="x", padx=20, pady=(0, 12))

        # Lista de cuentas
        self.frameLista = ctk.CTkScrollableFrame(
            self, fg_color="transparent")
        self.frameLista.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._refrescarLista()

    def _abrirFormulario(self, cuenta=None):
        FormularioCuenta(self, cuenta=cuenta, on_guardado=self._refrescarLista)

    def _refrescarLista(self):
        for widget in self.frameLista.winfo_children():
            widget.destroy()

        cuentas = db.obtener_cuentas(solo_activas=False)
        activas  = [c for c in cuentas if c["activa"]]
        inactivas = [c for c in cuentas if not c["activa"]]

        if not cuentas:
            ctk.CTkLabel(
                self.frameLista,
                text="No hay cuentas registradas",
                font=(FUENTE, 13),
                text_color=COLOR_MUTED
            ).pack(pady=40)
            return

        for cuenta in activas:
            saldo = db.calcular_saldo(cuenta["id"])

            fila = ctk.CTkFrame(
                self.frameLista, fg_color=COLOR_CARD, corner_radius=8)
            fila.pack(fill="x", pady=(0, 8))
            fila.grid_columnconfigure(1, weight=1)

            # Barra de color izquierda
            ctk.CTkFrame(
                fila, width=4,
                fg_color=cuenta["color"],
                corner_radius=0
            ).grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 12))

            # Nombre
            ctk.CTkLabel(
                fila,
                text=cuenta["nombre"],
                font=(FUENTE, 14, "bold"),
                text_color=COLOR_TEXTO,
                anchor="w"
            ).grid(row=0, column=1, sticky="w", pady=(10, 0))

            # Saldo y tipo
            tipos = {"debito": "Débito", "credito": "Crédito",
                     "ahorros": "Ahorros", "efectivo": "Efectivo", "otro": "Otro"}
            ctk.CTkLabel(
                fila,
                text=f"{tipos.get(cuenta['tipo'], '')} · ${saldo:,.2f}",
                font=(FUENTE, 11),
                text_color=COLOR_MUTED,
                anchor="w"
            ).grid(row=1, column=1, sticky="w", pady=(0, 10))

            # Botón editar
            ctk.CTkButton(
                fila,
                text="Editar",
                font=(FUENTE, 11),
                height=28, width=70,
                fg_color="transparent",
                border_width=1, border_color="#E0DED6",
                text_color=COLOR_MUTED, hover_color="#E8E6DF",
                command=lambda c=cuenta: self._abrirFormulario(cuenta=c)
            ).grid(row=0, column=2, rowspan=2, padx=12)

            #Boton eliminar
            ctk.CTkButton(
                fila,
                text="Eliminar",
                font=(FUENTE, 11),
                height=28,
                fg_color="transparent",
                border_width=1,
                border_color="#E0DED6",
                text_color="#D85A30",
                hover_color="#FDECEA",
                command=lambda c=cuenta: self._eliminarCuenta(c)
            ).grid(row=1, column=2, rowspan=1, padx=12)

        # Sección de cuentas archivadas
        if inactivas:
            ctk.CTkLabel(
                self.frameLista,
                text=f"Archivadas ({len(inactivas)})",
                font=(FUENTE, 11),
                text_color=COLOR_MUTED,
                anchor="w"
            ).pack(fill="x", pady=(8, 8))

            for cuenta in inactivas:
                fila = ctk.CTkFrame(
                    self.frameLista, fg_color=COLOR_CARD, corner_radius=8)
                fila.pack(fill="x", pady=(0, 8))
                fila.grid_columnconfigure(1, weight=1)

                # Barra gris — está inactiva
                ctk.CTkFrame(
                    fila, width=4,
                    fg_color="#CCCCCC",
                    corner_radius=0
                ).grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 12))

                # Nombre en gris
                ctk.CTkLabel(
                    fila,
                    text=cuenta["nombre"],
                    font=(FUENTE, 14, "bold"),
                    text_color=COLOR_MUTED,
                    anchor="w"
                ).grid(row=0, column=1, sticky="w", pady=(10, 0))

                # Tipo
                tipos = {"debito": "Débito", "credito": "Crédito",
                         "ahorros": "Ahorros", "efectivo": "Efectivo", "otro": "Otro"}
                ctk.CTkLabel(
                    fila,
                    text=f"{tipos.get(cuenta['tipo'], '')} · Archivada",
                    font=(FUENTE, 11),
                    text_color=COLOR_MUTED,
                    anchor="w"
                ).grid(row=1, column=1, sticky="w", pady=(0, 10))

                # Botón reactivar
                ctk.CTkButton(
                    fila,
                    text="Reactivar",
                    font=(FUENTE, 11),
                    height=28, width=80,
                    fg_color="transparent",
                    border_width=1, border_color="#E0DED6",
                    text_color="#1D9E75", hover_color="#E8F5F0",
                    command=lambda c=cuenta: self._reactivarCuenta(c)
                ).grid(row=0, column=2, rowspan=2, padx=12)

    def _eliminarCuenta(self, cuenta):
        db.archivar_cuenta(cuenta["id"])
        self._refrescarLista()

    def _reactivarCuenta(self, cuenta):
        db.reactivar_cuenta(cuenta["id"])
        self._refrescarLista()


if __name__ == "__main__":
    db.inicializar_db()
    raiz = ctk.CTk()
    raiz.withdraw()
    app = GestionCuentas(raiz)
    app.mainloop()