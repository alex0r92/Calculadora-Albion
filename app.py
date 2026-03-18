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
        "Curación (T2/T4/T6)": {"id": "T6_POTION_HEAL", "rama": "Curación", "foco": 1648, "mats": {"T6_FOXGLOVE": 72, "T3_EGG": 18, "T1_ALCOHOL": 18}},
        "Veneno (T4/T6/T8)": {"id": "T8_POTION_COOLDOWN", "rama": "Veneno", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T8_ALCOHOL": 18, "T6_MILK": 18}},
        "Resistencia (T3/T5/T7)": {"id": "T7_POTION_STONESKIN", "rama": "Resistencia", "foco": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Berserker/Ácido (T8)": {"id": "T8_POTION_BERSERK", "rama": "Berserker", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}}
    },
    "esencias": {1: "ARCANEM_EXTRACT_LOW", 2: "ARCANEM_EXTRACT_MEDIUM", 3: "ARCANEM_EXTRACT_HIGH"},
    "ramas": ["Curación", "Energía", "Gigantismo", "Resistencia", "Pegajosa", "Invisibilidad", "Veneno", "Ácido", "Berserker", "Fuego Infernal", "Tornado"],
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

st.set_page_config(page_title="Albion Terminal", layout="wide")
st.sidebar.header("Perfil de Alquimista")
premium = st.sidebar.checkbox("Premium", value=True)
tax_v, setup_fee = (0.04 if premium else 0.08), 0.025
spec_base = st.sidebar.slider("Nivel Alquimia", 0, 100, 100)
u_specs = {r: st.sidebar.slider(r, 0, 100, 0) for r in ALBION_DB["ramas"]}

def calcular_foco(f_base, rama_p):
    pts = (spec_base * 30) + (u_specs.get(rama_p, 0) * 250)
    for r, lvl in u_specs.items():
        if r != rama_p: pts += (lvl * 18)
    return f_base * (0.5 ** (pts / 10000))

t1, t2, t3 = st.tabs(["🌱 Cultivos", "🧪 Alquimia", "📈 Logística"])
with t1:
    st.header("Análisis de Granja")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_c = st.selectbox("Isla en:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"])
    with c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Parcelas:", min_value=1, value=10)
    
    if st.button("🔍 Escanear Mercados"):
        info = ALBION_DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            bono = 1.1 if hie_e in ALBION_DB["bonos"].get(ciu_c, []) else 1.0
            h_tot = parc * 9
            cos_est = math.floor(h_tot * 9 * bono)
            s_perd = math.ceil(h_tot * (1 - info["ret"]))
            
            m_h = pg.get(hie_e, {}); c_v = max(m_h, key=lambda k: m_h[k]['s']) if m_h else ciu_c
            m_s = pg.get(info["seed"], {}); c_s = min(m_s, key=lambda k: m_s[k]['s']) if m_s else ciu_c
            
            neto = (cos_est * m_h.get(c_v, {}).get('s', 0) * (1-tax_v-setup_fee)) - (s_perd * m_s.get(c_s, {}).get('s', 0))
            
            if bono > 1: st.success(f"✅ Bono Activo en {ciu_c}")
            st.metric("Beneficio Neto (Tras Reposición)", f"{neto:,.0f} silver")
            st.write(f"🛒 **Compra semillas en:** {c_s} | 📍 **Vende hierba en:** {c_v}")

with t2:
    st.header("Calculadora de Alquimia")
    p_sel = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()))
    e_sel = st.selectbox("Encantamiento:", [0, 1, 2, 3])
    rec = ALBION_DB["recetas"][p_sel]
    cant = st.number_input("Cantidad:", min_value=5, step=5, value=100)
    foco = st.checkbox("Usar Foco", value=True)
    
    pg_a = get_p([rec["id"]] + list(rec["mats"].keys()))
    if pg_a:
        coste_m = 0; rrr = 0.482 if foco else 0.248; cic = math.ceil(cant / 5)
        for m, qb in rec["mats"].items():
            ps = pg_a.get(m, {}).get("Brecilien", {}).get("s", 0)
            p_in = st.number_input(f"Precio {m}", value=int(ps), key=f"al_{m}")
            coste_m += (math.ceil((qb * cic) * (1 - rrr)) * p_in)
        
        pv = st.number_input("Precio Venta Brecilien", value=int(pg_a.get(rec["id"], {}).get("Brecilien", {}).get("s", 0)))
        st.success(f"Beneficio Neto: {(cant * pv * (1-tax_v-setup_fee)) - coste_m:,.0f} silver")

with t3:
    st.header("Logística Cruzada")
    st.write("Compara si te sale más rentable vender la planta o usarla en la poción.")
    if st.button("Calcular Diferencial"):
        st.write("Analizando costes de oportunidad...")
