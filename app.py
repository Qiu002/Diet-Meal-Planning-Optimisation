import streamlit as st
import pandas as pd
from pulp import LpProblem, LpVariable, LpMinimize, LpStatus, lpSum, value

st.set_page_config(page_title="Meal Plan Optimizer", page_icon="🥗")

st.title("🥗 Daily Meal Plan Optimizer")
st.write("This tool finds the **lowest-cost daily meal plan** that still meets basic nutritional requirements.")

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv("Food_and_Nutrition_with_Price.csv") 

# --------- silently normalize column names ---------
norm = {c.lower().strip(): c for c in df.columns}

def get_col(possible):
    for p in possible:
        if p in norm:
            return norm[p]
    return None

food_col = get_col(["food", "item", "name", "meal"])
cal_col = get_col(["calories", "energy", "kcal"])
pro_col = get_col(["protein", "proteins"])
fat_col = get_col(["fat", "total fat"])
price_col = get_col(["price", "cost", "price (rm)", "rm"])

required = [food_col, cal_col, pro_col, fat_col, price_col]

food_col = get_col(["food", "item", "name", "meal", "food_name"])
cal_col  = get_col(["calories", "energy", "kcal"])
pro_col  = get_col(["protein", "proteins", "protein_g"])
fat_col  = get_col(["fat", "total fat", "fat_g"])
price_col= get_col(["price", "cost", "price (rm)", "rm", "rm_price"])


# -----------------------------
# Show dataset
# -----------------------------
st.subheader("📦 Available Meals")
st.write("Columns in CSV:", df.columns.tolist())
st.write("Mapped columns:", food_col, cal_col, pro_col, fat_col, price_col)
st.dataframe(df[[food_col, cal_col, pro_col, fat_col, price_col]])

# -----------------------------
# User input: nutrition targets
# -----------------------------
st.sidebar.header("⚙️ Nutrition Requirements")

cal_need = st.sidebar.number_input("Minimum Calories", value=2000, step=100)
pro_need = st.sidebar.number_input("Minimum Protein (g)", value=50, step=5)
fat_need = st.sidebar.number_input("Minimum Fat (g)", value=70, step=5)

run_button = st.sidebar.button("Run Optimization")

# -----------------------------
# Optimization
# -----------------------------
if run_button:

    prob = LpProblem("Diet_Optimization", LpMinimize)

    # decision variables (serving quantity)
    x = LpVariable.dicts("portion", df.index, lowBound=0)

    # objective: minimize total cost
    prob += lpSum(df.loc[i, price_col] * x[i] for i in df.index)

    # constraints
    prob += lpSum(df.loc[i, cal_col] * x[i] for i in df.index) >= cal_need
    prob += lpSum(df.loc[i, pro_col] * x[i] for i in df.index) >= pro_need
    prob += lpSum(df.loc[i, fat_col] * x[i] for i in df.index) >= fat_need

    prob.solve()

    st.subheader("🧮 Optimization Status")
    st.write(LpStatus[prob.status])

    if LpStatus[prob.status] != "Optimal":
        st.error("No feasible solution found. Increase number of foods or reduce requirements.")
    else:
        results = []

        for i in df.index:
            qty = value(x[i])
            if qty > 0.001:
                results.append([
                    df.loc[i, food_col],
                    round(qty, 2),
                    round(df.loc[i, cal_col] * qty, 2),
                    round(df.loc[i, pro_col] * qty, 2),
                    round(df.loc[i, fat_col] * qty, 2),
                    round(df.loc[i, price_col] * qty, 2)
                ])

        result_df = pd.DataFrame(
            results,
            columns=["Food", "Quantity", "Calories", "Protein", "Fat", "Cost (RM)"]
        )

        st.subheader("🍽️ Optimal Meal Combination")
        st.table(result_df)

        st.subheader("💰 Minimum Total Cost")
        st.write("RM", round(result_df["Cost (RM)"].sum(), 2))

        st.subheader("📊 Total Nutrition Achieved")
        st.write("Calories:", round(result_df["Calories"].sum(), 2))
        st.write("Protein:", round(result_df["Protein"].sum(), 2), "g")
        st.write("Fat:", round(result_df["Fat"].sum(), 2), "g")

        st.success("🎉 Optimization completed successfully")
