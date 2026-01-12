import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Meal Plan Optimizer", page_icon="🥗")
st.title("🥗 Daily Meal Plan Optimizer (Fast)")

# -----------------------------
# Load CSV
# -----------------------------
try:
    df = pd.read_csv("Food_and_Nutrition_with_Price.csv")
except:
    st.error("CSV file not found.")
    st.stop()

# Auto-detect columns
food_col = next((c for c in df.columns if "food" in c.lower()), None)
cal_col = next((c for c in df.columns if "calorie" in c.lower()), None)
pro_col = next((c for c in df.columns if "protein" in c.lower()), None)
fat_col = next((c for c in df.columns if "fat" in c.lower()), None)
price_col = next((c for c in df.columns if "price" in c.lower()), None)

if None in [food_col, cal_col, pro_col, fat_col, price_col]:
    st.error("❌ Could not detect required columns.")
    st.stop()

# -----------------------------
# Nutrition requirements
# -----------------------------
st.sidebar.header("⚙️ Set Nutrition Requirements")
cal_need = st.sidebar.number_input("Minimum Calories", value=2000, step=100)
pro_need = st.sidebar.number_input("Minimum Protein (g)", value=50, step=5)
fat_need = st.sidebar.number_input("Minimum Fat (g)", value=70, step=5)

# Meal selection
meal_options = df[food_col].tolist()
selected_meals = st.sidebar.multiselect("Select meals to include", meal_options, default=meal_options)
run_button = st.sidebar.button("Optimize Meal Plan")

# -----------------------------
# Filtered dataset
# -----------------------------
filtered_df = df[df[food_col].isin(selected_meals)].reset_index(drop=True)
n_foods = len(filtered_df)

# -----------------------------
# Vectorized fitness function
# -----------------------------
cal_values = filtered_df[cal_col].values
pro_values = filtered_df[pro_col].values
fat_values = filtered_df[fat_col].values
price_values = filtered_df[price_col].values

def fitness(pop):
    # pop: shape (population_size, n_foods)
    calories = pop @ cal_values
    protein = pop @ pro_values
    fat = pop @ fat_values
    cost = pop @ price_values

    penalty = np.zeros(pop.shape[0])
    penalty += np.maximum(0, cal_need - calories) * 10
    penalty += np.maximum(0, pro_need - protein) * 10
    penalty += np.maximum(0, fat_need - fat) * 10

    return cost + penalty

# -----------------------------
# Fast Evolution Strategy
# -----------------------------
def evolution_strategy(n_generations=100, population_size=20, sigma=0.5):
    pop = np.random.rand(population_size, n_foods) * 2
    for _ in range(n_generations):
        fit_vals = fitness(pop)
        num_parents = max(1, population_size // 5)
        parents = pop[np.argsort(fit_vals)[:num_parents]]

        # Generate next population
        indices = np.random.randint(num_parents, size=population_size)
        noise = np.random.randn(population_size, n_foods) * sigma
        pop = np.clip(parents[indices] + noise, 0, None)
    return pop[np.argmin(fitness(pop))]

# -----------------------------
# Run optimization
# -----------------------------
if run_button:
    if n_foods == 0:
        st.error("❌ Please select at least one meal.")
    else:
        with st.spinner("Optimizing meal plan quickly..."):
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
