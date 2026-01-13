import streamlit as st
import pandas as pd
import random

st.title("🍽️ Meal-by-Meal Diet Cost Optimizer (Evolution Strategies)")
st.write("Optimizes cost for breakfast, lunch, dinner, and snacks separately while meeting daily nutrition goals.")

uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    st.subheader("📋 Dataset Preview")
    st.dataframe(data.head())

    # Column names based on your dataset
    CAL = "Calories"
    PRO = "Protein"
    FAT = "Fat"
    PRICE = "Price_RM"

    # ---------------- Nutrition Targets ----------------
    st.sidebar.header("🎯 Daily Nutrition Requirements")
    req_cal = st.sidebar.number_input("Minimum Calories", 1200, 4000, 1800)
    req_pro = st.sidebar.number_input("Minimum Protein (g)", 30, 300, 60)
    req_fat = st.sidebar.number_input("Maximum Fat (g)", 10, 300, 80)

    st.sidebar.header("🧬 Evolution Strategy Settings")
    pop_size = st.sidebar.slider("Population Size", 10, 200, 40)
    generations = st.sidebar.slider("Generations", 20, 600, 300)
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.1)

    # --------- Evolution Strategy for single meal ----------
    def optimize_meal(meal_column):
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

            # sort by price only FOR THIS MEAL
            combined = sorted(combined, key=lambda i: data.loc[i, PRICE])

            population = combined[:pop_size]

        best_index = population[0]
        return data.loc[best_index, meal_column], data.loc[best_index, PRICE], data.loc[best_index]

    if st.button("🚀 Optimize Meal Costs"):
        # optimize each meal suggestion independently
        bmeal, bprice, bfull = optimize_meal("Breakfast Suggestion")
        lmeal, lprice, lfull = optimize_meal("Lunch Suggestion")
        dmeal, dprice, dfull = optimize_meal("Dinner Suggestion")
        smeal, sprice, sfull = optimize_meal("Snack Suggestion")

        st.success("Optimization complete!")

        st.subheader("🍽️ Optimized Meal Choices")

        st.write(f"🍳 **Breakfast:** {bmeal} — RM {bprice:.2f}")
        st.write(f"🍛 **Lunch:** {lmeal} — RM {lprice:.2f}")
        st.write(f"🍲 **Dinner:** {dmeal} — RM {dprice:.2f}")
        st.write(f"🍪 **Snack:** {smeal} — RM {sprice:.2f}")

        total_daily_cost = bprice + lprice + dprice + sprice

        st.subheader("💰 Total Daily Cost")
        st.write(f"👉 **RM {total_daily_cost:.2f} per day**")

        # total nutrients
        total_cal = bfull[CAL]
        total_pro = bfull[PRO]
        total_fat = bfull[FAT]

        st.subheader("📊 Daily Nutrition Summary")
        st.write(f"🔥 Calories: **{total_cal} kcal**")
        st.write(f"💪 Protein: **{total_pro} g**")
        st.write(f"🧈 Fat: **{total_fat} g**")

        # warnings if not met
        if total_cal < req_cal:
            st.warning("⚠️ Calories requirement NOT met")
        if total_pro < req_pro:
            st.warning("⚠️ Protein requirement NOT met")
        if total_fat > req_fat:
            st.warning("⚠️ Fat limit exceeded")

else:
    st.info("Upload your CSV file to start.")
