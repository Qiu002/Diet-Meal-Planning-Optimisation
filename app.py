import streamlit as st
import pandas as pd
import random

st.title("🍽️ Daily Diet Cost Optimizer (Evolution Strategies)")
st.write("Optimizes breakfast, lunch, dinner, and snack together while meeting nutrition goals.")

uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    st.subheader("📋 Dataset Preview")
    st.dataframe(data.head())

    # Column names
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
    pop_size = st.sidebar.slider("Population Size", 20, 200, 60)
    generations = st.sidebar.slider("Generations", 50, 600, 300)
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.15)

    # --------- Fitness Function ----------
    def fitness(solution):
        b, l, d, s = solution

        total_price = (
            data.loc[b, PRICE] +
            data.loc[l, PRICE] +
            data.loc[d, PRICE] +
            data.loc[s, PRICE]
        )

        total_cal = data.loc[[b, l, d, s], CAL].sum()
        total_pro = data.loc[[b, l, d, s], PRO].sum()
        total_fat = data.loc[[b, l, d, s], FAT].sum()

        penalty = 0
        if total_cal < req_cal:
            penalty += (req_cal - total_cal) * 10
        if total_pro < req_pro:
            penalty += (req_pro - total_pro) * 15
        if total_fat > req_fat:
            penalty += (total_fat - req_fat) * 10

        # discourage same food for multiple meals
        penalty += (4 - len(set(solution))) * 50

        return total_price + penalty

    # --------- Evolution Strategy ----------
    def optimize_daily_plan():
        n = len(data)

        population = [
            [random.randrange(n) for _ in range(4)]
            for _ in range(pop_size)
        ]

        for _ in range(generations):
            offspring = []

            for parent in population:
                child = parent.copy()
                if random.random() < mutation_rate:
                    idx = random.randint(0, 3)
                    child[idx] = random.randrange(n)
                offspring.append(child)

            population += offspring
            population = sorted(population, key=fitness)[:pop_size]

        return population[0]

    if st.button("🚀 Optimize Daily Meal Plan"):
        solution = optimize_daily_plan()
        b, l, d, s = solution

        st.success("Optimization complete!")

        st.subheader("🍽️ Optimized Meal Choices")
        st.write(f"🍳 **Breakfast:** {data.loc[b, 'Breakfast Suggestion']} — RM {data.loc[b, PRICE]:.2f}")
        st.write(f"🍛 **Lunch:** {data.loc[l, 'Lunch Suggestion']} — RM {data.loc[l, PRICE]:.2f}")
        st.write(f"🍲 **Dinner:** {data.loc[d, 'Dinner Suggestion']} — RM {data.loc[d, PRICE]:.2f}")
        st.write(f"🍪 **Snack:** {data.loc[s, 'Snack Suggestion']} — RM {data.loc[s, PRICE]:.2f}")

        total_price = data.loc[[b, l, d, s], PRICE].sum()
        total_cal = data.loc[[b, l, d, s], CAL].sum()
        total_pro = data.loc[[b, l, d, s], PRO].sum()
        total_fat = data.loc[[b, l, d, s], FAT].sum()

        st.subheader("💰 Total Daily Cost")
        st.write(f"👉 **RM {total_price:.2f} per day**")

        st.subheader("📊 Daily Nutrition Summary")
        st.write(f"🔥 Calories: **{total_cal} kcal**")
        st.write(f"💪 Protein: **{total_pro} g**")
        st.write(f"🧈 Fat: **{total_fat} g**")

        if total_cal < req_cal:
            st.warning("⚠️ Calories requirement NOT met")
        if total_pro < req_pro:
            st.warning("⚠️ Protein requirement NOT met")
        if total_fat > req_fat:
            st.warning("⚠️ Fat limit exceeded")

else:
    st.info("Upload your CSV file to start.")
