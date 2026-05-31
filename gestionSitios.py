import customtkinter as ctk
import database as db
from config import FUENTE, COLOR_BG, COLOR_CARD, COLOR_TEXTO, COLOR_MUTED


class FormularioSitio(ctk.CTkToplevel):
    def __init__(self, padre, sitio=None, on_guardado=None):
        super().__init__(padre)
        self.sitio      = sitio       # None = nuevo, dict = editar
        self.on_guardado = on_guardado
        self.title("Nuevo sitio" if not sitio else "Editar sitio")
        self.geometry("380x320")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self.grab_set()
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Nombre
        ctk.CTkLabel(scroll, text="Nombre *",
                     font=(FUENTE, 11), text_color=COLOR_MUTED,
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.entryNombre = ctk.CTkEntry(
            scroll, font=(FUENTE, 13), height=36,
            placeholder_text="Ej: Nu, Santander, Físico...")
        self.entryNombre.pack(fill="x", pady=(0, 12))

        # Tipo
        ctk.CTkLabel(scroll, text="Tipo *",
                     font=(FUENTE, 11), text_color=COLOR_MUTED,
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.comboTipo = ctk.CTkComboBox(
            scroll, font=(FUENTE, 13), height=36,
            values=["banco", "billetera", "efectivo", "otro"],
            state="readonly")
        self.comboTipo.set("banco")
        self.comboTipo.pack(fill="x", pady=(0, 12))

        # Notas
        ctk.CTkLabel(scroll, text="Notas",
                     font=(FUENTE, 11), text_color=COLOR_MUTED,
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.txtNotas = ctk.CTkTextbox(
            scroll, font=(FUENTE, 13), height=60, corner_radius=6)
        self.txtNotas.pack(fill="x", pady=(0, 16))

        # Botones
        frameBotones = ctk.CTkFrame(scroll, fg_color="transparent")
        frameBotones.pack(fill="x")
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

        # Si es edición, llenar los campos
        if self.sitio:
            self.entryNombre.insert(0, self.sitio["nombre"])
            self.comboTipo.set(self.sitio["tipo"])
            if self.sitio.get("notas"):
                self.txtNotas.insert("1.0", self.sitio["notas"])

    def _guardar(self):
        nombre = self.entryNombre.get().strip()
        if not nombre:
            self.lblError.configure(text="⚠ El nombre es obligatorio")
            return

        tipo  = self.comboTipo.get()
        notas = self.txtNotas.get("1.0", "end").strip()

        if self.sitio:
            db.editar_sitio(self.sitio["id"], nombre, tipo, notas)
        else:
            db.agregar_sitio(nombre, tipo, notas)

        if self.on_guardado:
            self.on_guardado()

        self.destroy()

class GestionSitios(ctk.CTkToplevel):
    def __init__(self, padre):
        super().__init__(padre)
        self.title("Sitios y bancos")
        self.geometry("500x560")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self._construir()

    def _construir(self):
        ctk.CTkLabel(
            self,
            text="Sitios y bancos",
            font=(FUENTE, 18, "bold"),
            text_color=COLOR_TEXTO,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 16))

        # Botón agregar
        ctk.CTkButton(
            self,
            text="+ Agregar sitio",
            font=(FUENTE, 13),
            height=36,
            command=self._abrirFormulario
        ).pack(fill="x", padx=20, pady=(0, 12))

        #Lista de sitios
        self.frameLista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frameLista.pack(fill="both", expand=True, padx=20, pady=16)

        self._refrescarLista()
    
    def _abrirFormulario(self, sitio=None):
        FormularioSitio(self, sitio=sitio, on_guardado=self._refrescarLista)

    def _refrescarLista(self):
        # Limpiar lista actual
        for widget in self.frameLista.winfo_children():
            widget.destroy()

        sitios = db.obtener_sitios()

        if not sitios:
            ctk.CTkLabel(
                self.frameLista,
                text="No hay sitios registrados",
                font=(FUENTE, 13),
                text_color=COLOR_MUTED
            ).pack(pady=40)
            return

        for sitio in sitios:
            fila = ctk.CTkFrame(
                self.frameLista,
                fg_color=COLOR_CARD,
                corner_radius=8
            )
            fila.pack(fill="x", pady=(0, 8))
            fila.grid_columnconfigure(1, weight=1)

            # Tipo como etiqueta de color
            tipos_color = {
                "banco"    : "#378ADD",
                "billetera": "#1D9E75",
                "efectivo" : "#888780",
                "otro"     : "#BA7517"
            }
            color = tipos_color.get(sitio["tipo"], "#888780")

            ctk.CTkFrame(
                fila,
                width=4,
                fg_color=color,
                corner_radius=0
            ).grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 12))

            # Nombre
            ctk.CTkLabel(
                fila,
                text=sitio["nombre"],
                font=(FUENTE, 14, "bold"),
                text_color=COLOR_TEXTO,
                anchor="w"
            ).grid(row=0, column=1, sticky="w", pady=(10, 0))

            # Tipo
            ctk.CTkLabel(
                fila,
                text=sitio["tipo"].capitalize(),
                font=(FUENTE, 11),
                text_color=COLOR_MUTED,
                anchor="w"
            ).grid(row=1, column=1, sticky="w", pady=(0, 10))

            # Botón editar
            ctk.CTkButton(
                fila,
                text="Editar",
                font=(FUENTE, 11),
                height=28,
                width=70,
                fg_color="transparent",
                border_width=1,
                border_color="#E0DED6",
                text_color=COLOR_MUTED,
                hover_color="#E8E6DF",
                command=lambda s=sitio: self._abrirFormulario(sitio=s)
            ).grid(row=0, column=2, rowspan=2, padx=12)

            #Boton Eliminar
            ctk.CTkButton(
                fila,
                text="Eliminar",
                font=(FUENTE, 11),
                height=28,
                width=70,
                fg_color="transparent",
                border_width=1,
                border_color="#E0DED6",
                text_color="#D85A30",
                hover_color="#FDECEA",
                command=lambda s=sitio: self._eliminarSitio(s)
            ).grid(row=1, column=2, rowspan=1, padx=12)

    def _eliminarSitio(self, sitio):
        db.eliminar_sitio(sitio["id"])
        self._refrescarLista()


if __name__ == "__main__":
    db.inicializar_db()
    raiz = ctk.CTk()
    raiz.withdraw()
    app = GestionSitios(raiz)
    app.mainloop()