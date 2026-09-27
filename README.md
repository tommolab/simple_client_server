# simple_client_server

Esempio minimo di web app **senza JavaScript**: FastAPI + Jinja2 + matplotlib.

Il browser invia un normale form HTML, il server chiama (in questo esempio, simula) un
servizio interno, genera un grafico con matplotlib e restituisce una pagina HTML con
l'immagine incorporata in base64 e, se richiesto, una tabella dei dati.

## Struttura

```
app.py              # applicazione FastAPI (rotte, simulazione dati, grafico)
templates/
  base.html         # layout comune
  form.html         # pagina 1: form di input
  risultati.html    # pagina 2: grafico e tabella
requirements.txt
```

## Avvio

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app:app --reload
```

Poi aprire <http://127.0.0.1:8000>.

## Collegare un server reale

La funzione `chiama_server_interno` in `app.py` genera dati finti. Per usare un servizio
vero basta sostituirla con una chiamata HTTP, ad esempio:

```python
r = httpx.post("http://server-interno:9000/misura", json={...})
dati = r.json()
```

## Autenticazione / SSO

L'app non gestisce l'autenticazione. Per aggiungere il SSO si può mettere davanti un
reverse proxy come [Caddy](https://caddyserver.com/) (con un plugin di autenticazione,
es. OIDC/forward auth) oppure affidarsi a un servizio di terze parti.
