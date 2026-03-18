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
    }
}

# ==========================================
# 2. CONECTORES A LA API (Precios y Volumen)
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

# --- MÓDULO 0: PERFIL GLOBAL (Panel Lateral) ---
st.sidebar.header("Módulo 0: Tu Perfil")
premium = st.sidebar.checkbox("Premium Activo (Tax 4%)", value=True)
tax_venta = 0.04 if premium else 0.08
setup_fee = 0.025 
nutricion_brecilien = st.sidebar.number_input("Tasa Nutrición (Brecilien)", value=400)

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

# --- PESTAÑAS PRINCIPALES ---
tab1, tab_placeholder = st.tabs(["🌱 Módulo 1: Cultivos", "🚧 Próximamente: Alquimia y Logística"])

# --- MÓDULO 1: CULTIVOS ---
with tab1:
    st.header("Análisis de Rentabilidad Agrícola")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        ciudad_cultivo = st.selectbox("¿En qué ciudad está tu isla (cultivo)?", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"])
    with col_c2:
        hierba_elegida = st.selectbox("Hierba a plantar:", list(ALBION_DB["hierbas"].keys()))
    with col_c3:
        parcelas = st.number_input("Número de Parcelas activas:", min_value=1, value=10)

    tipo_venta = st.radio("¿Cómo sueles vender la cosecha?", ["Venta Directa (Solo Tax)", "Crear Orden de Venta (+2.5% Setup Fee)"])
    impuesto_total = tax_venta if "Venta Directa" in tipo_venta else (tax_venta + setup_fee)

    if st.button("Ejecutar Análisis de Granja"):
        id_semilla = ALBION_DB["hierbas"][hierba_elegida]["seed"]
        
        precios_globales = obtener_precios_globales([hierba_elegida, id_semilla])
        
        if not precios_globales:
            st.error("Error conectando con Albion Data Project. Reintenta en unos segundos.")
        else:
            bono_local = 1.1 if hierba_elegida in ALBION_DB["bonos_ciudad"].get(ciudad_cultivo, []) else 1.0
            huecos_totales = parcelas * 9
            cosecha_estimada = math.floor(huecos_totales * 9 * bono_local)
            semillas_perdidas = math.ceil(huecos_totales * (1 - ALBION_DB["hierbas"][hierba_elegida]["return_base"]))
            
            # Buscar el mejor mercado para semillas
            datos_semillas = precios_globales.get(id_semilla, {})
            # Filtramos para asegurarnos de que tengan precio listado
            mercados_semillas_validos = {k: v for k, v in datos_semillas.items() if v.get('sell_min', 0) > 0}
            ciudad_semillas_optima = min(mercados_semillas_validos, key=lambda k: mercados_semillas_validos[k]['sell_min']) if mercados_semillas_validos else ciudad_cultivo
            precio_semilla_optimo = mercados_semillas_validos.get(ciudad_semillas_optima, {}).get('sell_min', 0)

            # Buscar el mejor mercado para vender la hierba
            datos_hierba = precios_globales.get(hierba_elegida, {})
            mercados_hierba_validos = {k: v for k, v in datos_hierba.items() if v.get('sell_min', 0) > 0}
            ciudad_hierba_optima = max(mercados_hierba_validos, key=lambda k: mercados_hierba_validos[k]['sell_min']) if mercados_hierba_validos else ciudad_cultivo
            precio_hierba_optimo = mercados_hierba_validos.get(ciudad_hierba_optima, {}).get('sell_min', 0)

            ingreso_bruto = cosecha_estimada * precio_hierba_optimo
            ingreso_neto = ingreso_bruto * (1 - impuesto_total)
            coste_reposicion = semillas_perdidas * precio_semilla_optimo
            beneficio_real = ingreso_neto - coste_reposicion
            
            st.markdown("---")
            if bono_local == 1.1:
                st.info(f"✨ Aplicando bono local de +10% en {ciudad_cultivo.replace('_', ' ')} para {hierba_elegida}.")
                
            st.success(f"### Beneficio Neto Estimado: {beneficio_real:,.0f} silver diarios")
            
            col_r1, col_r2 = st.columns
