import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import requests
import json

# Set up clean visual page layout
st.set_page_config(page_title="🦾 FitTrack Pro AI", page_icon="🏋️‍♂️", layout="wide")

st.title("🏋️‍♂️ FitTrack Pro + Nutrition Suite")
st.subheader("Your Advanced Workout Analytics, Grid Logger & AI Training Assistant")

st.markdown("---")

# ==================== NEW SIDEBAR: SMART NUTRITION CALCULATOR ====================
st.sidebar.header("🥗 Smart Nutrition Calculator")
with st.sidebar.expander("Calculate My Daily Macros", expanded=False):
    weight_kg = st.number_input("Your Weight (kg):", min_value=30.0, max_value=200.0, value=60.0, step=0.5)
    fitness_goal = st.selectbox("Nutrition Goal:", ["Muscle Gain / Bulk", "Maintenance", "Fat Loss / Cut"])
    
    # Calculate macro estimations based on standard fitness science formulas
    if fitness_goal == "Muscle Gain / Bulk":
        total_calories = int((weight_kg * 2.2) * 16)
        protein_g = int(weight_kg * 2.2)  # ~1g per lb of bodyweight
        fats_g = int((total_calories * 0.25) / 9)
    elif fitness_goal == "Fat Loss / Cut":
        total_calories = int((weight_kg * 2.2) * 12)
        protein_g = int(weight_kg * 2.4)  # Higher protein during deficit
        fats_g = int((total_calories * 0.20) / 9)
    else:
        total_calories = int((weight_kg * 2.2) * 14)
        protein_g = int(weight_kg * 2.0)
        fats_g = int((total_calories * 0.25) / 9)
        
    carbs_g = int((total_calories - ((protein_g * 4) + (fats_g * 9))) / 4)
    
    # Display results cleanly inside the sidebar
    st.markdown(f"**Target Calories:** `{total_calories} kcal`")
    st.write(f"🍗 Protein: **{protein_g}g**")
    st.write(f"🥑 Fats: **{fats_g}g**")
    st.write(f"🍚 Carbs: **{carbs_g}g**")

# Initialize base historical training arrays if missing
historical_dates = [
    "2026-08-12", "2026-08-14", "2026-08-17", "2026-08-18", "2026-08-19", 
    "2026-08-24", "2026-08-26", "2026-08-27", "2026-08-28", "2026-08-31", 
    "2026-09-01", "2026-09-05", "2026-09-07", "2026-09-08", "2026-09-09", 
    "2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18", "2026-09-22"
]
machine_dataset = {
    "Date": historical_dates,
    "Rudern sitzend / Seated row": [0.0, 39.4, 0.0, 39.4, 0.0, 0.0, 40.3, 0.0, 40.3, 0.0, 39.4, 0.0, 34.6, 0.0, 39.4, 0.0, 39.4, 0.0, 39.4, 0.0, 41.9],
    "Adducktor":                   [27.9, 0.0, 29.0, 0.0, 29.0, 29.0, 0.0, 29.5, 0.0, 29.0, 0.0, 28.3, 0.0, 33.2, 0.0, 28.3, 0.0, 21.9, 0.0, 28.1, 0.0],
    "Shoulderpress / Schulterpress": [0.0, 21.9, 0.0, 21.9, 0.0, 0.0, 17.9, 0.0, 17.9, 0.0, 17.9, 0.0, 21.9, 0.0, 21.9, 0.0, 17.2, 0.0, 21.9, 0.0, 21.5],
    "Latzug / Lat pull down":       [0.0, 34.7, 0.0, 34.7, 0.0, 0.0, 34.7, 0.0, 34.7, 0.0, 34.7, 0.0, 36.5, 0.0, 44.3, 0.0, 44.3, 0.0, 44.3, 0.0, 44.8],
    "Seated leg curl / beinbeuger": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 27.9, 0.0, 28.3, 0.0, 28.3, 0.0, 32.3, 0.0, 28.3, 0.0],
    "Pec fly":                     [0.0, 6.8, 0.0, 6.8, 0.0, 0.0, 8.0, 0.0, 8.0, 0.0, 8.3, 0.0, 8.3, 0.0, 8.5, 0.0, 8.5, 0.0, 8.5, 0.0, 9.3],
    "Tricep machine":              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 40.3, 0.0, 42.6]
}

try:
    df_history = pd.read_csv("clean_workout_history.csv")
except FileNotFoundError:
    df_history = pd.DataFrame(machine_dataset)
    df_history.to_csv("clean_workout_history.csv", index=False)

# Render Application UI Tabs
tab_analytics, tab_log, tab_ai, tab_file = st.tabs(["📊 Progress Charts", "📝 Log Today's Session", "🤖 AI Training Coach", "📋 View Raw Log Files"])

# --- TAB 1: DISPLAY TIMELINE CHARTS ---
with tab_analytics:
    st.markdown("### 📈 Visual Trajectory Analytics")
    machines_list = [col for col in df_history.columns if col != "Date"]
    selected_machine = st.selectbox("Choose Exercise Machine to Visualize:", machines_list)
    
    plot_df = df_history[["Date", selected_machine]].copy()
    plot_df["Date"] = pd.to_datetime(plot_df["Date"])
    plot_df = plot_df.set_index("Date").replace(0, np.nan).dropna()
    
    if not plot_df.empty:
        st.line_chart(plot_df, use_container_width=True)
        current_peak = round(plot_df[selected_machine].max(), 1)
        st.metric(label=f"Current Top Calculated 1RM limit for {selected_machine}", value=f"{current_peak} kg", delta="🏆 All-Time Max")

# --- TAB 2: POWERFUL GRID-BASED INPUT FORMS ---
with tab_log:
    st.markdown("### 📆 Session Configuration")
    col_a, col_b = st.columns(2)
    with col_a: log_date = st.date_input("Workout Date:", date.today())
    with col_b: day_type = st.selectbox("Select Today's Routine Split:", ["Upper Body", "Lower Body", "Rest Day"])
    st.markdown("---")
    
    if day_type == "Upper Body":
        active_machines = ["Rudern sitzend / Seated row", "Shoulderpress / Schulterpress", "Latzug / Lat pull down", "Pec fly", "Tricep machine"]
    elif day_type == "Lower Body":
        active_machines = ["Adducktor", "Seated leg curl / beinbeuger"]
    else:
        active_machines = []
        st.info("🛋️ Active rest and recovery day. Enjoy your break!")

    if active_machines:
        st.markdown("### 📋 Enter Weight & Reps Grid")
        with st.form("grid_workout_form", clear_on_submit=True):
            calculated_maxes = {}
            for mach in active_machines:
                st.markdown(f"#### ⚙️ {mach}")
                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
                with c1: w1 = st.number_input("S1 Wt (kg)", min_value=0.0, step=0.5, key=f"{mach}_w1")
                with c2: r1 = st.number_input("S1 Reps", min_value=0, step=1, key=f"{mach}_r1")
                with c3: w2 = st.number_input("S2 Wt (kg)", min_value=0.0, step=0.5, key=f"{mach}_w2")
                with c4: r2 = st.number_input("S2 Reps", min_value=0, step=1, key=f"{mach}_r2")
                with c5: w3 = st.number_input("S3 Wt (kg)", min_value=0.0, step=0.5, key=f"{mach}_w3")
                with c6: r3 = st.number_input("S3 Reps", min_value=0, step=1, key=f"{mach}_r3")
                with c7: w4 = st.number_input("S4 Wt (kg)", min_value=0.0, step=0.5, key=f"{mach}_w4")
                with c8: r4 = st.number_input("S4 Reps", min_value=0, step=1, key=f"{mach}_r4")
                
                set_weights, set_reps = [w1, w2, w3, w4], [r1, r2, r3, r4]
                calculated_1rms = [w * (1 + r / 30) for w, r in zip(set_weights, set_reps) if w > 0 and r > 0]
                calculated_maxes[mach] = max(calculated_1rms) if calculated_1rms else 0.0
                st.markdown("---")
            
            submit_btn = st.form_submit_button("💾 Lock and Save Session Metrics", use_container_width=True)
            if submit_btn:
                new_row = {"Date": str(log_date)}
                for col in df_history.columns:
                    if col != "Date": new_row[col] = calculated_maxes.get(col, 0.0)
                df_history = pd.concat([df_history, pd.DataFrame([new_row])], ignore_index=True)
                df_history.to_csv("clean_workout_history.csv", index=False)
                st.balloons()

# --- TAB 3: LOCAL OFFLINE AI COACH CENTER ---
with tab_ai:
    st.markdown("### 🤖 Local AI Personal Trainer Insights")
    ai_goal = st.selectbox("What advice do you need today?", [
        "Analyze my strength progression history trends",
        "Generate a tailored workout split strategy based on my lifts",
        "Provide specific nutritional macro counts for muscle retention"
    ])
    
    latest_stats = df_history.tail(1).to_dict(orient='records') if not df_history.empty else {}
    
    if st.button("🧠 Consult My Local AI Coach"):
        context_prompt = f"""
        You are a highly supportive strength coach. Athlete name: Minal. Recent max 1RM metrics:
        {json.dumps(latest_stats, indent=2)}
        Answer this query clearly: '{ai_goal}'. Keep your tone motivating and practical.
        """
        
        lm_studio_url = "http://localhost:1234/v1/chat/completions"
        payload = {
            "model": "local-model",
            "messages": [{"role": "user", "content": context_prompt}],
            "temperature": 0.7
        }
        
        with st.spinner("🤖 Local AI Trainer is reviewing your files..."):
            try:
                response = requests.post(lm_studio_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
                if response.status_code == 200:
                    ai_text = response.json()['choices']['message']['content']
                    st.markdown("---")
                    st.success("💪 **AI Coach Feedback:**")
                    st.write(ai_text)
                else:
                    st.error(f"Error {response.status_code}. Ensure LM Studio local server is running.")
            except Exception as e:
                st.warning("Could not reach LM Studio. Verify the green 'Start Server' button is active!")

# --- TAB 4: FILE VIEW SPREADSHEETS ---
with tab_file:
    st.markdown("### 📁 Live System Log Registry")
    st.dataframe(df_history, use_container_width=True)
