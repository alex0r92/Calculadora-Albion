import streamlit as st
import requests
import math

# --- 1. BASE DE DATOS Y MOTOR API ---
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
        "Ácido (T8)": {"id": "T8_POTION_ACID", "rama": "Ácido", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T6_MILK": 18}},
        "Berserker (T8)": {"id": "T8_POTION_BERSERK", "rama": "Berserker", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T6_MILK": 18}}
    },
    "ramas": ["Curación", "Energía", "Gigantismo", "Resistencia", "Pegajosa", "Invisibilidad", "Veneno", "Limpieza", "Ácido", "Calmante", "Recolección", "Fuego Infernal", "Berserker", "Tornado", "Destilados"],
    "bonos": {"Lymhurst": ["T4_BURDOCK"], "Martlock": ["T6_FOXGLOVE"], "Thetford": ["T7_MULLEIN", "T2_AGARIC"]}
}

@st.cache_data(ttl=60)
def get_p(ids):
    c_list = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(ids)}?locations={c_list}&qualities=1"
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

# --- 2. CONFIGURACIÓN SIDEBAR (PERFIL) ---
st.set_page_config(page_title="Albion Master Terminal", layout="wide")
st.sidebar.header("Módulo 0: Perfil")
premium = st.sidebar.checkbox("Premium Activo", value=True)
tax_v = 0.04 if premium else 0.08
setup_fee = 0.025
spec_base = st.sidebar.slider("Rama General (Alquimia)", 0, 100, 100)
user_specs = {r: st.sidebar.slider(r, 0, 100, 0 if r != "Curación" else 100) for r in ALBION_DB["ramas"]}

def calcular_foco(f_base, rama_p):
    pts = (spec_base * 30) + (user_specs.get(rama_p, 0) * 250)
    for r, lvl in user_specs.items():
        if r != rama_p: pts += (lvl * 18)
    return f_base * (0.5 ** (pts / 10000))

t1, t2, t3 = st.tabs(["🌱 1. Cultivos", "🧪 2. Alquimia Pro", "📈 3. Estrategia Cruzada"])

# --- MODULO 1: CULTIVOS ---
with t1:
    st.header("Análisis de Granja")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_c = st.selectbox("Ciudad Isla:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"])
    with c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Parcelas:", min_value=1, value=10)
    
    if st.button("Ejecutar Análisis"):
        info = ALBION_DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            bono = 1.1 if hie_e in ALBION_DB["bonos"].get(ciu_c, []) else 1.0
            h_tot = parc * 9
            cos_est = math.floor(h_tot * 9 * bono)
            s_perd = math.ceil(h_tot * (1 - info["ret"]))
            m_h = pg.get(hie_e, {}); cv_o = max(m_h, key=lambda k: m_h[k]['s']) if m_h else ciu_c
            m_s = pg.get(info["seed"], {}); cc_o = min(m_s, key=lambda k: m_s[k]['s']) if m_s else ciu_c
            ing = (cos_est * m_h.get(cv_o, {}).get('s', 0)) * (1-tax_v-setup_fee)
            cst = s_perd * m_s.get(cc_o, {}).get('s', 0)
            st.success(f"Beneficio Diario: {ing - cst:,.0f} s")
            st.info(f"Retorno: {info['ret']*100:.1f}% | Repones {s_perd} semillas.")
            with st.expander("Ver mercados"): st.write(m_h)

# --- MODULO 2: ALQUIMIA PRO ---
with t2:
    st.header("Calculadora Avanzada")
    p_sel = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()))
    rec = ALBION_DB["recetas"][p_sel]
    cant = st.number_input("Pociones totales:", min_value=5, step=5, value=100)
    foco = st.checkbox("Usar Foco", value=True)
    pg_alq = get_p([rec["id"]] + list(rec["mats"].keys()))
    
    if pg_alq:
        coste_mats = 0
        rrr = 0.482 if foco else 0.248
        crafteos = math.ceil(cant / 5)
        st.subheader("Entrada Manual de Precios")
        for m, qb in rec["mats"].items():
            m_p = pg_alq.get(m, {})
            cb = min(m_p, key=lambda x: m_p[x]['s']) if m_p else "N/A"
            ps = m_p.get(cb, {}).get('s', 0)
            p_in = st.number_input(f"{m} (Mejor: {ps} en {cb})", value=int(ps), key=f"m_{m}")
            qr = math.ceil((qb * crafteos) * (1 - rrr))
            coste_mats += (qr * p_in)
        
        pv_api = pg_alq.get(rec["id"], {}).get("Brecilien", {}).get("s", 0)
        pv_man = st.number_input(f"Precio Venta Poción (API Brecilien: {pv_api})", value=int(pv_api))
        benef = (cant * pv_man * (1 - tax_v - setup_fee)) - coste_mats
        st.success(f"Beneficio Neto: {benef:,.0f} s")
        if foco: st.info(f"Foco total: {calcular_foco(rec['foco'], rec['rama']) * crafteos:,.0f} pts")

# --- MODULO 3: ESTRATEGIA ---
with t3:
    st.header("📈 Logística Cruzada")
    st.write("¿Qué ingredientes produces tú mismo?")
    ing_p = [m for m in rec["mats"].keys() if m in ALBION_DB["hierbas"]]
    check_mats = {m: st.checkbox(f"Tengo granja de {m}", value=False) for m in ing_p}
    if st.button("Analizar Ahorro"):
        ahorro = 0
        for mat, es_propio in check_mats.items():
            if es_propio:
                p_m = pg_alq.get(mat, {}).get("Brecilien", {}).get("s", 0)
                ahorro += (math.ceil((rec["mats"][mat]*crafteos)*(1-rrr)) * p_m * 0.4)
        st.write(f"Ahorro estimado por producción propia: **{ahorro:,.0f} silver**")
