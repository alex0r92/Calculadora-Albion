import streamlit as st
import requests
import math

# --- 1. BASE DE DATOS MAESTRA (ALBION EUROPA) ---
DB = {
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
        "Curación Menor (T4)": {"id": "T4_POTION_HEAL", "rama": "Curación", "foco": 1200, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Curación Mayor (T6)": {"id": "T6_POTION_HEAL", "rama": "Curación", "foco": 3000, "mats": {"T6_FOXGLOVE": 72, "T5_EGG": 18, "T6_ALCOHOL": 18}},
        "Energía Menor (T4)": {"id": "T4_POTION_ENERGY", "rama": "Energía", "foco": 1200, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Energía Mayor (T6)": {"id": "T6_POTION_ENERGY", "rama": "Energía", "foco": 3000, "mats": {"T6_FOXGLOVE": 72, "T6_MILK": 18, "T6_ALCOHOL": 18}},
        "Veneno Menor (T4)": {"id": "T4_POTION_COOLDOWN", "rama": "Veneno", "foco": 1200, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Veneno (T6)": {"id": "T6_POTION_COOLDOWN", "rama": "Veneno", "foco": 3000, "mats": {"T6_FOXGLOVE": 24, "T5_TEASEL": 12, "T3_COMFREY": 12, "T6_MILK": 6}},
        "Veneno Mayor (T8)": {"id": "T8_POTION_COOLDOWN", "rama": "Veneno", "foco": 6000, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T8_MILK": 18, "T8_ALCOHOL": 18}},
        "Pegajosa Menor (T4)": {"id": "T4_POTION_SLOWFIELD", "rama": "Pegajosa", "foco": 1200, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Pegajosa (T6)": {"id": "T6_POTION_SLOWFIELD", "rama": "Pegajosa", "foco": 3000, "mats": {"T6_FOXGLOVE": 24, "T5_TEASEL": 12, "T3_COMFREY": 12, "T6_MILK": 6}},
        "Pegajosa Mayor (T8)": {"id": "T8_POTION_SLOWFIELD", "rama": "Pegajosa", "foco": 6000, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T8_MILK": 18, "T8_ALCOHOL": 18}},
        "Resistencia Menor (T3)": {"id": "T3_POTION_STONESKIN", "rama": "Resistencia", "foco": 600, "mats": {"T3_COMFREY": 24}},
        "Resistencia (T5)": {"id": "T5_POTION_STONESKIN", "rama": "Resistencia", "foco": 2000, "mats": {"T5_TEASEL": 24, "T3_COMFREY": 12}},
        "Resistencia Mayor (T7)": {"id": "T7_POTION_STONESKIN", "rama": "Resistencia", "foco": 4600, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Gigantismo Menor (T3)": {"id": "T3_POTION_REVIVE", "rama": "Gigantismo", "foco": 600, "mats": {"T3_COMFREY": 24}},
        "Gigantismo (T5)": {"id": "T5_POTION_REVIVE", "rama": "Gigantismo", "foco": 2000, "mats": {"T5_TEASEL": 24, "T3_COMFREY": 12}},
        "Gigantismo Mayor (T7)": {"id": "T7_POTION_REVIVE", "rama": "Gigantismo", "foco": 4600, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Invisibilidad (T8)": {"id": "T8_POTION_INVIS_1", "rama": "Invisibilidad", "foco": 6000, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCOHOL": 18}},
        "Recolección Menor (T4)": {"id": "T4_POTION_GATHER", "rama": "Recolección", "foco": 1500, "mats": {"T4_ALCHEMICAL_EXTRACT": 10, "T4_BUTTER": 16, "T3_RUNESTONE_TOOTH": 1}},
        "Recolección (T6)": {"id": "T6_POTION_GATHER", "rama": "Recolección", "foco": 3000, "mats": {"T6_ALCHEMICAL_EXTRACT": 10, "T6_BUTTER": 16, "T5_RUNESTONE_TOOTH": 1}},
        "Recolección Mayor (T8)": {"id": "T8_POTION_GATHER", "rama": "Recolección", "foco": 4500, "mats": {"T8_ALCHEMICAL_EXTRACT": 10, "T8_BUTTER": 16, "T7_RUNESTONE_TOOTH": 1}},
        "Berserker (T8)": {"id": "T8_POTION_BERSERK", "rama": "Berserker", "foco": 6000, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1, "T8_RUNESTONE_TOOTH": 1}},
        "Ácido (T8)": {"id": "T8_POTION_ACID", "rama": "Ácido", "foco": 6000, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1, "T8_RUNESTONE_BONE": 1}},
        "Tornado (T8)": {"id": "T8_POTION_TORNADO", "rama": "Tornado", "foco": 6000, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1, "T8_RUNESTONE_CLAW": 1}},
        "Fuego Infernal (T8)": {"id": "T8_POTION_HELL", "rama": "Fuego Infernal", "foco": 6000, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1, "T8_RUNESTONE_FEATHER": 1}},
        "Limpieza (T8)": {"id": "T8_POTION_CLEANSE", "rama": "Limpieza", "foco": 6000, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T8_ALCHEMICAL_EXTRACT": 1, "T8_RUNESTONE_BEAK": 1}}
    },
    "esencias": {1: "ARCANEM_EXTRACT_LOW", 2: "ARCANEM_EXTRACT_MEDIUM", 3: "ARCANEM_EXTRACT_HIGH"},
    "ramas": ["Curación", "Energía", "Gigantismo", "Resistencia", "Pegajosa", "Invisibilidad", "Veneno", "Limpieza", "Ácido", "Calmante", "Recolección", "Fuego Infernal", "Berserker", "Tornado", "Destilados"],
    "bonos": {"Lymhurst": ["T4_BURDOCK"], "Martlock": ["T6_FOXGLOVE"], "Thetford": ["T7_MULLEIN", "T2_AGARIC"]}
}

@st.cache_data(ttl=60)
def get_p(ids):
    c = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    res = {}
    for i in range(0, len(ids), 40):
        url = f"https://europe.albion-online-data.com/api/v2/stats/prices/{','.join(ids[i:i+40])}?locations={c}&qualities=1"
        try:
            data = requests.get(url, timeout=10).json()
            for it in data:
                ciu, item = it['city'].replace(" ", "_"), it['item_id']
                if it['sell_price_min'] > 0 or it['buy_price_max'] > 0:
                    if item not in res: res[item] = {}
                    res[item][ciu] = {"s": it['sell_price_min'], "b": it['buy_price_max']}
        except: pass
    return res

@st.cache_data(ttl=300)
def get_h(item_id):
    c = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://europe.albion-online-data.com/api/v2/stats/history/{item_id}?locations={c}&time-scale=24"
    try:
        data = requests.get(url, timeout=10).json()
        res = {}
        for d in data:
            if d.get('data') and len(d['data']) > 0:
                res[d['location'].replace(" ", "_")] = d['data'][-1]['item_count']
        return res
    except: return {}

st.set_page_config(page_title="Albion Terminal Pro", layout="wide")

if 'inventario_islas' not in st.session_state:
    st.session_state['inventario_islas'] = {}

st.sidebar.header("Tus Specs (0-100)")
premium = st.sidebar.checkbox("Premium", value=True)
tax_v, s_fee = (0.04 if premium else 0.08), 0.025
spec_base = st.sidebar.slider("Alquimia General", 0, 100, 100)

u_specs = {}
with st.sidebar.expander("Tus 15 Ramas de Spec"):
    for rama in DB["ramas"]: u_specs[rama] = st.slider(rama, 0, 100, 100 if rama == "Curación" else 0)

def calc_foco(f_base, rama_p):
    pts = (spec_base * 30) + sum(lvl * (250 if r == rama_p else 15) for r, lvl in u_specs.items())
    return f_base * (0.5 ** (pts / 10000))

t1, t2, t3, t4 = st.tabs(["🌱 1. Cultivos", "🧪 2. Alquimia", "⚖️ 3. Balance Total", "📊 4. Escáner"])

# --- MÓDULO 1: CULTIVOS ---
with t1:
    st.header("Gestión Agrícola")
    num_islas = st.number_input("¿Cuántas islas quieres gestionar?", 1, 5, 1)
    
    # Reiniciar inventario para recalcular
    st.session_state['inventario_islas'] = {h: 0 for h in DB["hierbas"].keys()}
    total_neto_islas = 0
    
    for i in range(int(num_islas)):
        st.markdown(f"### 🏝️ Isla {i+1}")
        c1, c2, c3 = st.columns(3)
        with c1: ciu_c = st.selectbox("Ubicación:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"], key=f"ciu_{i}")
        with c2: hie_e = st.selectbox("Planta:", list(DB["hierbas"].keys()), key=f"hie_{i}")
        with c3: parc = st.number_input("Nº Parcelas:", 1, 30, 10, key=f"parc_{i}")
        
        info = DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            bono = 1.1 if hie_e in DB["bonos"].get(ciu_c, []) else 1.0
            p_s_api, p_v_api = pg.get(info["seed"], {}).get(ciu_c, {}).get('s', 0), pg.get(hie_e, {}).get(ciu_c, {}).get('s', 0)
            
            cm1, cm2 = st.columns(2)
            with cm1: p_s_man = st.number_input(f"Compra Semilla (API: {p_s_api:,})", value=int(p_s_api), key=f"ps_man_{i}")
            with cm2: p_v_man = st.number_input(f"Venta Hierba (API: {p_v_api:,})", value=int(p_v_api), key=f"pv_man_{i}")
            
            cosecha_est, s_perd = math.floor(parc * 81 * bono), math.ceil(parc * 9 * (1 - info["ret"]))
            neto_isla = ((cosecha_est * p_v_man) * (1 - tax_v - s_fee)) - (s_perd * p_s_man)
            total_neto_islas += neto_isla
            
            st.session_state['inventario_islas'][hie_e] += cosecha_est
            st.metric(f"Producción Isla {i+1}", f"{cosecha_est} uds | {neto_isla:,.0f} silver")
        st.divider()

# --- MÓDULO 2: ALQUIMIA ---
with t2:
    st.header("Crafteo de Precisión")
    p_sel = st.selectbox("Poción a fabricar:", list(DB["recetas"].keys()))
    e_sel = st.selectbox("Encantamiento:", [0, 1, 2, 3])
    rec = DB["recetas"][p_sel]
    
    es_rec = "GATHER" in rec["id"]
    salida_por_ciclo = 10 if es_rec else 5
    
    # Lógica de autocompletado con inventario de granja
    ingrediente_principal = list(rec["mats"].keys())[0] # Asumimos que el primero es la hierba principal
    stock_disponible = st.session_state['inventario_islas'].get(ingrediente_principal, 0)
    
    col_a, col_b = st.columns([2, 1])
    with col_b:
        usar_granja = st.checkbox("🔄 Calcular máximo desde mi Granja", value=False)
        if usar_granja:
            req_principal = rec["mats"][ingrediente_principal]
            ciclos_posibles = stock_disponible // req_principal if req_principal > 0 else 0
            cant_default = max(salida_por_ciclo, ciclos_posibles * salida_por_ciclo)
            st.info(f"Tienes {stock_disponible} {ingrediente_principal}. Da para {cant_default} pociones.")
        else:
            cant_default = 100

        cant = st.number_input("Cantidad de pociones:", min_value=salida_por_ciclo, step=salida_por_ciclo, value=int(cant_default))
        f_check = st.checkbox("Usar Foco", value=True)
        t_nutri = st.number_input("Coste Nutrición total:", value=400)
        
        f_est = calc_foco(rec['foco'], rec['rama'])
        foco_real_input = st.number_input("Foco por Click:", value=int(f_est)) if f_check else 0

    id_f = f"{rec['id']}@{e_sel}" if e_sel > 0 else rec['id']
    ids_pedir = [id_f] + list(rec["mats"].keys())
    if e_sel > 0: ids_pedir.append(f"T{rec['id'][1:2]}_{DB['esencias'][e_sel]}")
    pg_a = get_p(ids_pedir)
    
    coste_mats = 0
    rrr = 0.482 if f_check else 0.248
    ciclos = math.ceil(cant / salida_por_ciclo)
    
    with col_a:
        st.subheader("Ajuste Manual de Costes (0 si usas tu stock)")
        for m, qb in rec["mats"].items():
            p_api = pg_a.get(m, {}).get("Brecilien", {}).get("s", 0)
            # Si marcaste usar granja y es una hierba que tienes, autocompleta con 0
            precio_defecto = 0 if (usar_granja and m in DB["hierbas"]) else int(p_api)
            p_real = st.number_input(f"Coste {m} (Mercado: {p_api:,})", value=precio_defecto, key=f"mat_alq_{m}")
            coste_mats += (math.ceil((qb * ciclos) * (1 - rrr)) * p_real)
            
        if e_sel > 0:
            id_es = f"T{rec['id'][1:2]}_{DB['esencias'][e_sel]}"
            p_es = pg_a.get(id_es, {}).get("Brecilien", {}).get("s", 0)
            p_es_real = st.number_input(f"Coste Esencia (Mercado: {p_es:,})", value=int(p_es), key=f"mat_es_{id_es}")
            coste_mats += (math.ceil((salida_por_ciclo * ciclos) * (1 - rrr)) * p_es_real)
            
        pv_api = pg_a.get(id_f, {}).get("Brecilien", {}).get("s", 0)
        st.divider()
        pv_real = st.number_input(f"Precio Venta Poción (API: {pv_api:,})", value=int(pv_api))
        
        ben_alq = (cant * pv_real * (1 - tax_v - s_fee)) - (coste_mats + t_nutri)
        st.success(f"### Beneficio Limpio: {ben_alq:,.0f} silver")

# --- MÓDULO 3: BALANCE TOTAL ---
with t3:
    st.header("⚖️ Balance Global del Imperio")
    st.write("Visión pura de tu flujo de caja: todo lo que vendes menos todo lo que te cuesta (semillas, nutrición, ingredientes extra).")
    
    # Sumar costes de semillas gastados en Pestaña 1
    coste_total_semillas = sum([math.ceil(st.session_state[f"parc_{i}"] * 9 * (1 - DB["hierbas"][st.session_state[f"hie_{i}"]]["ret"])) * st.session_state[f"ps_man_{i}"] for i in range(int(num_islas)) if f"parc_{i}" in st.session_state])
    
    st.markdown(f"**Gasto Diario en Semillas:** {coste_total_semillas:,.0f} silver")
    st.markdown(f"**Beneficio Alquimia (Pestaña 2):** {ben_alq:,.0f} silver")
    
    balance_final = ben_alq - coste_total_semillas
    
    if balance_final > 0:
        st.success(f"💸 **TU IMPERIO CRECE.** Ganancia neta absoluta: **{balance_final:,.0f} silver diarios**. Estás subiendo specs y ganando plata real.")
    else:
        st.error(f"📉 **PÉRDIDAS DETECTADAS.** Balance negativo de **{abs(balance_final):,.0f} silver**. Revisa el precio de la poción o no craftees sin foco hoy.")

# --- MÓDULO 4: ESCÁNER ---
with t4:
    st.header("📊 Escáner de Mercado")
    cat = st.radio("¿Qué deseas escanear?", ["Pociones", "Ingredientes", "Artefactos/Restos", "Semillas"], horizontal=True)
    item_id = ""
    if cat == "Pociones":
        c_p1, c_p2 = st.columns(2)
        with c_p1: p_s = st.selectbox("Poción:", list(DB["recetas"].keys()), key="esc_p")
        with c_p2: e_s = st.selectbox("Encanto:", [0, 1, 2, 3], key="esc_e")
        item_id = f"{DB['recetas'][p_s]['id']}@{e_s}" if e_s > 0 else DB['recetas'][p_s]['id']
    elif cat == "Ingredientes":
        l_com = list(DB["hierbas"].keys()) + ["T3_EGG", "T5_EGG", "T6_MILK", "T8_MILK", "T4_BUTTER", "T6_BUTTER", "T8_BUTTER", "T6_ALCOHOL", "T7_ALCOHOL", "T8_ALCOHOL"] + list(DB["esencias"].values())
        item_id = st.selectbox("Item:", sorted(list(set(l_com))))
    elif cat == "Artefactos/Restos":
        c_a1, c_a2 = st.columns(2)
        with c_a1: t_a = st.selectbox("Tipo:", ["RARE_ANIMAL_REMNANT", "ALCHEMICAL_EXTRACT", "RUNESTONE_BONE", "RUNESTONE_TOOTH", "RUNESTONE_CLAW", "RUNESTONE_FEATHER", "RUNESTONE_BEAK"])
        with c_a2: tier = st.selectbox("Tier:", [4, 6, 8] if t_a == "ALCHEMICAL_EXTRACT" else [3, 5, 7, 8])
        item_id = f"T{tier}_{t_a}"
    else: item_id = st.selectbox("Semilla:", [v["seed"] for v in DB["hierbas"].values()])

    if st.button("Escanear Volumen", type="primary"):
        with st.spinner("Consultando..."):
            pd, vd = get_p([item_id]).get(item_id, {}), get_h(item_id)
            for c in ["Brecilien", "Caerleon", "Martlock", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling"]:
                pv, pc, vol = pd.get(c, {}).get('s', 0), pd.get(c, {}).get('b', 0), vd.get(c, 0)
                st.markdown(f"#### 🏙️ {c}")
                c1, c2, c3 = st.columns(3)
                c1.metric("Venta", f"{pv:,}" if pv > 0 else "-"); c2.metric("Compra", f"{pc:,}" if pc > 0 else "-")
                if vol == 0: c3.error("Vol 24h: Muerto")
                else: c3.success(f"Vol 24h: {vol:,}")
                st.divider()
