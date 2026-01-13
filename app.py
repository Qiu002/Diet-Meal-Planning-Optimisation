import streamlit as st
import pandas as pd
import numpy as np
import random

st.title("Diet Meal Optimizer with Evolution Strategy")

uploaded_file = st.file_uploader("Upload Food_and_Nutrition_with_Price CSV", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(data.head())

    # ----------- COLUMN KEYS ----------
    CAL = "Calories"
    PRO = "Protein"
    FAT = "Fat"
    PRICE = "Price_RM"
    PREF = "Dietary Preference"
    DISEASE = "Disease"
    WEIGHT = "Weight"

    # ----------- USER FILTER INPUT ----------
    st.sidebar.header("User Profile Filters")

    user_weight = st.sidebar.number_input("Your Weight (kg)", 30, 200, 60)
    user_pref = st.sidebar.selectbox("Dietary Preference", ["Any", "Vegetarian", "Non-Vegetarian", "Vegan"])
    user_disease = st.sidebar.selectbox("Health Condition", ["None", "Diabetes", "Hypertension"])

    # ----------- DAILY REQUIREMENTS ----------
    st.sidebar.header("Daily Nutrition Requirements")

    # Suggest calories based on weight (30 kcal/kg simple estimate)
    suggested_cal = int(user_weight * 30)

    req_cal = st.sidebar.number_input("Minimum Calories", 1200, 4000, suggested_cal)
    req_pro = st.sidebar.number_input("Minimum Protein (g)", 20, 300, 60)
    req_fat = st.sidebar.number_input("Maximum Fat (g)", 10, 300, 80)

    # ----------- HEALTH FILTERING ----------
    filtered = data.copy()

    if user_pref != "Any":
        filtered = filtered[filtered[PREF] == user_pref]

    if user_disease == "Diabetes":
        filtered = filtered[filtered["Sugar"] < 20]

    if user_disease == "Hypertension":
        filtered = filtered[filtered["Sodium"] < 400]

    st.write("Filtered Foods Count:", len(filtered))

    # ----------- FITNESS FUNCTION ----------
    def fitness(solution):
        meals = filtered.loc[solution]

        total_cal = meals[CAL].sum()
        total_pro = meals[PRO].sum()
        total_fat = meals[FAT].sum()
        total_cost = meals[PRICE].sum()

        penalty = 0

        if total_cal < req_cal:
            penalty += (req_cal - total_cal) * 0.5

        if total_pro < req_pro:
            penalty += (req_pro - total_pro) * 1.0

        if total_fat > req_fat:
            penalty += (total_fat - req_fat) * 1.0

        return total_cost + penalty

    # ----------- EVOLUTION STRATEGY ----------
    def evolve():
        n = len(filtered)
        population = [np.random.randint(0, n, 4) for _ in range(40)]

        for _ in range(300):
            offspring = []
            for parent in population:
                child = parent.copy()
                for i in range(4):
                    if random.random() < 0.3:
                        child[i] = random.randrange(n)
                offspring.append(child)

            population = sorted(population + offspring, key=fitness)[:40]

        return population[0]

    # ----------- RUN ----------
    if st.button("Optimize Meal Plan"):
        best = evolve()
        meals = filtered.iloc[best].reset_index(drop=True)

        st.subheader("Selected Meals")
        st.write("Breakfast :", meals.loc[0, "Breakfast Suggestion"], "RM", meals.loc[0, PRICE])
        st.write("Lunch :", meals.loc[1, "Lunch Suggestion"], "RM", meals.loc[1, PRICE])
        st.write("Dinner :", meals.loc[2, "Dinner Suggestion"], "RM", meals.loc[2, PRICE])
        st.write("Snack :", meals.loc[3, "Snack Suggestion"], "RM", meals.loc[3, PRICE])

        total_cost = meals[PRICE].sum()
        total_cal = meals[CAL].sum()
        total_pro = meals[PRO].sum()
        total_fat = meals[FAT].sum()

        st.subheader("Daily Cost")
        st.write("RM", round(total_cost, 2))

        st.subheader("Nutrition Totals")
        st.write("Calories:", total_cal, "kcal")
        st.write("Protein:", total_pro, "g")
        st.write("Fat:", total_fat, "g")

        if total_cal < req_cal:
            st.warning("Calories requirement NOT met")
        if total_pro < req_pro:
            st.warning("Protein requirement NOT met")
        if total_fat > req_fat:
            st.error("Fat limit exceeded")

else:
    st.info("Upload a CSV file to start")
