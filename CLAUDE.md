# Generador de UTMs — Hofmann

Contexto para trabajar en este proyecto. Léelo antes de tocar código.

## Qué es
App **Streamlit** para construir y normalizar las UTMs de las campañas de Hofmann,
de modo que la atribución llegue consistente a HubSpot y GA4.

- **Repo:** `WeRise-ESP/utms-hofmann` (rama `main`)
- **App:** https://utms-hofmann.streamlit.app
- **Entry point / main file:** `app.py`  (repo minimalista: solo `app.py` + `requirements.txt`)
- **Actualizar = `git push` a `main`** → Streamlit Cloud redespliega solo.

## Arrancar en local
```bash
pip install -r requirements.txt
streamlit run app.py
```
La app está protegida por contraseña vía `st.secrets["auth"]["password"]`, que se
configura en **App settings → Secrets** de Streamlit (NO está en git).

## ⚠️ Seguridad — clave de Google Cloud
En la carpeta superior de este proyecto (`SISTEMA UTMS/`) hay una **clave privada de
service account de Google Cloud** (`utms-hofmann-*.json`). **NUNCA la subas** a ningún
repositorio. El `.gitignore` ya excluye `*.json`, `.env` y `secrets.toml` — no lo
relajes.
