import streamlit as st
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

# -----------------------------------
# Load Data
# -----------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Food_and_Nutrition_with_Price.csv")

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


data = load_data()

# -----------------------------------
# Sidebar – User Controls
# -----------------------------------
st.sidebar.header("Nutrition Constraints")

min_calories = st.sidebar.slider("Minimum Calories", 1000, 3000, 2000)
min_protein = st.sidebar.slider("Minimum Protein (g)", 30, 200, 80)
max_fat = st.sidebar.slider("Maximum Fat (g)", 20, 150, 80)

st.sidebar.header("Genetic Algorithm Parameters")

population_size = st.sidebar.slider("Population Size", 50, 200, 100)
generations = st.sidebar.slider("Generations", 100, 400, 200)
mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.3, 0.05)

# -----------------------------------
# Genetic Algorithm
# -----------------------------------
num_meals = len(data)

def create_individual():
    return np.random.randint(0, 2, num_meals)

def fitness(individual):
    total_cal = np.sum(individual * data["calories"])
    total_pro = np.sum(individual * data["protein"])
    total_fat = np.sum(individual * data["fat"])
    total_cost = np.sum(individual * data["price_rm"])

    penalty = 0

    if total_cal < min_calories:
        penalty += (min_calories - total_cal) * 100

    if total_pro < min_protein:
        penalty += (min_protein - total_pro) * 100

    if total_fat > max_fat:
        penalty += (total_fat - max_fat) * 100

    # Objective: minimize cost + penalties
    return total_cost + penalty


def selection(pop):
    return min(random.sample(pop, 3), key=fitness)

def crossover(p1, p2):
    point = random.randint(1, num_meals - 1)
    return np.concatenate((p1[:point], p2[point:]))

def mutation(ind):
    for i in range(num_meals):
        if random.random() < mutation_rate:
            ind[i] = 1 - ind[i]
    return ind

def run_ga():
    population = [create_individual() for _ in range(population_size)]
    history = []

    for _ in range(generations):
        new_pop = []
        for _ in range(population_size):
            p1, p2 = selection(population), selection(population)
            child = mutation(crossover(p1, p2))
            new_pop.append(child)
        population = new_pop
        best = min(population, key=fitness)
        history.append(fitness(best))

    return best, history

# -----------------------------------
# UI
# -----------------------------------
st.title("🥗 Diet Meal Planning Optimisation")

if st.button("Run Optimisation"):
    solution, curve = run_ga()
    plan = data[solution == 1]

    # Totals
    total_cost = plan["Price_RM"].sum()
    total_cal = plan["Calories"].sum()
    total_pro = plan["Protein"].sum()
    total_fat = plan["Fat"].sum()

    # -----------------------------------
    # Summary Results (MATCH IMAGE)
    # -----------------------------------
    st.subheader("💰 Summary Results")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cost", f"RM {total_cost:.2f}")
    c2.metric("Total Calories", f"{int(total_cal)} kcal")
    c3.metric("Total Protein", f"{total_pro:.1f} g")
    c4.metric("Total Fat", f"{total_fat:.1f} g")

    # -----------------------------------
    # Personalized Plan
    # -----------------------------------
    st.subheader("📋 Your Personalized Plan")

    for meal_type in ["Breakfast", "Lunch", "Dinner", "Snack"]:
        meal = plan[plan["Meal_Type"] == meal_type]
        if not meal.empty:
            m = meal.iloc[0]
            st.markdown(
                f"""
                **{meal_type}: {m['Meal']}**  
                Price: RM {m['Price_RM']:.2f} |
                Prot: {m['Protein']}g |
                Fat: {m['Fat']}g
                """
            )

    # -----------------------------------
    # Convergence Curve
    # -----------------------------------
    st.subheader("📉 Algorithm Convergence")

    fig, ax = plt.subplots()
    ax.plot(curve)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness (Cost + Penalty)")
    st.pyplot(fig)

# -----------------------------------
# Footer
# -----------------------------------
st.markdown("""
---
**Evolutionary Diet Optimisation Dashboard**  
Objective: Minimise Cost | Constraints: Nutrition | Method: Genetic Algorithm
""")
