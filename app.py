import streamlit as st
import pandas as pd
import random
import numpy as np

# ---------------- App Title ----------------
st.title("🍽️ Meal-by-Meal Diet Cost Optimizer (Evolution Strategies)")
st.write("Optimizes daily meal plans at the lowest cost while meeting nutrition requirements.")

uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    st.subheader("📋 Dataset Preview")
    st.dataframe(data.head())

    # Column names (adjust only if your CSV differs)
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

        total_cost = meals[PRICE].sum()
        total_cal = meals[CAL].sum()
        total_pro = meals[PRO].sum()
        total_fat = meals[FAT].sum()

        penalty = 0

        if total_cal < req_cal:
            penalty += (req_cal - total_cal) * 0.05
        if total_pro < req_pro:
            penalty += (req_pro - total_pro) * 0.1
        if total_fat > req_fat:
            penalty += (total_fat - req_fat) * 0.1

        return total_cost + penalty

    # ---------------- Evolution Strategy ----------------
    def evolve_meal_plan():
        n = len(data)

        population = [
            np.random.randint(0, n, size=4)
            for _ in range(pop_size)
        ]

        for _ in range(generations):
            offspring = []

            for parent in population:
                child = parent.copy()
                for i in range(4):
                    if random.random() < mutation_rate:
                        child[i] = random.randrange(n)
                offspring.append(child)

            combined = population + offspring
            combined.sort(key=fitness)

            population = combined[:pop_size]

        return population[0]

    # ---------------- Optimization Button ----------------
    if st.button("🚀 Optimize Meal Costs"):
        best_solution = evolve_meal_plan()
        meals = data.loc[best_solution].reset_index(drop=True)

        st.success("Optimization complete!")

        st.subheader("🍽️ Optimized Meal Choices")

        st.write(f"🍳 **Breakfast:** {meals.loc[0, 'Breakfast Suggestion']} — RM {meals.loc[0, PRICE]:.2f}")
        st.write(f"🍛 **Lunch:** {meals.loc[1, 'Lunch Suggestion']} — RM {meals.loc[1, PRICE]:.2f}")
        st.write(f"🍲 **Dinner:** {meals.loc[2, 'Dinner Suggestion']} — RM {meals.loc[2, PRICE]:.2f}")
        st.write(f"🍪 **Snack:** {meals.loc[3, 'Snack Suggestion']} — RM {meals.loc[3, PRICE]:.2f}")

        # ---------------- Corrected Daily Totals ----------------
        # Average nutrition across meals to avoid inflated values

        total_cost = meals[PRICE].sum()

        avg_cal = meals[CAL].mean()
        avg_pro = meals[PRO].mean()
        avg_fat = meals[FAT].mean()

        # Daily totals = average × 4 meals
        total_cal = avg_cal * 4
        total_pro = avg_pro * 4
        total_fat = avg_fat * 4

        st.subheader("📊 Daily Nutrition Summary (Combined Meals)")
        st.write(f"🔥 Calories: **{total_cal:.0f} kcal**")
        st.write(f"💪 Protein: **{total_pro:.1f} g**")
        st.write(f"🧈 Fat: **{total_fat:.1f} g**")

        # ---------------- Warnings ----------------
        if total_cal < req_cal:
            st.warning("⚠️ Calories requirement NOT met")
        if total_pro < req_pro:
            st.warning("⚠️ Protein requirement NOT met")
        if total_fat > req_fat:
            st.warning("⚠️ Fat limit exceeded")

else:
    st.info("📂 Upload your CSV file to begin optimization.")
