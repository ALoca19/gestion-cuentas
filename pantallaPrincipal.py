from datetime import date
from formularioMovimiento import FormularioMovimiento as FormMov
import customtkinter as ctk
import database as db
from exportar import exportar_excel as exportar
from gestionSitios import GestionSitios as GesSitios
from gestionCuentas import GestionCuentas as GesCuentas
from graficas import VentanaGraficas as Graficas
from config import FUENTE, COLOR_BG, COLOR_CARD, COLOR_TEXTO, COLOR_MUTED



#Configuracion global de la apariencia
ctk.set_appearance_mode("light") #Modos: "light", "dark", "system"
ctk.set_default_color_theme("blue") #Temas: "blue", "dark-blue

#Clase
class TarjetaCuenta(ctk.CTkFrame):
    def __init__(self, padre, cuenta, saldo, on_click=None):
        super().__init__(
            padre,
            fg_color=COLOR_CARD,
            corner_radius=12
        )
        self.cuenta = cuenta
        self.saldo = saldo
        self.on_click = on_click
        self._construir()

        self.bind("<Button-1>", self._click)  # Vincula el clic a toda la tarjeta

    def resaltar(self, activa):
        if activa:
            self.configure(border_width=2, border_color=self.cuenta["color"])
        else:
            self.configure(border_width=0)

    def _click(self, event=None):
        if self.on_click:
            self.on_click(self.cuenta["id"])

    def _construir(self):
        # Barra de color arriba
        ctk.CTkFrame(
            self,
            height=4,
            fg_color=self.cuenta["color"],
            corner_radius=0
        ).pack(fill="x")

        # Contenido
        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.pack(fill="both", padx=14, pady=12)

        # Nombre de la cuenta
        ctk.CTkLabel(
            contenido,
            text=self.cuenta["nombre"],
            font=(FUENTE, 12),
            text_color=COLOR_MUTED,
            anchor="w"
        ).pack(fill="x")

        # Saldo
        color_saldo = "#D85A30" if self.saldo < 0 else COLOR_TEXTO
        ctk.CTkLabel(
            contenido,
            text=f"${self.saldo:,.2f}",
            font=(FUENTE, 18, "bold"),
            text_color=color_saldo,
            anchor="w"
        ).pack(fill="x")

        # Tipo
        tipos = {
            "debito"  : "Débito",
            "credito" : "Crédito",
            "ahorros" : "Ahorros",
            "efectivo": "Efectivo",
            "otro"    : "Otro"
        }
        ctk.CTkLabel(
            contenido,
            text=tipos.get(self.cuenta["tipo"], ""),
            font=(FUENTE, 10),
            text_color=COLOR_MUTED,
            anchor="w"
        ).pack(fill="x")

# ── Fila de movimiento ─────────────────────
class FilaMovimiento(ctk.CTkFrame):
    def __init__(self, padre, mov, on_eliminar=None):
        super().__init__(padre, fg_color="transparent")
        self.on_eliminar = on_eliminar
        self._construir(mov)

    def _construir(self, mov):
        self.grid_columnconfigure(1, weight=1)

        # Punto de color de la cuenta
        ctk.CTkFrame(
            self,
            width=10, height=10,
            fg_color=mov["cuenta_color"],
            corner_radius=5
        ).grid(row=0, column=0, rowspan=2, padx=(6, 10), pady=6)

        # Descripción
        ctk.CTkLabel(
            self,
            text=mov["descripcion"],
            font=(FUENTE, 13),
            text_color=COLOR_TEXTO,
            anchor="w"
        ).grid(row=0, column=1, sticky="w")

        # Detalle: cuenta · categoría · fecha
        detalle = mov["cuenta_nombre"]
        if mov.get("categoria_nombre"):
            detalle += f" · {mov['categoria_nombre']}"
        detalle += f" · {mov['fecha']}"

        ctk.CTkLabel(
            self,
            text=detalle,
            font=(FUENTE, 11),
            text_color=COLOR_MUTED,
            anchor="w"
        ).grid(row=1, column=1, sticky="w")

        # Monto
        signo = "+" if mov["tipo"] == "ingreso" else "−"
        color = "#1D9E75" if mov["tipo"] == "ingreso" else "#D85A30"
        ctk.CTkLabel(
            self,
            text=f"{signo}${mov['monto']:,.2f}",
            font=(FUENTE, 13, "bold"),
            text_color=color
        ).grid(row=0, column=2, rowspan=2, padx=12)

        # Eliminar
        btnEliminar =  ctk.CTkButton(
            self,
            text="Eliminar",
            font=(FUENTE, 11),
            height=28,
            fg_color="transparent",
            border_width=1,
            border_color="#E0DED6",
            text_color="#D85A30",
            hover_color="#FDECEA",
            command=lambda: self.on_eliminar(mov["id"]) if self.on_eliminar else None
        )
        btnEliminar.grid(row=0, column=3, rowspan=2, padx=12)

        # Separador
        ctk.CTkFrame(
            self,
            height=1,
            fg_color="#E0DED6"
        ).grid(row=2, column=0, columnspan=3, sticky="ew", padx=4)

class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Administrador de cuentas")
        self.geometry("900x650")
        self.configure(fg_color=COLOR_BG)
        self.cuentaActivaId = None #Para saber en qué cuenta se está trabajando al abrir el formulario
        self.listaMov = None #Referencia a la lista de movimientos para refrescarla después de agregar uno nuevo
        self.tarjetas = {} #Lista de tarjetas para poder resaltar la activa
        self.fechaDesde = None #Para recordar el rango de fechas seleccionado al exportar
        self.fechaHasta = None
        self.construirUI()

    def construirUI(self):

        #Barra superior
        barra = ctk.CTkFrame(self,
                             fg_color=COLOR_CARD,
                             corner_radius=0)
        barra.pack(fill="x")

        ctk.CTkLabel(
            barra,
            text="Mis cuentas",
            font=(FUENTE, 20, "bold"),
            text_color=COLOR_TEXTO
        ).pack(padx=16, pady=14, side="left")

        ctk.CTkButton(
            barra,
            text="+ Nuevo Movimiento",
            font=(FUENTE, 13),
            height=34,
            command = self._abrirFormulario
        ).pack(padx=16, pady=10, side="right")

        ctk.CTkButton(
            barra,
            text="Sitios",
            font=(FUENTE, 13),
            height=34,
            fg_color="transparent",
            border_width=1,
            border_color="#E0DED6",
            text_color=COLOR_MUTED,
            hover_color="#E8E6DF",
            command=self._abrirSitios
        ).pack(side="right", padx=(0, 8), pady=10)

        ctk.CTkButton(
            barra,
            text="Cuentas",
            font=(FUENTE, 13),
            height=34,
            fg_color="transparent",
            border_width=1,
            border_color="#E0DED6",
            text_color=COLOR_MUTED,
            hover_color="#E8E6DF",
            command=self._abrirCuentas
        ).pack(side="right", padx=(0, 8), pady=10)

        ctk.CTkButton(
            barra,
            text="Exportar",
            font=(FUENTE, 13),
            height=34,
            fg_color="transparent",
            border_width=1,
            border_color="#E0DED6",
            text_color=COLOR_MUTED,
            hover_color="#E8E6DF",
            command=self._exportar
        ).pack(side="right", padx=(0, 8), pady=10)

        ctk.CTkButton(
            barra,
            text="Gráficas",
            font=(FUENTE, 13),
            height=34,
            fg_color="transparent",
            border_width=1,
            border_color="#E0DED6",
            text_color=COLOR_MUTED,
            hover_color="#E8E6DF",
            command=self._abrirGraficas
        ).pack(side="right", padx=(0, 8), pady=10)

        

        

        #Resumen de cuentas
        frameResumen = ctk.CTkFrame(self,
                                  fg_color="transparent"
                                  )
        frameResumen.pack(fill="x", padx=16, pady=(16,0))

        frameResumen.grid_columnconfigure((0,1,2), weight=1) #Hace que las columnas se expandan por igual

        #Obtener los datos para el resumen
        hoy = date.today()
        resumen =  db.resumen_mes(hoy.year, hoy.month) #Obtiene el resumen del mes actual

        totalDisponible = sum(db.calcular_saldo(c["id"]) for c in db.obtener_cuentas())
        totalGastos = sum(r["total_gastos"] for r in resumen)
        totalIngresos = sum(r["total_ingresos"] for r in resumen)

        datosResumen = [
            ("Total disponible",  f"${totalDisponible:,.2f}", COLOR_TEXTO),
            ("Gastos este mes",   f"${totalGastos:,.2f}", "#D85A30"),
            ("Ingresos este mes", f"${totalIngresos:,.2f}", "#1D9E75"),
        ]

        for i, (etiqueta, valor, color) in enumerate(datosResumen):
            card = ctk.CTkFrame(frameResumen,
                                 fg_color=COLOR_CARD,
                                 corner_radius=10)
            
            card.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0), sticky="ew")

            ctk.CTkLabel(card, text=etiqueta,
                     font=(FUENTE, 11),
                     text_color=COLOR_MUTED,
                     anchor="w").pack(fill="x", padx=14, pady=(10, 0))

            ctk.CTkLabel(card, text=valor,
                     font=(FUENTE, 22, "bold"),
                     text_color=color,
                     anchor="w").pack(fill="x", padx=14, pady=(0, 10))
        
        #Panel de cuentas
        frameCuentas = ctk.CTkFrame(self,
                                    fg_color="transparent")
        frameCuentas.pack(fill="x", padx=16, pady=12)

        cuentas =  db.obtener_cuentas() #Obtiene las cuentas desde la base de datos

        for i, cuenta in enumerate(cuentas):
            saldo = db.calcular_saldo(cuenta["id"])
            tarjeta = TarjetaCuenta(frameCuentas, cuenta, saldo, on_click=self._filtrarPorCuenta)
            tarjeta.grid(row=0, column=i, padx=(0 if i == 0 else 8, 0), sticky="ew")
            frameCuentas.grid_columnconfigure(i, weight=1) #Hace que cada tarjeta se expanda por igual
            self.tarjetas[cuenta["id"]] = tarjeta #Guarda referencia a la tarjeta para poder resaltar después

        #Fechas
        # ── Filtro por fechas ──────────────────────
        frameFiltro = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        frameFiltro.pack(fill="x", padx=16, pady=(0, 8))
        frameFiltro.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            frameFiltro, text="Desde:",
            font=(FUENTE, 12), text_color=COLOR_MUTED
        ).grid(row=0, column=0, padx=(14, 6), pady=10)

        self.entryDesde = ctk.CTkEntry(
            frameFiltro, font=(FUENTE, 12),
            height=32, placeholder_text="YYYY-MM-DD")
        self.entryDesde.grid(row=0, column=1, sticky="ew", pady=10)

        ctk.CTkLabel(
            frameFiltro, text="Hasta:",
            font=(FUENTE, 12), text_color=COLOR_MUTED
        ).grid(row=0, column=2, padx=(14, 6), pady=10)

        self.entryHasta = ctk.CTkEntry(
            frameFiltro, font=(FUENTE, 12),
            height=32, placeholder_text="YYYY-MM-DD")
        self.entryHasta.grid(row=0, column=3, sticky="ew", pady=10)

        ctk.CTkButton(
            frameFiltro, text="Filtrar",
            font=(FUENTE, 12), height=32, width=80,
            command=self._aplicarFiltro
        ).grid(row=0, column=4, padx=(10, 6), pady=10)

        ctk.CTkButton(
            frameFiltro, text="Limpiar",
            font=(FUENTE, 12), height=32, width=80,
            fg_color="transparent", border_width=1,
            border_color="#E0DED6", text_color=COLOR_MUTED,
            hover_color="#E8E6DF",
            command=self._limpiarFiltro
        ).grid(row=0, column=5, padx=(0, 14), pady=10)

        # ── Movimientos recientes ──────────────────
        panel_movs = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        panel_movs.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        ctk.CTkLabel(
            panel_movs,
            text="Movimientos recientes",
            font=(FUENTE, 14, "bold"),
            text_color=COLOR_TEXTO,
            anchor="w"
        ).pack(fill="x", padx=16, pady=(12, 8))

        self.listaMov = ctk.CTkScrollableFrame(panel_movs, fg_color="transparent")
        self.listaMov.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        #Cargar movimientos
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

    def _abrirGraficas(self):
        ventana = Graficas(self)
        ventana.grab_set()
    
    def _abrirSitios(self):
        ventana = GesSitios(self)
        ventana.grab_set()
        self.wait_window(ventana)

    def _exportar(self):
        ruta = exportar()
        import os
        os.startfile(ruta)  # abre el archivo automáticamente en Excel

    def _abrirCuentas(self):
        ventana = GesCuentas(self)
        ventana.grab_set()
        self.wait_window(ventana)
        self._refrescar()  # refresca la pantalla principal al cerrar

    def _abrirFormulario(self):
        formulario = FormMov(self)
        formulario.grab_set()  # bloquea la ventana principal mientras el formulario está abierto
        self.wait_window(formulario)  # espera a que el formulario se cierre
        self._refrescar()  # refresca los datos al cerrar

    def _refrescar(self):
        # Destruye todos los widgets y reconstruye la UI con datos frescos
        for widget in self.winfo_children():
            widget.destroy()
        self.construirUI()

    def _refrescarLista(self):
        # Borrar solo los movimientos
        for widget in self.listaMov.winfo_children():
            widget.destroy()

        movimientos = db.obtener_movimientos(
            cuenta_id=self.cuentaActivaId,
            fecha_desde=self.fechaDesde,
            fecha_hasta=self.fechaHasta,
            limite=20
        )

        if not movimientos:
            ctk.CTkLabel(
                self.listaMov,
                text="Sin movimientos registrados",
                font=(FUENTE, 13),
                text_color=COLOR_MUTED
            ).pack(pady=40)
        else:
            for mov in movimientos:
                FilaMovimiento(self.listaMov, mov, on_eliminar=self._eliminarMovimiento).pack(fill="x")

    def _filtrarPorCuenta(self, cuenta_id):
        # Si se hace clic en la misma cuenta, regresa a mostrar todas
        if self.cuentaActivaId == cuenta_id:
            self.cuentaActivaId = None
        else:
            self.cuentaActivaId = cuenta_id

        # Resaltar tarjeta activa
        for tid, tarjeta in self.tarjetas.items():
            tarjeta.resaltar(tid == self.cuentaActivaId)

        self._refrescarLista()

    def _eliminarMovimiento(self, mov_id):
        db.eliminar_movimiento(mov_id)
        self._refrescar()

#Arranca
if __name__ == "__main__":
    
    db.inicializar_db() #Asegura que la base de datos esté lista antes de iniciar la app
    app = VentanaPrincipal()
    app.mainloop()