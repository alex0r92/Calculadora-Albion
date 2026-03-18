import streamlit as st
import requests
import math

# --- 1. BASE DE DATOS MAESTRA ---
ALBION_DB = {
    "hierbas": {
        "T2_AGARIC": {"seed": "T2_FARM_AGARIC_SEED", "ret": 0.333},
        "T3_COMFREY": {"seed": "T3_FARM_COMFREY_SEED", "ret": 0.600},
        "T4_BURDOCK": {"seed": "T4_FARM_BURDOCK_SEED", "ret": 0.733},
        "T5_TEASEL": {"seed": "T5_FARM_TEASEL_SEED", "ret": 0.800},
        "T6_FOXGLOVE": {"seed": "T6_FARM_FOXGLOVE_SEED", "ret": 0.866},
        "T7_MULLEIN": {"seed": "T7_FARM_MULLEIN_SEED", "ret": 0.911},
        "T8_YARROW": {"seed": "T8_FARM_YARROW_SEED", "ret": 0.933}
    },
    "recetas": {
        "Curación Mayor (T6)": {"id": "T6_POTION_HEAL", "rama": "Curación", "foco": 1648, "mats": {"T6_FOXGLOVE": 72, "T3_EGG": 18, "T1_ALCOHOL": 18}},
        "Veneno Mayor (T8)": {"id": "T8_POTION_COOLDOWN", "rama": "Veneno", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T8_ALCOHOL": 18, "T6_MILK": 18}},
        "Resistencia Mayor (T7)": {"id": "T7_POTION_STONESKIN", "rama": "Resistencia", "foco": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Invisibilidad (T8)": {"id": "T8_POTION_INVIS_1", "rama": "Invisibilidad", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T8_ALCOHOL": 18, "T6_MILK": 18}},
        "Gigantismo Mayor (T7)": {"id": "T7_POTION_REVIVE", "rama": "Gigantismo", "foco": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Energía Mayor (T6)": {"id": "T6_POTION_ENERGY", "rama": "Energía", "foco": 1648, "mats": {"T6_FOXGLOVE": 72, "T3_EGG": 18, "T1_ALCOHOL": 18}},
        "Pegajosa (T6)": {"id": "T6_POTION_STICKY", "rama": "Pegajosa", "foco": 1648, "mats": {"T6_FOXGLOVE": 24, "T5_TEASEL": 12, "T3_EGG": 6}}
    },
    "ramas": ["Curación", "Energía", "Gigantismo", "Resistencia", "Pegajosa", "Invisibilidad", "Veneno", "Limpieza", "Ácido", "Calmante", "Recolección", "Fuego Infernal", "Berserker", "Tornado", "Destilados"],
    "bonos": {"Lymhurst": ["T4_BURDOCK"], "Martlock": ["T6_FOXGLOVE"], "Thetford": ["T7_MULLEIN", "T2_AGARIC"]}
}

@st.cache_data(ttl=60)
def get_p(ids):
    ciu = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(ids)}?locations={ciu}&qualities=1"
    try:
        data = requests.get(url, timeout=10).json()
        res = {}
        for it in data:
            c, i = it['city'].replace(" ", "_"), it['item_id']
            if it['sell_price_min'] > 0:
                if i not in res: res[i] = {}
                res[i][c] = {"s": it['sell_price_min'], "b": it['buy_price_max']}
        return res
    except: return {}

st.set_page_config(page_title="Albion Master Terminal", layout="wide")
st.sidebar.header("Módulo 0: Perfil")
premium = st.sidebar.checkbox("Premium Activo", value=True)
tax_v = 0.04 if premium else 0.08
setup_fee = 0.025

spec_base = st.sidebar.slider("Rama General (Alquimia)", 0, 100, 100)
user_specs = {}
with st.sidebar.expander("Tus 15 Ramas de Especialización"):
    for rama in ALBION_DB["ramas"]:
        user_specs[rama] = st.slider(rama, 0, 100, 0 if rama != "Curación" else 100)

def calcular_foco(foco_base, rama_p):
    puntos = (spec_base * 30) + (user_specs.get(rama_p, 0) * 250)
    for r, lvl in user_specs.items():
        if r != rama_p: puntos += (lvl * 18)
    return foco_base * (0.5 ** (puntos / 10000))
with t1:
    st.header("Análisis de Rentabilidad Agrícola")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_c = st.selectbox("Ciudad de tu isla:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"])
    with c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Parcelas:", min_value=1, value=10)
    t_v_m = st.radio("Venta de cosecha:", ["Venta Directa", "Orden de Venta (+2.5%)"], horizontal=True)
    imp_t = tax_v + (0.025 if "Orden" in t_v_m else 0)

    if st.button("Ejecutar Análisis de Granja"):
        info = ALBION_DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            bono = 1.1 if hie_e in ALBION_DB["bonos"].get(ciu_c, []) else 1.0
            h_tot = parc * 9
            cosecha = math.floor(h_tot * 9 * bono)
            s_perd = math.ceil(h_tot * (1 - info["ret"]))
            m_h = pg.get(hie_e, {}); c_v_o = max(m_h, key=lambda k: m_h[k]['s']) if m_h else ciu_c
            p_v_o = m_h.get(c_v_o, {}).get('s', 0)
            m_s = pg.get(info["seed"], {}); c_c_o = min(m_s, key=lambda k: m_s[k]['s']) if m_s else ciu_c
            p_s_o = m_s.get(c_c_o, {}).get('s', 0)
            ing_n = (cosecha * p_v_o) * (1 - imp_t); cost_s = (s_perd * p_s_o)
            st.success(f"### Beneficio Neto: {ing_n - cost_s:,.0f} silver"); st.caption(f"🌱 Retorno: {info['ret']*100:.1f}% | Repones {s_perd} semillas.")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(f"Vender en {c_v_o}", f"{ing_n:,.0f} s")
                with st.expander("Ver mercados de venta"):
                    for c, d in m_h.items(): st.write(f"{c}: {d['s']} s")
            with col_b:
                st.metric(f"Semillas en {c_c_o}", f"-{cost_s:,.0f} s")
                with st.expander("Ver precios de semillas"):
                    for c, d in m_s.items(): st.write(f"{c}: {d['s']} s")
t1, t2, t3 = st.tabs(["🌱 1. Cultivos", "🧪 2. Alquimia Pro", "📈 3. Estrategia Cruzada"])
with t1:
    st.header("Análisis de Rentabilidad Agrícola")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_c = st.selectbox("Ciudad de tu isla:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"])
    with c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Parcelas:", min_value=1, value=10)
    t_v_m = st.radio("Venta de cosecha:", ["Venta Directa", "Orden de Venta (+2.5%)"], horizontal=True)
    imp_t = tax_v + (0.025 if "Orden" in t_v_m else 0)

    if st.button("Ejecutar Análisis de Granja"):
        info = ALBION_DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            bono = 1.1 if hie_e in ALBION_DB["bonos"].get(ciu_c, []) else 1.0
            h_tot = parc * 9
            cosecha = math.floor(h_tot * 9 * bono)
            s_perd = math.ceil(h_tot * (1 - info["ret"]))
            m_h = pg.get(hie_e, {}); c_v_o = max(m_h, key=lambda k: m_h[k]['s']) if m_h else ciu_c
            p_v_o = m_h.get(c_v_o, {}).get('s', 0)
            m_s = pg.get(info["seed"], {}); c_c_o = min(m_s, key=lambda k: m_s[k]['s']) if m_s else ciu_c
            p_s_o = m_s.get(c_c_o, {}).get('s', 0)
            ing_n = (cosecha * p_v_o) * (1 - imp_t); cost_s = (s_perd * p_s_o)
            st.success(f"### Beneficio Neto: {ing_n - cost_s:,.0f} silver"); st.caption(f"🌱 Retorno: {info['ret']*100:.1f}% | Repones {s_perd} semillas.")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(f"Vender en {c_v_o}", f"{ing_n:,.0f} s")
                with st.expander("Ver mercados de venta"):
                    for c, d in m_h.items(): st.write(f"{c}: {d['s']} s")
            with col_b:
                st.metric(f"Semillas en {c_c_o}", f"-{cost_s:,.0f} s")
                with st.expander("Ver precios de semillas"):
                    for c, d in m_s.items(): st.write(f"{c}: {d['s']} s")
                        with t2:
    st.header("🧪 Calculadora de Alquimia Avanzada")
    p_sel = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()))
    rec = ALBION_DB["recetas"][p_sel]
    col_alq_a, col_alq_b = st.columns([2, 1])
    with col_alq_b:
        tasa_nutri = st.number_input("Tasa Nutrición Tienda:", value=400)
        incluir_orden = st.checkbox("Tasa Orden Venta (2.5%)", value=True)
        cant_crafteo = st.number_input("Cantidad pociones:", min_value=5, step=5, value=100)
        usar_foco = st.checkbox("Usar Foco en Crafteo", value=True)

    pg_alq = get_p([rec["id"]] + list(rec["mats"].keys()))
    with col_alq_a:
        coste_mats_total = 0; rrr = 0.482 if usar_foco else 0.248; crafteos = math.ceil(cant_crafteo / 5)
        for m, qb in rec["mats"].items():
            m_p = pg_alq.get(m, {})
            cb = min(m_p, key=lambda x: m_p[x]['s']) if m_p else "N/A"
            ps = m_p.get(cb, {}).get('s', 0)
            p_in = st.number_input(f"Precio {m} (API: {ps} en {cb})", value=int(ps), key=f"m_{m}")
            qr = math.ceil((qb * crafteos) * (1 - rrr))
            coste_mats_total += (qr * p_in)
            with st.expander(f"Precios de {m} en Albion"):
                for ciu, dat in m_p.items(): st.write(f"{ciu}: {dat['s']} s")
        pv_api = pg_alq.get(rec["id"], {}).get("Brecilien", {}).get("s", 0)
        pv_man = st.number_input(f"Precio Venta (API Brecilien: {pv_api})", value=int(pv_api))
        beneficio = (cant_crafteo * pv_man * (1 - (tax_v + (0.025 if incluir_orden else 0)))) - coste_mats_total
        st.success(f"### Beneficio Neto: {beneficio:,.0f} silver")
        if usar_foco:
            st.info(f"Foco total estimado: {calcular_foco(rec['foco'], rec['rama']) * crafteos:,.0f}")
            with t3:
    st.header("📈 Estrategia Cruzada")
    mats_pocion = rec["mats"]
    ingredientes_producibles = [m for m in mats_pocion.keys() if m in ALBION_DB["hierbas"]]
    check_mats = {}
    st.write("¿Qué ingredientes produces en tu granja?")
    for mat in ingredientes_producibles:
        check_mats[mat] = st.checkbox(f"Produzco mi propio {mat}", value=False)
    
    if st.button("Calcular Ahorro Real"):
        ahorro_total = 0
        for mat, es_propio in check_mats.items():
            if es_propio:
                p_mercado = pg_alq.get(mat, {}).get("Brecilien", {}).get("s", 0)
                # Ahorro neto aproximado por unidad (Precio mercado - coste semilla estimado)
                ahorro_unid = p_mercado * 0.4 
                unidades = math.ceil((mats_pocion[mat] * crafteos) * (1 - rrr))
                ahorro_total += (unidades * ahorro_unid)
        st.write(f"Utilizando tus propios ingredientes ahorras: **{ahorro_total:,.0f} silver**")
        st.caption("Nota: Este cálculo descuenta el coste de oportunidad (lo que dejarías de ganar si vendieras la planta directamente).")
