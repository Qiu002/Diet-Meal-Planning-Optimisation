import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Meal Plan Optimizer", page_icon="🥗")
st.title("🥗 Daily Meal Plan Optimizer")

# -----------------------------
# Load CSV
# -----------------------------
try:
    df = pd.read_csv("Food_and_Nutrition_with_Price.csv")
except:
    st.error("CSV file not found. Make sure it is in the same folder as app.py and named correctly.")
    st.stop()

# Show column names for debugging
st.write("Detected columns:", df.columns.tolist())

# Map columns automatically if common names exist
food_col = next((c for c in df.columns if "food" in c.lower()), None)
cal_col = next((c for c in df.columns if "calorie" in c.lower()), None)
pro_col = next((c for c in df.columns if "protein" in c.lower()), None)
fat_col = next((c for c in df.columns if "fat" in c.lower()), None)
price_col = next((c for c in df.columns if "price" in c.lower()), None)

if None in [food_col, cal_col, pro_col, fat_col, price_col]:
    st.error("❌ Could not automatically detect all required columns (Food, Calories, Protein, Fat, Price).")
    st.stop()

# -----------------------------
# Nutrition requirement inputs
# -----------------------------
st.sidebar.header("⚙️ Set Nutrition Requirements")
cal_need = st.sidebar.number_input("Minimum Calories", value=2000, step=100)
pro_need = st.sidebar.number_input("Minimum Protein (g)", value=50, step=5)
fat_need = st.sidebar.number_input("Minimum Fat (g)", value=70, step=5)

# meal selection
meal_options = df[food_col].tolist()
selected_meals = st.sidebar.multiselect("Select meals to include", meal_options, default=meal_options)
run_button = st.sidebar.button("Optimize Meal Plan")

# -----------------------------
# Filter selection
# -----------------------------
filtered_df = df[df[food_col].isin(selected_meals)].reset_index(drop=True)
n_foods = len(filtered_df)

# -----------------------------
# Fitness function
# -----------------------------
def fitness(portions):
    calories = np.sum(portions * filtered_df[cal_col].values)
    protein = np.sum(portions * filtered_df[pro_col].values)
    fat = np.sum(portions * filtered_df[fat_col].values)
    cost = np.sum(portions * filtered_df[price_col].values)

    penalty = 0
    if calories < cal_need:
        penalty += (cal_need - calories) * 10
    if protein < pro_need:
        penalty += (pro_need - protein) * 10
    if fat < fat_need:
        penalty += (fat_need - fat) * 10

    return cost + penalty

# -----------------------------
# Evolution Strategies
# -----------------------------
def evolution_strategy(n_generations=200, population_size=30, sigma=0.7):
    population = np.random.rand(population_size, n_foods) * 2
    for _ in range(n_generations):
        fitness_values = np.array([fitness(ind) for ind in population])
        num_parents = max(1, population_size // 5)
        parents = population[fitness_values.argsort()[:num_parents]]
        population = np.array([
            np.clip(parents[np.random.randint(num_parents)] + np.random.randn(n_foods) * sigma, 0, None)
            for _ in range(population_size)
        ])
    fitness_values = np.array([fitness(ind) for ind in population])
    return population[fitness_values.argmin()]

# -----------------------------
# Run optimization
# -----------------------------
if run_button:
    if n_foods == 0:
        st.error("❌ Please select at least one meal to optimize.")
    else:
        with st.spinner("Optimizing meal plan..."):
            best_portions = evolution_strategy()

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

        result_df = pd.DataFrame(results, columns=["Food", "Quantity", "Calories", "Protein", "Fat", "Cost"])

        st.subheader("🍽️ Optimal Meal Plan")
        st.table(result_df)

        st.subheader("💰 Minimum Total Daily Cost")
        st.write("RM", round(result_df["Cost"].sum(), 2))

        st.subheader("📊 Total Nutrition Achieved")
        st.write("Calories:", round(result_df["Calories"].sum(), 2))
        st.write("Protein:", round(result_df["Protein"].sum(), 2), "g")
        st.write("Fat:", round(result_df["Fat"].sum(), 2), "g")

        st.success("🎉 Optimization completed!")
