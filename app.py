import streamlit as st
import requests
import math

ALBION_DB = {
    "bonos_ciudad": {
        "Lymhurst": ["T4_BURDOCK"], "Bridgewatch": ["T5_TEASEL"], "Martlock": ["T6_FOXGLOVE"],
        "Thetford": ["T7_MULLEIN", "T2_AGARIC"], "Fort_Sterling": ["T8_YARROW"],
        "Caerleon": ["T3_COMFREY", "T5_TEASEL", "T7_MULLEIN"], "Brecilien": [] 
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
        "Curación Mayor (T6)": {"id_base": "T6_POTION_HEAL", "tier_extracto": "T6", "rama": "Curación", "foco_base": 1648, "mats": {"T6_FOXGLOVE": 72, "T3_EGG": 18, "T1_ALCOHOL": 18}},
        "Veneno Mayor (T8)": {"id_base": "T8_POTION_COOLDOWN", "tier_extracto": "T8", "rama": "Veneno", "foco_base": 2736, "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36, "T6_MILK": 18, "T8_ALCOHOL": 18}},
        "Resistencia Mayor (T7)": {"id_base": "T7_POTION_STONESKIN", "tier_extracto": "T8", "rama": "Resistencia", "foco_base": 2736, "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18, "T7_ALCOHOL": 18}}
    }
}

@st.cache_data(ttl=60)
def obtener_precios_globales(lista_ids):
    if not lista_ids: return {}
    ciu = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(lista_ids)}?locations={ciu}&qualities=1"
    try:
        data = requests.get(url, timeout=10).json()
        res = {}
        for it in data:
            c = "Fort_Sterling" if it['city'] == "Fort Sterling" else it['city']
            i = it['item_id']
            if it['sell_price_min'] > 0:
                if i not in res: res[i] = {}
                res[i][c] = {"sell": it['sell_price_min'], "buy": it['buy_price_max']}
        return res
    except: return {}
        st.set_page_config(page_title="Albion Terminal", layout="wide")
st.title("⚖️ Terminal de Mercado")

st.sidebar.header("Perfil")
premium = st.sidebar.checkbox("Premium", value=True)
tax_v = 0.04 if premium else 0.08
s_fee = 0.025
spec_b = st.sidebar.slider("Espec. Base", 0, 100, 100)
spec_p = st.sidebar.slider("Espec. Poción", 0, 100, 100)

t1, t2, t3 = st.tabs(["🌱 Cultivos", "🧪 Alquimia", "📈 Estrategia"])

with t1:
    st.header("Rentabilidad Granja")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_c = st.selectbox("Isla en:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling"])
    with c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Parcelas:", min_value=1, value=10)
    
    if st.button("Analizar Cultivo"):
        pg = obtener_precios_globales([hie_e, ALBION_DB["hierbas"][hie_e]["seed"]])
        if pg:
            bono = 1.1 if hie_e in ALBION_DB["bonos_ciudad"].get(ciu_c, []) else 1.0
            h_tot = parc * 9
            cos_est = math.floor(h_tot * 9 * bono)
            ret_b = ALBION_DB["hierbas"][hie_e]["return_base"]
            s_perd = math.ceil(h_tot * (1 - ret_b))
            
            p_h = pg.get(hie_e, {}).get(ciu_c, {}).get('sell', 0)
            p_s = pg.get(ALBION_DB["hierbas"][hie_e]["seed"], {}).get(ciu_c, {}).get('sell', 0)
            
            benef = (cos_est * p_h * (1-tax_v)) - (s_perd * p_s)
            st.metric("Beneficio Diario Estimado", f"{benef:,.0f} silver")

with t2:
    st.header("Crafteo en Brecilien")
    if st.button("Escanear Alquimia"):
        st.write("Calculando márgenes con precios de Brecilien...")
        # Aquí irá el escáner de pociones

with t3:
    st.write("Módulo de Estrategia Cruzada en desarrollo.")
