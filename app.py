import streamlit as st
import requests
import math

# --- 1. BASE DE DATOS MAESTRA (15 RAMAS) ---
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
        "Veneno Mayor (T8)": {"id": "T8_POTION_COOLDOWN", "rama": "Veneno", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36}},
        "Resistencia Mayor (T7)": {"id": "T7_POTION_STONESKIN", "rama": "Resistencia", "foco": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18}},
        "Invisibilidad (T8)": {"id": "T8_POTION_INVIS_1", "rama": "Invisibilidad", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36}}
    },
    "ramas": ["Curación", "Energía", "Gigantismo", "Resistencia", "Pegajosa", "Invisibilidad", "Veneno", "Limpieza", "Ácido", "Calmante", "Recolección", "Fuego Infernal", "Berserker", "Tornado", "Destilados"]
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

# --- 2. PERFIL PERSONALIZADO (SIDEBAR) ---
st.set_page_config(page_title="Albion Master Terminal", layout="wide")
st.sidebar.header("Módulo 0: Perfil de Alquimista")
premium = st.sidebar.checkbox("Premium Activo", value=True)
tax_v = 0.04 if premium else 0.08

st.sidebar.subheader("Niveles de Especialización")
spec_base = st.sidebar.slider("Rama General (Alquimia)", 0, 100, 100)
user_specs = {}
with st.sidebar.expander("Espec. por Rama (15)"):
    for rama in ALBION_DB["ramas"]:
        user_specs[rama] = st.slider(rama, 0, 100, 0 if rama != "Curación" else 100)

# Cálculo de eficiencia de foco
def calcular_foco(foco_base, rama_p):
    # Puntos: 30 por nivel base + 250 por nivel rama + 18 por otros niveles
    puntos = (spec_base * 30) + (user_specs[rama_p] * 250)
    for r, lvl in user_specs.items():
        if r != rama_p: puntos += (lvl * 18)
    return foco_base * (0.5 ** (puntos / 10000))

t1, t2, t3 = st.tabs(["🌱 Cultivos", "🧪 Alquimia Pro", "📈 Logística Cruzada"])
with t2:
    st.header("Calculadora de Alquimia con Entrada Manual")
    p_sel = st.selectbox("Selecciona Poción:", list(ALBION_DB["recetas"].keys()))
    rec = ALBION_DB["recetas"][p_sel]
    
    col_a, col_b = st.columns([2, 1])
    with col_b:
        tasa_nutricion = st.number_input("Tasa Nutrición Tienda (Brecilien):", value=400)
        tasa_orden = st.checkbox("Incluir tasa 2.5% de Orden de Venta", value=True)
    
    pg = get_p([rec["id"]] + list(rec["mats"].keys()))
    if pg:
        st.subheader("🛒 Desglose de Ingredientes")
        c_mats_total = 0
        precios_finales = {}
        
        for m, q in rec["mats"].items():
            m_data = pg.get(m, {})
            c_opt = min(m_data, key=lambda k: m_data[k]['s']) if m_data else "N/A"
            p_api = m_data.get(c_opt, {}).get('s', 0)
            
            # ENTRADA MANUAL POR INGREDIENTE
            p_manual = st.number_input(f"Precio para {m} (API dice {p_api} en {c_opt}):", value=int(p_api))
            precios_finales[m] = p_manual
            c_mats_total += (q * (p_manual / 5)) # Coste por poción (la receta es para 5)
        
        # CÁLCULO FINAL
        p_v_api = pg.get(rec["id"], {}).get("Brecilien", {}).get("s", 0)
        p_v_manual = st.number_input(f"Precio de Venta Poción (Brecilien API: {p_v_api}):", value=int(p_v_api))
        
        rrr = 0.482 # Foco en Brecilien
        coste_final = c_mats_total * (1 - rrr)
        impuestos = (p_v_manual * (tax_v + (0.025 if tasa_orden else 0)))
        beneficio = p_v_manual - coste_final - impuestos
        
        st.success(f"### Beneficio por Poción: {beneficio:,.2f} silver")
        st.info(f"Foco necesario por cada 5 pociones: {calcular_foco(rec['foco'], rec['rama']):,.0f}")

with t3:
    st.header("Estrategia Cruzada: Granja vs Mercado")
    st.write("Selecciona qué ingredientes produces tú mismo para ver cómo cambia el beneficio real.")
    
    rec_est = ALBION_DB["recetas"][p_sel]
    produccion_propia = {}
    for mat in rec_est["mats"].keys():
        if mat in ALBION_DB["hierbas"]:
            produccion_propia[mat] = st.checkbox(f"Produzco mi propio {mat}", value=False)
    
    if st.button("Calcular Diferencial de Beneficio"):
        st.write("Comparando coste de oportunidad...")
        # Lógica: Si produces, el coste es el de la semilla + tiempo vs el precio de venta en mercado.
        st.warning("Si produces el ingrediente, tu beneficio aumenta, pero dejas de ganar el silver que obtendrías vendiendo la planta directamente.")
