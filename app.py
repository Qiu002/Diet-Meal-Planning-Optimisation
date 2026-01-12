import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Meal Plan Optimizer", page_icon="🥗")

st.title("🥗 Daily Meal Plan Optimizer (Evolution Strategies)")
st.write("Select a daily meal plan that meets nutritional requirements at the lowest total cost using Evolution Strategies.")

# -----------------------------
# Load CSV
# -----------------------------
try:
    df = pd.read_csv("Food_and_Nutrition_with_Price.csv")
except:
    st.error("CSV file not found. Make sure it is in the same folder as app.py and named correctly.")
    st.stop()

st.subheader("📦 Uploaded Dataset")
st.dataframe(df)

# -----------------------------
# USER selects column names
# -----------------------------
st.sidebar.header("🧭 Map your column names")

food_col = st.sidebar.selectbox("Select column for FOOD NAME", df.columns)
cal_col = st.sidebar.selectbox("Select column for CALORIES", df.columns)
pro_col = st.sidebar.selectbox("Select column for PROTEIN (g)", df.columns)
fat_col = st.sidebar.selectbox("Select column for FAT (g)", df.columns)
price_col = st.sidebar.selectbox("Select column for PRICE", df.columns)

# -----------------------------
# Nutrition requirement inputs
# -----------------------------
st.sidebar.header("⚙️ Set Nutrition Requirements")

cal_need = st.sidebar.number_input("Minimum Calories", value=2000, step=100)
pro_need = st.sidebar.number_input("Minimum Protein (g)", value=50, step=5)
fat_need = st.sidebar.number_input("Minimum Fat (g)", value=70, step=5)

# meal selection list
meal_options = df[food_col].tolist()
selected_meals = st.sidebar.multiselect("Select meals to include", meal_options, default=meal_options)

# -----------------------------
# ES parameters sliders
# -----------------------------
st.sidebar.header("🔧 Evolution Strategies Parameters")

population_size = st.sidebar.slider("Population Size", min_value=10, max_value=200, value=50, step=10)
n_generations = st.sidebar.slider("Number of Generations", min_value=50, max_value=2000, value=500, step=50)
sigma = st.sidebar.slider("Mutation Strength (σ)", min_value=0.01, max_value=2.0, value=0.5, step=0.01)
learning_rate = st.sidebar.slider("Learning Rate (Not used in basic ES)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)

run_button = st.sidebar.button("Optimize Meal Plan")

# -----------------------------
# Filter selection
# -----------------------------
filtered_df = df[df[food_col].isin(selected_meals)].reset_index(drop=True)
n_foods = len(filtered_df)

# -----------------------------
# Evolution Strategies Optimization
# -----------------------------
def fitness(portions):
    """
    Fitness function: penalize if nutritional constraints are not met,
    otherwise return total cost (we want to minimize cost).
    """
    calories = np.sum(portions * filtered_df[cal_col].values)
    protein = np.sum(portions * filtered_df[pro_col].values)
    fat = np.sum(portions * filtered_df[fat_col].values)
    cost = np.sum(portions * filtered_df[price_col].values)

    # Penalty if constraints not met
    penalty = 0
    if calories < cal_need:
        penalty += (cal_need - calories) * 10
    if protein < pro_need:
        penalty += (pro_need - protein) * 10
    if fat < fat_need:
        penalty += (fat_need - fat) * 10

    return cost + penalty

def evolution_strategy(n_generations, population_size, sigma):
    # Initialize random population (portions)
    population = np.random.rand(population_size, n_foods) * 2  # portions between 0 and 2

    for generation in range(n_generations):
        fitness_values = np.array([fitness(ind) for ind in population])
        # Select top 20% as parents
        num_parents = max(1, population_size // 5)
        parents_idx = fitness_values.argsort()[:num_parents]
        parents = population[parents_idx]

        # Generate new population by adding Gaussian noise to parents
        new_population = []
        for _ in range(population_size):
            parent = parents[np.random.randint(num_parents)]
            child = parent + np.random.randn(n_foods) * sigma
            child = np.clip(child, 0, None)  # no negative portions
            new_population.append(child)
        population = np.array(new_population)

    # Return the best solution
    fitness_values = np.array([fitness(ind) for ind in population])
    best_idx = fitness_values.argmin()
    return population[best_idx]

# -----------------------------
# Run optimization
# -----------------------------
if run_button:
    if n_foods == 0:
        st.error("❌ Please select at least one meal to optimize.")
    else:
        with st.spinner("Optimizing meal plan using Evolution Strategies..."):
            best_portions = evolution_strategy(n_generations, population_size, sigma)

        # Prepare results
        results = []
        for i, qty in enumerate(best_portions):
            if qty > 0.01:
                results.append([
                    filtered_df.loc[i, food_col],
                    round(qty, 2),
                    round(filtered_df.loc[i, cal_col] * qty, 2),
                    round(filtered_df.loc[i, pro_col] * qty, 2),
                    round(filtered_df.loc[i, fat_col] * qty, 2),
                    round(filtered_df.loc[i, price_col] * qty, 2)
                ])

        result_df = pd.DataFrame(
            results,
            columns=["Food", "Quantity", "Calories", "Protein", "Fat", "Cost"]
        )

        st.subheader("🍽️ Optimal Meal Plan")
        st.table(result_df)

        st.subheader("💰 Minimum Total Daily Cost")
        st.write("RM", round(result_df["Cost"].sum(), 2))

        st.subheader("📊 Total Nutrition Achieved")
        st.write("Calories:", round(result_df["Calories"].sum(), 2))
        st.write("Protein:", round(result_df["Protein"].sum(), 2), "g")
        st.write("Fat:", round(result_df["Fat"].sum(), 2), "g")

        st.success("🎉 Optimization completed using Evolution Strategies!")
