import streamlit as st
import pandas as pd
import numpy as np
import random
import re

st.title("🍽️ Diet Meal Plan Optimizer with Evolution Strategies")
st.write("Select a daily meal plan meeting nutritional needs at minimum total cost.")

# ------------------------ Upload CSV ------------------------
uploaded_file = st.file_uploader("📂 Upload your meal dataset CSV", type=["csv"])

def normalize_columns(df):
    df = df.copy()
    new_cols = []
    for c in df.columns:
        c2 = c.lower()
        c2 = re.sub(r'[^a-z0-9]+', '', c2)
        new_cols.append(c2)
    df.columns = new_cols
    return df

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    # normalize column names
    data = normalize_columns(data)

    # ----------- auto-detect required columns -----------
    column_map = {}

    # calories
    for cand in ["calories", "calorie", "kcal", "energy"]:
        if cand in data.columns:
            column_map["calories"] = cand
            break

    # protein
    for cand in ["protein", "proteins"]:
        if cand in data.columns:
            column_map["protein"] = cand
            break

    # fat
    for cand in ["fat", "fats", "totalfat"]:
        if cand in data.columns:
            column_map["fat"] = cand
            break

    # price / cost
    for cand in ["price", "cost", "pricerm", "pricepermeal"]:
        if cand in data.columns:
            column_map["price"] = cand
            break

    # meal type
    for cand in ["mealtype", "type", "category", "meal_category"]:
        if cand in data.columns:
            column_map["meal_type"] = cand
            break

    required = ["calories", "protein", "fat", "price", "meal_type"]

    missing = [c for c in required if c not in column_map]

    if missing:
        st.error(
            "Your CSV is missing the following required logical fields: "
            + ", ".join(missing)
            + ".\nPlease ensure your CSV has columns for calories, protein, fat, price, and meal type."
        )
        st.stop()

    st.subheader("📋 Preview of Meal Dataset (normalized)")
    st.dataframe(data.head())

    # ------------------------ User Inputs ------------------------
    st.sidebar.header("⚙️ Nutritional Requirements")
    req_cal = st.sidebar.number_input("Minimum Daily Calories", 1200, 4000, 1800)
    req_pro = st.sidebar.number_input("Minimum Daily Protein (g)", 30, 300, 60)
    req_fat = st.sidebar.number_input("Maximum Daily Fat (g)", 10, 300, 80)

    pop_size = st.sidebar.slider("Population Size", 10, 200, 50)
    generations = st.sidebar.slider("Generations", 10, 500, 200)
    mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.1)

    # ------------------------ Fitness Function ------------------------
    def fitness(individual):
        subset = data.iloc[individual]

        total_cal = subset[column_map["calories"]].sum()
        total_pro = subset[column_map["protein"]].sum()
        total_fat = subset[column_map["fat"]].sum()
        total_cost = subset[column_map["price"]].sum()

        penalty = 0
        if total_cal < req_cal:
            penalty += (req_cal - total_cal)
        if total_pro < req_pro:
            penalty += (req_pro - total_pro)
        if total_fat > req_fat:
            penalty += (total_fat - req_fat)

        return total_cost + 10 * penalty

    # ------------------------ Evolution Strategies ------------------------
    def evolution_strategies():
        n = len(data)
        mu = pop_size

        population = [random.sample(range(n), 4) for _ in range(mu)]

        for _ in range(generations):
            offspring = []
            for parent in population:
                child = parent.copy()
                if random.random() < mutation_rate:
                    idx = random.randrange(4)
                    child[idx] = random.randrange(n)
                offspring.append(child)

            combined = population + offspring
            scored = sorted(combined, key=lambda ind: fitness(ind))
            population = scored[:mu]

        best = population[0]
        return data.iloc[best]

    # ------------------------ Run Optimizer ------------------------
    if st.button("🚀 Optimize Meal Plan"):
        best_plan = evolution_strategies()

        st.success("Optimization completed!")

        st.subheader("🥗 Best Daily Meal Plan")

        mt = column_map["meal_type"]

        breakfast = best_plan[best_plan[mt].str.contains("break", case=False, na=False)].head(1)
        lunch = best_plan[best_plan[mt].str.contains("lunch", case=False, na=False)].head(1)
        dinner = best_plan[best_plan[mt].str.contains("dinner", case=False, na=False)].head(1)
        snack = best_plan[best_plan[mt].str.contains("snack", case=False, na=False)].head(1)

        st.write("### 🍳 Breakfast Suggestion")
        st.table(breakfast)

        st.write("### 🍛 Lunch Suggestion")
        st.table(lunch)

        st.write("### 🍲 Dinner Suggestion")
        st.table(dinner)

        st.write("### 🍪 Snack Suggestion")
        st.table(snack)

        total_cal = best_plan[column_map["calories"]].sum()
        total_pro = best_plan[column_map["protein"]].sum()
        total_fat = best_plan[column_map["fat"]].sum()
        total_cost = best_plan[column_map["price"]].sum()

        st.subheader("📊 Nutrition Summary")
        st.write(f"Total Calories: **{total_cal}** kcal")
        st.write(f"Total Protein: **{total_pro}** g")
        st.write(f"Total Fat: **{total_fat}** g")
        st.write(f"💰 Total Cost: **RM {total_cost:.2f}**")

else:
    st.info("Please upload your CSV file to begin.")
