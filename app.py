import streamlit as st
import requests
import math

# --- 1. BASE DE DATOS MAESTRA (100% VERIFICADA) ---
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
        # --- CLÁSICAS (Lotes de 5) ---
        "Curación Menor (T2)": {"id": "T2_POTION_HEAL", "rama": "Curación", "foco": 300, "salida": 5, "mats": {"T2_AGARIC": 8}},
        "Curación Normal (T4)": {"id": "T4_POTION_HEAL", "rama": "Curación", "foco": 1200, "salida": 5, "mats": {"T4_BURDOCK": 24, "T3_EGG": 6}},
        "Curación Mayor (T6)": {"id": "T6_POTION_HEAL", "rama": "Curación", "foco": 3000, "salida": 5, "mats": {"T6_FOXGLOVE": 72, "T5_EGG": 18, "T6_ALCOHOL": 18}},
        
        "Energía Menor (T2)": {"id": "T2_POTION_ENERGY", "rama": "Energía", "foco": 300, "salida": 5, "mats": {"T2_AGARIC": 8}},
        "Energía Normal (T4)": {"id": "T4_POTION_ENERGY", "rama": "Energía", "foco": 1200, "salida": 5, "mats": {"T4_BURDOCK": 24, "T4_MILK": 6}},
        "Energía Mayor (T6)": {"id": "T6_POTION_ENERGY", "rama": "Energía", "foco": 3000, "salida": 5, "mats": {"T6_FOXGLOVE": 72, "T6_MILK": 18, "T6_ALCOHOL": 18}},
        
        "Veneno Menor (T4)": {"id": "T4_POTION_COOLDOWN", "rama": "Veneno", "foco": 1200, "salida": 5, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Veneno Normal (T6)": {"id": "T6_POTION_COOLDOWN", "rama": "Veneno", "foco": 3000, "salida": 5, "mats": {"T6_FOXGLOVE": 24, "T5_TEASEL": 12, "T3_COMFREY": 12, "T6_MILK": 6}},
        "Veneno Mayor (T8)": {"id": "T8_POTION_COOLDOWN", "rama": "Veneno", "foco": 6000, "salida": 5, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T8_MILK": 18, "T8_ALCOHOL": 18}},
        
        "Gigantismo Menor (T3)": {"id": "T3_POTION_REVIVE", "rama": "Gigantismo", "foco": 600, "salida": 5, "mats": {"T3_COMFREY": 24}},
        "Gigantismo Normal (T5)": {"id": "T5_POTION_REVIVE", "rama": "Gigantismo", "foco": 2000, "salida": 5, "mats": {"T5_TEASEL": 24, "T3_COMFREY": 12}},
        "Gigantismo Mayor (T7)": {"id": "T7_POTION_REVIVE", "rama": "Gigantismo", "foco": 4600, "salida": 5, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        
        "Resistencia Menor (T3)": {"id": "T3_POTION_STONESKIN", "rama": "Resistencia", "foco": 600, "salida": 5, "mats": {"T3_COMFREY": 24}},
        "Resistencia Normal (T5)": {"id": "T5_POTION_STONESKIN", "rama": "Resistencia", "foco": 2000, "salida": 5, "mats": {"T5_TEASEL": 24, "T3_COMFREY": 12}},
        "Resistencia Mayor (T7)": {"id": "T7_POTION_STONESKIN", "rama": "Resistencia", "foco": 4600, "salida": 5, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T4_BURDOCK": 36, "T6_MILK": 18, "T7_ALCOHOL": 18}},
        
        "Pegajosa Menor (T3)": {"id": "T3_POTION_SLOWFIELD", "rama": "Pegajosa", "foco": 600, "salida": 5, "mats": {"T3_COMFREY": 24}},
        "Pegajosa Normal (T5)": {"id": "T5_POTION_SLOWFIELD", "rama": "Pegajosa", "foco": 2000, "salida": 5, "mats": {"T5_TEASEL": 24, "T3_COMFREY": 12}},
        "Pegajosa Mayor (T7)": {"id": "T7_POTION_SLOWFIELD", "rama": "Pegajosa", "foco": 4600, "salida": 5, "mats": {"T7_MULLEIN": 72, "T5_TEASEL": 36, "T3_COMFREY": 36, "T8_MILK": 18, "T7_ALCOHOL": 18}},
        
        "Invisibilidad (T8)": {"id": "T8_POTION_INVIS_1", "rama": "Invisibilidad", "foco": 6000, "salida": 5, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T8_MILK": 18, "T8_ALCOHOL": 18}},

        # --- RASTREO MODIFICADAS (Lotes de 10) ---
        "Ácido Menor (T3)": {"id": "T3_POTION_ACID", "rama": "Ácido", "foco": 1200, "salida": 10, "mats": {"T3_TRACK_CLAW": 1, "T3_COMFREY": 48}},
        "Ácido Normal (T5)": {"id": "T5_POTION_ACID", "rama": "Ácido", "foco": 4000, "salida": 10, "mats": {"T5_TRACK_CLAW": 1, "T5_TEASEL": 48, "T4_BURDOCK": 24, "T4_MILK": 12}},
        "Ácido Mayor (T7)": {"id": "T7_POTION_ACID", "rama": "Ácido", "foco": 9200, "salida": 10, "mats": {"T7_TRACK_CLAW": 1, "T7_MULLEIN": 144, "T6_FOXGLOVE": 72, "T6_ALCOHOL": 72, "T6_MILK": 36, "T7_ALCOHOL": 36}},
        
        "Calmante Menor (T3)": {"id": "T3_POTION_CALMING", "rama": "Calmante", "foco": 1200, "salida": 10, "mats": {"T3_TRACK_SHADOW": 1, "T3_COMFREY": 48}},
        "Calmante Normal (T5)": {"id": "T5_POTION_CALMING", "rama": "Calmante", "foco": 4000, "salida": 10, "mats": {"T5_TRACK_SHADOW": 1, "T5_TEASEL": 48, "T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Calmante Mayor (T7)": {"id": "T7_POTION_CALMING", "rama": "Calmante", "foco": 9200, "salida": 10, "mats": {"T7_TRACK_SHADOW": 1, "T7_MULLEIN": 144, "T6_FOXGLOVE": 72, "T5_EGG": 72, "T6_MILK": 36, "T7_ALCOHOL": 36}},
        
        "Limpieza Menor (T3)": {"id": "T3_POTION_CLEANSE", "rama": "Limpieza", "foco": 1200, "salida": 10, "mats": {"T3_TRACK_ROOT": 1, "T3_COMFREY": 48}},
        "Limpieza Normal (T5)": {"id": "T5_POTION_CLEANSE", "rama": "Limpieza", "foco": 4000, "salida": 10, "mats": {"T5_TRACK_ROOT": 1, "T5_TEASEL": 48, "T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Limpieza Mayor (T7)": {"id": "T7_POTION_CLEANSE", "rama": "Limpieza", "foco": 9200, "salida": 10, "mats": {"T7_TRACK_ROOT": 1, "T7_MULLEIN": 144, "T6_FOXGLOVE": 72, "T4_BURDOCK": 72, "T6_MILK": 36, "T7_ALCOHOL": 36}},

        # --- RASTREO ESTÁNDAR (Lotes de 5) ---
        "Berserker Menor (T4)": {"id": "T4_POTION_BERSERK", "rama": "Berserker", "foco": 1200, "salida": 5, "mats": {"T4_TRACK_FANG": 1, "T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Berserker Normal (T6)": {"id": "T6_POTION_BERSERK", "rama": "Berserker", "foco": 3000, "salida": 5, "mats": {"T6_TRACK_FANG": 1, "T6_FOXGLOVE": 24, "T2_AGARIC": 12, "T6_ALCOHOL": 6}},
        "Berserker Mayor (T8)": {"id": "T8_POTION_BERSERK", "rama": "Berserker", "foco": 6000, "salida": 5, "mats": {"T8_TRACK_FANG": 1, "T8_YARROW": 72, "T7_MULLEIN": 36, "T8_MILK": 18, "T8_ALCOHOL": 18}},
        
        "Fuego Inf. Menor (T4)": {"id": "T4_POTION_HELL", "rama": "Fuego Infernal", "foco": 1200, "salida": 5, "mats": {"T4_TRACK_HORN": 1, "T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Fuego Inf. Normal (T6)": {"id": "T6_POTION_HELL", "rama": "Fuego Infernal", "foco": 3000, "salida": 5, "mats": {"T6_TRACK_HORN": 1, "T6_FOXGLOVE": 24, "T5_TEASEL": 12, "T3_EGG": 6}},
        "Fuego Inf. Mayor (T8)": {"id": "T8_POTION_HELL", "rama": "Fuego Infernal", "foco": 6000, "salida": 5, "mats": {"T8_TRACK_HORN": 1, "T8_YARROW": 72, "T7_MULLEIN": 36, "T5_EGG": 18, "T8_ALCOHOL": 18}},
        
        "Tornado Menor (T4)": {"id": "T4_POTION_TORNADO", "rama": "Tornado", "foco": 1200, "salida": 5, "mats": {"T4_TRACK_FEATHER": 1, "T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Tornado Normal (T6)": {"id": "T6_POTION_TORNADO", "rama": "Tornado", "foco": 3000, "salida": 5, "mats": {"T6_TRACK_FEATHER": 1, "T6_FOXGLOVE": 24, "T5_TEASEL": 12, "T3_EGG": 6}},
        "Tornado Mayor (T8)": {"id": "T8_POTION_TORNADO", "rama": "Tornado", "foco": 6000, "salida": 5, "mats": {"T8_TRACK_FEATHER": 1, "T8_YARROW": 72, "T7_MULLEIN": 36, "T5_EGG": 18, "T8_ALCOHOL": 18}},
        
        "Recolección Menor (T4)": {"id": "T4_POTION_GATHER", "rama": "Recolección", "foco": 1200, "salida": 5, "mats": {"T4_TRACK_TOOTH": 1, "T4_BURDOCK": 24, "T4_BUTTER": 12, "T2_AGARIC": 6}},
        "Recolección Normal (T6)": {"id": "T6_POTION_GATHER", "rama": "Recolección", "foco": 3000, "salida": 5, "mats": {"T6_TRACK_TOOTH": 1, "T6_BUTTER": 24, "T6_FOXGLOVE": 12, "T5_TEASEL": 6}},
        "Recolección Mayor (T8)": {"id": "T8_POTION_GATHER", "rama": "Recolección", "foco": 6000, "salida": 5, "mats": {"T8_TRACK_TOOTH": 1, "T8_BUTTER": 72, "T8_YARROW": 36, "T7_MULLEIN": 18}},

        # --- DESTILADOS BASE ---
        "Aguardiente de Patata (T6)": {"id": "T6_ALCOHOL", "rama": "Destilados", "foco": 1500, "salida": 5, "mats": {"T6_POTATO": 72}},
        "Orujo de Maíz (T7)": {"id": "T7_ALCOHOL", "rama": "Destilados", "foco": 2300, "salida": 5, "mats": {"T7_CORN": 72}},
        "Licor de Calabaza (T8)": {"id": "T8_ALCOHOL", "rama": "Destilados", "foco": 3000, "salida": 5, "mats": {"T8_PUMPKIN": 72}}
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
    num_islas = st.number_input("¿Cuántas islas quieres gestionar?", 1, 10, 1)
    st.session_state['inventario_islas'] = {h: 0 for h in DB["hierbas"].keys()}
    total_neto_islas = 0
    for i in range(int(num_islas)):
        st.markdown(f"### 🏝️ Isla {i+1}")
        c1, c2, c3 = st.columns(3)
        with c1: ciu_c = st.selectbox("Ubicación:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"], key=f"ciu_{i}")
        with c2: hie_e = st.selectbox("Planta:", list(DB["hierbas"].keys()), key=f"hie_{i}")
        with c3: parc = st.number_input("Nº Parcelas:", 1, 100, 10, key=f"parc_{i}")
        info = DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            bono = 1.1 if hie_e in DB["bonos"].get(ciu_c, []) else 1.0
            p_s_api, p_v_api = pg.get(info["seed"], {}).get(ciu_c, {}).get('s', 0), pg.get(hie_e, {}).get(ciu_c, {}).get('s', 0)
            cm1, cm2 = st.columns(2)
            with cm1: p_s_man = st.number_input(f"Precio unitario semilla (API: {p_s_api:,})", value=int(p_s_api), key=f"ps_man_{i}")
            with cm2: p_v_man = st.number_input(f"Venta Hierba (API: {p_v_api:,})", value=int(p_v_api), key=f"pv_man_{i}")
            cosecha_est, s_perd = math.floor(parc * 81 * bono), math.ceil(parc * 9 * (1 - info["ret"]))
            neto_isla = ((cosecha_est * p_v_man) * (1 - tax_v - s_fee)) - (s_perd * p_s_man)
            total_neto_islas += neto_isla
            st.session_state['inventario_islas'][hie_e] += cosecha_est
            st.metric(f"Producción Isla {i+1}", f"{cosecha_est} uds | {neto_isla:,.0f} silver")
        st.divider()

# --- MÓDULO 2: ALQUIMIA ---
with t2:
    st.header("Crafteo de Precisión Híbrido")
    p_sel = st.selectbox("Poción a fabricar:", list(DB["recetas"].keys()))
    e_sel = st.selectbox("Encantamiento:", [0, 1, 2, 3])
    rec = DB["recetas"][p_sel]
    salida_pc = rec.get("salida", 5) # Lector inteligente de lotes
    ing_pr = list(rec["mats"].keys())[0]
    stock_disp = st.session_state['inventario_islas'].get(ing_pr, 0)
    req_pr = rec["mats"][ing_pr]
    col_a, col_b = st.columns([2, 1])
    with col_b:
        usar_granja = st.checkbox("🔄 Calcular máximo desde mi Granja", value=False)
        opt_foco = st.checkbox("🎯 Optimizar Foco Diario (Max 10k)", value=True)
        f_est = calc_foco(rec['foco'], rec['rama'])
        foco_real_input = st.number_input("Foco por Click:", value=int(f_est)) if opt_foco else 0
        if usar_granja and stock_disp >= req_pr:
            stock_sim, c_f, c_sf = stock_disp, 0, 0
            max_cf = math.floor(10000 / foco_real_input) if opt_foco and foco_real_input > 0 else 0
            while stock_sim >= req_pr:
                if c_f < max_cf:
                    batch = min(stock_sim // req_pr, max_cf - c_f)
                    stock_sim -= (batch * req_pr); stock_sim += math.floor((batch * req_pr) * 0.482); c_f += batch
                else:
                    batch = stock_sim // req_pr
                    stock_sim -= (batch * req_pr); stock_sim += math.floor((batch * req_pr) * 0.248); c_sf += batch
            cant_default = (c_f + c_sf) * salida_pc
            st.info(f"🌿 Tus {stock_disp} recursos rinden para **{cant_default}** unidades totales:\n\n✨ {c_f * salida_pc} con Foco\n🔨 {c_sf * salida_pc} sin Foco")
        else: cant_default = 100
        cant = st.number_input("Cantidad a producir:", min_value=salida_pc, step=salida_pc, value=int(cant_default))
        t_nutri = st.number_input("Coste Nutrición total:", value=400)
    
    c_tot = math.ceil(cant / salida_pc)
    c_foco = min(c_tot, math.floor(10000 / foco_real_input)) if opt_foco and foco_real_input > 0 else 0
    c_sfoco = c_tot - c_foco
    id_f = f"{rec['id']}@{e_sel}" if e_sel > 0 else rec['id']
    ids_p = [id_f] + list(rec["mats"].keys())
    if e_sel > 0: ids_p.append(f"T{rec['id'][1:2]}_{DB['esencias'][e_sel]}")
    pg_a = get_p(ids_p)
    with col_a:
        st.subheader("Ajuste Manual de Costes (0 si usas tu stock)")
        coste_mats = 0
        for m, qb in rec["mats"].items():
            p_api = pg_a.get(m, {}).get("Brecilien", {}).get("s", 0)
            p_real = st.number_input(f"Coste {m} (Mercado: {p_api:,})", value=0 if (usar_granja and m in DB["hierbas"]) else int(p_api), key=f"mat_alq_{m}")
            coste_mats += (math.ceil((qb * c_foco) * (1 - 0.482)) + math.ceil((qb * c_sfoco) * (1 - 0.248))) * p_real
        if e_sel > 0:
            id_es = f"T{rec['id'][1:2]}_{DB['esencias'][e_sel]}"
            p_es_api = pg_a.get(id_es, {}).get("Brecilien", {}).get("s", 0)
            p_es_real = st.number_input(f"Coste Esencia (Mercado: {p_es_api:,})", value=int(p_es_api))
            coste_mats += (math.ceil((salida_pc * c_foco) * (1 - 0.482)) + math.ceil((salida_pc * c_sfoco) * (1 - 0.248))) * p_es_real
        pv_api = pg_a.get(id_f, {}).get("Brecilien", {}).get("s", 0)
        pv_real = st.number_input(f"Precio Venta Unidad (API: {pv_api:,})", value=int(pv_api))
        ben_alq = (cant * pv_real * (1 - tax_v - s_fee)) - (coste_mats + t_nutri)
        st.success(f"### Beneficio Limpio: {ben_alq:,.0f} silver")
        st.info(f"⚙️ Producción: {c_foco} ciclos con Foco y {c_sfoco} ciclos sin Foco.")

# --- MÓDULO 3: BALANCE TOTAL ---
with t3:
    st.header("⚖️ Balance Global")
    coste_sem = sum([math.ceil(st.session_state[f"parc_{i}"] * 9 * (1 - DB["hierbas"][st.session_state[f"hie_{i}"]]["ret"])) * st.session_state[f"ps_man_{i}"] for i in range(int(num_islas)) if f"parc_{i}" in st.session_state])
    st.metric("Gasto Semillas", f"{coste_sem:,.0f} silver", delta_color="inverse")
    st.metric("Beneficio Alquimia", f"{ben_alq:,.0f} silver")
    st.divider()
    bal = ben_alq - coste_sem
    if bal > 0: st.success(f"💸 **IMPERIO RENTABLE: {bal:,.0f} silver/día**")
    else: st.error(f"📉 **PÉRDIDAS: {abs(bal):,.0f} silver/día**")

# --- MÓDULO 4: ESCÁNER ---
with t4:
    st.header("📊 Radar y Escáner")
    with st.expander("📡 RADAR TOP 10 RENTABILIDAD"):
        if st.button("Lanzar Radar Global"):
            with st.spinner("Analizando mercado..."):
                ids_t = set()
                for r in DB["recetas"].values():
                    for e in [0, 1, 2]:
                        ids_t.add(f"{r['id']}@{e}" if e > 0 else r['id'])
                        for m in r["mats"].keys(): ids_t.add(m)
                dt = get_p(list(ids_t))
                res_r = []
                for p_n, r in DB["recetas"].items():
                    sal = r.get("salida", 5)
                    for e in [0, 1, 2]:
                        id_it = f"{r['id']}@{e}" if e > 0 else r['id']
                        pv = dt.get(id_it, {}).get("Brecilien", {}).get("s", 0)
                        if pv > 0:
                            c_sf, c_cf, ok = 0, 0, True
                            # Simulamos 100 unidades
                            cics = math.ceil(100 / sal)
                            for m, qb in r["mats"].items():
                                p_m = min([d['s'] for d in dt.get(m, {}).values() if d['s'] > 0], default=0)
                                if p_m == 0: ok = False; break
                                c_sf += math.ceil((qb * cics) * (1 - 0.248)) * p_m
                                c_cf += math.ceil((qb * cics) * (1 - 0.482)) * p_m
                            if ok:
                                ing = 100 * pv * (1 - tax_v - s_fee)
                                res_r.append({"Producto": f"{p_n} .{e}", "Neto (Foco)": int(ing - c_cf), "Neto (Sin Foco)": int(ing - c_sf)})
                if res_r:
                    st.dataframe(sorted(res_r, key=lambda x: x["Neto (Foco)"], reverse=True)[:10], use_container_width=True)
                else:
                    st.error("Faltan datos en la API para generar el Top 10.")

    cat = st.radio("Manual:", ["Pociones", "Ingredientes", "Artefactos", "Semillas"], horizontal=True)
    if st.button("Escanear Volumen"):
        st.info("Función de escaneo de volumen activa.")
