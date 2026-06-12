# =============================================================
#  Sistema de UTMs — Escuela Hofmann  (versión online multiusuario)
#  Streamlit + Google Sheets como base de datos compartida
# =============================================================
import re
import unicodedata
from datetime import date, datetime
from urllib.parse import quote

import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Sistema de UTMs · Escuela Hofmann",
                   page_icon="🔗", layout="wide")

# ---------- estilos ----------
st.markdown("""
<style>
  .titulo{background:#1b2a4a;color:#fff;padding:18px 26px;border-radius:10px;margin-bottom:6px;}
  .titulo h1{font-size:1.4rem;margin:0;}
  .titulo span{color:#c9a227;}
  .titulo small{opacity:.75;}
  div[data-testid="stMetricValue"]{color:#1b2a4a;}
</style>
<div class="titulo"><h1>Sistema de UTMs · <span>Escuela Hofmann</span></h1>
<small>Generador online multiusuario — el histórico se guarda en Google Sheets</small></div>
""", unsafe_allow_html=True)

# ---------- conexión a Google Sheets ----------
conn = st.connection("gsheets", type=GSheetsConnection)

COLS_HIST = ["fecha_creacion", "usuario", "fecha_campana", "utm_campaign",
             "utm_source", "utm_medium", "utm_content", "utm_term",
             "utm_id", "utm_creative_format", "url_final"]
FUENTES_DEF = ["google", "facebook", "instagram", "linkedin", "tiktok",
               "youtube", "x", "whatsapp", "newsletter", "referido"]
MEDIOS_DEF = ["cpc", "social", "organic", "email", "referral",
              "display", "banner", "video", "sms", "qr"]


def leer_hoja(ws: str, columnas: list) -> pd.DataFrame:
    """Lee una pestaña de la hoja; si no existe la crea vacía."""
    try:
        df = conn.read(worksheet=ws, ttl=0)
        df = df.dropna(how="all")
        for c in columnas:
            if c not in df.columns:
                df[c] = ""
        return df[columnas].fillna("").astype(str)
    except Exception:
        df = pd.DataFrame(columns=columnas)
        try:
            conn.create(worksheet=ws, data=df)
        except Exception:
            pass
        return df


def guardar_hoja(ws: str, df: pd.DataFrame):
    conn.update(worksheet=ws, data=df)


def leer_lista(ws: str, col: str, defaults: list) -> list:
    df = leer_hoja(ws, [col])
    valores = [v for v in df[col].tolist() if v]
    if not valores:                       # primera vez: sembrar valores por defecto
        guardar_hoja(ws, pd.DataFrame({col: defaults}))
        return defaults[:]
    return sorted(set(valores))


def normalizar(t: str) -> str:
    """minúsculas, sin acentos, espacios -> _, solo caracteres seguros"""
    t = str(t or "").strip().lower()
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"\s+", "_", t)
    t = re.sub(r"[^a-z0-9_\-\.]", "", t)
    return t


# ---------- cargar datos compartidos ----------
fuentes = leer_lista("fuentes", "fuente", FUENTES_DEF)
medios = leer_lista("medios", "medio", MEDIOS_DEF)
historial = leer_hoja("historial", COLS_HIST)

# ---------- pestañas ----------
tab_gen, tab_fuente, tab_informe, tab_config = st.tabs(
    ["🔗 Generador", "📋 Tablas por fuente", "📊 Informe", "⚙️ Fuentes y Medios"])

# =============================================================
#  GENERADOR
# =============================================================
with tab_gen:
    st.subheader("Crear nueva URL con UTMs")
    with st.form("form_utm", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            url_base = st.text_input("URL de destino *",
                                     placeholder="https://www.escuelahofmann.com/curso-seo")
            campana = st.text_input("Nombre de campaña * (utm_campaign)",
                                    placeholder="lanzamiento curso")
            fuente = st.selectbox("Fuente * (utm_source)", [""] + fuentes)
            termino = st.text_input("Término (utm_term — palabra clave)",
                                    placeholder="aprender seo")
            utm_id = st.text_input("ID de campaña (utm_id) — opcional",
                                   placeholder="camp_987")
        with c2:
            usuario = st.text_input("Tu nombre (quién crea la UTM)",
                                    placeholder="ej: maria")
            fecha_camp = st.date_input("Fecha de campaña *", value=date.today())
            medio = st.selectbox("Medio * (utm_medium)", [""] + medios)
            contenido = st.text_input("Contenido (utm_content — variante del anuncio)",
                                      placeholder="banner azul")
            formato = st.text_input("Formato creativo (utm_creative_format) — opcional",
                                    placeholder="image / video / carousel")

        enviado = st.form_submit_button("⚡ Generar y guardar UTM",
                                        type="primary", use_container_width=True)

    st.caption("Todo se convierte automáticamente a minúsculas, sin acentos y con "
               "guiones bajos. La fecha se añade al nombre de campaña "
               "(ej: **lanzamiento_curso_2026-06-12**).")

    if enviado:
        errores = []
        if not url_base.strip():
            errores.append("Falta la URL de destino.")
        if not normalizar(campana):
            errores.append("Falta el nombre de campaña.")
        if not fuente:
            errores.append("Elige una fuente.")
        if not medio:
            errores.append("Elige un medio.")
        if errores:
            for e in errores:
                st.error(e)
        else:
            url = url_base.strip()
            if not re.match(r"^https?://", url, re.I):
                url = "https://" + url
            camp_fecha = f"{normalizar(campana)}_{fecha_camp.isoformat()}"
            params = [("utm_source", fuente), ("utm_medium", medio),
                      ("utm_campaign", camp_fecha)]
            if normalizar(contenido):
                params.append(("utm_content", normalizar(contenido)))
            if normalizar(termino):
                params.append(("utm_term", normalizar(termino)))
            if normalizar(utm_id):
                params.append(("utm_id", normalizar(utm_id)))
            if normalizar(formato):
                params.append(("utm_creative_format", normalizar(formato)))

            sep = "&" if "?" in url else "?"
            url_final = url + sep + "&".join(f"{k}={quote(v)}" for k, v in params)

            fila = {"fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "usuario": normalizar(usuario) or "anonimo",
                    "fecha_campana": fecha_camp.isoformat(),
                    "utm_campaign": camp_fecha,
                    "utm_source": fuente, "utm_medium": medio,
                    "utm_content": normalizar(contenido),
                    "utm_term": normalizar(termino),
                    "utm_id": normalizar(utm_id),
                    "utm_creative_format": normalizar(formato),
                    "url_final": url_final}
            historial = pd.concat([pd.DataFrame([fila]), historial],
                                  ignore_index=True)
            guardar_hoja("historial", historial)

            st.success("✅ UTM generada y guardada en el histórico compartido")
            st.code(url_final, language=None)   # incluye botón de copiar

# =============================================================
#  TABLAS POR FUENTE
# =============================================================
with tab_fuente:
    st.subheader("UTMs creadas, separadas por fuente")
    if historial.empty:
        st.info("Aún no hay UTMs guardadas.")
    else:
        conteo = historial["utm_source"].value_counts()
        cols_metr = st.columns(min(len(conteo), 6))
        for i, (f, n) in enumerate(conteo.items()):
            cols_metr[i % len(cols_metr)].metric(f, int(n))
        st.divider()
        for f in conteo.index:
            df_f = historial[historial["utm_source"] == f]
            st.markdown(f"### 🔹 {f} &nbsp; <small>({len(df_f)} UTMs)</small>",
                        unsafe_allow_html=True)
            st.dataframe(
                df_f[["fecha_campana", "utm_campaign", "utm_medium",
                      "utm_content", "utm_term", "usuario", "url_final"]],
                use_container_width=True, hide_index=True,
                column_config={"url_final": st.column_config.LinkColumn("URL")})

# =============================================================
#  INFORME
# =============================================================
with tab_informe:
    st.subheader("Informe general")
    if historial.empty:
        st.info("Aún no hay UTMs guardadas.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("UTMs creadas", len(historial))
        m2.metric("Campañas distintas", historial["utm_campaign"].nunique())
        m3.metric("Usuarios", historial["usuario"].nunique())

        g1, g2 = st.columns(2)
        with g1:
            st.markdown("**UTMs por fuente**")
            st.bar_chart(historial["utm_source"].value_counts())
        with g2:
            st.markdown("**UTMs por medio**")
            st.bar_chart(historial["utm_medium"].value_counts())

        st.divider()
        f1, f2, f3 = st.columns(3)
        filtro_f = f1.selectbox("Filtrar por fuente",
                                ["— todas —"] + sorted(historial["utm_source"].unique()))
        filtro_m = f2.selectbox("Filtrar por medio",
                                ["— todos —"] + sorted(historial["utm_medium"].unique()))
        filtro_u = f3.selectbox("Filtrar por usuario",
                                ["— todos —"] + sorted(historial["usuario"].unique()))

        datos = historial.copy()
        if filtro_f != "— todas —":
            datos = datos[datos["utm_source"] == filtro_f]
        if filtro_m != "— todos —":
            datos = datos[datos["utm_medium"] == filtro_m]
        if filtro_u != "— todos —":
            datos = datos[datos["usuario"] == filtro_u]

        st.dataframe(datos, use_container_width=True, hide_index=True,
                     column_config={"url_final": st.column_config.LinkColumn("URL")})
        st.download_button("⬇ Exportar CSV",
                           datos.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"informe_utms_hofmann_{date.today()}.csv",
                           mime="text/csv")

# =============================================================
#  CONFIGURACIÓN
# =============================================================
with tab_config:
    st.subheader("Fuentes y medios predeterminados (compartidos por todo el equipo)")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Fuentes (utm_source)**")
        nueva_f = st.text_input("Nueva fuente", placeholder="ej: pinterest",
                                key="nf")
        if st.button("+ Agregar fuente"):
            v = normalizar(nueva_f)
            if not v:
                st.error("Escribe un valor válido.")
            elif v in fuentes:
                st.warning(f"Ya existe: {v}")
            else:
                fuentes.append(v)
                guardar_hoja("fuentes", pd.DataFrame({"fuente": sorted(fuentes)}))
                st.success(f"Agregada: {v}")
                st.rerun()
        elim_f = st.selectbox("Eliminar fuente", [""] + fuentes, key="ef")
        if st.button("🗑 Eliminar fuente") and elim_f:
            fuentes.remove(elim_f)
            guardar_hoja("fuentes", pd.DataFrame({"fuente": sorted(fuentes)}))
            st.rerun()
        st.write(" · ".join(f"`{f}`" for f in fuentes))

    with c2:
        st.markdown("**Medios (utm_medium)**")
        nuevo_m = st.text_input("Nuevo medio", placeholder="ej: push",
                                key="nm")
        if st.button("+ Agregar medio"):
            v = normalizar(nuevo_m)
            if not v:
                st.error("Escribe un valor válido.")
            elif v in medios:
                st.warning(f"Ya existe: {v}")
            else:
                medios.append(v)
                guardar_hoja("medios", pd.DataFrame({"medio": sorted(medios)}))
                st.success(f"Agregado: {v}")
                st.rerun()
        elim_m = st.selectbox("Eliminar medio", [""] + medios, key="em")
        if st.button("🗑 Eliminar medio") and elim_m:
            medios.remove(elim_m)
            guardar_hoja("medios", pd.DataFrame({"medio": sorted(medios)}))
            st.rerun()
        st.write(" · ".join(f"`{m}`" for m in medios))
