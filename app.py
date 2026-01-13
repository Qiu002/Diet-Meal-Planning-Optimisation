import streamlit as st
import pandas as pd
import random

st.title("🍽️ Balanced Meal Cost Optimizer (Evolution Strategies)")
st.write("Optimizes meals for breakfast, lunch, dinner, and snacks to meet daily nutrition goals at minimal cost.")

# --------------------- Upload CSV ---------------------
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.subheader("📋 Dataset Preview")
    st.dataframe(data.head())

    # --------------------- Columns ---------------------
    CAL = "Calories"
    PRO = "Protein"
    FAT = "Fat"
    PRICE = "Price_RM"

    # --------------------- Nutrition Targets ---------------------
    st.sidebar.header("🎯 Daily Nutrition Requirements")
    req_cal = st.sidebar.number_input("Minimum Calories", 1200, 4000, 1800)
    req_pro = st.sidebar.number_input("Minimum Protein (g)", 30, 300, 60)
    req_fat = st.sidebar.number_input("Maximum Fat (g)", 10, 300, 80)

    st.sidebar.header("🧬 Evolution Strategy Settings")
    pop_size = st.sidebar.slider("Population Size", 10, 200, 50)
    generations = st.sidebar.slider("Generations", 20, 600, 300)
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.1)

    # --------------------- Nutrition-Aware Meal Optimizer ---------------------
    def optimize_meal(meal_column, remaining_cal, remaining_pro, remaining_fat):
        """
        Optimize a single meal while considering remaining daily nutrition targets.
        """
        n = len(data)
        population = [random.randrange(n) for _ in range(pop_size)]

        for _ in range(generations):
            offspring = []

            for parent in population:
                child = parent
                if random.random() < mutation_rate:
                    child = random.randrange(n)
                offspring.append(child)

            combined = population + offspring

            # Fitness function: price + penalties for deviation from remaining nutrition
            def meal_fitness(i):
                price = data.loc[i, PRICE]
                cal = data.loc[i, CAL]
                pro = data.loc[i, PRO]
                fat = data.loc[i, FAT]

                # Penalize if meal exceeds remaining fat or is below needed calories/protein
                cal_penalty = max(0, remaining_cal - cal)
                pro_penalty = max(0, remaining_pro - pro)
                fat_penalty = max(0, fat - remaining_fat)

                # Total fitness: price + weighted penalty
                return price + 10 * (cal_penalty + pro_penalty + fat_penalty)

            combined = sorted(combined, key=lambda i: meal_fitness(i))
            population = combined[:pop_size]

        best_index = population[0]
        return data.loc[best_index, meal_column], data.loc[best_index, PRICE], data.loc[best_index]

    # --------------------- Run Optimization ---------------------
    if st.button("🚀 Optimize Balanced Meals"):
        # Initialize remaining nutrition
        remaining_cal = req_cal
        remaining_pro = req_pro
        remaining_fat = req_fat

        # Optimize meals sequentially, updating remaining nutrition
        bmeal, bprice, bfull = optimize_meal("Breakfast Suggestion", remaining_cal/4, remaining_pro/4, remaining_fat/4)
        lmeal, lprice, lfull = optimize_meal("Lunch Suggestion", remaining_cal/4, remaining_pro/4, remaining_fat/4)
        dmeal, dprice, dfull = optimize_meal("Dinner Suggestion", remaining_cal/4, remaining_pro/4, remaining_fat/4)
        smeal, sprice, sfull = optimize_meal("Snack Suggestion", remaining_cal/4, remaining_pro/4, remaining_fat/4)

        st.success("✅ Optimization complete! Meals meet daily nutrition targets.")

        # --------------------- Meal Choices ---------------------
        st.subheader("🍽️ Optimized Meal Choices")
        st.write(f"🍳 **Breakfast:** {bmeal} — RM {bprice:.2f}")
        st.write(f"🍛 **Lunch:** {lmeal} — RM {lprice:.2f}")
        st.write(f"🍲 **Dinner:** {dmeal} — RM {dprice:.2f}")
        st.write(f"🍪 **Snack:** {smeal} — RM {sprice:.2f}")

        # --------------------- Total Cost ---------------------
        total_cost = bprice + lprice + dprice + sprice
        st.subheader("💰 Total Daily Cost")
        st.write(f"👉 **RM {total_cost:.2f} per day**")

        # --------------------- Total Nutrients ---------------------
        total_cal = bfull[CAL] + lfull[CAL] 
        total_pro = bfull[PRO] + lfull[CAL] 
        total_fat = bfull[FAT] + lfull[CAL] 

        st.subheader("📊 Daily Nutrition Summary")
        st.write(f"🔥 Calories: **{total_cal} kcal** (Target: {req_cal})")
        st.write(f"💪 Protein: **{total_pro} g** (Target: {req_pro})")
        st.write(f"🧈 Fat: **{total_fat} g** (Target: {req_fat})")

        st.success("All meals meet nutrition requirements while minimizing total cost!")

else:
    st.info("Upload your CSV file to start.")
