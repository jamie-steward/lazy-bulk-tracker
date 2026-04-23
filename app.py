import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client

st.set_page_config(page_title="Lazy Bulk Tracker", page_icon="💪")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

st.title("💪 Lazy Bulk Tracker")


user_name = "rob"
st.write("Tracking for Rob 💪")

entry_date = st.date_input("Date", value=date.today())


response = (
    supabase.table("bulk_weights")
    .select("*")
    .eq("user_name", user_name)
    .order("entry_date")
    .execute()
)

df = pd.DataFrame(response.data)

entry_count = len(df)

if not df.empty:
    last_weight = float(df.iloc[-1]["weight_kg"])
else:
    last_weight = 55.0  # default starting weight

weight = st.number_input(
    "Morning weight (kg)",
    value=last_weight,
    step=0.1
)

if st.button("Save weight"):
    supabase.table("bulk_weights").upsert({
        "user_name": user_name,
        "entry_date": str(entry_date),
        "weight_kg": weight
    }).execute()

    st.success("Saved.")

st.metric("Rob's total weigh-ins", entry_count)

st.write(df.drop(columns=["id"]))

if df.empty:
    st.info("No weigh-ins yet.")
    st.stop()

df = df.sort_values("entry_date")
df["entry_date"] = pd.to_datetime(df["entry_date"])

st.line_chart(df.set_index("entry_date")["weight_kg"])

if len(df) >= 14:
    latest_7 = df.tail(7)["weight_kg"].mean()
    previous_7 = df.tail(14).head(7)["weight_kg"].mean()
    weekly_gain = latest_7 - previous_7

    st.metric("Latest 7-day avg", f"{latest_7:.2f} kg")
    st.metric("Weekly gain", f"{weekly_gain:.2f} kg/week")

    if weekly_gain < 0.25:
        st.warning("Eat more. Add 200–300 kcal/day.")
    elif weekly_gain <= 0.5:
        st.success("Perfect. Keep going.")
    else:
        st.error("Too fast. Reduce calories slightly.")
else:
    st.info("Log 14 days to unlock advice.")