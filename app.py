import streamlit as st
import pandas as pd
import random

st.title("🍽️ Daily Diet Cost Optimizer (Evolution Strategies)")

uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    CAL = "Calories"
    PRO = "Protein"
    FAT = "Fat"
    PRICE = "Price_RM"

    st.sidebar.header("🎯 Nutrition Requirements")
    req_cal = st.sidebar.number_input("Minimum Calories", 1200, 4000, 1800)
    req_pro = st.sidebar.number_input("Minimum Protein", 30, 300, 60)
    req_fat = st.sidebar.number_input("Maximum Fat", 10, 300, 80)

    pop_size = 50
    generations = 200
    mutation_rate = 0.2

    def fitness(i):
        penalty = 0
        if data.loc[i, CAL] < req_cal:
            penalty += (req_cal - data.loc[i, CAL]) * 100
        if data.loc[i, PRO] < req_pro:
            penalty += (req_pro - data.loc[i, PRO]) * 100
        if data.loc[i, FAT] > req_fat:
            penalty += (data.loc[i, FAT] - req_fat) * 100

        return data.loc[i, PRICE] + penalty

    def optimize():
        n = len(data)
        population = [random.randrange(n) for _ in range(pop_size)]

        for _ in range(generations):
            offspring = []
            for p in population:
                c = p
                if random.random() < mutation_rate:
                    c = random.randrange(n)
                offspring.append(c)

            population += offspring
            population = sorted(population, key=fitness)[:pop_size]

        return population[0]

    if st.button("🚀 Optimize"):
        best_idx = optimize()
        best = data.loc[best_idx]

        st.success("Optimization complete!")

        st.write(f"💰 **Cost:** RM {best[PRICE]:.2f}")
        st.write(f"🔥 Calories: {best[CAL]}")
        st.write(f"💪 Protein: {best[PRO]}")
        st.write(f"🧈 Fat: {best[FAT]}")
