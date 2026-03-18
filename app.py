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
        "Curación Menor (T2)": {"id": "T2_POTION_HEAL", "rama": "Curación", "foco": 154, "mats": {"T2_AGARIC": 12}},
        "Curación (T4)": {"id": "T4_POTION_HEAL", "rama": "Curación", "foco": 464, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Curación Mayor (T6)": {"id": "T6_POTION_HEAL", "rama": "Curación", "foco": 1648, "mats": {"T6_FOXGLOVE": 72, "T3_EGG": 18, "T1_ALCOHOL": 18}},
        "Energía Menor (T2)": {"id": "T2_POTION_ENERGY", "rama": "Energía", "foco": 154, "mats": {"T2_AGARIC": 12}},
        "Energía (T4)": {"id": "T4_POTION_ENERGY", "rama": "Energía", "foco": 464, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Energía Mayor (T6)": {"id": "T6_POTION_ENERGY", "rama": "Energía", "foco": 1648, "mats": {"T6_FOXGLOVE": 72, "T3_EGG": 18, "T1_ALCOHOL": 18}},
        "Veneno (T4)": {"id": "T4_POTION_COOLDOWN", "rama": "Veneno", "foco": 464, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Veneno Mayor (T6)": {"id": "T6_POTION_COOLDOWN", "rama": "Veneno", "foco": 1648, "mats": {"T6_FOXGLOVE": 24, "T5_TEASEL": 12, "T3_EGG": 6}},
        "Veneno (T8)": {"id": "T8_POTION_COOLDOWN", "rama": "Veneno", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T8_ALCOHOL": 18, "T6_MILK": 18}},
        "Resistencia Menor (T3)": {"id": "T3_POTION_STONESKIN", "rama": "Resistencia", "foco": 234, "mats": {"T3_COMFREY": 24}},
        "Resistencia (T5)": {"id": "T5_POTION_STONESKIN", "rama": "Resistencia", "foco": 834, "mats": {"T5_TEASEL": 24, "T3_COMFREY": 12}},
        "Resistencia Mayor (T7)": {"id": "T7_POTION_STONESKIN", "rama": "Resistencia", "foco": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Gigantismo (T3)": {"id": "T3_POTION_REVIVE", "rama": "Gigantismo", "foco": 234, "mats": {"T3_COMFREY": 24}},
        "Gigantismo Mayor (T7)": {"id": "T7_POTION_REVIVE", "rama": "Gigantismo", "foco": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Invisibilidad (T8)": {"id": "T8_POTION_INVIS_1", "rama": "Invisibilidad", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCOHOL": 18}},
        "Ácido (T8)": {"id": "T8_POTION_ACID", "rama": "Ácido", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}},
        "Berserker (T8)": {"id": "T8_POTION_BERSERK", "rama": "Berserker", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}},
        "Fuego Infernal (T8)": {"id": "T8_POTION_HELL", "rama": "Fuego Infernal", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}},
        "Tornado (T8)": {"id": "T8_POTION_TORNADO", "rama": "Tornado", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}}
    },
    "esencias": {1: "ARCANEM_EXTRACT_LOW", 2: "ARCANEM_EXTRACT_MEDIUM", 3: "ARCANEM_EXTRACT_HIGH"},
    "ramas": ["Curación", "Energía", "Gigantismo", "Resistencia", "Pegajosa", "Invisibilidad", "Veneno", "Limpieza", "Ácido", "Calmante", "Recolección", "Fuego Infernal", "Berserker", "Tornado", "Destilados"],
    "bonos": {"Lymhurst": ["T4_BURDOCK"], "Martlock": ["T6_FOXGLOVE"], "Thetford": ["T7_MULLEIN", "T2_AGARIC"]}
}

@st.cache_data(ttl=60)
def get_p(ids):
    c = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(ids)}?locations={c}&qualities=1"
    try:
        data = requests.get(url, timeout=10).json()
        res = {}
        for it in data:
            ciu, item = it['city'].replace(" ", "_"), it['item_id']
            if it['sell_price_min'] > 0:
                if item not in res: res[item] = {}
                res[item][ciu] = {"s": it['sell_price_min'], "b": it['buy_price_max']}
        return res
    except: return {}

# --- INTERFAZ ---
st.set_page_config(page_title="Albion Terminal", layout="wide")
st.sidebar.header("Tus Specs (0-100)")
premium = st.sidebar.checkbox("Premium", value=True)
tax_v, s_fee = (0.04 if premium else 0.08), 0.025
spec_base = st.sidebar.slider("Nivel Alquimia General", 0, 100, 100)
u_specs = {r: st.sidebar.slider(r, 0, 100, 0 if r != "Curación" else 100) for r in ALBION_DB["ramas"]}

def calcular_foco(f_base, rama_p):
    pts = (spec_base * 30) + (u_specs.get(rama_p, 0) * 250)
    for r, lvl in u_specs.items():
        if r != rama_p: pts += (lvl * 18)
    return f_base * (0.5 ** (pts / 10000))

t1, t2, t3 = st.tabs(["🌱 1. Cultivos", "🧪 2. Alquimia Pro", "📈 3. Estrategia"])

with t1:
    st.header("Análisis de Granja")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_c = st.selectbox("Isla en:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"])
    with c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Parcelas:", min_value=1, value=10)
    if st.button("Ejecutar Análisis Granja"):
        info = ALBION_DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            bono = 1.1 if hie_e in ALBION_DB["bonos"].get(ciu_c, []) else 1.0
            h_tot = parc * 9
            cos_est = math.floor(h_tot * 9 * bono)
            s_perd = math.ceil(h_tot * (1 - info["ret"]))
            m_h = pg.get(hie_e, {}); cv_o = max(m_h, key=lambda k: m_h[k]['s']) if m_h else ciu_c
            m_s = pg.get(info["seed"], {}); cc_o = min(m_s, key=lambda k: m_s[k]['s']) if m_s else ciu_c
            ing = (cos_est * m_h.get(cv_o, {}).get('s', 0)) * (1-tax_v-s_fee)
            cst = s_perd * m_s.get(cc_o, {}).get('s', 0)
            st.success(f"Beneficio Diario: {ing - cst:,.0f} s | Vende en: {cv_o} | Semillas en: {cc_o}")
            st.info(f"Retorno: {info['ret']*100:.1f}% | Repones {s_perd} semillas.")

with t2:
    st.header("Escáner de Alquimia Pro")
    p_sel = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()))
    e_sel = st.selectbox("Encantamiento:", [0, 1, 2, 3])
    rec = ALBION_DB["recetas"][p_sel]
    col_a, col_b = st.columns([2, 1])
    with col_b:
        cant = st.number_input("Cantidad:", min_value=5, step=5, value=100)
        f_check = st.checkbox("Usar Foco", value=True)
        nutri = st.number_input("Tasa Nutrición:", value=400)
    
    id_f = f"{rec['id']}@{e_sel}" if e_sel > 0 else rec['id']
    ids_pedir = [id_f] + list(rec["mats"].keys())
    if e_sel > 0: ids_pedir.append(f"T{rec['id'][1:2]}_{ALBION_DB['esencias'][e_sel]}")
    pg_alq = get_p(ids_pedir)
    
    with col_a:
        coste_mats = 0; rrr = 0.482 if f_check else 0.248; cic = math.ceil(cant / 5)
        for m, qb in rec["mats"].items():
            m_p = pg_alq.get(m, {})
            cb = min(m_p, key=lambda x: m_p[x]['s']) if m_p else "N/A"
            ps = m_p.get(cb, {}).get('s', 0)
            p_in = st.number_input(f"Precio {m} (Mejor: {ps} en {cb})", value=int(ps), key=f"m_{m}")
            qr = math.ceil((qb * cic) * (1 - rrr))
            coste_mats += (qr * p_in)
            with st.expander(f"Ver ciudades para {m}"): st.write(m_p)
        
        pv_api = pg_alq.get(id_f, {}).get("Brecilien", {}).get("s", 0)
        pv_man = st.number_input(f"Venta en Brecilien (API: {pv_api})", value=int(pv_api))
        benef = (cant * pv_man * (1 - tax_v - s_fee)) - (coste_mats + (nutri * cic))
        st.success(f"Beneficio Neto: {benef:,.0f} silver")
        if f_check: st.info(f"Foco total: {calcular_foco(rec['foco'], rec['rama']) * cic:,.0f} pts")

with t3:
    st.header("Logística Cruzada")
    mats_c = [m for m in rec["mats"].keys() if m in ALBION_DB["hierbas"]]
    checks = {m: st.checkbox(f"Produzco mi propio {m}", value=False) for m in mats_c}
    if st.button("Calcular Diferencial"):
        ahorro = sum([(math.ceil((rec["mats"][m]*cic)*(1-rrr)) * pg_alq.get(m, {}).get("Brecilien", {}).get("s", 0) * 0.4) for m, v in checks.items() if v])
        st.write(f"Ahorro estimado por producción propia: **{ahorro:,.0f} silver**")
