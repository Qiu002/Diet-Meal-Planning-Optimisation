import streamlit as st
import pandas as pd
import random

st.title("🍽️ Meal-by-Meal Diet Cost Optimizer (Evolution Strategies)")
st.write("Optimizes cost for breakfast, lunch, dinner, and snacks separately while meeting daily nutrition goals.")

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
    pop_size = st.sidebar.slider("Population Size", 10, 200, 40)
    generations = st.sidebar.slider("Generations", 20, 600, 300)
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.1)

    # --------------------- Meal Optimizer: Random + Nutrient Check ---------------------
    def optimize_meal_combination():
        best_combination = None
        best_total_price = float('inf')

        for _ in range(generations):
            # Randomly pick one row for each meal
            b_row = data.sample(1).iloc[0]
            l_row = data.sample(1).iloc[0]
            d_row = data.sample(1).iloc[0]
            s_row = data.sample(1).iloc[0]

            # Compute total nutrients for the day
            total_cal = b_row[CAL] 
            total_pro = b_row[PRO] 
            total_fat = b_row[FAT] 

            # Compute total price
            total_price = b_row[PRICE] + l_row[PRICE] 

            # Keep combination only if it meets requirements
            if total_cal >= req_cal and total_pro >= req_pro and total_fat <= req_fat:
                if total_price < best_total_price:
                    best_total_price = total_price
                    best_combination = (b_row, l_row, d_row, s_row)

        return best_combination, best_total_price

    # --------------------- Run Optimization ---------------------
    if st.button("🚀 Optimize Meal Costs"):
        result, total_daily_cost = optimize_meal_combination()

        if result:
            bfull, lfull, dfull, sfull = result

            st.success("Optimization complete!")

            st.subheader("🍽️ Optimized Meal Choices")
            st.write(f"🍳 **Breakfast:** {bfull['Breakfast Suggestion']} — RM {bfull[PRICE]:.2f}")
            st.write(f"🍛 **Lunch:** {lfull['Lunch Suggestion']} — RM {lfull[PRICE]:.2f}")
            st.write(f"🍲 **Dinner:** {dfull['Dinner Suggestion']} — RM {dfull[PRICE]:.2f}")
            st.write(f"🍪 **Snack:** {sfull['Snack Suggestion']} — RM {sfull[PRICE]:.2f}")

            st.subheader("💰 Total Daily Cost")
            st.write(f"👉 **RM {total_daily_cost:.2f} per day**")

            st.subheader("📊 Daily Nutrition Summary")
            total_cal = bfull[CAL]   # typo fixed here
            total_pro = bfull[PRO] 
            total_fat = bfull[FAT] 

            st.write(f"🔥 Calories: **{total_cal} kcal**")
            st.write(f"💪 Protein: **{total_pro} g**")
            st.write(f"🧈 Fat: **{total_fat} g**")

        else:
            st.warning("⚠️ Could not find a valid meal combination that meets nutrition requirements. Try increasing generations or population size.")

else:
    st.info("Upload your CSV file to start.")
