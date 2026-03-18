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
        "Veneno T8": {"id": "T8_POTION_COOLDOWN", "rama": "Veneno", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T8_ALCOHOL": 18, "T6_MILK": 18}},
        "Resistencia Menor (T3)": {"id": "T3_POTION_STONESKIN", "rama": "Resistencia", "foco": 234, "mats": {"T3_COMFREY": 24}},
        "Resistencia (T5)": {"id": "T5_POTION_STONESKIN", "rama": "Resistencia", "foco": 834, "mats": {"T5_TEASEL": 24, "T3_COMFREY": 12}},
        "Resistencia Mayor (T7)": {"id": "T7_POTION_STONESKIN", "rama": "Resistencia", "foco": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Gigantismo (T3)": {"id": "T3_POTION_REVIVE", "rama": "Gigantismo", "foco": 234, "mats": {"T3_COMFREY": 24}},
        "Gigantismo Mayor (T7)": {"id": "T7_POTION_REVIVE", "rama": "Gigantismo", "foco": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Invisibilidad (T8)": {"id": "T8_POTION_INVIS_1", "rama": "Invisibilidad", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCOHOL": 18}},
        "Berserker (T8)": {"id": "T8_POTION_BERSERK", "rama": "Berserker", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}},
        "Ácido (T8)": {"id": "T8_POTION_ACID", "rama": "Ácido", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}},
        "Fuego Infernal (T8)": {"id": "T8_POTION_HELL", "rama": "Fuego Infernal", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}},
        "Tornado (T8)": {"id": "T8_POTION_TORNADO", "rama": "Tornado", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}}
    },
    "esencias": {1: "ARCANEM_EXTRACT_LOW", 2: "ARCANEM_EXTRACT_MEDIUM", 3: "ARCANEM_EXTRACT_HIGH"},
    "ramas": ["Curación", "Energía", "Gigantismo", "Resistencia", "Pegajosa", "Invisibilidad", "Veneno", "Limpieza", "Ácido", "Calmante", "Recolección", "Fuego Infernal", "Berserker", "Tornado", "Destilados"],
    "bonos": {"Lymhurst": ["T4_BURDOCK"], "Martlock": ["T6_FOXGLOVE"], "Thetford": ["T7_MULLEIN", "T2_AGARIC"]}
}

# --- 2. MOTORES DE CONEXIÓN A LA API ---
@st.cache_data(ttl=60)
def get_p(ids):
    c = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(ids)}?locations={c}&qualities=1"
    try:
        data = requests.get(url, timeout=10).json()
        res = {}
        for it in data:
            ciu, item = it['city'].replace(" ", "_"), it['item_id']
            if it['sell_price_min'] > 0 or it['buy_price_max'] > 0:
                if item not in res: res[item] = {}
                res[item][ciu] = {"s": it['sell_price_min'], "b": it['buy_price_max']}
        return res
    except: return {}

@st.cache_data(ttl=300)
def get_h(item_id):
    c = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/history/{item_id}?locations={c}&time-scale=24"
    try:
        data = requests.get(url, timeout=10).json()
        res = {}
        for d in data:
            ciu = d['location'].replace(" ", "_")
            if d.get('data') and len(d['data']) > 0:
                res[ciu] = d['data'][-1]['item_count']
        return res
    except: return {}

# --- 3. CONFIGURACIÓN Y PERFIL ---
st.set_page_config(page_title="Albion Terminal Pro", layout="wide")
st.sidebar.header("Tus Specs (0-100)")
premium = st.sidebar.checkbox("Premium", value=True)
tax_v, s_fee = (0.04 if premium else 0.08), 0.025

spec_base = st.sidebar.slider("Nivel Alquimia General", 0, 100, 100)
u_specs = {}
with st.sidebar.expander("Tus 15 Ramas de Spec"):
    for rama in ALBION_DB["ramas"]:
        u_specs[rama] = st.slider(rama, 0, 100, 100 if rama == "Curación" else 0)

def calcular_foco(f_base, rama_p):
    pts = (spec_base * 30) + (u_specs.get(rama_p, 0) * 250)
    for r, lvl in u_specs.items():
        if r != rama_p: pts += (lvl * 18)
    return f_base * (0.5 ** (pts / 10000))

t1, t2, t3, t4 = st.tabs(["🌱 1. Cultivos", "🧪 2. Alquimia", "📈 3. Estrategia", "📊 4. Escáner"])

# --- MÓDULO 1: CULTIVOS ---
with t1:
    st.header("Análisis de Granja y Reposición")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_c = st.selectbox("Isla en:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"])
    with c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Nº Parcelas:", min_value=1, value=10)

    if st.button("Calcular Granja"):
        info = ALBION_DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            tiene_bono = hie_e in ALBION_DB["bonos"].get(ciu_c, [])
            bono = 1.1 if tiene_bono else 1.0
            h_tot = parc * 9
            cosecha_est = math.floor(h_tot * 9 * bono)
            s_perd = math.ceil(h_tot * (1 - info["ret"]))
            
            m_h = pg.get(hie_e, {})
            c_v_opt = max(m_h, key=lambda k: m_h[k]['s']) if m_h else ciu_c
            p_v_opt = m_h.get(c_v_opt, {}).get('s', 0)
            
            m_s = pg.get(info["seed"], {})
            c_s_opt = min(m_s, key=lambda k: m_s[k]['s']) if m_s else ciu_c
            p_s_opt = m_s.get(c_s_opt, {}).get('s', 0)
            
            ing_bruto = cosecha_est * p_v_opt
            coste_repo = s_perd * p_s_opt
            ing_neto = ing_bruto * (1 - tax_v - s_fee)
            
            if tiene_bono: st.success(f"✅ Bono Activo: {ciu_c} tiene +10% de producción.")
            st.metric("Beneficio Neto (Tras Reposición e Impuestos)", f"{ing_neto - coste_repo:,.0f} silver")
            st.info(f"Venta Óptima: {c_v_opt} ({p_v_opt}s) | Compra Semillas: {c_s_opt} ({p_s_opt}s)")

# --- MÓDULO 2: ALQUIMIA ---
with t2:
    st.header("Alquimia Pro (Precios Rápidos)")
    p_sel = st.selectbox("Poción a Fabricar:", list(ALBION_DB["recetas"].keys()))
    e_sel = st.selectbox("Encantamiento:", [0, 1, 2, 3])
    rec = ALBION_DB["recetas"][p_sel]
    
    col_a, col_b = st.columns([2, 1])
    with col_b:
        cant = st.number_input("Cantidad a fabricar:", min_value=5, step=5, value=100)
        foco = st.checkbox("Usar Foco", value=True)
        t_nutri = st.number_input("Tasa Nutrición total:", value=400)
        
    id_final = f"{rec['id']}@{e_sel}" if e_sel > 0 else rec['id']
    ids_pedir = [id_final] + list(rec["mats"].keys())
    if e_sel > 0: ids_pedir.append(f"T{rec['id'][1:2]}_{ALBION_DB['esencias'][e_sel]}")
        
    pg_alq = get_p(ids_pedir)
    
    with col_a:
        coste_mats = 0
        rrr = 0.482 if foco else 0.248
        ciclos = math.ceil(cant / 5)
        
        for m, qb in rec["mats"].items():
            m_p = pg_alq.get(m, {})
            c_opt = min(m_p, key=lambda x: m_p[x]['s']) if m_p else "N/A"
            p_opt = m_p.get(c_opt, {}).get('s', 0)
            p_in = st.number_input(f"{m} (Mejor: {p_opt}s en {c_opt})", value=int(p_opt), key=f"mat_{m}")
            coste_mats += (math.ceil((qb * ciclos) * (1 - rrr)) * p_in)
            
        pv_api = pg_alq.get(id_final, {}).get("Brecilien", {}).get("s", 0)
        pv_man = st.number_input(f"Precio Venta sugerido ({id_final}):", value=int(pv_api))
        
        beneficio_alq = (cant * pv_man * (1 - tax_v - s_fee)) - (coste_mats + t_nutri)
        st.success(f"### Beneficio Neto: {beneficio_alq:,.0f} silver")
        if foco: st.info(f"💡 Foco necesario: {calcular_foco(rec['foco'], rec['rama']) * ciclos:,.0f} pts")
