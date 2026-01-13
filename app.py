import streamlit as st
import pandas as pd
import random

st.title("🍽️ Diet Meal Optimizer Using Evolution Strategies")
st.write("Finds breakfast, lunch, dinner and snack that meet nutrition needs while minimizing total cost.")

# ------------------ Upload CSV ------------------
uploaded_file = st.file_uploader("📂 Upload your dataset CSV", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    st.subheader("📋 Dataset Preview")
    st.dataframe(data.head())

    # use your exact columns
    CAL = "Calories"
    PRO = "Protein"
    FAT = "Fat"
    PRICE = "Price_RM"

    BCOL = "Breakfast Suggestion"
    LCOL = "Lunch Suggestion"
    DCOL = "Dinner Suggestion"
    SCOL = "Snack Suggestion"

    # ------------------ User nutrition requirements ------------------
    st.sidebar.header("🎯 Daily Nutrition Targets")
    req_cal = st.sidebar.number_input("Minimum Calories", 1200, 4000, 1800)
    req_pro = st.sidebar.number_input("Minimum Protein (g)", 20, 300, 60)
    max_fat = st.sidebar.number_input("Maximum Fat (g)", 10, 300, 80)

    # ------------------ Evolution Strategy parameters ------------------
    st.sidebar.header("🧬 Evolution Strategy Settings")
    pop_size = st.sidebar.slider("Population Size", 10, 200, 60)
    generations = st.sidebar.slider("Generations", 20, 600, 300)
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.15)

    # -------------- Fitness with HARD constraints --------------
    def is_valid(ind):
        subset = data.iloc[ind]

        total_cal = subset[CAL].sum()
        total_pro = subset[PRO].sum()
        total_fat = subset[FAT].sum()

        return (
            total_cal >= req_cal and
            total_pro >= req_pro and
            total_fat <= max_fat
        )

    def fitness(ind):
        subset = data.iloc[ind]
        total_cost = subset[PRICE].sum()
        return total_cost  # minimize cost ONLY for valid solutions

    # -------- Evolution Strategy across 4 meals --------
    def evolution_strategies():
        n = len(data)

        # each individual = 4 rows index
        population = [
            random.sample(range(n), 4) for _ in range(pop_size)
        ]

        for _ in range(generations):

            # mutate to create offspring
            offspring = []
            for parent in population:
                child = parent.copy()
                if random.random() < mutation_rate:
                    pos = random.randrange(4)
                    child[pos] = random.randrange(n)
                offspring.append(child)

            # combine populations
            combined = population + offspring

            # keep only VALID solutions
            feasible = [ind for ind in combined if is_valid(ind)]

            # if no feasible yet, continue searching
            if len(feasible) == 0:
                population = combined[:pop_size]
                continue

            # sort feasible ones by total cost
            feasible_sorted = sorted(feasible, key=lambda ind: fitness(ind))

            # keep best mu
            population = feasible_sorted[:pop_size]

        # final best valid solution
        feasible_final = [ind for ind in population if is_valid(ind)]
        if len(feasible_final) == 0:
            return None

        best = sorted(feasible_final, key=lambda ind: fitness(ind))[0]
        return data.iloc[best]

    # ------------------ RUN OPTIMIZATION ------------------
    if st.button("🚀 Optimize Meal Plan"):
        best_plan = evolution_strategies()

        if best_plan is None:
            st.error("No feasible solution found. Try relaxing nutrition limits.")
        else:
            st.success("Optimization successful! Requirements satisfied ✔")

            st.subheader("🍽️ Selected Meals")

            st.write("🍳 **Breakfast:** ", best_plan[BCOL].iloc[0])
            st.write("🍛 **Lunch:** ", best_plan[LCOL].iloc[1])
            st.write("🍲 **Dinner:** ", best_plan[DCOL].iloc[2])
            st.write("🍪 **Snack:** ", best_plan[SCOL].iloc[3])

            total_cost = best_plan[PRICE].sum()
            total_cal = best_plan[CAL].sum()
            total_pro = best_plan[PRO].sum()
            total_fat = best_plan[FAT].sum()

            st.subheader("📊 Daily Nutrition Summary")
            st.write(f"🔥 Calories: **{total_cal} kcal** (target ≥ {req_cal})")
            st.write(f"💪 Protein: **{total_pro} g** (target ≥ {req_pro})")
            st.write(f"🧈 Fat: **{total_fat} g** (limit ≤ {max_fat})")

            st.subheader("💰 Total Daily Cost")
            st.write(f"👉 **RM {total_cost:.2f} per day**")

else:
    st.info("Upload your CSV to begin.")
