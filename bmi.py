import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="BMI Health Dashboard", page_icon="🩺", layout="wide")


# Full-width charts and tables on both newer and older Streamlit versions
def show_chart(fig):
    try:
        st.plotly_chart(fig, width="stretch")
    except Exception:
        st.plotly_chart(fig, use_container_width=True)


def show_table(data):
    try:
        st.dataframe(data, width="stretch", hide_index=True)
    except Exception:
        st.dataframe(data, use_container_width=True, hide_index=True)


# Adult BMI categories (WHO / CDC cutoffs)
CLASS_ORDER = ["Underweight", "Normal", "Overweight", "Obese"]
CLASS_COLORS = {"Underweight": "#4C9BE8", "Normal": "#2CA02C", "Overweight": "#FF9F1C", "Obese": "#D62728"}


def adult_class(bmi):
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def obesity_class(bmi):
    if bmi < 30:
        return None
    if bmi < 35:
        return "Class 1 (30 to 34.9)"
    if bmi < 40:
        return "Class 2 (35 to 39.9)"
    return "Class 3 (40 or higher)"


# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("bmi_health_data.csv")
    # Use lowercase column names so the rest of the code is consistent
    df = df.rename(columns={"Age": "age", "Gender": "gender", "Height_cm": "height_cm",
                            "Weight_kg": "weight_kg", "BMI": "bmi", "BMI_Class": "bmi_class"})
    df["bmi_calculated"] = (df["weight_kg"] / (df["height_cm"] / 100) ** 2).round(1)
    df["age_group"] = pd.cut(df["age"], bins=[0, 17, 39, 64, 120],
                             labels=["Under 18", "18 to 39", "40 to 64", "65 and older"])
    df["is_child"] = df["age"] < 18
    return df


df = load_data()

# Sidebar Filters
st.sidebar.header("Filters")

age_min, age_max = int(df["age"].min()), int(df["age"].max())
age_range = st.sidebar.slider("Select Age Range", age_min, age_max, (age_min, age_max))
gender_filter = st.sidebar.selectbox("Gender", ["All", "Male", "Female"])
adults_only = st.sidebar.checkbox(
    "Adults only (18 and older)", value=False,
    help="Adult BMI categories do not apply to children. See the Data Quality tab.",
)

filtered_df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]
if gender_filter != "All":
    filtered_df = filtered_df[filtered_df["gender"] == gender_filter]
if adults_only:
    filtered_df = filtered_df[~filtered_df["is_child"]]

# Dashboard Title
st.title("🩺 BMI Health Classification Explorer")
st.write(
    "This dashboard shows BMI category distributions across age and gender, and includes a patient BMI check. "
    "BMI is a screening tool, not a diagnosis. For real health concerns, please talk with a healthcare provider."
)

tab_patient, tab_population, tab_quality = st.tabs(["🧍 Patient Check", "📊 Population Overview", "🔍 Data Quality"])

# ---------------- Patient Check tab ----------------
with tab_patient:
    st.subheader("🧍 Patient BMI Check")
    st.caption("Enter a patient's measurements to see their BMI, category, and healthy weight range.")

    units = st.radio("Units", ["Metric (cm, kg)", "US (ft/in, lb)"], horizontal=True)

    c1, c2, c3, c4 = st.columns(4)
    p_age = c1.number_input("Age (years)", min_value=2, max_value=110, value=45)
    p_sex = c2.selectbox("Sex", ["Female", "Male"])
    if units == "Metric (cm, kg)":
        p_height = c3.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.5)
        p_weight = c4.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=85.0, step=0.5)
    else:
        f1, f2 = c3.columns(2)
        feet = f1.number_input("Height (ft)", min_value=2, max_value=8, value=5)
        inches = f2.number_input("Height (in)", min_value=0, max_value=11, value=7)
        pounds = c4.number_input("Weight (lb)", min_value=20.0, max_value=660.0, value=187.0, step=1.0)
        p_height = (feet * 12 + inches) * 2.54
        p_weight = pounds * 0.453592
    p_waist = st.number_input(
        "Waist circumference (cm, optional, enter 0 to skip)", min_value=0.0, max_value=200.0, value=0.0, step=0.5,
        help="Waist-to-height ratio adds information about central (abdominal) fat that BMI alone misses.",
    )

    p_bmi = p_weight / (p_height / 100) ** 2
    height_m = p_height / 100
    healthy_low, healthy_high = 18.5 * height_m ** 2, 24.9 * height_m ** 2

    if p_age < 18:
        st.metric("BMI", f"{p_bmi:.1f}")
        st.warning(
            "**Adult BMI categories do not apply to patients under 18.** For children and teens, BMI is "
            "interpreted as a percentile for age and sex on CDC growth charts. Use a pediatric BMI-for-age "
            "calculator to classify this patient."
        )
    else:
        p_class = adult_class(p_bmi)
        m1, m2, m3 = st.columns(3)
        m1.metric("BMI", f"{p_bmi:.1f}")
        m2.metric("Category", p_class)
        m3.metric("Healthy weight for this height", f"{healthy_low:.0f} to {healthy_high:.0f} kg")

        if p_weight > healthy_high:
            st.info(f"This patient is **{p_weight - healthy_high:.1f} kg above** the top of the healthy range for their height.")
        elif p_weight < healthy_low:
            st.info(f"This patient is **{healthy_low - p_weight:.1f} kg below** the bottom of the healthy range for their height.")
        else:
            st.success("This patient's weight is within the healthy range for their height.")

        if obesity_class(p_bmi):
            st.write(f"Obesity severity: **{obesity_class(p_bmi)}**")

        # Clinically meaningful weight-loss targets (5% and 10% of body weight)
        if p_bmi >= 25:
            st.markdown("**Weight-loss milestones**")
            st.caption("A 5% to 10% weight loss is linked to clinically meaningful improvements in blood pressure, "
                       "blood sugar, and cholesterol.")
            goals = pd.DataFrame({
                "Goal": ["5% loss", "10% loss", "Reach BMI 24.9"],
                "Target weight (kg)": [p_weight * 0.95, p_weight * 0.90, healthy_high],
            })
            goals["Weight to lose (kg)"] = p_weight - goals["Target weight (kg)"]
            goals["New BMI"] = goals["Target weight (kg)"] / height_m ** 2
            show_table(goals.round(1))

        # Waist-to-height ratio (0.5 is a widely used cutoff for increased cardiometabolic risk)
        if p_waist > 0:
            whtr = p_waist / p_height
            if whtr >= 0.5:
                st.warning(f"Waist-to-height ratio: **{whtr:.2f}**. A ratio of 0.5 or higher suggests increased "
                           "central fat and cardiometabolic risk, even when BMI looks normal.")
            else:
                st.success(f"Waist-to-height ratio: **{whtr:.2f}** (under 0.5).")

        # Where the patient sits on the BMI scale
        bands = pd.DataFrame({
            "Category": CLASS_ORDER,
            "start": [10, 18.5, 25, 30],
            "end": [18.5, 25, 30, 50],
        })
        bands["width"] = bands["end"] - bands["start"]
        fig_scale = px.bar(bands, x="width", y=["BMI scale"] * 4, base="start", color="Category",
                           orientation="h", color_discrete_map=CLASS_COLORS,
                           title="Where this patient falls on the adult BMI scale")
        fig_scale.add_vline(x=min(max(p_bmi, 10), 50), line_width=4, line_color="black",
                            annotation_text=f"Patient: {p_bmi:.1f}", annotation_position="top")
        fig_scale.update_layout(height=260, yaxis_title="", xaxis_title="BMI", showlegend=True,
                                xaxis_range=[10, 50], legend=dict(orientation="h", y=-0.45, title=""))
        show_chart(fig_scale)

        # Compare with adults of the same sex in the dataset
        peers = df[(~df["is_child"]) & (df["gender"] == p_sex)]
        pct = (peers["bmi"] < p_bmi).mean() * 100
        st.write(f"This BMI is higher than **{pct:.0f}%** of the {len(peers)} adult {p_sex.lower()} patients in this dataset.")

        fig_peer = px.histogram(peers, x="bmi", nbins=30, color_discrete_sequence=["#9AA5B1"],
                                title=f"This patient compared with adult {p_sex.lower()} patients",
                                labels={"bmi": "BMI"})
        fig_peer.add_vline(x=p_bmi, line_width=3, line_color="black",
                           annotation_text=f"Patient: {p_bmi:.1f}", annotation_position="top")
        fig_peer.update_layout(yaxis_title="Patients")
        show_chart(fig_peer)

        st.caption(
            "BMI does not measure body fat directly and can misclassify very muscular people and older adults. "
            "Waist circumference and clinical context help complete the picture."
        )

# ---------------- Population Overview tab ----------------
with tab_population:
    st.write(f"Showing **{len(filtered_df)}** of {len(df)} patients")

    if filtered_df.empty:
        st.warning("No patients match these filters.")
    else:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Patients", len(filtered_df))
        k2.metric("Average BMI", f"{filtered_df['bmi'].mean():.1f}")
        k3.metric("Overweight or Obese", f"{filtered_df['bmi_class'].isin(['Overweight', 'Obese']).mean():.1%}")
        k4.metric("Obese", f"{(filtered_df['bmi_class'] == 'Obese').mean():.1%}")

        # BMI Distribution by Age & Gender
        st.subheader("📉 BMI Distribution")
        fig_dist = px.scatter(
            filtered_df,
            x="age",
            y="bmi",
            color="bmi_class",
            symbol="gender",
            category_orders={"bmi_class": CLASS_ORDER},
            color_discrete_map=CLASS_COLORS,
            labels={"bmi": "BMI", "age": "Age", "bmi_class": "BMI class", "gender": "Gender"},
            title="BMI Distribution by Age & Gender",
        )
        for cutoff in [18.5, 25, 30]:
            fig_dist.add_hline(y=cutoff, line_dash="dot", line_color="gray", annotation_text=f"BMI {cutoff}")
        fig_dist.add_vrect(x0=filtered_df["age"].min() - 1, x1=17.5, fillcolor="gray", opacity=0.1,
                           annotation_text="Under 18: adult cutoffs do not apply", annotation_position="top left")
        show_chart(fig_dist)

        # Percentage Breakdown of Categories
        st.subheader("📊 BMI Category Percentages")
        percent_df = filtered_df["bmi_class"].value_counts(normalize=True).reindex(CLASS_ORDER, fill_value=0).reset_index()
        percent_df.columns = ["bmi_class", "percentage"]
        percent_df["percentage"] = (percent_df["percentage"] * 100).round(1)
        fig_pie = px.pie(percent_df, names="bmi_class", values="percentage", hole=0.45,
                         color="bmi_class", color_discrete_map=CLASS_COLORS,
                         category_orders={"bmi_class": CLASS_ORDER},
                         title="Percentage Breakdown of BMI Categories")
        show_chart(fig_pie)

        # Summary table by age group and gender
        st.subheader("🧾 Summary by Age Group and Gender")
        summary = (filtered_df.groupby(["age_group", "gender"], observed=True)
                   .agg(patients=("bmi", "size"), average_bmi=("bmi", "mean"),
                        overweight_or_obese=("bmi_class", lambda x: x.isin(["Overweight", "Obese"]).mean() * 100),
                        obese=("bmi_class", lambda x: (x == "Obese").mean() * 100))
                   .round(1).reset_index())
        summary.columns = ["Age group", "Gender", "Patients", "Average BMI", "Overweight or obese (%)", "Obese (%)"]
        show_table(summary)

        col1, col2 = st.columns(2)

        # Category share by age group
        with col1:
            by_age = (filtered_df.groupby(["age_group", "bmi_class"], observed=True).size()
                      .reset_index(name="patients"))
            by_age["share"] = by_age["patients"] / by_age.groupby("age_group", observed=True)["patients"].transform("sum") * 100
            fig_age = px.bar(by_age, x="age_group", y="share", color="bmi_class", text=by_age["share"].round(0),
                             category_orders={"bmi_class": CLASS_ORDER}, color_discrete_map=CLASS_COLORS,
                             title="BMI Category by Age Group (%)",
                             labels={"age_group": "Age group", "share": "% of patients", "bmi_class": "BMI class"})
            show_chart(fig_age)

        # Category share by gender
        with col2:
            by_gender = filtered_df.groupby(["gender", "bmi_class"]).size().reset_index(name="patients")
            by_gender["share"] = by_gender["patients"] / by_gender.groupby("gender")["patients"].transform("sum") * 100
            fig_gender = px.bar(by_gender, x="gender", y="share", color="bmi_class", text=by_gender["share"].round(0),
                                category_orders={"bmi_class": CLASS_ORDER}, color_discrete_map=CLASS_COLORS,
                                title="BMI Category by Gender (%)",
                                labels={"gender": "Gender", "share": "% of patients", "bmi_class": "BMI class"})
            show_chart(fig_gender)

        # BMI histogram with cutoffs
        fig_hist = px.histogram(filtered_df, x="bmi", nbins=30, color="bmi_class",
                                category_orders={"bmi_class": CLASS_ORDER}, color_discrete_map=CLASS_COLORS,
                                title="How BMI Values Are Spread", labels={"bmi": "BMI", "bmi_class": "BMI class"})
        for cutoff in [18.5, 25, 30]:
            fig_hist.add_vline(x=cutoff, line_dash="dot", line_color="gray")
        show_chart(fig_hist)

        # Obesity severity among adults
        adults_obese = filtered_df[(~filtered_df["is_child"]) & (filtered_df["bmi"] >= 30)].copy()
        if not adults_obese.empty:
            st.subheader("⚖️ Obesity Severity (adults)")
            adults_obese["severity"] = adults_obese["bmi"].apply(obesity_class)
            sev = adults_obese["severity"].value_counts().reindex(
                ["Class 1 (30 to 34.9)", "Class 2 (35 to 39.9)", "Class 3 (40 or higher)"], fill_value=0
            ).reset_index()
            sev.columns = ["Obesity class", "Patients"]
            fig_sev = px.bar(sev, x="Obesity class", y="Patients", text="Patients",
                             color_discrete_sequence=["#D62728"],
                             title="Adults with Obesity, by Severity Class")
            show_chart(fig_sev)

        # Patient list for follow-up
        st.subheader("📋 Patients to Review")
        st.caption("Adults with a BMI under 18.5 or 35 and over, sorted by how far they are from the healthy range.")
        review = filtered_df[(~filtered_df["is_child"]) & ((filtered_df["bmi"] < 18.5) | (filtered_df["bmi"] >= 35))].copy()
        review["distance_from_healthy"] = np.where(review["bmi"] < 18.5, 18.5 - review["bmi"], review["bmi"] - 24.9).round(1)
        review = review.sort_values("distance_from_healthy", ascending=False)
        show_table(review[["age", "gender", "height_cm", "weight_kg", "bmi", "bmi_class", "distance_from_healthy"]])

        st.download_button(
            "⬇️ Download filtered data (CSV)",
            filtered_df.drop(columns=["is_child"]).to_csv(index=False),
            file_name="filtered_bmi_data.csv",
            mime="text/csv",
        )

# ---------------- Data Quality tab ----------------
with tab_quality:
    st.subheader("🔍 Clinical Data Quality Checks")

    children = df[df["is_child"]]
    young = df[df["age"] < 10]
    tall_young = young[young["height_cm"] >= 160]
    bmi_matches = ((df["bmi_calculated"] - df["bmi"]).abs() <= 0.11).mean()
    label_mismatch = (df["bmi"].apply(adult_class) != df["bmi_class"]).sum()

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("BMI matches height and weight", f"{bmi_matches:.0%}")
    q2.metric("Children given adult categories", len(children))
    q3.metric("Under-10s at least 160 cm tall", f"{len(tall_young)} of {len(young)}")
    q4.metric("Labels that disagree with BMI", label_mismatch)

    st.markdown(
        f"""
- **The BMI math is correct.** Every BMI matches weight divided by height squared.
- **{len(children)} patients are under 18, but all of them were labeled with adult cutoffs.** For children,
  BMI must be read as a percentile for age and sex, so their labels are not clinically valid.
- **{len(tall_young)} of {len(young)} children under 10 are 160 cm or taller** (median height
  {young['height_cm'].median():.0f} cm). Most real children that age are well under 150 cm.
- **Men and women have the same average height** ({df.groupby('gender')['height_cm'].mean().round(1).tolist()[0]} cm),
  and height does not change with age, unlike real populations.
- **{label_mismatch} labels disagree with the BMI shown** because their BMI was rounded onto a cutoff
  (for example, 24.96 shown as 25.0).

Together these suggest the dataset is synthetic. Results should be read as a demonstration of the method,
not as real population health findings.
"""
    )

    fig_height = px.box(df, x="age_group", y="height_cm", color="gender",
                        title="Height by Age Group: children are as tall as adults",
                        labels={"age_group": "Age group", "height_cm": "Height (cm)", "gender": "Gender"})
    show_chart(fig_height)

st.divider()
st.info("BMI classifications are general references and not medical advice. For personal guidance, "
        "talk with a healthcare provider.")
st.success("Use the filters on the left to explore BMI patterns in the sample dataset!")