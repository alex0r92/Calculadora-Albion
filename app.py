import streamlit as st
import requests
import math

# ==========================================
# 1. BASE DE DATOS INTERNA (Diccionario)
# ==========================================
ALBION_DB = {
    "hierbas": {
        "T4_HERB_BURDOCK": {"seed": "T4_SEED_BURDOCK", "return_prem": 0.811},
        "T5_HERB_TEASEL": {"seed": "T5_SEED_TEASEL", "return_prem": 0.844},
        "T6_HERB_FOXGLOVE": {"seed": "T6_SEED_FOXGLOVE", "return_prem": 0.888},
        "T7_HERB_MULLEN": {"seed": "T7_SEED_MULLEN", "return_prem": 0.911},
        "T8_HERB_COMFREY": {"seed": "T8_SEED_COMFREY", "return_prem": 0.933}
    },
    "recetas": {
        "Gigantismo T7": {
            "id_final": "T7_POTION_GROWTH",
            "mats": {"T7_HERB_MULLEN": 72, "T6_HERB_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}
        },
        "Veneno T4": {
            "id_final": "T4_POTION_COOLDOWN",
            "mats": {"T4_HERB_BURDOCK": 24, "T2_AGARIC": 12}
        },
        "Curación T6": {
            "id_final": "T6_POTION_HEAL",
            "mats": {"T6_HERB_FOXGLOVE": 36, "T5_HERB_TEASEL": 18, "T3_EGG": 9}
        }
    }
}

# ==========================================
# 2. CONECTOR A LA API
# ==========================================
@st.cache_data(ttl=300) # Guarda los precios 5 minutos para no saturar la API
def obtener_precios(lista_ids, ciudad):
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(lista_ids)}?locations={ciudad}"
    try:
        data = requests.get(url).json()
        return {item['item_id']: item['sell_price_min'] for item in data}
    except:
        return {}

# ==========================================
# 3. INTERFAZ GRÁFICA Y LÓGICA
# ==========================================
st.set_page_config(page_title="Albion CEO - Planner", layout="wide")
st.title("🧪 Planificador Logístico de Alquimia")

# --- PANEL LATERAL (Inputs del Usuario) ---
st.sidebar.header("Tus Parámetros")
ciudad = st.sidebar.selectbox("Ciudad de crafteo", ["Brecilien", "Martlock", "Caerleon", "Lymhurst"])
premium = st.sidebar.checkbox("Premium Activo", value=True)
tax_mercado = 0.065 if premium else 0.10

st.sidebar.subheader("Niveles de Foco")
spec_base = st.sidebar.slider("Alquimista (Base)", 0, 100, 100)
spec_pocion = st.sidebar.slider("Spec Poción Elegida", 0, 100, 35)
spec_otras = st.sidebar.number_input("Suma de otras Specs", 0, 1400, 50)

st.sidebar.subheader("Opciones de Tienda")
tasa_nutricion = st.sidebar.number_input("Tasa de Nutrición (Tienda)", value=345)
usar_foco = st.sidebar.checkbox("Craftear con Foco (RRR 48.2%)", value=True)
rrr = 0.482 if usar_foco else 0.248

# --- PANEL CENTRAL (Cálculo Inverso) ---
st.subheader("🎯 Tu Meta de Producción")
col1, col2 = st.columns(2)
with col1:
    pocion_elegida = st.selectbox("¿Qué quieres fabricar?", list(ALBION_DB["recetas"].keys()))
with col2:
    meta_pociones = st.number_input("¿Cuántas pociones quieres en total?", min_value=5, step=5, value=1000)

if st.button("🚀 Calcular Logística y Rentabilidad", type="primary"):
    receta = ALBION_DB["recetas"][pocion_elegida]
    crafteos_necesarios = math.ceil(meta_pociones / 5)
    
    # Recopilar todos los IDs para la API
    ids_a_buscar = [receta["id_final"]]
    for mat, cant in receta["mats"].items():
        ids_a_buscar.append(mat)
        if mat in ALBION_DB["hierbas"]:
            ids_a_buscar.append(ALBION_DB["hierbas"][mat]["seed"])
            
    precios = obtener_precios(ids_a_buscar, ciudad)
    
    if not precios:
        st.error("Error conectando a la API de Albion Data. Inténtalo en unos segundos.")
    else:
        st.success("✅ Precios actualizados en tiempo real.")
        
        # --- LÓGICA MATEMÁTICA ---
        st.markdown("### 📋 Lista de la Compra y Logística de Islas")
        
        coste_total_materiales = 0
        
        for mat, cant_base in receta["mats"].items():
            # Material real necesario descontando el Retorno de Recursos (RRR)
            mat_real_necesario = math.ceil((cant_base * crafteos_necesarios) * (1 - rrr))
            precio_mat = precios.get(mat, 0)
            coste_total_materiales += mat_real_necesario * precio_mat
            
            # Si es una hierba, calculamos las parcelas
            if mat in ALBION_DB["hierbas"]:
                plantas_por_parcela = 81 # 9 huecos * 9 plantas (media)
                parcelas_necesarias = math.ceil(mat_real_necesario / plantas_por_parcela)
                
                # Pérdida de semillas
                semillas_perdidas = (parcelas_necesarias * 9) * (1 - ALBION_DB["hierbas"][mat]["return_prem"])
                coste_reposicion = semillas_perdidas * precios.get(ALBION_DB["hierbas"][mat]["seed"], 0)
                
                st.info(f"🌱 **{mat}**: Necesitas **{mat_real_necesario}** unidades. \n\n"
                        f"👉 Para cultivarlo tú mismo necesitas mantener **{parcelas_necesarias} parcelas**. \n\n"
                        f"👉 Coste de reponer las semillas que mueran: **{coste_reposicion:,.0f} silver**.")
            else:
                st.warning(f"🛒 **{mat}** (Comprar en mercado): Necesitas **{mat_real_necesario}** unidades. Coste: **{mat_real_necesario * precio_mat:,.0f} silver**.")

        # --- RENTABILIDAD Y FOCO ---
        st.markdown("### 💰 Resumen Financiero")
        ingreso_bruto = meta_pociones * precios.get(receta["id_final"], 0)
        ingreso_neto = ingreso_bruto * (1 - tax_mercado)
        
        # Cálculo de Foco
        eficiencia = (spec_base * 30) + (spec_pocion * 250) + (spec_otras * 18)
        coste_foco_click = 4650 * (0.5 ** (eficiencia / 10000))
        foco_total = coste_foco_click * crafteos_necesarios
        
        beneficio_limpio = ingreso_neto - coste_total_materiales
        
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Valor de las Pociones", f"{ingreso_neto:,.0f} silver")
        col_res2.metric("Beneficio Neto", f"{beneficio_limpio:,.0f} silver")
        col_res3.metric("Foco Necesario", f"{foco_total:,.0f} pts")
        
        if beneficio_limpio > 0:
            st.balloons()
