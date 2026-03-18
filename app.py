import streamlit as st
import requests
import math

# --- CONFIGURACIÓN Y DB ---
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
        "Curación Mayor (T6)": {"id": "T6_POTION_HEAL", "mats": {"T6_FOXGLOVE": 72, "T3_EGG": 18, "T1_ALCOHOL": 18}},
        "Veneno Mayor (T8)": {"id": "T8_POTION_COOLDOWN", "mats": {"T8_YARROW": 72, "T7_MULLEIN": 36, "T5_TEASEL": 36}},
        "Resistencia Mayor (T7)": {"id": "T7_POTION_STONESKIN", "mats": {"T7_MULLEIN": 72, "T6_FOXGLOVE": 36, "T5_EGG": 18}}
    },
    "bonos": {"Lymhurst": ["T4_BURDOCK"], "Martlock": ["T6_FOXGLOVE"], "Thetford": ["T7_MULLEIN", "T2_AGARIC"]}
}

@st.cache_data(ttl=60)
def get_p(ids):
    ciu = "Martlock,Caerleon,Lymhurst,Bridgewatch,Thetford,Fort_Sterling,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(ids)}?locations={ciu}&qualities=1"
    try:
        data = requests.get(url, timeout=10).json()
        res = {}
        for it in data:
            c = it['city'].replace(" ", "_")
            i = it['item_id']
            if it['sell_price_min'] > 0:
                if i not in res: res[i] = {}
                res[i][c] = {"s": it['sell_price_min'], "b": it['buy_price_max']}
        return res
    except: return {}

st.set_page_config(page_title="Albion Terminal", layout="wide")
st.sidebar.header("Perfil")
premium = st.sidebar.checkbox("Premium", value=True)
tax_v = 0.04 if premium else 0.08
s_fee = 0.025

t1, t2, t3 = st.tabs(["🌱 Cultivos", "🧪 Alquimia", "📈 Estrategia"])

with t1:
    st.header("Análisis de Granja")
    c1, c2, c3 = st.columns(3)
    with c1: ciu_i = st.selectbox("Isla en:", ["Martlock", "Caerleon", "Lymhurst", "Bridgewatch", "Thetford", "Fort_Sterling"])
    with c2: hie_e = st.selectbox("Planta:", list(ALBION_DB["hierbas"].keys()))
    with c3: parc = st.number_input("Parcelas:", min_value=1, value=10)
    
    if st.button("Analizar Cultivo"):
        info = ALBION_DB["hierbas"][hie_e]
        pg = get_p([hie_e, info["seed"]])
        if pg:
            bono = 1.1 if hie_e in ALBION_DB["bonos"].get(ciu_i, []) else 1.0
            h_tot = parc * 9
            cosecha = math.floor(h_tot * 9 * bono)
            s_perd = math.ceil(h_tot * (1 - info["ret"]))
            
            m_h = pg.get(hie_e, {})
            c_v_o = max(m_h, key=lambda k: m_h[k]['s']) if m_h else ciu_i
            p_v_o = m_h.get(c_v_o, {}).get('s', 0)
            
            m_s = pg.get(info["seed"], {})
            c_c_o = min(m_s, key=lambda k: m_s[k]['s']) if m_s else ciu_i
            p_s_o = m_s.get(c_c_o, {}).get('s', 0)
            
            ing_n = (cosecha * p_v_o) * (1 - tax_v)
            cost_s = (s_perd * p_s_o)
            
            st.success(f"### Beneficio Neto: {ing_n - cost_s:,.0f} silver")
            st.info(f"Retorno: {info['ret']*100:.1f}% | Repones {s_perd} semillas")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"Vender en {c_v_o}", f"{ing_n:,.0f} s")
                with st.expander("Otros mercados"):
                    for c, d in m_h.items(): st.write(f"{c}: {d['s']} s")
            with col2:
                st.metric(f"Semillas en {c_c_o}", f"-{cost_s:,.0f} s")
                with st.expander("Otros precios"):
                    for c, d in m_s.items(): st.write(f"{c}: {d['s']} s")

with t2:
    st.header("Escáner de Alquimia")
    a1, a2, a3 = st.columns(3)
    with a1: p_sel = st.selectbox("Poción:", list(ALBION_DB["recetas"].keys()))
    with a2: e_sel = st.selectbox("Encanto:", [0, 1, 2, 3])
    with a3: cant = st.number_input("Cantidad:", min_value=5, step=5, value=100)
    foco = st.checkbox("Usar Foco", value=True)
    
    if st.button("Escanear Rentabilidad"):
        rec = ALBION_DB["recetas"][p_sel]
        id_f = f"{rec['id']}@{e_sel}" if e_sel > 0 else rec['id']
        pg = get_p([id_f] + list(rec["mats"].keys()))
        if pg:
            c_tot = 0
            rrr = 0.482 if foco else 0.248
            st.markdown("### 🛒 Compras Optimizadas")
            for m, qb in rec["mats"].items():
                qr = math.ceil((qb * (cant/5)) * (1 - rrr))
                m_m = pg.get(m, {})
                cb = min(m_m, key=lambda k: m_m[k]['s']) if m_m else "N/A"
                pb = m_m.get(cb, {}).get('s', 0)
                c_tot += (qr * pb)
                st.write(f"**{m}**: {qr} uds en **{cb}** ({qr*pb:,.0f} s)")
            
            m_p = pg.get(id_f, {})
            cv = max(m_p, key=lambda k: m_p[k]['s']) if m_p else "Brecilien"
            pv = m_p.get(cv, {}).get('s', 0)
            ing = (cant * pv) * (1 - tax_v)
            st.markdown("---")
            st.metric(f"Beneficio Vendiendo en {cv}", f"{ing - c_tot:,.0f} s")

with t3:
    st.header("Estrategia Cruzada")
    st.write("Compara si te sale más rentable vender tu cosecha o transformarla.")
