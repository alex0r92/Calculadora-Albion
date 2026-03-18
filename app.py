import streamlit as st
import requests
import math

# --- BASE DE DATOS ---
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
    "bonos": {"Lymhurst": ["T4_BURDOCK"], "Martlock": ["T6_FOXGLOVE"], "Thetford": ["T7_MULLEIN", "T2_AGARIC"]}
}

@st.cache_data(ttl=60)
def get_p(ids):
    c = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(ids)}?locations={c}&qualities=1"
    try:
        data = requests.get(url, timeout=10).json()
        res = {}
        for it in data:
            ciu = it['city'].replace(" ", "_")
            item = it['item_id']
            if it['sell_price_min'] > 0:
                if item not in res: res[item] = {}
                res[item][ciu] = {"s": it['sell_price_min'], "b": it['buy_price_max']}
        return res
    except: return {}

# --- INTERFAZ ---
st.set_page_config(page_title="Albion Terminal", layout="wide")
st.title("⚖️ Terminal de Mercado")

st.sidebar.header("Perfil")
premium = st.sidebar.checkbox("Premium", value=True)
tax_v = 0.04 if premium else 0.08

t1, t2 = st.tabs(["🌱 Cultivos", "🧪 Alquimia (Próximamente)"])

with t1:
    st.header("Rentabilidad de Granja")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_i = st.selectbox("Isla en:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling"])
    with c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Parcelas:", min_value=1, value=10)
    
    if st.button("Analizar Cultivo"):
        info = ALBION_DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            # Cálculos de producción
            bono = 1.1 if hie_e in ALBION_DB["bonos"].get(ciu_i, []) else 1.0
            h_tot = parc * 9
            cosecha = math.floor(h_tot * 9 * bono)
            s_perd = math.ceil(h_tot * (1 - info["ret"]))
            
            # 1. Escáner de Semillas (DÓNDE COMPRAR)
            m_s = {k: v for k, v in pg.get(info["seed"], {}).items() if v['s'] > 0}
            c_c_o = min(m_s, key=lambda k: m_s[k]['s']) if m_s else ciu_i
            p_s_o = m_s.get(c_c_o, {}).get('s', 0)
            
            # 2. Escáner de Hierbas (DÓNDE VENDER)
            m_h = {k: v for k, v in pg.get(hie_e, {}).items() if v['s'] > 0}
            c_v_o = max(m_h, key=lambda k: m_h[k]['s']) if m_h else ciu_i
            p_v_o = m_h.get(c_v_o, {}).get('s', 0)
            
            # Resultados financieros
            ing_n = (cosecha * p_v_o) * (1 - tax_v)
            cost_s = s_perd * p_s_o
            beneficio = ing_n - cost_s
            
            st.success(f"### Beneficio Neto Estimado: {beneficio:,.0f} silver diarios")
            st.markdown(f"🌱 **Análisis de Producción:** Con un retorno del **{info['ret']*100:.1f}%**, de los {h_tot} huecos plantados, solo recuperas parte de las semillas. Debes reponer **{s_perd}** semillas diarias.")

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(f"Vender en {c_v_o.replace('_',' ')}", f"{ing_n:,.0f} s", f"A {p_v_o}s/ud")
                with st.expander("Ver otros mercados de venta"):
                    for c, d in m_h.items():
                        if c != c_v_o: st.write(f"**{c.replace('_',' ')}**: {d['s']} s")
            
            with col_b:
                st.metric(f"Semillas en {c_c_o.replace('_',' ')}", f"-{cost_s:,.0f} s", f"A {p_s_o}s/ud")
                with st.expander("Ver otros precios de semillas"):
                    for c, d in m_s.items():
                        if c != c_c_o: st.write(f"**{c.replace('_',' ')}**: {d['s']} s")
