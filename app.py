import streamlit as st
import pandas as pd
import random

st.title("🍽️ Daily Diet Cost Optimizer (Evolution Strategies)")

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
    generations = st.sidebar.slider("Generations", 50, 500, 200)
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.2)

    # --------- Fitness Function ----------
    def fitness(i):
        penalty = 0

        if data.loc[i, CAL] < req_cal:
            penalty += (req_cal - data.loc[i, CAL]) * 100
        if data.loc[i, PRO] < req_pro:
            penalty += (req_pro - data.loc[i, PRO]) * 100
        if data.loc[i, FAT] > req_fat:
            penalty += (data.loc[i, FAT] - req_fat) * 100

        return data.loc[i, PRICE] + penalty

    # --------- Evolution Strategy ----------
    def optimize():
        n = len(data)
        population = [random.randrange(n) for _ in range(pop_size)]

        for _ in range(generations):
            offspring = []
            for parent in population:
                child = parent
                if random.random() < mutation_rate:
                    child = random.randrange(n)
                offspring.append(child)

            population += offspring
            population = sorted(population, key=fitness)[:pop_size]

        return population[0]

    if st.button("🚀 Optimize Daily Meal Plan"):
        best_idx = optimize()
        best = data.loc[best_idx]

        st.success("✅ Optimization complete!")

        # ---------------- MEAL SUMMARY ----------------
        st.subheader("🍽️ Optimised Daily Meal Plan")

        st.write(f"🍳 **Breakfast:** {best['Breakfast Suggestion']}")
        st.write(f"🍛 **Lunch:** {best['Lunch Suggestion']}")
        st.write(f"🍲 **Dinner:** {best['Dinner Suggestion']}")
        st.write(f"🍪 **Snack:** {best['Snack Suggestion']}")

        # ---------------- COST SUMMARY ----------------
        st.subheader("💰 Cost Summary")
        st.write(f"👉 **Total Daily Cost:** RM {best[PRICE]:.2f}")

        # ---------------- NUTRITION SUMMARY ----------------
        st.subheader("📊 Nutrition Summary")
        st.write(f"🔥 **Calories:** {best[CAL]} kcal")
        st.write(f"💪 **Protein:** {best[PRO]} g")
        st.write(f"🧈 **Fat:** {best[FAT]} g")

        # ---------------- VALIDATION ----------------
        if best[CAL] < req_cal:
            st.warning("⚠️ Calories requirement NOT met")
        if best[PRO] < req_pro:
            st.warning("⚠️ Protein requirement NOT met")
        if best[FAT] > req_fat:
            st.warning("⚠️ Fat limit exceeded")

else:
    st.info("Upload your CSV file to start.")
