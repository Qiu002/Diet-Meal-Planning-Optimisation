import streamlit as st
import pandas as pd
import random
import numpy as np

st.title("🍽️ Meal-by-Meal Diet Cost Optimizer (Evolution Strategies)")

uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    st.subheader("📋 Dataset Preview")
    st.dataframe(data.head())

    CAL = "Calories"
    PRO = "Protein"
    FAT = "Fat"
    PRICE = "Price_RM"

    # ---------------- Nutrition Targets ----------------
    st.sidebar.header("🎯 Daily Nutrition Requirements")
    req_cal = st.sidebar.number_input("Minimum Calories", 1200, 4000, 1800)
    req_pro = st.sidebar.number_input("Minimum Protein (g)", 30, 300, 60)
    req_fat = st.sidebar.number_input("Maximum Fat (g)", 10, 300, 80)

    # ---------------- Evolution Settings ----------------
    st.sidebar.header("🧬 Evolution Strategy Settings")
    pop_size = st.sidebar.slider("Population Size", 20, 200, 50)
    generations = st.sidebar.slider("Generations", 100, 600, 300)
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.05, 0.5, 0.2)

    # ---------------- Fitness Function ----------------
    def fitness(solution):
        meals = data.loc[solution]

        # SCALE nutrition per meal (¼ per meal)
        total_cal = meals[CAL].sum() / 4
        total_pro = meals[PRO].sum() / 4
        total_fat = meals[FAT].sum() / 4
        total_cost = meals[PRICE].sum()

        penalty = 0
        if total_cal < req_cal:
            penalty += (req_cal - total_cal) * 0.1
        if total_pro < req_pro:
            penalty += (req_pro - total_pro) * 0.2
        if total_fat > req_fat:
            penalty += (total_fat - req_fat) * 0.2

        return total_cost + penalty

    # ---------------- Evolution Strategy ----------------
    def evolve_meal_plan():
        n = len(data)
        population = [np.random.randint(0, n, 4) for _ in range(pop_size)]

        for _ in range(generations):
            offspring = []
            for parent in population:
                child = parent.copy()
                for i in range(4):
                    if random.random() < mutation_rate:
                        child[i] = random.randrange(n)
                offspring.append(child)

            population = sorted(population + offspring, key=fitness)[:pop_size]

        return population[0]

    # ---------------- Run Optimization ----------------
    if st.button("🚀 Optimize Meal Costs"):
        best = evolve_meal_plan()
        meals = data.loc[best].reset_index(drop=True)

        st.subheader("🍽️ Optimized Meal Choices")
        st.write(f"🍳 Breakfast: {meals.loc[0,'Breakfast Suggestion']} — RM {meals.loc[0,PRICE]:.2f}")
        st.write(f"🍛 Lunch: {meals.loc[1,'Lunch Suggestion']} — RM {meals.loc[1,PRICE]:.2f}")
        st.write(f"🍲 Dinner: {meals.loc[2,'Dinner Suggestion']} — RM {meals.loc[2,PRICE]:.2f}")
        st.write(f"🍪 Snack: {meals.loc[3,'Snack Suggestion']} — RM {meals.loc[3,PRICE]:.2f}")

        # ---------------- Corrected Daily Nutrition ----------------
        total_cost = meals[PRICE].sum()
        total_cal = meals[CAL].sum() / 4
        total_pro = meals[PRO].sum() / 4
        total_fat = meals[FAT].sum() / 4

        st.subheader("💰 Total Daily Cost")
        st.write(f"RM {total_cost:.2f}")

        st.subheader("📊 Daily Nutrition Summary (CORRECTED)")
        st.write(f"Calories: **{total_cal:.0f} kcal**")
        st.write(f"Protein: **{total_pro:.1f} g**")
        st.write(f"Fat: **{total_fat:.1f} g**")

        if total_cal < req_cal:
            st.warning("Calories requirement NOT met")
        if total_pro < req_pro:
            st.warning("Protein requirement NOT met")
        if total_fat > req_fat:
            st.warning("Fat limit exceeded")

else:
    st.info("Upload a CSV file to start.")
