import streamlit as st
import pandas as pd
import random

st.title("🍽️ Daily Meal Plan Optimizer (Evolution Strategies)")
st.write("Select a combination of breakfast, lunch, dinner, and snack that meets daily nutritional requirements while minimizing total cost.")

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
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.2)

    # --------------------- Evolution Strategy on Meal Combinations ---------------------
    def fitness(individual):
        """Fitness = total cost if nutrition requirements are met, else penalize heavily."""
        b, l, d, s = individual
        total_cal = data.loc[b, CAL] + data.loc[l, CAL] + data.loc[d, CAL] + data.loc[s, CAL]
        total_pro = data.loc[b, PRO] + data.loc[l, PRO] + data.loc[d, PRO] + data.loc[s, PRO]
        total_fat = data.loc[b, FAT] + data.loc[l, FAT] + data.loc[d, FAT] + data.loc[s, FAT]
        total_price = data.loc[b, PRICE] + data.loc[l, PRICE] + data.loc[d, PRICE] + data.loc[s, PRICE]

        # If any requirement is violated, apply heavy penalty
        if total_cal < req_cal or total_pro < req_pro or total_fat > req_fat:
            return 1e6  # very high penalty
        return total_price

    def evolution_strategies():
        """Optimize meal combination using ES."""
        n = len(data)
        # Each individual = tuple of 4 meal indices (b,l,d,s)
        population = [tuple(random.choices(range(n), k=4)) for _ in range(pop_size)]

        for _ in range(generations):
            offspring = []
            for ind in population:
                child = list(ind)
                # mutate each meal with mutation_rate
                for i in range(4):
                    if random.random() < mutation_rate:
                        child[i] = random.randrange(n)
                offspring.append(tuple(child))
            combined = population + offspring
            # sort by fitness (lower cost is better)
            combined = sorted(combined, key=lambda ind: fitness(ind))
            population = combined[:pop_size]

        return population[0]  # best individual

    if st.button("🚀 Optimize Daily Meal Plan"):
        best = evolution_strategies()
        b, l, d, s = best

        total_price = data.loc[b, PRICE] + data.loc[l, PRICE] + data.loc[d, PRICE] + data.loc[s, PRICE]
        total_cal = data.loc[b, CAL] + data.loc[l, CAL] + data.loc[d, CAL] + data.loc[s, CAL]
        total_pro = data.loc[b, PRO] + data.loc[l, PRO] + data.loc[d, PRO] + data.loc[s, PRO]
        total_fat = data.loc[b, FAT] + data.loc[l, FAT] + data.loc[d, FAT] + data.loc[s, FAT]

        st.success("✅ Optimization Complete!")

        st.subheader("🍽️ Selected Meals")
        st.write(f"🍳 Breakfast: {data.loc[b, 'Breakfast Suggestion']} — RM {data.loc[b, PRICE]:.2f}")
        st.write(f"🍛 Lunch: {data.loc[l, 'Lunch Suggestion']} — RM {data.loc[l, PRICE]:.2f}")
        st.write(f"🍲 Dinner: {data.loc[d, 'Dinner Suggestion']} — RM {data.loc[d, PRICE]:.2f}")
        st.write(f"🍪 Snack: {data.loc[s, 'Snack Suggestion']} — RM {data.loc[s, PRICE]:.2f}")

        st.subheader("💰 Total Daily Cost")
        st.write(f"RM {total_price:.2f}")

        st.subheader("📊 Daily Nutrition Summary")
        st.write(f"🔥 Calories: {total_cal} kcal")
        st.write(f"💪 Protein: {total_pro} g")
        st.write(f"🧈 Fat: {total_fat} g")

        # Warnings
        if total_cal < req_cal:
            st.warning("⚠️ Calories requirement NOT met")
        if total_pro < req_pro:
            st.warning("⚠️ Protein requirement NOT met")
        if total_fat > req_fat:
            st.warning("⚠️ Fat limit exceeded")

else:
    st.info("Upload your CSV file to start.")
