# 🩺 BMI Health Dashboard with Streamlit"

🚀 **Live App:** [bmi-health-dashboard.streamlit.app](https://bmi-health-dashboard.streamlit.app/)

## 📌 Project Overview

This project is an interactive dashboard built in Python and Streamlit to explore body mass index (BMI) data. It uses 500 patients aged 5 to 79, with age, gender, height, weight, BMI, and BMI category (Underweight, Normal, Overweight, or Obese).

The base dashboard plots BMI by age and gender, shows the share of each BMI category, and includes a simple BMI calculator. I then expanded it to answer the questions a clinician would actually ask about a patient: what this BMI means, what a healthy weight would be, what a realistic first weight-loss goal looks like, and whether BMI alone tells the full story. I added a patient check with a healthy weight range, weight-loss milestones, waist-to-height ratio, obesity severity classes, and a follow-up list. I also audited the data for clinical plausibility and found that **all 90 children in the dataset were labeled with adult BMI cutoffs**, which do not apply to anyone under 18.

## 🎯 Key Features

✅ Patient BMI Check: Calculates BMI, category, and the healthy weight range for the patient's height.<br>
✅ Metric and US Units: Accepts height and weight in cm and kg, or feet, inches, and pounds.<br>
✅ Weight-Loss Milestones: Shows the target weight and new BMI for a 5% loss, a 10% loss, and reaching BMI 24.9.<br>
✅ Waist-to-Height Ratio: Flags central fat at a ratio of 0.5 or higher, which BMI alone can miss.<br>
✅ Obesity Severity: Classifies BMI 30 and higher as Class 1, 2, or 3.<br>
✅ Pediatric Safeguard: Does not apply adult categories to patients under 18 and explains why.<br>
✅ Peer Comparison: Shows where the patient falls among adults of the same sex.<br>
✅ Population Overview: KPI cards, BMI by age and gender with cutoff lines, and a category donut chart.<br>
✅ Summary Table: Average BMI and overweight and obesity rates by age group and gender.<br>
✅ Patients to Review: Lists adults with a BMI under 18.5 or 35 and over for follow-up.<br>
✅ Data Quality Tab: Flags children labeled with adult cutoffs and physically implausible heights.<br>
✅ Interactive Filters and Export: Filters by age, gender, and adults only, with CSV download.

## 🗂️ Repository Files

| File | Description |
|------|-------------|
| `bmi.py` | Streamlit app that builds the interactive dashboard |
| `bmi_health_data.csv` | Raw dataset: 500 rows and 6 columns of patient BMI records |
| `requirements.txt` | Packages used to deploy the app |

## 🧹 Data Preparation

- Loaded the data with `pd.read_csv()` using a relative file path, so the app runs on any computer and on Streamlit Cloud.
- Confirmed the dataset has no missing values and no duplicate rows.
- Renamed columns to lowercase so the code reads consistently.
- Recalculated BMI from height and weight and confirmed it matches the recorded BMI for every patient.
- Grouped age into four bands: under 18, 18 to 39, 40 to 64, and 65 and older.
- Cached the loaded data with `@st.cache_data` so filters respond quickly.
- **Flagged a clinical plausibility issue.** All 90 patients under 18 were labeled with adult BMI cutoffs. For children, BMI is read as a percentile for age and sex on CDC growth charts, so these labels are not clinically valid. In addition, 28 of the 39 children under 10 are 160 cm or taller, men and women have the same average height (166 cm), and height does not change with age. These point to synthetic practice data, so the results should be read as a demonstration of the method, not as real population findings.

## 🛠️ Skills & Tools Applied

- Language and Environment: Python, Visual Studio Code
- Libraries: pandas, NumPy, Plotly Express, Streamlit
- Analysis: BMI calculation, age binning, grouping and aggregation, percentile comparison
- Visualization: Scatter, histogram, stacked bar, donut, box, and BMI scale charts
- App Development: Tabs, sidebar filters, KPI metrics, unit conversion, data caching, CSV download
- Deployment: GitHub and Streamlit Community Cloud
- Clinical Knowledge: Adult BMI categories, obesity classes, pediatric BMI-for-age, waist-to-height ratio, weight-loss targets

## 📈 Business Questions Answered

This project provides insights into:

- What does a patient's BMI mean, and what is a healthy weight for their height?
- What is a realistic first weight-loss goal for a patient with overweight or obesity?
- How common are overweight and obesity across age groups and genders?
- Which patients should be flagged for follow-up?
- Is the data clinically plausible?

## 💡 Key Insights

### Overall BMI Profile (410 adults)

- The average adult BMI was **25.8**, just above the overweight cutoff.
- **51.5% of adults had overweight or obesity**, and **24.1% had obesity**.
- **12.4% of adults were underweight**, a group that is easy to overlook when the focus is on obesity.
- Among the 99 adults with obesity, **63 were Class 1, 30 were Class 2, and 7 were Class 3** (BMI 40 or higher).

### BMI by Age Group and Gender (adults)

| Group | Patients | Average BMI | Overweight or Obese | Obese |
|---|---|---|---|---|
| 18 to 39 | 155 | 24.9 | 43.9% | 18.7% |
| 40 to 64 | 161 | 26.3 | **57.1%** | 26.7% |
| 65 and older | 94 | 26.4 | 54.3% | **28.7%** |
| Female | 196 | 25.9 | 51.0% | 24.0% |
| Male | 214 | 25.7 | 51.9% | 24.3% |

- **Overweight and obesity rose with age**, from 43.9% in adults 18 to 39 to 57.1% in adults 40 to 64.
- **Obesity was highest in adults 65 and older (28.7%)**, compared with 18.7% in the youngest group.
- **Men and women had nearly identical rates**, with less than one percentage point of difference.

### Patients to Review

- **88 adults fell outside the range where follow-up is usually considered:** 51 with a BMI under 18.5 and 37 with a BMI of 35 or higher.
- Adult BMIs ranged from **11.8 to 49.9**. Values this low are rarely seen outside severe illness or eating disorders, which is another sign of synthetic data.

### Clinical Plausibility Check

| Check | Result |
|---|---|
| BMI matches height and weight | Yes, for all 500 patients |
| Children labeled with adult cutoffs | **90 of 90** |
| Children under 10 who are 160 cm or taller | **28 of 39** |
| Average height, men vs. women | 166 cm vs. 166 cm |

- These findings are why the dashboard includes an **"Adults only"** filter, shades the under-18 group on the BMI chart, and refuses to give adult categories to patients under 18 in the Patient Check.

*Note: This dataset appears to be synthetic. The findings demonstrate dashboard and clinical screening methods, not real population health. BMI is a screening tool, not a diagnosis, and this app is not medical advice.*

## 🚀 Learning Outcomes

Building this project strengthened my skills in:

📌 Building an interactive, multi-tab dashboard with Streamlit and Plotly<br>
📌 Turning a BMI value into clinical context: healthy weight range, severity, and realistic goals<br>
📌 Designing inputs for real users, including US and metric units<br>
📌 Building safeguards so the app does not give misleading results for children<br>
📌 Comparing groups with rates instead of raw counts<br>
📌 Checking a dataset for clinical plausibility before trusting the results<br>
📌 Deploying a Python app to the web with GitHub and Streamlit Community Cloud

## 🔮 Next Steps

- Add CDC BMI-for-age percentiles so children can be classified correctly.
- Add waist circumference, blood pressure, and lab values to the dataset for a fuller cardiometabolic risk picture.
- Track patients over time to show BMI change and progress toward weight-loss goals.
- Apply the dashboard to a larger, real-world dataset such as NHANES.

## 🙌 Acknowledgment

This project taught me that a dashboard is only as useful as the questions it answers. A chart of BMI categories is a starting point. Asking what a patient's BMI means for them, what a realistic goal looks like, and whether the data even applies to children turned it into a tool a clinician could act on.

## 👨‍💻 Author

**Omar Shazley**: Data Analyst | Python, Excel, SQL, and healthcare data analytics

💼 [LinkedIn](https://www.linkedin.com/in/omar-shazley-914a16b1/)<br>
💻 [GitHub Portfolio](https://github.com/Bromar95)<br>
📧 Email: [omarshazley@gmail.com](mailto:omarshazley@gmail.com)

✨ If you like this project, don't forget to ⭐ star the repo!
