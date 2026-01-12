import streamlit as st
import pandas as pd
import numpy as np
import random

# -----------------------------------
# Load Data
# -----------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("Food_and_Nutrition_with_Price.csv")

data = load_data()

# -----------------------------------
# Sidebar – User Controls
# -----------------------------------
st.sidebar.header("Nutrition Constraints")

min_calories = st.sidebar.slider("Minimum Calories", 1000, 3000, 2000)
min_protein = st.sidebar.slider("Minimum Protein (g)", 30, 200, 80)
max_fat = st.sidebar.slider("Maximum Fat (g)", 20, 150, 70)

st.sidebar.header("Genetic Algorithm Parameters")

population_size = st.sidebar.slider("Population Size", 20, 300, 100)
generations = st.sidebar.slider("Generations", 50, 500, 200)
mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.05)

# -----------------------------------
# Genetic Algorithm Functions
# -----------------------------------
num_meals = len(data)

def create_individual():
    return np.random.randint(0, 2, num_meals)

def fitness(individual):
    total_cal = np.sum(individual * data["Calories"])
    total_pro = np.sum(individual * data["Protein"])
    total_fat = np.sum(individual * data["Fat"])
    total_cost = np.sum(individual * data["Price_RM"])

    penalty = 0
    if total_cal < min_calories:
        penalty += (min_calories - total_cal) * 10
    if total_pro < min_protein:
        penalty += (min_protein - total_pro) * 10
    if total_fat > max_fat:
        penalty += (total_fat - max_fat) * 10

    return total_cost + penalty

def selection(population):
    return min(random.sample(population, 3), key=fitness)

def crossover(parent1, parent2):
    point = random.randint(1, num_meals - 1)
    return np.concatenate((parent1[:point], parent2[point:]))

def mutation(individual):
    for i in range(num_meals):
        if random.random() < mutation_rate:
            individual[i] = 1 - individual[i]
    return individual

# -----------------------------------
# Run Genetic Algorithm
# -----------------------------------
def run_ga():
    population = [create_individual() for _ in range(population_size)]
    best_fitness_history = []
    best_solution = None

    for gen in range(generations):
        new_population = []

        for _ in range(population_size):
            p1 = selection(population)
            p2 = selection(population)
            child = crossover(p1, p2)
            child = mutation(child)
            new_population.append(child)

        population = new_population
        best = min(population, key=fitness)
        best_fitness_history.append(fitness(best))
        best_solution = best

    return best_solution, best_fitness_history

# -----------------------------------
# Run Button
# -----------------------------------
st.title("🥗 Diet Meal Planning Optimisation using Evolutionary Algorithm")

if st.button("Run Optimisation"):
    best_solution, fitness_curve = run_ga()

    selected_meals = data[best_solution == 1]

    total_calories = selected_meals["Calories"].sum()
    total_protein = selected_meals["Protein"].sum()
    total_fat = selected_meals["Fat"].sum()
    total_cost = selected_meals["Price_RM"].sum()

    # -----------------------------------
    # Results Display
    # -----------------------------------
    st.subheader("✅ Optimal Meal Plan")
    st.dataframe(selected_meals)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Calories", f"{total_calories:.1f}")
    col2.metric("Protein (g)", f"{total_protein:.1f}")
    col3.metric("Fat (g)", f"{total_fat:.1f}")
    col4.metric("Total Cost ($)", f"{total_cost:.2f}")

    # -----------------------------------
    # Convergence Curve
    # -----------------------------------
    st.subheader("📉 Convergence Curve")

    fig, ax = plt.subplots()
    ax.plot(fitness_curve)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness (Cost + Penalty)")
    ax.set_title("Evolutionary Algorithm Convergence")

    st.pyplot(fig)

    # -----------------------------------
    # Trade-off Visualization
    # -----------------------------------
    st.subheader("⚖️ Nutrition vs Cost Trade-off")

    fig2, ax2 = plt.subplots()
    ax2.scatter(data["Calories"], data["Price"], alpha=0.5, label="All Meals")
    ax2.scatter(selected_meals["Calories"], selected_meals["Price_RM"],
                color="red", label="Selected Meals")
    ax2.set_xlabel("Calories")
    ax2.set_ylabel("Price_RM")
    ax2.legend()

    st.pyplot(fig2)

# -----------------------------------
# Footer
# -----------------------------------
st.markdown("""
---
**Evolutionary Diet Optimisation Dashboard**
- Objective: Minimise cost
- Constraints: Calories, Protein, Fat
- Algorithm: Genetic Algorithm
""")
