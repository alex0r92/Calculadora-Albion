import streamlit as st
import requests
import math

# ==========================================
# 1. BASE DE DATOS MAESTRA (Verificada)
# ==========================================
ALBION_DB = {
    "bonos_ciudad": {
        "Lymhurst": ["T4_BURDOCK"],
        "Bridgewatch": ["T5_TEASEL"],
        "Martlock": ["T6_FOXGLOVE"],
        "Thetford": ["T7_MULLEN", "T2_AGARIC"],
        "Fort Sterling": ["T8_YARROW"],
        "Caerleon": ["T3_COMFREY", "T5_TEASEL", "T7_MULLEN"],
        "Brecilien": [] 
    },
    "hierbas": {
        "T2_AGARIC": {"seed": "T2_SEED_AGARIC", "return_base": 0.333},
        "T3_COMFREY": {"seed": "T3_SEED_COMFREY", "return_base": 0.600},
        "T4_BURDOCK": {"seed": "T4_SEED_BURDOCK", "return_base": 0.733},
        "T5_TEASEL": {"seed": "T5_SEED_TEASEL", "return_base": 0.800},
        "T6_FOXGLOVE": {"seed": "T6_SEED_FOXGLOVE", "return_base": 0.866},
        "T7_MULLEN": {"seed": "T7_SEED_MULLEN", "return_base": 0.911},
        "T8_YARROW": {"seed": "T8_SEED_YARROW", "return_base": 0.933}
    },
    "recetas": {
        "Curación Menor (T2)": {"id_base": "T2_POTION_HEAL", "tier_extracto": "T4", "rama": "Curación", "foco_base": 150, "mats": {"T2_AGARIC": 8}}, 
        "Gigantismo Menor (T3)": {"id_base": "T3_POTION_REVIVE", "tier_extracto": "T4", "rama": "Gigantismo", "foco_base": 250, "mats": {"T3_COMFREY": 12, "T2_AGARIC": 6}},
        "Veneno Menor (T4)": {"id_base": "T4_POTION_COOLDOWN", "tier_extracto": "T4", "rama": "Veneno", "foco_base": 464, "mats": {"T4_BURDOCK": 8, "T2_AGARIC": 4}},
        "Curación (T4)": {"id_base": "T4_POTION_HEAL", "tier_extracto": "T4", "rama": "Curación", "foco_base": 464, "mats": {"T4_BURDOCK": 24, "T2_AGARIC": 12}},
        "Energía (T4)": {"id_base": "T4_POTION_ENERGY", "tier_extracto": "T4", "rama": "Energía", "foco_base": 464, "mats": {"T4_BURDOCK": 24, "T3_COMFREY": 12}},
        "Resistencia (T5)": {"id_base": "T5_POTION_STONESKIN", "tier_extracto": "T6", "rama": "Resistencia", "foco_base": 1648, "mats": {"T5_TEASEL": 24, "T4_BURDOCK": 12, "T3_EGG": 6}},
        "Gigantismo (T5)": {"id_base": "T5_POTION_REVIVE", "tier_extracto": "T6", "rama": "Gigantismo", "foco_base": 1648, "mats": {"T5_TEASEL": 24, "T4_BURDOCK": 12, "T5_EGG": 6}},
        "Curación Mayor (T6)": {"id_base": "T6_POTION_HEAL", "tier_extracto": "T6", "rama": "Curación", "foco_base": 1648, "mats": {"T6_FOXGLOVE": 72, "T3_EGG": 18, "T1_ALCOHOL": 18}},
        "Veneno (T6)": {"id_base": "T6_POTION_COOLDOWN", "tier_extracto": "T6", "rama": "Veneno", "foco_base": 1648, "mats": {"T6_FOXGLOVE": 24, "T5_TEASEL": 12, "T3_EGG": 6}},
        "Gigantismo Mayor (T7)": {"id_base": "T7_POTION_REVIVE", "tier_extracto": "T8", "rama": "Gigantismo", "foco_base": 2736, "mats": {"T7_MULLEN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Resistencia Mayor (T7)": {"id_base": "T7_POTION_STONESKIN", "tier_extracto": "T8", "rama": "Resistencia", "foco_base": 2736, "mats": {"T7_MULLEN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Veneno Mayor (T8)": {"id_base": "T8_POTION_COOLDOWN", "tier_extracto": "T8", "rama": "Veneno", "foco_base": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEN": 36, "T5_TEASEL": 36, "T6_MILK": 18, "T8_ALCOHOL": 18}},
        "Invisibilidad (T8)": {"id_base": "T8_POTION_INVISIBILITY", "tier_extracto": "T8", "rama": "Invisibilidad", "foco_base": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEN": 36, "T5_TEASEL": 36, "T6_MILK": 18, "T8_ALCOHOL": 18}}
    }
}

# ==========================================
# 2. CONECTOR A LA API
# ==========================================
@st.cache_data(ttl=60)
def obtener_precios(lista_ids, ciudad):
    # Evitar peticiones vacías
    if not lista_ids: return {}
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(lista_ids)}?locations={ciudad}"
    try:
        data = requests.get(url, timeout=5).json()
        return {item['item_id']: item['sell_price_min'] for item in data}
    except:
        return {}

# ==========================================
# 3. INTERFAZ Y LÓGICA PRINCIPAL
# ==========================================
st.set_page_config(page_title="Albion Planner", layout="wide")
st.title("⚖️ Centro de Operaciones Alquímicas")

# --- PANEL LATERAL ---
st.sidebar.header("Tus Parámetros")
ciudad = st.sidebar.selectbox("Ciudad de mercado/isla", ["Brecilien", "Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort Sterling"])
premium = st.sidebar.checkbox("Premium Activo", value=True)
tax_mercado = 0.065 if premium else 0.10
tasa_nutricion = st.sidebar.number_input("Tasa de Nutrición (Tienda)", value=345)

st.sidebar.subheader("Destiny Board (Niveles)")
spec_base = st.sidebar.slider("Alquimista (Base)", 0, 100, 100)
with st.sidebar.expander("Ramas de Pociones"):
    specs_usuario = {
        "Curación": st.slider("Curación", 0, 100, 0),
        "Energía": st.slider("Energía", 0, 100, 0),
        "Gigantismo": st.slider("Gigantismo", 0, 100, 0),
        "Resistencia": st.slider("Resistencia", 0, 100, 0),
        "Invisibilidad": st.slider("Invisibilidad", 0, 100, 0),
        "Veneno": st.slider("Veneno", 0, 100, 0)
    }

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🌱 1. Cultivos (Granja)", "🧪 2. Alquimia (Mercado)", "📈 3. Cruzados (Estrategia)"])

# ==========================================
# MÓDULO 1: CULTIVOS
# ==========================================
with tab1:
    st.header("Rentabilidad de Semillas y Cosecha")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        hierba_elegida = st.selectbox("Hierba a plantar:", list(ALBION_DB["hierbas"].keys()))
    with col_c2:
        parcelas = st.number_input("Número de Parcelas activas:", min_value=1, value=10)
    
    if st.button("Calcular Granja"):
        id_semilla = ALBION_DB["hierbas"][hierba_elegida]["seed"]
        precios_granja = obtener_precios([hierba_elegida, id_semilla], ciudad)
        
        # Bono de ciudad
        bono_local = 1.1 if hierba_elegida in ALBION_DB["bonos_ciudad"].get(ciudad, []) else 1.0
        
        huecos_totales = parcelas * 9
        cosecha_estimada = math.floor(huecos_totales * 9 * bono_local)
        semillas_perdidas = math.ceil(huecos_totales * (1 - ALBION_DB["hierbas"][hierba_elegida]["return_base"]))
        
        ingreso_bruto = cosecha_estimada * precios_granja.get(hierba_elegida, 0)
        ingreso_neto = ingreso_bruto * (1 - tax_mercado)
        coste_reposicion = semillas_perdidas * precios_granja.get(id_semilla, 0)
        beneficio_real = ingreso_neto - coste_reposicion
        
        st.write(f"**Bono de ciudad aplicado:** {'Sí (+10%)' if bono_local == 1.1 else 'No'}")
        col_res1, col_res2 = st.columns(2)
        col_res1.metric("Ingreso por Venta (Crudo)", f"{ingreso_neto:,.0f} silver")
        col_res2.metric("Coste Reposición Semillas", f"-{coste_reposicion:,.0f} silver")
        st.success(f"Beneficio Pasivo Diario: **{beneficio_real:,.0f} silver**")

# ==========================================
# MÓDULO 2: ALQUIMIA
# ==========================================
with tab2:
    st.header("Rentabilidad de Crafteo (Comprando materiales)")
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        pocion_alq = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()), key="alq_poc")
    with col_a2:
        encantamiento_alq = st.selectbox("Encantamiento:", [0, 1, 2, 3, 4], format_func=lambda x: f".{x}", key="alq_enc")
    with col_a3:
        cantidad_alq = st.number_input("Cantidad:", min_value=5, step=5, value=100, key="alq_cant")
    with col_a4:
        usar_foco_alq = st.checkbox("Usar Foco", value=True, key="alq_foco")
        rrr_alq = 0.482 if usar_foco_alq else 0.248

    if st.button("Calcular Alquimia"):
        receta = ALBION_DB["recetas"][pocion_alq]
        crafteos = math.ceil(cantidad_alq / 5)
        
        # ID final con encantamiento
        id_final = receta["id_base"] if encantamiento_alq == 0 else f"{receta['id_base']}@{encantamiento_alq}"
        
        # Preparar lista de materiales reales a comprar
        mats_necesarios = receta["mats"].copy()
        if encantamiento_alq > 0:
            mats_necesarios[f"{receta['tier_extracto']}_ARCANE_EXTRACT"] = 18 * encantamiento_alq
            
        ids_a_buscar = [id_final] + list(mats_necesarios.keys())
        precios = obtener_precios(ids_a_buscar, ciudad)
        
        coste_materiales = 0
        for mat, cant in mats_necesarios.items():
            mat_real = math.ceil((cant * crafteos) * (1 - rrr_alq))
            coste_materiales += mat_real * precios.get(mat, 0)
            
        # Cálculo Foco
        rama_actual = receta["rama"]
        spec_especifica = specs_usuario.get(rama_actual, 0)
        spec_otras = sum(valor for rama, valor in specs_usuario.items() if rama != rama_actual)
        eficiencia = (spec_base * 30) + (spec_especifica * 250) + (spec_otras * 18)
        foco_total = (receta["foco_base"] * (0.5 ** (eficiencia / 10000))) * crafteos
        
        ingreso = cantidad_alq * precios.get(id_final, 0) * (1 - tax_mercado)
        beneficio = ingreso - coste_materiales
        
        st.metric("Beneficio Neto (Comprando todo)", f"{beneficio:,.0f} silver")
        if usar_foco_alq and beneficio > 0 and foco_total > 0:
            st.info(f"Rendimiento del foco: **{(beneficio / foco_total):,.2f} silver/foco** (Gasto total: {foco_total:,.0f} pts)")

# ==========================================
# MÓDULO 3: CRUZADOS (ESTRATEGIA)
# ==========================================
with tab3:
    st.header("Comparativa Logística: Comprar vs Plantar")
    st.write("Calcula si te compensa usar tus propias parcelas para alimentar esta producción.")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1:
        pocion_est = st.selectbox("Meta:", list(ALBION_DB["recetas"].keys()), key="est_poc")
    with col_e2:
        encantamiento_est = st.selectbox("Encantamiento:", [0, 1, 2, 3, 4], format_func=lambda x: f".{x}", key="est_enc")
    with col_e3:
        meta_est = st.number_input("Cantidad total:", min_value=5, step=5, value=1000, key="est_cant")
    with col_e4:
        usar_foco_est = st.checkbox("Foco en Alquimia", value=True, key="est_foco")
        rrr_est = 0.482 if usar_foco_est else 0.248
        
    if st.button("Comparar Estrategias"):
        receta_est = ALBION_DB["recetas"][pocion_est]
        crafteos_est = math.ceil(meta_est / 5)
        id_final_est = receta_est["id_base"] if encantamiento_est == 0 else f"{receta_est['id_base']}@{encantamiento_est}"
        
        # Preparar materiales
        mats_est = receta_est["mats"].copy()
        if encantamiento_est > 0:
            mats_est[f"{receta_est['tier_extracto']}_ARCANE_EXTRACT"] = 18 * encantamiento_est
            
        # Recopilar todos los IDs (Final, mats, y semillas de los mats si son hierbas)
        ids_est = [id_final_est] + list(mats_est.keys())
        for mat in mats_est.keys():
            if mat in ALBION_DB["hierbas"]:
                ids_est.append(ALBION_DB["hierbas"][mat]["seed"])
                
        precios_est = obtener_precios(ids_est, ciudad)
        
        # Separar costes
        coste_comprar_todo = 0
        coste_autosuficiente = 0
        
        st.markdown("### 🛒 Desglose de Materiales Necesarios:")
        for mat, cant in mats_est.items():
            mat_real = math.ceil((cant * crafteos_est) * (1 - rrr_est))
            precio_mercado = precios_est.get(mat, 0)
            coste_comprar_todo += mat_real * precio_mercado
            
            if mat in ALBION_DB["hierbas"]:
                # Logística de plantar esta hierba
                bono_local = 1.1 if mat in ALBION_DB["bonos_ciudad"].get(ciudad, []) else 1.0
                plantas_por_parcela = math.floor(81 * bono_local)
                parcelas_nec = math.ceil(mat_real / plantas_por_parcela)
                semillas_perdidas = math.ceil((parcelas_nec * 9) * (1 - ALBION_DB["hierbas"][mat]["return_base"]))
                coste_reposicion = semillas_perdidas * precios_est.get(ALBION_DB["hierbas"][mat]["seed"], 0)
                
                coste_autosuficiente += coste_reposicion
                st.write(f"- **{mat}**: Necesitas {mat_real} uds. (Si lo plantas: {parcelas_nec} parcelas activas. Reponer semillas cuesta {coste_reposicion:,.0f} silver).")
            else:
                # Si no es hierba (leche, extracto), hay que comprarlo en ambas rutas
                coste_autosuficiente += mat_real * precio_mercado
                st.write(f"- **{mat}**: Comprar {mat_real} uds. cuesta {mat_real * precio_mercado:,.0f} silver.")

        ingreso_est = meta_est * precios_est.get(id_final_est, 0) * (1 - tax_mercado)
        beneficio_ruta_a = ingreso_est - coste_comprar_todo
        beneficio_ruta_b = ingreso_est - coste_autosuficiente
        
        st.markdown("---")
        col_resA, col_resB = st.columns(2)
        col_resA.metric("Ruta A: Comprar todo en mercado", f"{beneficio_ruta_a:,.0f} silver")
        col_resB.metric("Ruta B: Autosuficiencia (Plantar hierbas)", f"{beneficio_ruta_b:,.0f} silver", delta=f"{beneficio_ruta_b - beneficio_ruta_a:,.0f} vs Ruta A")
