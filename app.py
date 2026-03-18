import streamlit as st
import requests
import math

# --- 1. BASE DE DATOS MAESTRA (ALBION EUROPA) ---
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

# --- 2. MOTORES DE CONEXIÓN API (FRAGMENTADO PARA EVITAR CORTES) ---
@st.cache_data(ttl=60)
def get_p(ids):
    c = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    res = {}
    for i in range(0, len(ids), 40):
        chunk = ids[i:i+40]
        url = f"https://europe.albion-online-data.com/api/v2/stats/prices/{','.join(chunk)}?locations={c}&qualities=1"
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
            ciu = d['location'].replace(" ", "_")
            if d.get('data') and len(d['data']) > 0:
                res[ciu] = d['data'][-1]['item_count']
        return res
    except: return {}

st.set_page_config(page_title="Albion Terminal Pro (EU)", layout="wide")
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
        if r != rama_p: pts += (lvl * 15)
    return f_base * (0.5 ** (pts / 10000))

t1, t2, t3, t4 = st.tabs(["🌱 1. Cultivos Pro", "🧪 2. Alquimia Pro", "⚖️ 3. El Veredicto", "📊 4. Escáner Total"])

# --- MÓDULO 1: CULTIVOS ---
with t1:
    st.header("Gestión Agrícola y Semillas")
    num_islas = st.number_input("¿Cuántas islas quieres gestionar?", min_value=1, max_value=5, value=1)
    beneficio_total_granjas = 0
    for i in range(int(num_islas)):
        st.markdown(f"### 🏝️ Isla {i+1}")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: ciu_c = st.selectbox("Ubicación:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"], key=f"ciu_{i}")
        with col_c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()), key=f"hie_{i}")
        with col_c3: parc = st.number_input("Nº Parcelas:", min_value=1, value=10, key=f"parc_{i}")
        info = ALBION_DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            bono = 1.1 if hie_e in ALBION_DB["bonos"].get(ciu_c, []) else 1.0
            p_s_api, p_v_api = pg.get(info["seed"], {}).get(ciu_c, {}).get('s', 0), pg.get(hie_e, {}).get(ciu_c, {}).get('s', 0)
            c_m1, c_m2 = st.columns(2)
            with c_m1: p_s_man = st.number_input(f"Compra Semilla (API: {p_s_api:,})", value=int(p_s_api), key=f"ps_man_{i}")
            with c_m2: p_v_man = st.number_input(f"Venta Hierba (API: {p_v_api:,})", value=int(p_v_api), key=f"pv_man_{i}")
            
            cosecha_est, s_perd = math.floor(parc * 81 * bono), math.ceil(parc * 9 * (1 - info["ret"]))
            neto_isla = ((cosecha_est * p_v_man) * (1 - tax_v - s_fee)) - (s_perd * p_s_man)
            beneficio_total_granjas += neto_isla
            st.metric(f"Beneficio Neto Isla {i+1}", f"{neto_isla:,.0f} silver")
        st.divider()
    if num_islas > 1: st.success(f"## 💰 Beneficio Total Diario: {beneficio_total_granjas:,.0f} silver")

# --- MÓDULO 2: ALQUIMIA ---
with t2:
    st.header("Crafteo de Precisión")
    p_sel = st.selectbox("Poción a fabricar:", list(ALBION_DB["recetas"].keys()))
    e_sel = st.selectbox("Encantamiento:", [0, 1, 2, 3])
    rec = ALBION_DB["recetas"][p_sel]
    
    col_a, col_b = st.columns([2, 1])
    with col_b:
        es_recoleccion = "GATHER" in rec["id"]
        salida_por_ciclo = 10 if es_recoleccion else 5
        cant = st.number_input("Cantidad de pociones:", min_value=salida_por_ciclo, step=salida_por_ciclo, value=100)
        f_check = st.checkbox("Usar Foco", value=True)
        t_nutri = st.number_input("Coste Nutrición total:", value=400)
        
        foco_estimado = calcular_foco(rec['foco'], rec['rama'])
        foco_real_input = st.number_input("Foco por Click (Juego):", value=int(foco_estimado)) if f_check else 0
            
    id_f = f"{rec['id']}@{e_sel}" if e_sel > 0 else rec['id']
    ids_pedir = [id_f] + list(rec["mats"].keys())
    if e_sel > 0: ids_pedir.append(f"T{rec['id'][1:2]}_{ALBION_DB['esencias'][e_sel]}")
    pg_a = get_p(ids_pedir)
    
    coste_mats = 0
    rrr = 0.482 if f_check else 0.248
    ciclos = math.ceil(cant / salida_por_ciclo)
    foco_total_gastado = ciclos * foco_real_input
    
    with col_a:
        st.subheader("Ajuste Manual de Costes")
        for m, qb in rec["mats"].items():
            p_api = pg_a.get(m, {}).get("Brecilien", {}).get("s", 0)
            p_real = st.number_input(f"Coste {m} (API: {p_api:,})", value=int(p_api), key=f"mat_alq_{m}")
            coste_mats += (math.ceil((qb * ciclos) * (1 - rrr)) * p_real)
            
        # NUEVO: Lógica de coste de esencias para pociones encantadas
        if e_sel > 0:
            id_esencia = f"T{rec['id'][1:2]}_{ALBION_DB['esencias'][e_sel]}"
            p_esencia_api = pg_a.get(id_esencia, {}).get("Brecilien", {}).get("s", 0)
            p_esencia_real = st.number_input(f"Coste Esencia {id_esencia} (API: {p_esencia_api:,})", value=int(p_esencia_api), key=f"mat_es_{id_esencia}")
            coste_mats += (math.ceil((salida_por_ciclo * ciclos) * (1 - rrr)) * p_esencia_real)
            
        pv_api = pg_a.get(id_f, {}).get("Brecilien", {}).get("s", 0)
        st.divider()
        pv_real = st.number_input(f"Precio Venta (Sugerido: {pv_api:,})", value=int(pv_api))
        
        beneficio_alq = (cant * pv_real * (1 - tax_v - s_fee)) - (coste_mats + t_nutri)
        st.success(f"### Beneficio Neto Crafteo: {beneficio_alq:,.0f} silver")
        if f_check: st.info(f"💡 Foco total gastado: {foco_total_gastado:,.0f} pts")

# --- MÓDULO 3: EL VEREDICTO ---
with t3:
    st.header("⚖️ Logística Cruzada: ¿Vender en Crudo o Fabricar?")
    if st.button("Dictar Veredicto de Rentabilidad"):
        valor_crudo = 0
        for m, qb in rec["mats"].items():
            p_venta_mat = pg_a.get(m, {}).get("Brecilien", {}).get("s", 0)
            valor_crudo += (math.ceil((qb * ciclos) * (1 - rrr)) * p_venta_mat * (1 - tax_v - s_fee))
        if e_sel > 0:
            p_venta_esencia = pg_a.get(f"T{rec['id'][1:2]}_{ALBION_DB['esencias'][e_sel]}", {}).get("Brecilien", {}).get("s", 0)
            valor_crudo += (math.ceil((salida_por_ciclo * ciclos) * (1 - rrr)) * p_venta_esencia * (1 - tax_v - s_fee))
            
        st.markdown(f"Si vendes tus ingredientes hoy (tras tasas): **{valor_crudo:,.0f} silver**")
        st.markdown(f"Si los transformas en pociones, el beneficio es: **{beneficio_alq:,.0f} silver**")
        diferencial = beneficio_alq - valor_crudo
        
        if diferencial > 0 and valor_crudo > 0: st.success(f"📈 **¡FABRICA!** Ganas **{diferencial:,.0f} silver extra** (+{(diferencial/valor_crudo)*100:.1f}%) transformando.")
        elif diferencial <= 0: st.error(f"📉 **VENDE EN CRUDO.** Pierdes **{abs(diferencial):,.0f} silver** si te pones a craftear.")

# --- MÓDULO 4: ESCÁNER TOTAL Y RADAR ---
with t4:
    st.header("📊 Escáner de Mercado (Europa)")
    
    # RADAR DE OPORTUNIDADES
    with st.expander("📡 RADAR DE OPORTUNIDADES (TOP 10 RENTABILIDAD)", expanded=False):
        st.write("Escanea todas las pociones (Tiers y .0 a .2) usando precios de Brecilien. *Aviso: Verifica siempre el volumen manualmente después.*")
        if st.button("Lanzar Radar Global", type="primary"):
            with st.spinner("Simulando cientos de crafteos..."):
                ids_totales = set()
                for rec in ALBION_DB["recetas"].values():
                    for enc in [0, 1, 2]:
                        ids_totales.add(f"{rec['id']}@{enc}" if enc > 0 else rec['id'])
                        for m in rec["mats"].keys(): ids_totales.add(m)
                        if enc > 0: ids_totales.add(f"T{rec['id'][1:2]}_{ALBION_DB['esencias'][enc]}")
                
                datos_radar = get_p(list(ids_totales))
                resultados_radar = []
                
                for p_name, rec in ALBION_DB["recetas"].items():
                    es_rec = "GATHER" in rec["id"]
                    salida = 10 if es_rec else 5
                    cics = math.ceil(100 / salida) # Simulamos 100 pociones
                    foco_est = calcular_foco(rec['foco'], rec['rama']) * cics
                    
                    for enc in [0, 1, 2]:
                        id_f = f"{rec['id']}@{enc}" if enc > 0 else rec['id']
                        pv_api = datos_radar.get(id_f, {}).get("Brecilien", {}).get("s", 0)
                        if pv_api == 0: continue
                        
                        valido, coste_sf, coste_cf = True, 0, 0
                        for m, qb in rec["mats"].items():
                            c_min = min([d['s'] for d in datos_radar.get(m, {}).values() if d['s'] > 0], default=0)
                            if c_min == 0: valido = False; break
                            coste_sf += math.ceil((qb * cics) * (1 - 0.248)) * c_min
                            coste_cf += math.ceil((qb * cics) * (1 - 0.482)) * c_min
                            
                        if enc > 0 and valido:
                            id_es = f"T{rec['id'][1:2]}_{ALBION_DB['esencias'][enc]}"
                            c_min_es = min([d['s'] for d in datos_radar.get(id_es, {}).values() if d['s'] > 0], default=0)
                            if c_min_es == 0: valido = False
                            else:
                                coste_sf += math.ceil((salida * cics) * (1 - 0.248)) * c_min_es
                                coste_cf += math.ceil((salida * cics) * (1 - 0.482)) * c_min_es
                        
                        if valido:
                            ingreso = 100 * pv_api * (1 - tax_v - s_fee)
                            resultados_radar.append({
                                "Poción": f"{p_name} .{enc}",
                                "Beneficio Neto (Con Foco)": int(ingreso - coste_cf),
                                "Beneficio Neto (Sin Foco)": int(ingreso - coste_sf),
                                "Coste Foco (100 uds)": int(foco_est)
                            })
                
                if resultados_radar:
                    # Ordenar por mayor beneficio con foco
                    resultados_radar = sorted(resultados_radar, key=lambda x: x["Beneficio Neto (Con Foco)"], reverse=True)[:10]
                    st.dataframe(resultados_radar, use_container_width=True)
                else:
                    st.error("No se han podido cruzar datos suficientes de la API en este momento.")

    st.markdown("---")
    categoria = st.radio("¿Qué deseas escanear manualmente?", ["Pociones", "Ingredientes Comunes", "Artefactos y Restos", "Semillas"], horizontal=True)
    item_id_scan = ""
    
    if categoria == "Pociones":
        c_p1, c_p2 = st.columns(2)
        with c_p1: pocion_sel = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()), key="esc_p")
        with c_p2: encanto_sel = st.selectbox("Encantamiento:", [0, 1, 2, 3], key="esc_e")
        base_id = ALBION_DB["recetas"][pocion_sel]["id"]
        item_id_scan = f"{base_id}@{encanto_sel}" if encanto_sel > 0 else base_id
        
    elif categoria == "Ingredientes Comunes":
        lista_comunes = list(ALBION_DB["hierbas"].keys()) + ["T3_EGG", "T5_EGG", "T4_MILK", "T6_MILK", "T8_MILK", "T4_BUTTER", "T6_BUTTER", "T8_BUTTER", "T6_ALCOHOL", "T7_ALCOHOL", "T8_ALCOHOL"] + list(ALBION_DB["esencias"].values())
        item_id_scan = st.selectbox("Ingrediente:", sorted(list(set(lista_comunes))))
        
    elif categoria == "Artefactos y Restos":
        c_a1, c_a2 = st.columns(2)
        with c_a1: tipo_art = st.selectbox("Tipo:", ["RARE_ANIMAL_REMNANT", "ALCHEMICAL_EXTRACT", "RUNESTONE_BONE", "RUNESTONE_TOOTH", "RUNESTONE_CLAW", "RUNESTONE_FEATHER", "RUNESTONE_BEAK"])
        with c_a2: tier_art = st.selectbox("Tier:", [4, 6, 8] if tipo_art == "ALCHEMICAL_EXTRACT" else [3, 5, 7, 8])
        item_id_scan = f"T{tier_art}_{tipo_art}"
        
    else:
        item_id_scan = st.selectbox("Semilla:", [v["seed"] for v in ALBION_DB["hierbas"].values()])

    if st.button("Lanzar Escáner de Volumen"):
        with st.spinner("Consultando liquidez..."):
            p_data = get_p([item_id_scan]).get(item_id_scan, {})
            v_data = get_h(item_id_scan)
            ciudades = ["Brecilien", "Caerleon", "Martlock", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling"]
            for c in ciudades:
                p_venta, p_compra, volumen = p_data.get(c, {}).get('s', 0), p_data.get(c, {}).get('b', 0), v_data.get(c, 0)
                st.markdown(f"#### 🏙️ {c.replace('_', ' ')}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Venta", f"{p_venta:,} s" if p_venta > 0 else "Sin Datos")
                col2.metric("Compra", f"{p_compra:,} s" if p_compra > 0 else "Sin Datos")
                if volumen == 0: col3.error("Volumen 24h: 0 (Muerto)")
                else: col3.success(f"Volumen 24h: {volumen:,} (Activo)")
                st.divider()
