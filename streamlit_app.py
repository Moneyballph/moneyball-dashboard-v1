
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Moneyball Phil", layout="wide")

st.markdown(
    """
    <style>
    .main {
        background-image: url("https://images.unsplash.com/photo-1546519638-68e109498ffc?ixlib=rb-4.0.3&auto=format&fit=crop&w=1400&q=80");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .stApp {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⚾ Moneyball Phil: Daily Betting Dashboard")

@st.cache_data
def load_initial_data():
    return pd.read_csv("top_hit_input.csv")

df = load_initial_data()

with st.form("add_player_form"):
    st.subheader("➕ Add a Player to Analyze")
    name = st.text_input("Player Name")
    team = st.text_input("Team")
    last7 = st.number_input("Last 7 Days AVG", format="%.3f")
    vshand = st.number_input("Vs Handedness AVG", format="%.3f")
    pitcher = st.number_input("Pitcher AVG (0 if none)", format="%.3f")
    default = st.number_input("Default AVG", format="%.3f")
    odds = st.number_input("Odds (e.g. -200)", step=1.0)

    submitted = st.form_submit_button("Add to Top Hit Board")

if submitted:
    new_row = pd.DataFrame([{
        "Player": name,
        "Team": team,
        "Last7AVG": last7,
        "VsHandAVG": vshand,
        "PitcherAVG": pitcher,
        "DefaultAVG": default,
        "Odds": odds
    }])
    df = pd.concat([df, new_row], ignore_index=True)

def calculate_weighted_avg(row):
    w1, w2, w3, w4 = 0.3, 0.3, 0.3, 0.1
    pitcher_weight = w3 if row["PitcherAVG"] > 0 else 0.1
    default_weight = w4 if row["PitcherAVG"] > 0 else 0.3
    return (
        row["Last7AVG"] * w1 +
        row["VsHandAVG"] * w2 +
        row["PitcherAVG"] * pitcher_weight +
        row["DefaultAVG"] * default_weight
    )

def hit_probability(avg, ab=4):
    return round(1 - (1 - avg)**ab, 4)

def get_zone(prob):
    if prob >= 0.80:
        return "Elite"
    elif prob >= 0.70:
        return "Strong"
    elif prob >= 0.60:
        return "Moderate"
    else:
        return "Bad"

def implied_probability(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)

def ev_rating(true_hit_prob, implied_prob):
    ev = true_hit_prob - implied_prob
    if ev >= 0.15:
        return "🔥 High Value"
    elif ev >= 0.05:
        return "✅ Fair"
    else:
        return "⚠️ Negative EV"

if not df.empty:
    df["WeightedAVG"] = df.apply(calculate_weighted_avg, axis=1)
    df["TrueHit%"] = df["WeightedAVG"].apply(lambda x: hit_probability(x) * 100)
    df["HitZone"] = df["TrueHit%"].apply(get_zone)
    df["Odds"] = df["Odds"].astype(float)
    df["Implied%"] = df["Odds"].apply(implied_probability).round(4) * 100
    df["EV%"] = (df["TrueHit%"] - df["Implied%"]).round(2)
    df["ValueTag"] = df.apply(lambda row: ev_rating(row["TrueHit%"] / 100, row["Implied%"] / 100), axis=1)
    df = df.sort_values(by="TrueHit%", ascending=False)
    st.dataframe(df[["Player", "Team", "TrueHit%", "Odds", "Implied%", "EV%", "ValueTag", "HitZone"]])
