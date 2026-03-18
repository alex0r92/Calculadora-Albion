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
        "Invisibilidad (T8)": {"id": "T8_POTION_INVIS_1", "rama": "Invisibilidad", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCOHOL": 18}},
        "Ácido/Berserker (T8)": {"id": "T8_POTION_BERSERK", "rama": "Berserker", "foco": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1}}
    },
    "esencias": {1: "ARCANEM_EXTRACT_LOW", 2: "ARCANEM_EXTRACT_MEDIUM", 3: "ARCANEM_EXTRACT_HIGH"},
    "ramas": ["Curación", "Energía", "Gigantismo", "Resistencia", "Pegajosa", "Invisibilidad", "Veneno", "Limpieza", "Ácido", "Calmante", "Recolección", "Fuego Infernal", "Berserker", "Tornado", "Destilados"],
    "bonos": {"Lymhurst": ["T4_BURDOCK"], "Martlock": ["T6_FOXGLOVE"], "Thetford": ["T7_MULLEIN", "T2_AGARIC"]}
}

@st.cache_data(ttl=60)
def get_p(ids):
    c = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://europe.albion-online-data.com/api/v2/stats/prices/{','.join(ids)}?locations={c}&qualities=1"
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
    url = f"https://europe.albion-online-data.com/api/v2/stats/history/{item_id}?locations={c}&time-scale=24"
    try:
        data = requests.get(url, timeout=10).json()
        res = {}
        for d in data:
            ciu = d['location'].replace(" ", "_")
            if d.get('data') and len(d['data']) > 0:
                res[ciu] = d['data'][-1]['item_count']
        return res
    except: return {}

# --- 2. CONFIGURACIÓN Y PERFIL ---
st.set_page_config(page_title="Albion Terminal Pro (EU)", layout="wide")
st.sidebar.header("Tus Specs (0-100)")
premium = st.sidebar.checkbox("Premium", value=True)
tax_v, s_fee = (0.04 if premium else 0.08), 0.025
spec_base = st.sidebar.slider("Nivel Alquimia General", 0, 100, 100)
u_specs = {r: st.sidebar.slider(r, 0, 100, 100 if r == "Curación" else 0) for r in ALBION_DB["ramas"]}

def calcular_foco(f_base, rama_p):
    pts = (spec_base * 30) + (u_specs.get(rama_p, 0) * 250)
    for r, lvl in u_specs.items():
        if r != rama_p: pts += (lvl * 18)
    return f_base * (0.5 ** (pts / 10000))

t1, t2, t3, t4 = st.tabs(["🌱 1. Cultivos Pro", "🧪 2. Alquimia Pro", "📈 3. Estrategia", "📊 4. Escáner"])

# --- MÓDULO 1: CULTIVOS (MULTI-ISLA) ---
with t1:
    st.header("Análisis de Granja Multi-Isla (Europa)")
    num_islas = st.number_input("¿Cuántas islas quieres gestionar?", min_value=1, max_value=5, value=1)
    beneficio_total_granjas = 0
    
    for i in range(int(num_islas)):
        st.markdown(f"#### 🏝️ Isla {i+1}")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: ciu_c = st.selectbox("Ubicación:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"], key=f"ciu_{i}")
        with col_c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()), key=f"hie_{i}")
        with col_c3: parc = st.number_input("Nº Parcelas:", min_value=1, value=10, key=f"parc_{i}")
        
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
            
            neto_isla = (cosecha_est * p_v_opt * (1 - tax_v - s_fee)) - (s_perd * p_s_opt)
            beneficio_total_granjas += neto_isla
            
            st.metric(f"Neto Isla {i+1}", f"{neto_isla:,.0f} silver")
            
            with st.expander(f"Ver desglose de mercados para Isla {i+1}"):
                tab_v, tab_s = st.tabs(["Precios Hierba (Venta)", "Precios Semilla (Compra)"])
                with tab_v:
                    st.write(f"📍 **Mejor Venta:** {c_v_opt} ({p_v_opt}s)")
                    for c, d in m_h.items():
                        st.write(f"**{c}**: {d['s']:,} s (Orden Compra: {d['b']:,} s)")
                with tab_s:
                    st.write(f"🛒 **Mejor Compra Semillas:** {c_s_opt} ({p_s_opt}s)")
                    for c, d in m_s.items():
                        st.write(f"**{c}**: {d['s']:,} s (Orden Compra: {d['b']:,} s)")
        st.divider()
    
    if num_islas > 1:
        st.success(f"## 💰 Beneficio Total Diario: {beneficio_total_granjas:,.0f} silver")

# --- MÓDULO 2: ALQUIMIA ---
with t2:
    st.header("Calculadora Alquimia Terminal (Europa)")
    p_sel = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()))
    e_sel = st.selectbox("Encantamiento:", [0, 1, 2, 3])
    rec = ALBION_DB["recetas"][p_sel]
    
    col_a, col_b = st.columns([2, 1])
    with col_b:
        cant = st.number_input("Cantidad:", min_value=5, step=5, value=100)
        f_check = st.checkbox("Usar Foco", value=True)
        t_nutri = st.number_input("Tasa Nutrición:", value=400)
    
    id_f = f"{rec['id']}@{e_sel}" if e_sel > 0 else rec['id']
    ids_pedir = [id_f] + list(rec["mats"].keys())
    if e_sel > 0: ids_pedir.append(f"T{rec['id'][1:2]}_{ALBION_DB['esencias'][e_sel]}")
    pg_a = get_p(ids_pedir)
    
    with col_a:
        coste_m = 0; rrr = 0.482 if f_check else 0.248; cic = math.ceil(cant / 5)
        for m, qb in rec["mats"].items():
            m_p = pg_a.get(m, {})
            cb = min(m_p, key=lambda x: m_p[x]['s']) if m_p else "N/A"
            ps = m_p.get(cb, {}).get('s', 0)
            p_in = st.number_input(f"Precio {m} (Mejor: {ps} en {cb})", value=int(ps), key=f"al_{m}")
            coste_m += (math.ceil((qb * cic) * (1 - rrr)) * p_in)
        
        pv_api = pg_a.get(id_f, {}).get("Brecilien", {}).get("s", 0)
        pv_man = st.number_input(f"Precio Venta API Brecilien: {pv_api}", value=int(pv_api))
        benef_alq = (cant * pv_man * (1 - tax_v - s_fee)) - (coste_m + t_nutri)
        st.success(f"### Beneficio Neto: {benef_alq:,.0f} silver")
        if f_check: st.info(f"💡 Foco necesario: {calcular_foco(rec['foco'], rec['rama']) * cic:,.0f} pts")

# --- MÓDULO 3: ESTRATEGIA ---
with t3:
    st.header("📈 Logística Cruzada")
    if st.button("Calcular Ahorro Real por Autoproducción"):
        m_hierba = [m for m in rec["mats"].keys() if m in ALBION_DB["hierbas"]]
        if not m_hierba: st.warning("No usa ingredientes cultivables.")
        else:
            ahorro = sum([(math.ceil((rec["mats"][m]*cic)*(1-rrr)) * pg_a.get(m, {}).get("Brecilien", {}).get("s", 0) * 0.4) for m in m_hierba])
            st.success(f"Ahorro estimado: {ahorro:,.0f} silver")

# --- MÓDULO 4: ESCÁNER ---
with t4:
    st.header("📊 Escáner de Mercado y Volumen")
    cat = st.radio("Categoría:", ["Pociones", "Ingredientes", "Semillas"], horizontal=True)
    item_id = ""
    if cat == "Pociones":
        p_s = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()), key="esc_p")
        e_s = st.selectbox("Encanto:", [0, 1, 2, 3], key="esc_e")
        base = ALBION_DB["recetas"][p_s]["id"]
        item_id = f"{base}@{e_s}" if e_s > 0 else base
    elif cat == "Ingredientes":
        lista = sorted(list(set(list(ALBION_DB["hierbas"].keys()) + ["T1_ALCOHOL", "T7_ALCOHOL", "T8_ALCOHOL", "T3_EGG", "T5_EGG", "T6_MILK", "T8_ALCHEMICAL_EXTRACT"] + list(ALBION_DB["esencias"].values()))))
        item_id = st.selectbox("Ingrediente:", lista)
    else:
        item_id = st.selectbox("Semilla:", [v["seed"] for v in ALBION_DB["hierbas"].values()])

    if st.button("Lanzar Escáner Definitivo"):
        p_d = get_p([item_id]).get(item_id, {})
        v_d = get_h(item_id)
        ciudades = ["Brecilien", "Caerleon", "Martlock", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling"]
        for c in ciudades:
            pv, pc, vol = p_d.get(c, {}).get('s', 0), p_d.get(c, {}).get('b', 0), v_d.get(c, 0)
            st.markdown(f"#### {c.replace('_',' ')}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Venta", f"{pv:,} s"); c2.metric("Compra", f"{pc:,} s")
            if vol == 0: c3.error("Volumen: 0 (Muerto)")
            elif vol < 50: c3.warning(f"Volumen: {vol:,} (Bajo)")
            else: c3.success(f"Volumen: {vol:,} (Activo)")
            st.divider()
