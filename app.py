import streamlit as st
import requests
import math

# ==========================================
# 1. BASE DE DATOS MAESTRA
# ==========================================
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
}@st.cache_data(ttl=60)
def obtener_precios_globales(lista_ids):
    if not lista_ids: return {}
    ciudades = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(lista_ids)}?locations={ciudades}&qualities=1"
    try:
        data = requests.get(url, timeout=10)
        if data.status_code == 200:
            res = {}
            for it in data.json():
                c = "Fort_Sterling" if it['city'] == "Fort Sterling" else it['city']
                i = it['item_id']
                if it['sell_price_min'] > 0 or it['buy_price_max'] > 0:
                    if i not in res: res[i] = {}
                    res[i][c] = {"sell": it['sell_price_min'], "buy": it['buy_price_max']}
            return res
        return {}
    except: return {}

@st.cache_data(ttl=300)
def obtener_historial_24h(item_id, ciudad):
    url = f"https://www.albion-online-data.com/api/v2/stats/history/{item_id}?locations={ciudad}&time-scale=24&qualities=1"
    try:
        data = requests.get(url, timeout=10)
        if data.status_code == 200 and len(data.json()) > 0:
            h = data.json()[0].get('data', [])
            if h: return {"med": h[-1].get('average_price', 0), "vol": h[-1].get('item_count', 0)}
        return {"med": 0, "vol": 0}
    except: return {"med": 0, "vol": 0}

st.set_page_config(page_title="Albion Market Terminal", layout="wide")
st.title("⚖️ Terminal de Mercado y Logística")

st.sidebar.header("Módulo 0: Perfil")
premium = st.sidebar.checkbox("Premium Activo", value=True)
tax_v = 0.04 if premium else 0.08
s_fee = 0.025
spec_b = st.sidebar.slider("Alquimista (Base)", 0, 100, 100)
with st.sidebar.expander("Specs de Pociones"):
    specs = {
        "Curación": st.slider("Curación", 0, 100, 100), "Energía": st.slider("Energía", 0, 100, 0),
        "Gigantismo": st.slider("Gigantismo", 0, 100, 0), "Resistencia": st.slider("Resistencia", 0, 100, 0),
        "Pegajosa": st.slider("Pegajosa", 0, 100, 0), "Invisibilidad": st.slider("Invisibilidad", 0, 100, 0),
        "Veneno": st.slider("Veneno", 0, 100, 0), "Limpieza": st.slider("Limpieza", 0, 100, 0),
        "Ácido": st.slider("Ácido", 0, 100, 0), "Calmante": st.slider("Calmante", 0, 100, 0),
        "Recolección": st.slider("Recolección", 0, 100, 0), "Fuego Infernal": st.slider("Fuego Infernal", 0, 100, 0),
        "Berserker": st.slider("Berserker", 0, 100, 0), "Tornado": st.slider("Tornado", 0, 100, 0),
        "Destilados": st.slider("Destilados", 0, 100, 0)
    }

t1, t2, t3 = st.tabs(["🌱 1. Cultivos", "🧪 2. Alquimia Inteligente", "📈 3. Estrategia Cruzada"])
with t1:
    st.header("Rentabilidad Agrícola")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_c = st.selectbox("Ciudad isla:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling", "Brecilien"])
    with c2: hie_e = st.selectbox("Hierba:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Parcelas:", min_value=1, value=10)

    t_v = st.radio("Venta:", ["Directa", "Orden (+2.5%)"])
    imp_t = tax_v if "Directa" in t_v else (tax_v + s_fee)

    if st.button("Calcular Granja"):
        id_s = ALBION_DB["hierbas"][hie_e]["seed"]
        pg = obtener_precios_globales([hie_e, id_s])
        if pg:
            bono = 1.1 if hie_e in ALBION_DB["bonos_ciudad"].get(ciu_c, []) else 1.0
            h_tot = parc * 9
            cos_est = math.floor(h_tot * 9 * bono)
            ret_b = ALBION_DB["hierbas"][hie_e]["return_base"]
            s_perd = math.ceil(h_tot * (1 - ret_b))
            
            m_s = {k: v for k, v in pg.get(id_s, {}).items() if v['sell'] > 0}
            c_s_o = min(m_s, key=lambda k: m_s[k]['sell']) if m_s else ciu_c
            p_s_o = m_s.get(c_s_o, {}).get('sell', 0)

            m_h = {k: v for k, v in pg.get(hie_e, {}).items() if v['sell'] > 0}
            c_h_o = max(m_h, key=lambda k: m_h[k]['sell']) if m_h else ciu_c
            p_h_o = m_h.get(c_h_o, {}).get('sell', 0)

            i_neto = (cos_est * p_h_o) * (1 - imp_t)
            c_rep = s_perd * p_s_o
            st.success(f"### Beneficio: {i_neto - c_rep:,.0f} silver/día")
            st.caption(f"Retorno: {ret_b*100:.1f}%. Repones {s_perd} semillas.")
            r1, r2 = st.columns(2)
            r1.metric(f"Venta en {c_h_o}", f"{i_neto:,.0f} s")
            r2.metric(f"Semillas en {c_s_o}", f"-{c_rep:,.0f} s")
            with t2:
    st.header("Alquimia Inteligente")
    a1, a2, a3, a4 = st.columns(4)
    with a1: p_alq = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()))
    with a2: e_alq = st.selectbox("Encantamiento:", [0,1,2,3,4], format_func=lambda x: f".{x}")
    with a3: q_alq = st.number_input("Cantidad:", min_value=5, step=5, value=1000)
    with a4: f_alq = st.checkbox("Foco", value=True)
    
    t_c = st.radio("Compra:", ["Directa", "Orden (+2.5%)"])

    if st.button("Escanear Alquimia"):
        rec = ALBION_DB["recetas"][p_alq]
        crf = math.ceil(q_alq / 5)
        rrr = 0.482 if f_alq else 0.248
        id_f = f"{rec['id_base']}@{e_alq}" if e_alq > 0 else rec['id_base']
        m_list = rec["mats"].copy()
        if e_alq > 0: m_list[f"{rec['tier_extracto']}_ARCANE_EXTRACT"] = 18 * e_alq
        pg = obtener_precios_globales([id_f] + list(m_list.keys()))
        if pg:
            c_m_t = 0
            for m, qb in m_list.items():
                qr = math.ceil((qb * crf) * (1 - rrr))
                m_m = {k: v for k, v in pg.get(m, {}).items() if v['sell'] > 0}
                ciu_b = min(m_m, key=lambda k: m_m[k]['sell']) if m_m else "N/A"
                p_m = m_m.get(ciu_b, {}).get('sell', 0)
                cost = (qr * p_m) * (1.025 if "Orden" in t_c else 1)
                c_m_t += cost
                st.write(f"- {m}: {qr} uds en **{ciu_b}** ({cost:,.0f} s)")
            
            m_p = {k: v for k, v in pg.get(id_f, {}).items() if v['sell'] > 0}
            ciu_c = max(m_p, key=lambda k: m_p[k]['sell']) if m_p else "Brecilien"
            p_v = m_p.get(ciu_c, {}).get('sell', 0)
            i_n = (q_alq * p_v) * (1 - tax_v)
            
            ram = rec["rama"]
            n_ex = sum(v for k, v in specs.items() if k != ram)
            efi = (spec_b * 30) + (specs.get(ram, 0) * 250) + (n_ex * 18)
            f_t = (rec["foco_base"] * (0.5**(efi/10000))) * crf
            
            st.markdown("---")
            res1, res2, res3 = st.columns(3)
            res1.metric(f"Ingreso ({ciu_c})", f"{i_n:,.0f} s")
            res2.metric("Beneficio", f"{i_n - c_m_t:,.0f} s")
            res3.metric("Foco Total", f"{f_t:,.0f} pts")

with t3:
    st.header("Estrategia Cruzada")
    st.write("Módulo en construcción. Usa las pestañas 1 y 2 para comparar manualmente por ahora.")
