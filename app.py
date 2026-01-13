import streamlit as st
import pandas as pd
import random
import numpy as np

st.title("Personalized Diet Meal Cost Optimizer")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(data.head())

    # ---- USER INPUTS ----
    st.sidebar.header("User Profile")

    weight = st.sidebar.number_input("Weight (kg)", 30, 200, 60)
    activity = st.sidebar.selectbox("Activity Level", ["Low", "Moderate", "High"])
    diet_pref = st.sidebar.selectbox("Dietary Preference", data["Dietary Preference"].unique())
    disease = st.sidebar.selectbox("Disease", data["Disease"].unique())

    # ---- CALCULATE DAILY NEEDS BASED ON WEIGHT ----
    if activity == "Low":
        req_cal = weight * 25
    elif activity == "Moderate":
        req_cal = weight * 30
    else:
        req_cal = weight * 35

    req_pro = weight * 0.8               # simple safe guideline
    req_fat_max = 0.35 * req_cal / 9     # WHO guideline upper bound

    st.sidebar.write(f"Estimated calorie need: {req_cal:.0f} kcal/day")

    # ---- FILTER DATA BASED ON USER ----
    filtered = data[
        (data["Dietary Preference"] == diet_pref) &
        (data["Disease"] == disease)
    ].copy()

    if filtered.empty:
        st.error("No food matches your dietary preference and disease filter!")
    else:
        st.success(f"{len(filtered)} meals available after filtering")

    # ---- COLUMN NAMES ----
    CAL = "Calories"
    PRO = "Protein"
    FAT = "Fat"
    PRICE = "Price_RM"

    # ---- FITNESS FUNCTION ----
    def fitness(solution):
        meals = filtered.loc[solution]

        total_cal = meals[CAL].sum()
        total_pro = meals[PRO].sum()
        total_fat = meals[FAT].sum()
        total_cost = meals[PRICE].sum()

        penalty = 0

        if total_cal < req_cal:
            penalty += (req_cal - total_cal) * 0.2

        if total_pro < req_pro:
            penalty += (req_pro - total_pro) * 0.5

        if total_fat > req_fat_max:
            penalty += (total_fat - req_fat_max) * 0.5

        return total_cost + penalty

    # ---- EVOLUTION STRATEGY ----
    def evolve():
        n = len(filtered)

        # index positions for meals
        population = [
            [
                random.randrange(n),  # breakfast
                random.randrange(n),  # lunch
                random.randrange(n),  # dinner
                random.randrange(n)   # snack
            ]
            for _ in range(50)
        ]

        for _ in range(300):

            offspring = []

            for parent in population:
                child = parent.copy()
                # mutation
                for i in range(4):
                    if random.random() < 0.3:
                        child[i] = random.randrange(n)
                offspring.append(child)

            # select best
            population = sorted(population + offspring, key=fitness)[:50]

        return population[0]

    # ---- RUN OPTIMIZATION ----
    if st.button("Optimize Meal Plan"):
        best = evolve()
        result = filtered.loc[best].reset_index(drop=True)

        st.subheader("Selected Meals")

        st.write("🍳 Breakfast:", result.loc[0, "Breakfast Suggestion"], " — RM", result.loc[0, PRICE])
        st.write("🍚 Lunch:", result.loc[1, "Lunch Suggestion"], " — RM", result.loc[1, PRICE])
        st.write("🍛 Dinner:", result.loc[2, "Dinner Suggestion"], " — RM", result.loc[2, PRICE])
        st.write("🍎 Snack:", result.loc[3, "Snack Suggestion"], " — RM", result.loc[3, PRICE])

        total_cost = result[PRICE].sum()
        total_cal = result[CAL].sum()
        total_pro = result[PRO].sum()
        total_fat = result[FAT].sum()

        st.subheader("Daily Totals")
        st.write(f"💰 Cost: RM {total_cost:.2f}")
        st.write(f"🔥 Calories: {total_cal:.0f} kcal")
        st.write(f"💪 Protein: {total_pro:.1f} g")
        st.write(f"🧈 Fat: {total_fat:.1f} g")

        # requirement status
        if total_cal < req_cal:
            st.warning("Calories requirement NOT met")
        if total_pro < req_pro:
            st.warning("Protein requirement NOT met")
        if total_fat > req_fat_max:
            st.warning("Fat limit exceeded")

else:
    st.info("Upload a CSV file to start.")
