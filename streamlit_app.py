
import streamlit as st
import pandas as pd

# Weighted AVG calculator
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

# Binomial hit probability over 4 ABs
def hit_probability(avg, ab=4):
    return round(1 - (1 - avg)**ab, 4)

# Value zone classification
def get_zone(prob):
    if prob >= 0.80:
        return "Elite"
    elif prob >= 0.70:
        return "Strong"
    elif prob >= 0.60:
        return "Moderate"
    else:
        return "Bad"

# Implied % from odds
def implied_probability(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)

# EV Tag
def ev_rating(true_hit_prob, implied_prob):
    ev = true_hit_prob - implied_prob
    if ev >= 0.15:
        return "🔥 High Value"
    elif ev >= 0.05:
        return "✅ Fair"
    else:
        return "⚠️ Negative EV"

# ---------------- STREAMLIT UI ----------------
st.title("💰 Moneyball Phil: Daily Hit Board")

uploaded_file = st.file_uploader("📂 Upload Your Player CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["WeightedAVG"] = df.apply(calculate_weighted_avg, axis=1)
    df["TrueHit%"] = df["WeightedAVG"].apply(lambda x: hit_probability(x) * 100)
    df["HitZone"] = df["TrueHit%"].apply(get_zone)

    df["Odds"] = df["Odds"].astype(float)
    df["Implied%"] = df["Odds"].apply(implied_probability).round(4) * 100
    df["EV%"] = (df["TrueHit%"] - df["Implied%"]).round(2)
    df["ValueTag"] = df.apply(lambda row: ev_rating(row["TrueHit%"] / 100, row["Implied%"] / 100), axis=1)

    df = df.sort_values(by="TrueHit%", ascending=False)

    st.success("✅ Top Hit Board Generated")
    st.dataframe(df[["Player", "Team", "TrueHit%", "Odds", "Implied%", "EV%", "ValueTag", "HitZone"]])
