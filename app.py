import streamlit as st
import pandas as pd
import random

st.title("🍽️ Random Meal Planner with Cost Optimization")
st.write("Selects random meals that meet basic nutrition requirements while minimizing total daily cost.")

# ---------------- Upload CSV ----------------
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.subheader("📋 Dataset Preview")
    st.dataframe(data.head())

    # ---------------- Nutrition Targets ----------------
    st.sidebar.header("🎯 Daily Nutrition Requirements")
    req_cal = st.sidebar.number_input("Minimum Calories", 1200, 4000, 1800)
    req_pro = st.sidebar.number_input("Minimum Protein (g)", 30, 300, 60)
    req_fat = st.sidebar.number_input("Maximum Fat (g)", 10, 300, 80)

    st.sidebar.header("⚙️ Random Meal Planner Settings")
    num_trials = st.sidebar.slider("Number of Random Combinations", 10, 1000, 200)

    # ---------------- Run Random Meal Optimization ----------------
    if st.button("🚀 Generate Random Meal Plan"):
        best_plan = None
        lowest_cost = float("inf")

        for _ in range(num_trials):
            # Randomly select one meal of each type
            bmeal_row = data.sample(n=1).iloc[0]
            lmeal_row = data.sample(n=1).iloc[0]
            dmeal_row = data.sample(n=1).iloc[0]
            smeal_row = data.sample(n=1).iloc[0]

            # Sum total nutrients
            total_cal = bmeal_row["Calories"] + lmeal_row["Calories"] + dmeal_row["Calories"] + smeal_row["Calories"]
            total_pro = bmeal_row["Protein"] + lmeal_row["Protein"] + dmeal_row["Protein"] + smeal_row["Protein"]
            total_fat = bmeal_row["Fat"] + lmeal_row["Fat"] + dmeal_row["Fat"] + smeal_row["Fat"]

            # Sum total cost
            total_cost = bmeal_row["Price_RM"] + lmeal_row["Price_RM"] + dmeal_row["Price_RM"] + smeal_row["Price_RM"]

            # Check if this combination meets nutrition requirements
            if total_cal >= req_cal and total_pro >= req_pro and total_fat <= req_fat:
                # Keep the plan if it has lower total cost than previous
                if total_cost < lowest_cost:
                    lowest_cost = total_cost
                    best_plan = {
                        "Breakfast": bmeal_row,
                        "Lunch": lmeal_row,
                        "Dinner": dmeal_row,
                        "Snack": smeal_row,
                        "Total Calories": total_cal,
                        "Total Protein": total_pro,
                        "Total Fat": total_fat,
                        "Total Cost": total_cost
                    }

        if best_plan:
            st.success("✅ Optimized Random Meal Plan Found!")

            st.subheader("🍽️ Meals Selected")
            st.write(f"🍳 **Breakfast:** {best_plan['Breakfast']['Breakfast Suggestion']} — RM {best_plan['Breakfast']['Price_RM']:.2f}")
            st.write(f"🍛 **Lunch:** {best_plan['Lunch']['Lunch Suggestion']} — RM {best_plan['Lunch']['Price_RM']:.2f}")
            st.write(f"🍲 **Dinner:** {best_plan['Dinner']['Dinner Suggestion']} — RM {best_plan['Dinner']['Price_RM']:.2f}")
            st.write(f"🍪 **Snack:** {best_plan['Snack']['Snack Suggestion']} — RM {best_plan['Snack']['Price_RM']:.2f}")

            st.subheader("💰 Total Daily Cost")
            st.write(f"👉 RM {best_plan['Total Cost']:.2f}")

            st.subheader("📊 Total Nutritional Summary")
            st.write(f"🔥 Calories: {best_plan['Total Calories']} kcal")
            st.write(f"💪 Protein: {best_plan['Total Protein']} g")
            st.write(f"🧈 Fat: {best_plan['Total Fat']} g")
        else:
            st.warning("⚠️ Could not find any meal combination that meets the requirements. Try increasing the number of random combinations or relaxing constraints.")
else:
    st.info("Upload your CSV file to start.")
