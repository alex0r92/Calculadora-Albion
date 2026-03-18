import streamlit as st
import requests
import math

# --- 1. BASE DE DATOS MAESTRA (TODOS LOS TIERS) ---
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
        # Curación (Pares)
        "Curación Menor (T2)": {"id": "T2_POTION_HEAL", "rama": "Curación", "foco": 154, "mats": {"T2_AGARIC": 12}},
        "Curación (T4)": {"id": "T4_POTION_HEAL", "rama": "Curación", "foco": 464, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Curación Mayor (T6)": {"id": "T6_POTION_HEAL", "rama": "Curación", "foco": 1648, "mats": {"T6_FOXGLOVE": 72, "T3_EGG": 18, "T1_ALCOHOL": 18}},
        # Energía (Pares)
        "Energía Menor (T2)": {"id": "T2_POTION_ENERGY", "rama": "Energía", "foco": 154, "mats": {"T2_AGARIC": 12}},
        "Energía (T4)": {"id": "T4_POTION_ENERGY", "rama": "Energía", "foco": 464, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Energía Mayor (T6)": {"id": "T6_POTION_ENERGY", "rama": "Energía", "foco": 1648, "mats": {"T6_FOXGLOVE": 72, "T3_EGG": 18, "T1_ALCOHOL": 18}},
        # Veneno (Pares + T8)
        "Veneno (T4)": {"id": "T4_POTION_COOLDOWN", "rama": "Veneno", "foco": 464, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Veneno Mayor (T6)": {"id": "T6_POTION_COOLDOWN", "rama": "Veneno", "foco": 1648, "mats": {"T6_FOXGLOVE": 24, "T5_TEASEL": 12, "T3_EGG": 6}},
        "Veneno T8": {"id": "T8_POTION_COOLDOWN", "rama": "Veneno", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T8_ALCOHOL": 18, "T6_MILK": 18}},
        # Resistencia (Impares)
        "Resistencia Menor (T3)": {"id": "T3_POTION_STONESKIN", "rama": "Resistencia", "foco": 234, "mats": {"T3_COMFREY": 24}},
        "Resistencia (T5)": {"id": "T5_POTION_STONESKIN", "rama": "Resistencia", "foco": 834, "mats": {"T5_TEASEL": 24, "T3_COMFREY": 12}},
        "Resistencia Mayor (T7)": {"id": "T7_POTION_STONESKIN", "rama": "Resistencia", "foco": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        # Rastreos T8
        "Berserker (T8)": {"id": "T8_POTION_BERSERK", "rama": "Berserker", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}},
        "Ácido (T8)": {"id": "T8_POTION_ACID", "rama": "Ácido", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}}
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

st.set_page_config(page_title="Terminal Alquimia", layout="wide")
st.sidebar.header("Tus Specs")
premium = st.sidebar.checkbox("Premium", value=True)
tax_v, s_fee = (0.04 if premium else 0.08), 0.025
spec_base = st.sidebar.slider("Nivel Alquimia", 0, 100, 100)
u_specs = {r: st.sidebar.slider(r, 0, 100, 0) for r in ALBION_DB["ramas"]}

def calcular_foco(f_base, rama_p):
    pts = (spec_base * 30) + (u_specs.get(rama_p, 0) * 250)
    for r, lvl in u_specs.items():
        if r != rama_p: pts += (lvl * 18)
    return f_base * (0.5 ** (pts / 10000))

t1, t2, t3 = st.tabs(["🌱 Granja", "🧪 Alquimia Pro", "📈 Estrategia"])
with t1:
    st.header("Gestión de Cultivos")
    # (Aquí iría el código de la Pestaña 1 que ya tienes, puedes pegarlo o dejarlo para después)

with t2:
    st.header("Escáner de Alquimia con Optimización de Compra")
    p_sel = st.selectbox("Poción a Fabricar:", list(ALBION_DB["recetas"].keys()))
    e_sel = st.selectbox("Encantamiento:", [0, 1, 2, 3])
    rec = ALBION_DB["recetas"][p_sel]
    
    col1, col2 = st.columns([2, 1])
    with col2:
        cant = st.number_input("Cantidad pociones:", min_value=5, step=5, value=100)
        foco = st.checkbox("Usar Foco", value=True)
        t_nutri = st.number_input("Nutrición Tienda:", value=400)

    # Lógica de IDs (Poción + Encanto + Mats)
    id_f = f"{rec['id']}@{e_sel}" if e_sel > 0 else rec['id']
    ids_pedir = [id_f] + list(rec["mats"].keys())
    if e_sel > 0: 
        tier_p = rec["id"][1:2]
        id_esc = f"T{tier_p}_{ALBION_DB['esencias'][e_sel]}"
        ids_pedir.append(id_esc)

    pg = get_p(ids_pedir)
    
    with col1:
        st.subheader("🛒 Dónde comprar ingredientes:")
        coste_mats = 0
        rrr = 0.482 if foco else 0.248
        ciclos = math.ceil(cant / 5)

        for m, qb in rec["mats"].items():
            m_precios = pg.get(m, {})
            c_opt = min(m_precios, key=lambda x: m_precios[x]['s']) if m_precios else "N/A"
            p_opt = m_precios.get(c_opt, {}).get('s', 0)
            
            p_in = st.number_input(f"Precio {m} (Mejor: {p_opt} en {c_opt})", value=int(p_opt), key=f"m_{m}")
            qr = math.ceil((qb * ciclos) * (1 - rrr))
            coste_mats += (qr * p_in)
            
            with st.expander(f"Precios de {m} en Albion"):
                for ciu, d in m_precios.items():
                    st.write(f"**{ciu}**: {d['s']} s")

        st.divider()
        pv_api = pg.get(id_f, {}).get("Brecilien", {}).get("s", 0)
        pv_man = st.number_input(f"Precio Venta en Brecilien (API: {pv_api})", value=int(pv_api))
        
        beneficio = (cant * pv_man * (1 - tax_v - s_fee)) - coste_mats
        st.success(f"### Beneficio Neto: {beneficio:,.0f} silver")
        if foco: st.info(f"Foco necesario: {calcular_foco(rec['foco'], rec['rama']) * ciclos:,.0f}")

with t3:
    st.write("Módulo de Estrategia Cruzada cargado.")
