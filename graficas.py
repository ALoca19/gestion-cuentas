import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
import database as db
from datetime import date
from config import FUENTE, COLOR_BG, COLOR_CARD, COLOR_TEXTO, COLOR_MUTED



class VentanaGraficas(ctk.CTkToplevel):
    def __init__(self, padre):
        super().__init__(padre)
        self.title("Gráficas")
        self.geometry("900x600")
        self.configure(fg_color=COLOR_BG)
        self._construir()

    def _construir(self):
        # Título
        ctk.CTkLabel(
            self,
            text="Análisis de gastos",
            font=(FUENTE, 18, "bold"),
            text_color=COLOR_TEXTO,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 16))

        # Frame para las gráficas
        self.frameGraficas = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        self.frameGraficas.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._graficar()

    def _graficar(self):
        hoy     = date.today()
        resumen = db.resumen_mes(hoy.year, hoy.month)
        meses   = db.gastos_ultimos_meses(6)

        # Crear figura con 2 subgráficas lado a lado
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        fig.patch.set_facecolor("#FFFFFF")

        # ── Gráfica A: Gastos por cuenta ──────────────
        cuentas  = [r["nombre"] for r in resumen]
        gastos   = [r["total_gastos"] for r in resumen]
        ingresos = [r["total_ingresos"] for r in resumen]
        colores  = [r["color"] for r in resumen]

        x = range(len(cuentas))
        ancho = 0.35

        ax1.bar([i - ancho/2 for i in x], ingresos,
                width=ancho, color="#1D9E75", label="Ingresos")
        ax1.bar([i + ancho/2 for i in x], gastos,
                width=ancho, color="#D85A30", label="Gastos")

        ax1.set_title("Ingresos y gastos por cuenta", fontsize=12, pad=12)
        ax1.set_xticks(list(x))
        ax1.set_xticklabels(cuentas, rotation=15, ha="right", fontsize=9)
        ax1.set_facecolor("#FAFAFA")
        ax1.legend(fontsize=9)
        ax1.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
        ax1.grid(axis="y", linestyle="--", alpha=0.5)

        # ── Gráfica B: Tendencia últimos meses ────────
        etiquetas_mes = [m["mes"] for m in meses]
        gastos_mes    = [m["gastos"] for m in meses]
        ingresos_mes  = [m["ingresos"] for m in meses]

        ax2.plot(etiquetas_mes, ingresos_mes,
                 color="#1D9E75", marker="o", linewidth=2, label="Ingresos")
        ax2.plot(etiquetas_mes, gastos_mes,
                 color="#D85A30", marker="o", linewidth=2, label="Gastos")
        ax2.fill_between(etiquetas_mes, ingresos_mes,
                         alpha=0.1, color="#1D9E75")
        ax2.fill_between(etiquetas_mes, gastos_mes,
                         alpha=0.1, color="#D85A30")

        ax2.set_title("Tendencia últimos meses", fontsize=12, pad=12)
        ax2.set_facecolor("#FAFAFA")
        ax2.legend(fontsize=9)
        ax2.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
        ax2.grid(axis="y", linestyle="--", alpha=0.5)
        plt.xticks(rotation=15, ha="right", fontsize=9)

        plt.tight_layout(pad=2.0)

        # Insertar gráfica en la ventana de CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frameGraficas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


if __name__ == "__main__":
    db.inicializar_db()
    raiz = ctk.CTk()
    raiz.withdraw()
    app = VentanaGraficas(raiz)
    app.mainloop()