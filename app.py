import streamlit as st
import pandas as pd
import random

# 1. Base Standings
initial_standings = {
    "Hajraa HS 1": 50, "NUMIDIA VC LIMAX HS 3": 49, "ROWI HS 1": 46,
    "Dunamis HS 1": 45, "Donki Sjot HS 1": 45, "Tupos HS 1": 42,
    "Peelpush HS 2": 41, "Volley Tilburg HS 2": 39,
    "Van Hoorn Carbide VC Weert HS 1": 27, "VC Landgraaf-VC FUROS comb. HS 1": 16
}

# 2. Remaining Matches
matches = [
    ("Van Hoorn Carbide VC Weert HS 1", "ROWI HS 1"),
    ("Tupos HS 1", "NUMIDIA VC LIMAX HS 3"),
    ("Peelpush HS 2", "Donki Sjot HS 1"),
    ("Hajraa HS 1", "Volley Tilburg HS 2"),
    ("Dunamis HS 1", "VC Landgraaf-VC FUROS comb. HS 1"),
    ("ROWI HS 1", "Tupos HS 1"),
    ("NUMIDIA VC LIMAX HS 3", "Dunamis HS 1"),
    ("Volley Tilburg HS 2", "Peelpush HS 2"),
    ("Donki Sjot HS 1", "Van Hoorn Carbide VC Weert HS 1"),
    ("VC Landgraaf-VC FUROS comb. HS 1", "Hajraa HS 1")
]

score_options = {
    "Select result...": None,
    "4-0 win": (5, 0), "3-1 win": (4, 1), "3-2 win": (3, 2),
    "2-3 loss": (2, 3), "1-3 loss": (1, 4), "0-4 loss": (0, 5)
}

st.set_page_config(page_title="Volleybal Predictor", layout="wide")
st.title("🏐 Volleybal Scenario & Probability Calculator")

# Sidebar for Inputs
st.sidebar.header("Uitslagen Vastzetten")
fixed_results = {}
for i, (t1, t2) in enumerate(matches):
    res = st.sidebar.selectbox(f"{t1} vs {t2}", list(score_options.keys()), key=i)
    fixed_results[(t1, t2)] = score_options[res]

# Layout: Two columns
col1, col2 = st.columns(2)

# --- COLUMN 1: MANUAL STANDINGS ---
with col1:
    st.subheader("Huidige Stand (Handmatig)")
    manual_points = initial_standings.copy()
    for (t1, t2), pts in fixed_results.items():
        if pts:
            manual_points[t1] += pts[0]
            manual_points[t2] += pts[1]
    
    df_manual = pd.DataFrame(list(manual_points.items()), columns=['Team', 'Punten']).sort_values('Punten', ascending=False).reset_index(drop=True)
    df_manual.index += 1
    st.table(df_manual)

# --- COLUMN 2: PROBABILITIES (Monte Carlo) ---
with col2:
    st.subheader("Kansberekening (%)")
    num_simulations = st.slider("Aantal simulaties", 1000, 100000, 50000)
    
    if st.button("Bereken Kansen 🚀"):
        results = {team: {"P1": 0, "P2": 0, "P8": 0} for team in initial_standings}
        all_possible_pts = [(5,0), (4,1), (3,2), (2,3), (1,4), (0,5)]
        
        with st.spinner('Simuleren...'):
            for _ in range(num_simulations):
                sim_points = initial_standings.copy()
                for (t1, t2), pts in fixed_results.items():
                    if pts: # If user fixed a result
                        sim_points[t1] += pts[0]
                        sim_points[t2] += pts[1]
                    else: # Random outcome for simulation
                        p1, p2 = random.choice(all_possible_pts)
                        sim_points[t1] += p1
                        sim_points[t2] += p2
                
                # Rank results
                sorted_sim = sorted(sim_points.items(), key=lambda x: (x[1], random.random()), reverse=True)
                results[sorted_sim[0][0]]["P1"] += 1
                results[sorted_sim[1][0]]["P2"] += 1
                results[sorted_sim[7][0]]["P8"] += 1

        # Process stats
        stats_list = []
        for team, counts in results.items():
            stats_list.append({
                "Team": team,
                "Kampioen (P1)": f"{(counts['P1']/num_simulations)*100:.1f}%",
                "Promotie (P2)": f"{(counts['P2']/num_simulations)*100:.1f}%",
                "Degradatie (P8)": f"{(counts['P8']/num_simulations)*100:.1f}%"
            })
        
        df_stats = pd.DataFrame(stats_list).sort_values("Kampioen (P1)", ascending=False)
        st.dataframe(df_stats, use_container_width=True)
        st.caption(f"Gebaseerd op {num_simulations} willekeurige uitkomsten voor niet-ingevulde wedstrijden.")
