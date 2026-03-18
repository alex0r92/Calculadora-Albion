import streamlit as st
import requests
import math
from datetime import datetime, timedelta

# ==========================================
# 1. BASE DE DATOS MAESTRA
# ==========================================
ALBION_DB = {
    "bonos_ciudad": {
        "Lymhurst": ["T4_BURDOCK"],
        "Bridgewatch": ["T5_TEASEL"],
        "Martlock": ["T6_FOXGLOVE"],
        "Thetford": ["T7_MULLEIN", "T2_AGARIC"],
        "Fort Sterling": ["T8_YARROW"],
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
def obtener_precios_completos(lista_ids, ciudad):
    if not lista_ids: return {}
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(lista_ids)}?locations={ciudad}"
    try:
        data = requests.get(url, timeout=10)
        if data.status_code == 200:
            resultados = {}
            for item in data.json():
                resultados[item['item_id']] = {
                    "sell_min": item['sell_price_min'],
                    "buy_max": item['buy_price_max']
                }
            return resultados
        return {}
    except:
        return {}

@st.cache_data(ttl=300) # El historial no cambia tan rápido, lo cacheamos 5 mins
def obtener_historial_24h(item_id, ciudad):
    url = f"https://www.albion-online-data.com/api/v2/stats/history/{item_id}?locations={ciudad}&time-scale=24"
    try:
        data = requests.get(url, timeout=10)
        if data.status_code == 200 and len(data.json()) > 0:
            historial = data.json()[0].get('data', [])
            if historial:
                # Coger el dato más reciente de las últimas 24h
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
setup_fee = 0.025 # Constante del 2.5% para órdenes
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
        hierba_elegida = st.selectbox("Hierba a plantar:", list(ALBION_DB["hierbas"].keys()))
    with col_c2:
        parcelas = st.number_input("Número de Parcelas activas:", min_value=1, value=10)
    with col_c3:
        ciudad_mercado = st.selectbox("Ciudad de Mercado:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort Sterling"])

    # Selector de tipo de venta para el impuesto
    tipo_venta = st.radio("¿Cómo vas a vender la cosecha?", ["Venta Directa (Solo Tax)", "Crear Orden de Venta (+2.5% Setup Fee)"])
    impuesto_total = tax_venta if "Venta Directa" in tipo_venta else (tax_venta + setup_fee)

    if st.button("Ejecutar Análisis de Granja"):
        id_semilla = ALBION_DB["hierbas"][hierba_elegida]["seed"]
        
        # Peticiones a la API
        precios = obtener_precios_completos([hierba_elegida, id_semilla], ciudad_mercado)
        datos_hist_hierba = obtener_historial_24h(hierba_elegida, ciudad_mercado)
        
        if not precios:
            st.error("Error conectando con Albion Data Project. Reintenta en unos segundos.")
        else:
            # Extracción de precios
            precio_venta_hierba = precios.get(hierba_elegida, {}).get("sell_min", 0)
            precio_compra_semilla = precios.get(id_semilla, {}).get("sell_min", 0) # Asumimos comprar semillas directo
            
            # Cálculos matemáticos
            bono_local = 1.1 if hierba_elegida in ALBION_DB["bonos_ciudad"].get(ciudad_mercado, []) else 1.0
            huecos_totales = parcelas * 9
            cosecha_estimada = math.floor(huecos_totales * 9 * bono_local)
            semillas_perdidas = math.ceil(huecos_totales * (1 - ALBION_DB["hierbas"][hierba_elegida]["return_base"]))
            
            ingreso_bruto = cosecha_estimada * precio_venta_hierba
            ingreso_neto = ingreso_bruto * (1 - impuesto_total)
            coste_reposicion = semillas_perdidas * precio_compra_semilla
            beneficio_real = ingreso_neto - coste_reposicion
            
            # Mostrar resultados
            st.markdown("---")
            st.success(f"### Beneficio Neto Estimado: {beneficio_real:,.0f} silver diarios")
            col_r1, col_r2 = st.columns(2)
            col_r1.metric(f"Ingreso (Vendiendo a {precio_venta_hierba}s)", f"{ingreso_neto:,.0f} silver", f"Impuesto aplicado: {impuesto_total*100:.1f}%")
            col_r2.metric("Coste Reposición Semillas", f"-{coste_reposicion:,.0f} silver", f"{semillas_perdidas} uds perdidas")
            
            # Tarjeta de Liquidez del Mercado
            with st.expander(f"📊 Ver análisis de mercado detallado para {hierba_elegida} en {ciudad_mercado}"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Orden de Venta (Sell)", f"{precios.get(hierba_elegida, {}).get('sell_min', 0)} s")
                c2.metric("Orden de Compra (Buy)", f"{precios.get(hierba_elegida, {}).get('buy_max', 0)} s")
                c3.metric("Precio Medio (24h)", f"{datos_hist_hierba['precio_medio']:.1f} s")
                c4.metric("Volumen Movido (24h)", f"{datos_hist_hierba['volumen']:,} uds")
                
                spread = precios.get(hierba_elegida, {}).get('sell_min', 0) - precios.get(hierba_elegida, {}).get('buy_max', 0)
                st.caption(f"**Análisis de Spread:** Hay una diferencia de {spread} silver entre compra y venta.")
