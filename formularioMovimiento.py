import customtkinter as ctk
import database as db
from datetime import date
from config import FUENTE, COLOR_BG, COLOR_CARD, COLOR_TEXTO, COLOR_MUTED



class FormularioMovimiento(ctk.CTkToplevel):
    def __init__(self, padre):
        super().__init__(padre)
        self.title("Nuevo movimiento")
        self.geometry("440x560")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self.tipo = "ingreso"
        self._construir()

    def _setTipo(self, tipo):
        self.tipo = tipo

        if tipo == "ingreso":
            self.btnIngreso.configure(fg_color="#1D9E75", text_color="white")
            self.btnGasto.configure(fg_color="#E8E6DF", text_color=COLOR_MUTED)
        else:
            self.btnGasto.configure(fg_color="#D85A30", text_color="white")
            self.btnIngreso.configure(fg_color="#E8E6DF", text_color=COLOR_MUTED)

        self._actualizarCategorias(tipo)

    def _construir(self):
        #Contenedor con scroll
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")

        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Título
        ctk.CTkLabel(
            scroll,
            text="Nuevo movimiento",
            font=(FUENTE, 18, "bold"),
            text_color=COLOR_TEXTO,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 16))

        # Tipo de movimiento
        ctk.CTkLabel(
            scroll,
            text="Tipo",
            font=(FUENTE, 11),
            text_color=COLOR_MUTED,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 4))

        frameTipo = ctk.CTkFrame(scroll, fg_color="transparent")
        frameTipo.pack(fill="x", padx=20, pady=(0, 12))
        frameTipo.grid_columnconfigure((0, 1), weight=1)

        self.btnIngreso = ctk.CTkButton(
            frameTipo,
            text="↓  Ingreso",
            font=(FUENTE, 13),
            height=38,
            fg_color="#1D9E75",
            hover_color="#178a63",
            command=lambda: self._setTipo("ingreso")
        )
        self.btnIngreso.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btnGasto = ctk.CTkButton(
            frameTipo,
            text="↑  Gasto",
            font=(FUENTE, 13),
            height=38,
            fg_color="#E8E6DF",
            text_color=COLOR_MUTED,
            hover_color="#d9d7d0",
            command=lambda: self._setTipo("gasto")
        )
        self.btnGasto.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Cuenta
        ctk.CTkLabel(
            scroll,
            text="Cuenta *",
            font=(FUENTE, 11),
            text_color=COLOR_MUTED,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 4))

        cuentas = db.obtener_cuentas()
        self.cuentasMap = {c["nombre"]: c["id"] for c in cuentas}

        self.comboCuenta = ctk.CTkComboBox(
            scroll,
            values=list(self.cuentasMap.keys()),
            font=(FUENTE, 13),
            height=36,
            state="readonly"
        )
        self.comboCuenta.set(cuentas[0]["nombre"] if cuentas else "")
        self.comboCuenta.pack(fill="x", padx=20, pady=(0, 12))

        # Monto
        ctk.CTkLabel(
            scroll,
            text="Monto *",
            font=(FUENTE, 11),
            text_color=COLOR_MUTED,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 4))

        frameMonto = ctk.CTkFrame(scroll, fg_color="transparent")
        frameMonto.pack(fill="x", padx=20, pady=(0, 12))
        frameMonto.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frameMonto,
            text="$",
            font=(FUENTE, 20, "bold"),
            text_color=COLOR_MUTED,
            width=24
        ).grid(row=0, column=0, padx=(0, 4))

        self.entryMonto = ctk.CTkEntry(
            frameMonto,
            font=(FUENTE, 20, "bold"),
            height=42,
            placeholder_text="0.00"
        )
        self.entryMonto.grid(row=0, column=1, sticky="ew")

        # Descripción
        ctk.CTkLabel(
            scroll,
            text="Descripción *",
            font=(FUENTE, 11),
            text_color=COLOR_MUTED,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 4))

        self.entryDesc = ctk.CTkEntry(
            scroll,
            font=(FUENTE, 13),
            height=36,
            placeholder_text="Ej: Venta a cliente, Supermercado..."
        )
        self.entryDesc.pack(fill="x", padx=20, pady=(0, 12))

        # Fecha y referencia
        frameFechaRef = ctk.CTkFrame(scroll, fg_color="transparent")
        frameFechaRef.pack(fill="x", padx=20, pady=(0, 12))
        frameFechaRef.grid_columnconfigure((0, 1), weight=1)

        # Fecha
        ctk.CTkLabel(
            frameFechaRef,
            text="Fecha *",
            font=(FUENTE, 11),
            text_color=COLOR_MUTED,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.entryFecha = ctk.CTkEntry(
            frameFechaRef,
            font=(FUENTE, 13),
            height=36,
            placeholder_text="YYYY-MM-DD"
        )
        self.entryFecha.insert(0, date.today().isoformat())
        self.entryFecha.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        # Referencia
        ctk.CTkLabel(
            frameFechaRef,
            text="Referencia",
            font=(FUENTE, 11),
            text_color=COLOR_MUTED,
            anchor="w"
        ).grid(row=0, column=1, sticky="w", pady=(0, 4))

        self.entryRef = ctk.CTkEntry(
            frameFechaRef,
            font=(FUENTE, 13),
            height=36,
            placeholder_text="# folio, orden..."
        )
        self.entryRef.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Categoría
        ctk.CTkLabel(
            scroll,
            text="Categoría",
            font=(FUENTE, 11),
            text_color=COLOR_MUTED,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 4))

        self.categoriasMap = {}

        self.comboCat = ctk.CTkComboBox(
            scroll,
            values=[],
            font=(FUENTE, 13),
            height=36,
            state="readonly"
        )
        self.comboCat.pack(fill="x", padx=20, pady=(0, 12))

        self._actualizarCategorias("ingreso")

        # Notas
        ctk.CTkLabel(
            scroll,
            text="Notas",
            font=(FUENTE, 11),
            text_color=COLOR_MUTED,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 4))

        self.txtNotas = ctk.CTkTextbox(
            scroll,
            font=(FUENTE, 13),
            height=70,
            corner_radius=6
        )
        self.txtNotas.pack(fill="x", padx=20, pady=(0, 16))

        # Botones
        frameBotones = ctk.CTkFrame(scroll, fg_color="transparent")
        frameBotones.pack(fill="x", padx=20, pady=(0, 20))
        frameBotones.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            frameBotones,
            text="Cancelar",
            font=(FUENTE, 13),
            height=38,
            width=100,
            fg_color="transparent",
            border_width=1,
            border_color="#E0DED6",
            text_color=COLOR_MUTED,
            hover_color="#E8E6DF",
            command=self.destroy
        ).grid(row=0, column=0, padx=(0, 8))

        self.btnGuardar = ctk.CTkButton(
            frameBotones,
            text="Guardar movimiento",
            font=(FUENTE, 13, "bold"),
            height=38,
            command=self._guardar
        )
        self.btnGuardar.grid(row=0, column=1, sticky="ew")

        # Mensaje de error
        self.lblError = ctk.CTkLabel(
            scroll,
            text="",
            font=(FUENTE, 12),
            text_color="#D85A30",
            anchor="w"
        )
        self.lblError.pack(fill="x", padx=20)

    def _actualizarCategorias(self, tipo):
        cats = db.obtener_categorias(tipo=tipo)
        self.categoriasMap = {c["nombre"]: c["id"] for c in cats}
        nombres = list(self.categoriasMap.keys())
        self.comboCat.configure(values=nombres)
        self.comboCat.set(nombres[0] if nombres else "")

    def _guardar(self):
        # Validar monto
        try:
            monto = float(self.entryMonto.get().replace(",", "."))
            if monto <= 0:
                raise ValueError
        except ValueError:
            self.lblError.configure(text="⚠ Ingresa un monto válido mayor a 0")
            return

        # Validar descripción
        desc = self.entryDesc.get().strip()
        if not desc:
            self.lblError.configure(text="⚠ La descripción es obligatoria")
            return

        # Validar fecha
        fecha = self.entryFecha.get().strip()
        if len(fecha) != 10 or fecha[4] != "-" or fecha[7] != "-":
            self.lblError.configure(text="⚠ Fecha inválida, usa YYYY-MM-DD")
            return

        # Obtener cuenta
        cuentaNombre = self.comboCuenta.get()
        cuentaId = self.cuentasMap.get(cuentaNombre)
        if not cuentaId:
            self.lblError.configure(text="⚠ Selecciona una cuenta")
            return

        # Obtener categoría y notas
        catNombre = self.comboCat.get()
        catId = self.categoriasMap.get(catNombre)
        ref   = self.entryRef.get().strip()
        notas = self.txtNotas.get("1.0", "end").strip()

        # Guardar en la base de datos
        db.agregar_movimiento(
            cuenta_id    = cuentaId,
            tipo         = self.tipo,
            monto        = monto,
            descripcion  = desc,
            fecha        = fecha,
            categoria_id = catId,
            referencia   = ref,
            notas        = notas
        )

        self.destroy()

if __name__ == "__main__":
    db.inicializar_db()
    raiz = ctk.CTk()
    raiz.withdraw()  # oculta la ventana raíz
    app = FormularioMovimiento(raiz)
    app.mainloop()