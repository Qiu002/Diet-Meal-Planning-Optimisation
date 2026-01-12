import streamlit as st
import pandas as pd
from pulp import LpProblem, LpVariable, LpMinimize, LpStatus, lpSum, value

st.set_page_config(page_title="Meal Plan Optimizer", page_icon="🥗")

st.title("🥗 Daily Meal Plan Optimizer")
st.write("Select a daily meal plan that meets nutritional requirements at the lowest total cost.")

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

st.write("Detected columns:", list(df.columns))

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

run_button = st.sidebar.button("Optimize Meal Plan")

# -----------------------------
# Filter selection
# -----------------------------
filtered_df = df[df[food_col].isin(selected_meals)].reset_index(drop=True)

# -----------------------------
# OPTIMIZATION
# -----------------------------
if run_button:

    prob = LpProblem("Diet_Optimization", LpMinimize)

    # decision variables (portion amounts)
    x = LpVariable.dicts("portion", filtered_df.index, lowBound=0)

    # objective function
    prob += lpSum(filtered_df.loc[i, price_col] * x[i] for i in filtered_df.index)

    # constraints
    prob += lpSum(filtered_df.loc[i, cal_col] * x[i] for i in filtered_df.index) >= cal_need
    prob += lpSum(filtered_df.loc[i, pro_col] * x[i] for i in filtered_df.index) >= pro_need
    prob += lpSum(filtered_df.loc[i, fat_col] * x[i] for i in filtered_df.index) >= fat_need

    prob.solve()

    st.subheader("🧮 Optimization Status")
    st.write(LpStatus[prob.status])

    if LpStatus[prob.status] != "Optimal":
        st.error("❌ No feasible solution. Increase food choices or reduce requirements.")
    else:
        results = []
        for i in filtered_df.index:
            qty = value(x[i])
            if qty > 0.001:
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

        st.success("🎉 Interactive optimization completed!")
