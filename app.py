"""
Esempio minimo: FastAPI + Jinja2, zero JavaScript.
Avvio:  pip install -r requirements.txt
        uvicorn app:app --reload
Poi aprire http://127.0.0.1:8000
"""
import base64
import io

import matplotlib
matplotlib.use("Agg")          # backend senza finestre, adatto a un server
import matplotlib.pyplot as plt
import numpy as np
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# ------------------------------------------------------------------
# Qui andrebbe la chiamata al vostro server interno.
# Per l'esempio simuliamo dei dati.
# In pratica sarebbe qualcosa tipo:
#   r = httpx.post("http://server-interno:9000/misura", json={...})
#   dati = r.json()
# ------------------------------------------------------------------
def chiama_server_interno(campione: str, e_min: float, e_max: float, n_punti: int):
    energia = np.linspace(e_min, e_max, n_punti)
    picco = 0.5 * (e_min + e_max)
    rng = np.random.default_rng(0)
    conteggi = 1000 * np.exp(-((energia - picco) ** 2) / 2.0) + rng.poisson(20, n_punti)
    return energia, conteggi


def grafico_png_base64(x, y, titolo: str) -> str:
    """Crea il grafico con matplotlib e lo restituisce come stringa base64,
    da mettere direttamente dentro <img src="data:image/png;base64,...">."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(x, y, marker="o", markersize=3, linewidth=1)
    ax.set_xlabel("Energia [keV]")
    ax.set_ylabel("Conteggi")
    ax.set_title(titolo)
    ax.grid(alpha=0.3)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


# Pagina 1: il form
@app.get("/", response_class=HTMLResponse)
def form(request: Request):
    return templates.TemplateResponse(request, "form.html", {"errore": None})


# Pagina 2: riceve il form, chiama il server, mostra risultati
@app.post("/risultati", response_class=HTMLResponse)
def risultati(
    request: Request,
    campione: str = Form(...),
    e_min: float = Form(...),
    e_max: float = Form(...),
    n_punti: int = Form(...),
    mostra_tabella: bool = Form(False),   # checkbox: assente se non spuntata
):
    if e_min >= e_max:
        return templates.TemplateResponse(
            request, "form.html",
            {"errore": "L'energia minima deve essere minore di quella massima."},
        )

    x, y = chiama_server_interno(campione, e_min, e_max, n_punti)

    contesto = {
        "campione": campione,
        "e_min": e_min,
        "e_max": e_max,
        "grafico": grafico_png_base64(x, y, f"Spettro — {campione}"),
        "righe": list(zip(x.round(2), y.round(1))) if mostra_tabella else None,
        "totale": int(y.sum()),
        "massimo": float(y.max()),
        "e_picco": float(x[y.argmax()]),
    }
    return templates.TemplateResponse(request, "risultati.html", contesto)
