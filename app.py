import streamlit as st
import pandas as pd
import numpy as np
import random

st.title("🍽️ Daily Diet Meal Plan Optimizer (Evolution Strategies)")
st.write("Optimizes breakfast, lunch, dinner and snack to meet nutrition goals at minimum cost.")

# --------------------- Load CSV ---------------------
uploaded_file = st.file_uploader("📂 Upload your dataset CSV", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    st.subheader("📋 Dataset Preview")
    st.dataframe(data.head())

    # --------------------- Nutrient Columns ---------------------
    CAL_COL = "Calories"
    PRO_COL = "Protein"
    FAT_COL = "Fat"
    PRICE_COL = "Price_RM"

    # --------------------- User Nutrition Requirements ---------------------
    st.sidebar.header("⚙️ Nutritional Requirements")
    req_cal = st.sidebar.number_input("Minimum Daily Calories", 1200, 4000, 1800)
    req_pro = st.sidebar.number_input("Minimum Daily Protein (g)", 30, 300, 60)
    req_fat = st.sidebar.number_input("Maximum Daily Fat (g)", 10, 300, 80)

    st.sidebar.header("🧬 Evolution Strategies Settings")
    pop_size = st.sidebar.slider("Population Size", 10, 200, 50)
    generations = st.sidebar.slider("Generations", 10, 500, 200)
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.1)

    # --------------------- Fitness Function ---------------------
    def fitness(individual):
        subset = data.iloc[individual]

        total_cal = subset[CAL_COL].sum()
        total_pro = subset[PRO_COL].sum()
        total_fat = subset[FAT_COL].sum()
        total_cost = subset[PRICE_COL].sum()

        penalty = 0
        if total_cal < req_cal:
            penalty += (req_cal - total_cal)
        if total_pro < req_pro:
            penalty += (req_pro - total_pro)
        if total_fat > req_fat:
            penalty += (total_fat - req_fat)

        return total_cost + 15 * penalty

    # --------------------- Evolution Strategies ---------------------
    def evolution_strategies():
        n = len(data)
        mu = pop_size

        # choose 4 meals per day (B,L,D,S)
        population = [random.sample(range(n), 4) for _ in range(mu)]

        for _ in range(generations):
            offspring = []

            for parent in population:
                child = parent.copy()
                if random.random() < mutation_rate:
                    idx = random.randrange(4)
                    child[idx] = random.randrange(n)
                offspring.append(child)

            combined = population + offspring
            scored = sorted(combined, key=lambda ind: fitness(ind))
            population = scored[:mu]

        best = population[0]
        return data.iloc[best]

    # --------------------- Run Optimizer ---------------------
    if st.button("🚀 Optimize Daily Meal Plan"):
        best_plan = evolution_strategies()

        st.success("Optimization complete!")

        st.subheader("🥗 Suggested Daily Meal Plan")

        st.write("### 🍳 Breakfast Suggestion")
        st.table(best_plan["Breakfast Suggestion"].head(1))

        st.write("### 🍛 Lunch Suggestion")
        st.table(best_plan["Lunch Suggestion"].head(1))

        st.write("### 🍲 Dinner Suggestion")
        st.table(best_plan["Dinner Suggestion"].head(1))

        st.write("### 🍪 Snack Suggestion")
        st.table(best_plan["Snack Suggestion"].head(1))

        total_cal = best_plan[CAL_COL].sum()
        total_pro = best_plan[PRO_COL].sum()
        total_fat = best_plan[FAT_COL].sum()
        total_cost = best_plan[PRICE_COL].sum()

        st.subheader("📊 Nutrition Summary")
        st.write(f"Total Calories: **{total_cal} kcal**")
        st.write(f"Total Protein: **{total_pro} g**")
        st.write(f"Total Fat: **{total_fat} g**")
        st.write(f"💰 Total Cost: **RM {total_cost:.2f}**")

else:
    st.info("Upload your CSV file to begin.")
