# Generador de UTMs — Hofmann

Aplicación **Streamlit** para construir y normalizar las UTMs de las campañas
de Hofmann, de modo que la atribución llegue consistente a HubSpot y GA4.

## Despliegue

| | |
|---|---|
| **Repositorio** | `WeRise-ESP/utms-hofmann` (rama `main`) |
| **App en producción** | https://utms-hofmann.streamlit.app |
| **Main file path** | `app.py` |

**Actualizar la app = hacer `git push` a `main`.** Streamlit Cloud redespliega solo.

## Credenciales

La app está protegida por contraseña vía `st.secrets["auth"]["password"]`, que
se configura en **App settings → Secrets** del panel de Streamlit.

> ⚠️ **Nunca subas credenciales al repositorio.** El `.gitignore` excluye
> `*.json`, `.env` y `.streamlit/secrets.toml`. En la carpeta superior de este
> proyecto hay una **clave privada de service account de Google Cloud**
> (`utms-hofmann-*.json`) que debe permanecer siempre fuera del control de
> versiones.

## Local

```bash
pip install -r requirements.txt
streamlit run app.py
```
