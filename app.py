import streamlit as st
import requests
import math

# --- 1. BASE DE DATOS MAESTRA (TIERS 2-8 Y RASTREOS) ---
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
        "Invisibilidad (T8)": {"id": "T8_POTION_INVIS_1", "rama": "Invisibilidad", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCOHOL": 18}},
        "Berserker (T8)": {"id": "T8_POTION_BERSERK", "rama": "Berserker", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}},
        "Ácido (T8)": {"id": "T8_POTION_ACID", "rama": "Ácido", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}}
    },
    "esencias": {1: "ARCANEM_EXTRACT_LOW", 2: "ARCANEM_EXTRACT_MEDIUM", 3: "ARCANEM_EXTRACT_HIGH"},
    "ramas": ["Curación", "Energía", "Gigantismo", "Resistencia", "Pegajosa", "Invisibilidad", "Veneno", "Ácido", "Berserker", "Fuego Infernal", "Tornado", "Limpieza", "Calmante", "Recolección", "Destilados"],
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

st.set_page_config(page_title="Terminal Albion Pro", layout="wide")
st.sidebar.header("Módulo 0: Perfil")
premium = st.sidebar.checkbox("Premium Activo", value=True)
tax_v, s_fee = (0.04 if premium else 0.08), 0.025
spec_base = st.sidebar.slider("Nivel Alquimia General", 0, 100, 100)
u_specs = {r: st.sidebar.slider(r, 0, 100, 100 if r == "Curación" else 0) for r in ALBION_DB["ramas"]}

def calcular_foco(f_base, rama_p):
    pts = (spec_base * 30) + (u_specs.get(rama_p, 0) * 250)
    for r, lvl in u_specs.items():
        if r != rama_p: pts += (lvl * 18)
    return f_base * (0.5 ** (pts / 10000))

t1, t2, t3, t4 = st.tabs(["🌱 1. Cultivos", "🧪 2. Alquimia Pro", "📈 3. Estrategia", "📊 4. Escáner Mercado"])

with t1:
    st.header("Análisis de Granja y Reposición")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_c = st.selectbox("Isla en:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"])
    with c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Nº Parcelas:", min_value=1, value=10)
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
            p_v = m_h.get(cv_o, {}).get('s', 0); p_s = m_s.get(cc_o, {}).get('s', 0)
            ing = (cos_est * p_v) * (1-tax_v-s_fee); cst = s_perd * p_s
            st.success(f"Beneficio Neto: {ing - cst:,.0f} silver")
            if bono > 1: st.success(f"✅ Bono Activo en {ciu_c}")
            st.info(f"🛒 Semillas baratas: {cc_o} | 📍 Vender en: {cv_o}")
            with t2:
    st.header("Calculadora Alquimia Terminal")
    p_sel = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()))
    e_sel = st.selectbox("Encantamiento:", [0, 1, 2, 3])
    rec = ALBION_DB["recetas"][p_sel]
    col_a, col_b = st.columns([2, 1])
    
    with col_b:
        cant = st.number_input("Cantidad:", min_value=5, step=5, value=100)
        f_check = st.checkbox("Usar Foco", value=True)
    
    id_f = f"{rec['id']}@{e_sel}" if e_sel > 0 else rec['id']
    ids_pedir = [id_f] + list(rec["mats"].keys())
    if e_sel > 0: 
        ids_pedir.append(f"T{rec['id'][1:2]}_{ALBION_DB['esencias'][e_sel]}")
    
    pg_a = get_p(ids_pedir)
    
    with col_a:
        coste_m = 0; rrr = 0.482 if f_check else 0.248; cic = math.ceil(cant / 5)
        for m, qb in rec["mats"].items():
            m_p = pg_a.get(m, {})
            cb = min(m_p, key=lambda x: m_p[x]['s']) if m_p else "N/A"
            ps = m_p.get(cb, {}).get('s', 0)
            p_in = st.number_input(f"Precio {m} (Brecilien: {ps})", value=int(ps), key=f"al_{m}")
            qr = math.ceil((qb * cic) * (1 - rrr))
            coste_m += (qr * p_in)
            
        pv_api = pg_a.get(id_f, {}).get("Brecilien", {}).get("s", 0)
        pv_man = st.number_input(f"Precio Venta API: {pv_api}", value=int(pv_api))
        benef = (cant * pv_man * (1 - tax_v - s_fee)) - coste_m
        st.success(f"Beneficio Neto: {benef:,.0f} s")
        if f_check: 
            st.info(f"Foco necesario: {calcular_foco(rec['foco'], rec['rama']) * cic:,.0f} pts")

with t3:
    st.header("Estrategia Cruzada")
    st.write("¿Sale rentable usar tus plantas o venderlas?")
    if st.button("Calcular Ahorro Real"):
        mats_hierba = [m for m in rec["mats"].keys() if m in ALBION_DB["hierbas"]]
        ahorro = 0
        for m in mats_hierba:
            p_m = pg_a.get(m, {}).get("Brecilien", {}).get("s", 0)
            ahorro += (math.ceil((rec["mats"][m]*cic)*(1-rrr)) * p_m * 0.4)
        st.success(f"Ahorro estimado por producción propia: {ahorro:,.0f} silver")

with t4:
    st.header("📊 Escáner de Mercado")
    item_scan = st.text_input("ID del Ítem:", value=rec['id'])
    if st.button("Escanear"):
        data_scan = get_p([item_scan])
        if data_scan:
            for ciu, precios in data_scan.get(item_scan, {}).items():
                st.write(f"**{ciu.replace('_',' ')}** | Venta: {precios['s']:,} s | Compra: {precios['b']:,} s")
