import streamlit as st
import pandas as pd
import numpy as np
import random

st.title("🍽️ Diet Meal Plan Optimizer with Evolution Strategies")
st.write("Select a daily meal plan meeting nutritional needs at minimum total cost.")

# ------------------------ Upload CSV ------------------------
uploaded_file = st.file_uploader("📂 Upload your meal dataset CSV", type=["csv"])
if uploaded_file:
    data = pd.read_csv(uploaded_file)

    st.subheader("📋 Preview of Meal Dataset")
    st.dataframe(data.head())

    # ------------------------ User Inputs ------------------------
    st.sidebar.header("⚙️ Nutritional Requirements")
    req_cal = st.sidebar.number_input("Minimum Daily Calories", 1200, 4000, 1800)
    req_pro = st.sidebar.number_input("Minimum Daily Protein (g)", 30, 300, 60)
    req_fat = st.sidebar.number_input("Maximum Daily Fat (g)", 10, 300, 80)

    pop_size = st.sidebar.slider("Population Size", 10, 200, 50)
    generations = st.sidebar.slider("Generations", 10, 500, 200)
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.1)

    st.sidebar.info("The optimizer will find the lowest-cost meal plan that meets your constraints.")

    # ------------------------ Evolution Strategies ------------------------
    def fitness(individual):
        subset = data.iloc[individual]

        total_cal = subset['calories'].sum()
        total_pro = subset['protein'].sum()
        total_fat = subset['fat'].sum()
        total_cost = subset['price'].sum()

        penalty = 0
        if total_cal < req_cal: penalty += (req_cal - total_cal)
        if total_pro < req_pro: penalty += (req_pro - total_pro)
        if total_fat > req_fat: penalty += (total_fat - req_fat)

        return total_cost + 10 * penalty

    def evolution_strategies():
        n = len(data)
        mu = pop_size
        lam = pop_size

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

    # ------------------------ Run Optimizer ------------------------
    if st.button("🚀 Optimize Meal Plan"):
        best_plan = evolution_strategies()

        st.success("Optimization completed!")

        st.subheader("🥗 Best Daily Meal Plan")

        breakfast = best_plan[best_plan["Breakfast Suggestion"] == "breakfast"].head(1)
        lunch = best_plan[best_plan["Lunch Suggestion"] == "lunch"].head(1)
        dinner = best_plan[best_plan["Dinner Suggestion"] == "dinner"].head(1)
        snack = best_plan[best_plan["Snack Suggestion"] == "snack"].head(1)

        st.write("### 🍳 Breakfast Suggestion")
        st.table(breakfast)

        st.write("### 🍛 Lunch Suggestion")
        st.table(lunch)

        st.write("### 🍲 Dinner Suggestion")
        st.table(dinner)

        st.write("### 🍪 Snack Suggestion")
        st.table(snack)

        total_cal = best_plan["calories"].sum()
        total_pro = best_plan["protein"].sum()
        total_fat = best_plan["fat"].sum()
        total_cost = best_plan["price"].sum()

        st.subheader("📊 Nutrition Summary")
        st.write(f"Total Calories: **{total_cal}** kcal")
        st.write(f"Total Protein: **{total_pro}** g")
        st.write(f"Total Fat: **{total_fat}** g")
        st.write(f"💰 Total Cost: **RM {total_cost:.2f}**")

else:
    st.info("Please upload your CSV file to begin.")
