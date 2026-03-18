import streamlit as st
import requests
import math

# ==========================================
# 1. BASE DE DATOS MAESTRA
# ==========================================
ALBION_DB = {
    "bonos_ciudad": {
        "Lymhurst": ["T4_BURDOCK"],
        "Bridgewatch": ["T5_TEASEL"],
        "Martlock": ["T6_FOXGLOVE"],
        "Thetford": ["T7_MULLEIN", "T2_AGARIC"],
        "Fort_Sterling": ["T8_YARROW"],
        "Caerleon": ["T3_COMFREY", "T5_TEASEL", "T7_MULLEIN"],
        "Brecilien": [] 
    },
    "hierbas": {
        "T2_AGARIC": {"seed": "T2_FARM_AGARIC_SEED", "return_base": 0.333},
        "T3_COMFREY": {"seed": "T3_FARM_COMFREY_SEED", "return_base": 0.600},
        "T4_BURDOCK": {"seed": "T4_FARM_BURDOCK_SEED", "return_base": 0.733},
        "T5_TEASEL": {"seed": "T5_FARM_TEASEL_SEED", "return_base": 0.800},
        "T6_FOXGLOVE": {"seed": "T6_FARM_FOXGLOVE_SEED", "return_base": 0.866},
        "T7_MULLEIN": {"seed": "T7_FARM_MULLEIN_SEED", "return_base": 0.911},
        "T8_YARROW": {"seed": "T8_FARM_YARROW_SEED", "return_base": 0.933}
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
        "Gigantismo Mayor (T7)": {"id_base": "T7_POTION_REVIVE", "tier_extracto": "T8", "rama": "Gigantismo", "foco_base": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Resistencia Mayor (T7)": {"id_base": "T7_POTION_STONESKIN", "tier_extracto": "T8", "rama": "Resistencia", "foco_base": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}},
        "Veneno Mayor (T8)": {"id_base": "T8_POTION_COOLDOWN", "tier_extracto": "T8", "rama": "Veneno", "foco_base": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T6_MILK": 18, "T8_ALCOHOL": 18}},
        "Invisibilidad (T8)": {"id_base": "T8_POTION_INVISIBILITY", "tier_extracto": "T8", "rama": "Invisibilidad", "foco_base": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T6_MILK": 18, "T8_ALCOHOL": 18}}
    }
}

# ==========================================
# 2. CONECTORES A LA API
# ==========================================
@st.cache_data(ttl=60)
def obtener_precios_globales(lista_ids):
    if not lista_ids: return {}
    ciudades = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(lista_ids)}?locations={ciudades}&qualities=1"
    try:
        data = requests.get(url, timeout=10)
        if data.status_code == 200:
            resultados = {}
            for item in data.json():
                ciudad_item = item['city']
                if ciudad_item == "Fort Sterling": ciudad_item = "Fort_Sterling" 
                
                item_id = item['item_id']
                if item['sell_price_min'] > 0 or item['buy_price_max'] > 0:
                    if item_id not in resultados:
                        resultados[item_id] = {}
                    resultados[item_id][ciudad_item] = {
                        "sell_min": item['sell_price_min'],
                        "buy_max": item['buy_price_max']
                    }
            return resultados
        return {}
    except:
        return {}

@st.cache_data(ttl=300)
def obtener_historial_24h(item_id, ciudad):
    url = f"https://www.albion-online-data.com/api/v2/stats/history/{item_id}?locations={ciudad}&time-scale=24&qualities=1"
    try:
        data = requests.get(url, timeout=10)
        if data.status_code == 200 and len(data.json()) > 0:
            historial = data.json()[0].get('data', [])
            if historial:
                ultimo_dato = historial[-1]
                return {
                    "precio_medio": ultimo_dato.get('average_price', 0),
                    "volumen": ultimo_dato.get('item_count', 0)
                }
        return {"precio_medio": 0, "volumen": 0}
    except:
        return {"precio_medio": 0, "volumen": 0}

# ==========================================
# 3. INTERFAZ Y MÓDULOS
# ==========================================
st.set_page_config(page_title="Albion Market Terminal", layout="wide")
st.title("⚖️ Terminal de Mercado y Logística")

# --- MÓDULO 0: PERFIL GLOBAL ---
st.sidebar.header("Módulo 0: Tu Perfil")
premium = st.sidebar.checkbox("Premium Activo (Tax 4%)", value=True)
tax_venta = 0.04 if premium else 0.08
setup_fee = 0.025 

st.sidebar.subheader("Specs de Alquimia")
spec_base = st.sidebar.slider("Alquimista (Base)", 0, 100, 100)
with st.sidebar.expander("Tus 15 Ramas de Pociones"):
    specs_usuario = {
        "Curación": st.slider("Curación", 0, 100, 100),
        "Energía": st.slider("Energía", 0, 100, 0),
        "Gigantismo": st.slider("Gigantismo", 0, 100, 0),
        "Resistencia": st.slider("Resistencia", 0, 100, 0),
        "Pegajosa": st.slider("Pegajosa", 0, 100, 0),
        "Invisibilidad": st.slider("Invisibilidad", 0, 100, 0),
        "Veneno": st.slider("Veneno", 0, 100, 0),
        "Limpieza": st.slider("Limpieza", 0, 100, 0),
        "Ácido": st.slider("Ácido", 0, 100, 0),
        "Calmante": st.slider("Calmante", 0, 100, 0),
        "Recolección": st.slider("Recolección", 0, 100, 0),
        "Fuego Infernal": st.slider("Fuego Infernal", 0, 100, 0),
        "Berserker": st.slider("Berserker", 0, 100, 0),
        "Tornado": st.slider("Tornado", 0, 100, 0),
        "Destilados": st.slider("Destilados (Alcohol)", 0, 100, 0)
    }

tab1, tab2, tab3 = st.tabs(["🌱 1. Cultivos", "🧪 2. Alquimia Inteligente", "📈 3. Estrategia Cruzada"])

# --- MÓDULO 1: CULTIVOS ---
with tab1:
    st.header("Análisis de Rentabilidad Agrícola")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        ciudad_cultivo = st.selectbox("Ciudad de tu isla:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"])
    with col_c2:
        hierba_elegida = st.selectbox("Hierba a plantar:", list(ALBION_DB["hierbas"].keys()))
    with col_c3:
        parcelas = st.number_input("Número de Parcelas:", min_value=1, value=10)

    tipo_venta = st.radio("Venta de la cosecha:", ["Venta Directa (Solo Tax)", "Crear Orden de Venta (+2.5% Setup Fee)"])
    impuesto_total = tax_venta if "Venta Directa" in tipo_venta else (tax_venta + setup_fee)

    if st.button("Ejecutar Análisis de Granja"):
        id_semilla = ALBION_DB["hierbas"][hierba_elegida]["seed"]
        precios_globales = obtener_precios_globales([hierba_elegida, id_semilla])
        
        if not precios_globales:
            st.error("Error conectando a la API.")
        else:
            bono_local = 1.1 if hierba_elegida in ALBION_DB["bonos_ciudad"].get(ciudad_cultivo, []) else 1.0
            huecos_totales = parcelas * 9
            cosecha_estimada = math.floor(huecos_totales * 9 * bono_local)
            semillas_perdidas = math.ceil(huecos_totales * (1 -
