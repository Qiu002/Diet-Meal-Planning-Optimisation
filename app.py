import streamlit as st
import pandas as pd
from pulp import LpProblem, LpVariable, LpMinimize, LpStatus, lpSum, value

st.set_page_config(page_title="Meal Plan Optimizer", page_icon="🥗")

st.title("🥗 Daily Meal Plan Optimizer")
st.write("Select a set of meals that meets nutritional requirements at the **lowest total cost**.")

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("Food_and_Nutrition_with_Price.csv")

st.subheader("📦 Available Meals")
st.dataframe(df)

# -----------------------------
# USER INTERACTION SECTION
# -----------------------------
st.sidebar.header("⚙️ Set Your Requirements")

# nutrition constraints
cal_need = st.sidebar.number_input("Minimum Calories (kcal)", value=2000, step=100)
pro_need = st.sidebar.number_input("Minimum Protein (g)", value=50, step=5)
fat_need = st.sidebar.number_input("Minimum Fat (g)", value=70, step=5)

# allow user to pick foods to include
meal_options = df["Food"].tolist()
selected_meals = st.sidebar.multiselect("Select meals to consider in optimization", meal_options, default=meal_options)

st.sidebar.write("Click button to calculate optimal plan ⬇️")
run_button = st.sidebar.button("Optimize Meal Plan")

# -----------------------------
# Filter based on selection
# -----------------------------
filtered_df = df[df["Food"].isin(selected_meals)].reset_index(drop=True)

# -----------------------------
# OPTIMIZATION
# -----------------------------
if run_button:

    st.subheader("🧮 Running Optimization...")

    # define LP problem
    prob = LpProblem("Meal_Diet_Problem", LpMinimize)

    # decision variable: number of portions of each meal (continuous, not forced integer)
    x = LpVariable.dicts("portion", filtered_df.index, lowBound=0)

    # objective function: minimize total cost
    prob += lpSum(filtered_df.loc[i, "Price"] * x[i] for i in filtered_df.index)

    # constraints
    prob += lpSum(filtered_df.loc[i, "Calories"] * x[i] for i in filtered_df.index) >= cal_need
    prob += lpSum(filtered_df.loc[i, "Protein"] * x[i] for i in filtered_df.index) >= pro_need
    prob += lpSum(filtered_df.loc[i, "Fat"] * x[i] for i in filtered_df.index) >= fat_need

    # solve
    prob.solve()

    st.write("Status:", LpStatus[prob.status])

    if LpStatus[prob.status] != "Optimal":
        st.error("❌ No feasible solution found. Try adjusting nutrition requirements or include more meals.")
    else:
        # prepare results
        results = []
        for i in filtered_df.index:
            qty = value(x[i])
            if qty > 0.001:
                results.append([
                    filtered_df.loc[i, "Food"],
                    round(qty, 2),
                    round(filtered_df.loc[i, "Calories"] * qty, 2),
                    round(filtered_df.loc[i, "Protein"] * qty, 2),
                    round(filtered_df.loc[i, "Fat"] * qty, 2),
                    round(filtered_df.loc[i, "Price"] * qty, 2)
                ])

        result_df = pd.DataFrame(results,
                                 columns=["Food", "Quantity (servings)", "Calories", "Protein", "Fat", "Cost (RM)"])

        st.subheader("🍽️ Optimal Meal Plan")
        st.table(result_df)

        st.subheader("💰 Minimum Total Daily Cost")
        st.write("RM", round(result_df["Cost (RM)"].sum(), 2))

        st.subheader("📊 Total Nutrition Achieved")
        st.write("Calories:", round(result_df["Calories"].sum(), 2))
        st.write("Protein:", round(result_df["Protein"].sum(), 2), "g")
        st.write("Fat:", round(result_df["Fat"].sum(), 2), "g")

        st.success("🎉 Optimization complete — dashboard is fully interactive!")

