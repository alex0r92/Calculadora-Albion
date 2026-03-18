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
                if item['sell_price_min'] > 0 or item['
