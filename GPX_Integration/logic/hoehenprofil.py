import matplotlib.pyplot as plt


def _wert(p, name):
    if p is None:
        return None
    if hasattr(p, name):
        return getattr(p, name)
    if isinstance(p, dict):
        return p.get(name)
    if hasattr(p, "__getitem__"):
        try:
            return p[name]
        except (KeyError, TypeError, IndexError):
            return None
    return None


def hoehenprofil_plot(streckenpunkte):
    """
    Erstellt ein Höhenprofil-Diagramm als Matplotlib-Figure.
    Gibt die Figure zurück, damit Streamlit sie anzeigen kann.
    """

    try:
        hoehen = [_wert(p, "hoehe") for p in streckenpunkte if _wert(p, "hoehe") is not None]
    except Exception:
        hoehen = []

    fig, ax = plt.subplots(figsize=(10, 4))

    if not hoehen:
        ax.text(0.5, 0.5, "Keine Höhenwerte verfügbar.", ha="center", va="center")
        ax.set_title("Höhenprofil")
        ax.set_xlabel("Streckenpunkte")
        ax.set_ylabel("Höhe (m)")
        return fig

    x_werte = list(range(len(hoehen)))

    ax.plot(x_werte, hoehen, color="brown", linewidth=2)
    ax.fill_between(x_werte, hoehen, color="sandybrown", alpha=0.4)

    ax.set_title("Höhenprofil")
    ax.set_xlabel("Streckenpunkte")
    ax.set_ylabel("Höhe (m)")

    ax.grid(True, linestyle="--", alpha=0.5)

    return fig
