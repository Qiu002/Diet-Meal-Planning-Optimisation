import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt

st.title("🍽️ Smart Diet Meal Optimizer")
st.write("Optimizes each meal cost while satisfying nutrition and health constraints.")

# ---------------- Upload CSV ----------------
uploaded_file = st.file_uploader("📂 Upload your meal dataset CSV", type=["csv"])

if not uploaded_file:
    st.info("Upload your CSV file to start.")
    st.stop()

data = pd.read_csv(uploaded_file)

st.subheader("📋 Dataset Preview")
st.dataframe(data.head())

# Column aliases based on your file
CAL = "Calories"
PRO = "Protein"
FAT = "Fat"
SUGAR = "Sugar"
SODIUM = "Sodium"
PRICE = "Price_RM"

# ---------------- USER SETTINGS ----------------
st.sidebar.header("🎯 Daily Nutrition Requirements")

req_cal = st.sidebar.number_input("Minimum Calories", 1000, 4000, 1800)
req_pro = st.sidebar.number_input("Minimum Protein (g)", 20, 300, 60)
req_fat = st.sidebar.number_input("Maximum Fat (g)", 10, 300, 80)

st.sidebar.header("🥗 Per-Meal Calorie Targets")
b_target = st.sidebar.slider("Breakfast (%)", 10, 40, 25)
l_target = st.sidebar.slider("Lunch (%)", 20, 50, 35)
d_target = st.sidebar.slider("Dinner (%)", 20, 50, 30)
s_target = st.sidebar.slider("Snacks (%)", 5, 30, 10)

# normalize so they total 100%
total_pct = b_target + l_target + d_target + s_target
b_target /= total_pct
l_target /= total_pct
d_target /= total_pct
s_target /= total_pct

# ---------------- DISEASE FILTER ----------------
st.sidebar.header("🩺 Health Condition (optional)")
disease = st.sidebar.selectbox(
    "Select Disease",
    ["None", "Diabetes", "Hypertension", "High Cholesterol"]
)

def disease_penalty(row):
    penalty = 0
    if disease == "Diabetes":
        penalty += row[SUGAR] * 0.5
    elif disease == "Hypertension":
        penalty += row[SODIUM] * 0.02
    elif disease == "High Cholesterol":
        penalty += row[FAT] * 0.3
    return penalty

# ---------------- Evolution Strategy per meal ----------------
pop_size = 40
generations = 250
mutation_rate = 0.1

def optimize_meal(meal_col, target_calories):
    n = len(data)
    population = [random.randrange(n) for _ in range(pop_size)]

    for _ in range(generations):
        offspring = []

        for parent in population:
            child = parent
            if random.random() < mutation_rate:
                child = random.randrange(n)
            offspring.append(child)

        combined = population + offspring

        def meal_score(i):
            row = data.loc[i]
            price = row[PRICE]
            cal_pen = abs(row[CAL] - target_calories)
            health_pen = disease_penalty(row)
            return price + 0.01 * cal_pen + health_pen

        combined = sorted(combined, key=meal_score)
        population = combined[:pop_size]

    best = population[0]
    return data.loc[best]

# ---------------- RUN OPTIMIZATION ----------------
if st.button("🚀 Optimize Meal Plan"):
    # target calories per meal
    b_cal_goal = req_cal * b_target
    l_cal_goal = req_cal * l_target
    d_cal_goal = req_cal * d_target
    s_cal_goal = req_cal * s_target

    breakfast = optimize_meal("Breakfast Suggestion", b_cal_goal)
    lunch = optimize_meal("Lunch Suggestion", l_cal_goal)
    dinner = optimize_meal("Dinner Suggestion", d_cal_goal)
    snack = optimize_meal("Snack Suggestion", s_cal_goal)

    st.success("Optimization completed!")

    # ----------- display results ----------
    st.subheader("🍽️ Optimized Daily Meal Plan")

    st.write(f"🍳 **Breakfast:** {breakfast['Breakfast Suggestion']} — RM {breakfast[PRICE]:.2f}")
    st.write(f"🍛 **Lunch:** {lunch['Lunch Suggestion']} — RM {lunch[PRICE]:.2f}")
    st.write(f"🍲 **Dinner:** {dinner['Dinner Suggestion']} — RM {dinner[PRICE]:.2f}")
    st.write(f"🍪 **Snack:** {snack['Snack Suggestion']} — RM {snack[PRICE]:.2f}")

    total_price = breakfast[PRICE] + lunch[PRICE] + dinner[PRICE] + snack[PRICE]
    st.subheader(f"💰 Total Daily Cost: **RM {total_price:.2f}**")

    total_cal = breakfast[CAL] + lunch[CAL] + dinner[CAL] + snack[CAL]
    total_pro = breakfast[PRO] + lunch[PRO] + dinner[PRO] + snack[PRO]
    total_fat = breakfast[FAT] + lunch[FAT] + dinner[FAT] + snack[FAT]

    st.subheader("📊 Nutrition Summary")
    st.write(f"🔥 Calories: {total_cal:.1f} kcal")
    st.write(f"💪 Protein: {total_pro:.1f} g")
    st.write(f"🧈 Fat: {total_fat:.1f} g")

    # warnings
    if total_cal < req_cal:
        st.warning("❌ Daily calories requirement NOT met")
    if total_pro < req_pro:
        st.warning("❌ Protein requirement NOT met")
    if total_fat > req_fat:
        st.warning("❌ Fat limit exceeded")

    # ------------ chart --------------
    st.subheader("📈 Calorie Distribution per Meal")
    labels = ["Breakfast", "Lunch", "Dinner", "Snack"]
    values = [breakfast[CAL], lunch[CAL], dinner[CAL], snack[CAL]]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    st.pyplot(fig)

    # ------------- export PDF --------------
    if st.button("📥 Export Meal Plan as PDF"):
        file_path = "meal_plan.pdf"
        doc = SimpleDocTemplate(file_path)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Optimized Meal Plan", styles['Title']))
        story.append(Spacer(1, 12))

        for label, row in zip(
            ["Breakfast", "Lunch", "Dinner", "Snack"],
            [breakfast, lunch, dinner, snack]
        ):
            story.append(Paragraph(f"{label}: {row[label + ' Suggestion']}", styles['Normal']))
            story.append(Paragraph(f"Calories: {row[CAL]} kcal", styles['Normal']))
            story.append(Paragraph(f"Price: RM {row[PRICE]:.2f}", styles['Normal']))
            story.append(Spacer(1, 12))
