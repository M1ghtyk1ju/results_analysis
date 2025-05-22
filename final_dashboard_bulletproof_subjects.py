import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px

def load_and_clean_excel(file):
    import pandas as pd
    xls = pd.ExcelFile(file)
    for sheet in xls.sheet_names:
        for header_row in range(10):
            df_try = xls.parse(sheet_name=sheet, header=header_row)
            colnames = [str(c).strip().lower() for c in df_try.columns]
            if 'name' in colnames and 'class' in colnames:
                df = df_try.copy()
                df.columns = [str(c).strip() for c in df.columns]
                return df, sheet, header_row
    raise ValueError("No valid header with 'Name' and 'Class' found.")


# --- Helper Functions ---
def mark_to_al(subject, mark):
    if pd.isna(mark): return None
    if subject.startswith("Fn "):  # Foundation
        if mark >= 75: return 'A'
        elif mark >= 30: return 'B'
        else: return 'C'
    elif subject in ['HCL', 'HML', 'HTL']:  # Higher MT
        if mark >= 80: return 'Distinction'
        elif mark >= 65: return 'Merit'
        elif mark >= 50: return 'Pass'
        else: return 'Ungraded'
    else:  # Standard
        if mark >= 90: return 'AL1'
        elif mark >= 85: return 'AL2'
        elif mark >= 80: return 'AL3'
        elif mark >= 75: return 'AL4'
        elif mark >= 65: return 'AL5'
        elif mark >= 45: return 'AL6'
        elif mark >= 20: return 'AL7'
        else: return 'AL8'

def al_to_numeric(al):
    if al in ['A', 'Distinction']: return 1
    elif al in ['B', 'Merit']: return 2
    elif al in ['C', 'Pass']: return 3
    elif al in ['Ungraded']: return 4
    try:
        return int(al.replace("AL", ""))
    except:
        return None

# --- App Setup ---
st.set_page_config(page_title="Student Dashboard", layout="wide")
st.title("🎓 Student Performance Dashboard")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df, sheet_used, header_row = load_and_clean_excel(uploaded_file)

# Define and filter subject columns
subject_columns = [
    'EL', 'Maths', 'Sci', 'CL', 'ML', 'TL',
    'HCL', 'HML', 'HTL',
    'Fn EL', 'Fn Maths', 'Fn Sci', 'Fn CL', 'Fn ML', 'Fn TL'
]
subject_columns = [s for s in subject_columns if s in df.columns]
    st.success(f"✅ Loaded '{sheet_used}' using header row {header_row + 1}")
else:
    st.info("Please upload a file to begin.")
    st.stop()

if uploaded_file:

# Define and filter subject columns based on available headers


# --- Sidebar Filters ---
chart_type = "Stacked Bar"


# --- Define Sort Order by Subject Type ---
if selected_subject.startswith("Fn "):
    sort_order = ['A', 'B', 'C']
elif selected_subject in ['HCL', 'HML', 'HTL']:
    sort_order = ['Distinction', 'Merit', 'Pass', 'Ungraded']
    sort_order = ['AL1', 'AL2', 'AL3', 'AL4', 'AL5', 'AL6', 'AL7', 'AL8']

# --- Summary Insights ---
if total_students > 0:
    qty_pct = (quantity_passes / total_students) * 100
    qlt_pct = (quality_passes / total_students) * 100

    with col1:
    with col2:

# --- Class Summary Table ---
for cat in sort_order:
    if cat not in grouped:
        grouped[cat] = 0
grouped = grouped[sort_order]
grouped['Total'] = grouped.sum(axis=1)
for cat in sort_order:
    grouped[f"{cat} (%)"] = (grouped[cat] / grouped['Total'] * 100).round(1)

# --- Distribution Chart ---
x_axis = alt.X('Category:N', sort=sort_order, title="Category")
y_axis = alt.Y('Count:Q', title="No. of Students")
color = alt.Color('Class:N', title='Class')
chart = alt.Chart(chart_data).mark_bar().encode(
    x=x_axis,
    y=y_axis,
    color=color,
    tooltip=['Class', 'Category', 'Count']
).properties(height=400)
pie_data.columns = ['Category', 'Count']
pie_colors = ['#003f5c', '#2f4b7c', '#416c99', '#5b8bb4', '#77a7cf', '#a0c4e4', '#ff6347', '#d62728'][:len(sort_order)]
fig = px.pie(pie_data, names='Category', values='Count', title=f"{selected_subject} Breakdown")
fig.update_traces(marker=dict(colors=pie_colors), sort=False)

# --- Individual Student Table ---
al_cols = []
        al_col = f"{sub}_AL"
        al_cols.append(al_col)


# Recalculate Aggregate AL using only best 4 scores from standard + foundation
def map_to_al_for_agg(subject, mark):
    if pd.isna(mark): return None
    if subject.startswith("Fn "):  # Foundation
        if mark >= 75: return 6
        elif mark >= 30: return 7
    elif subject in ['HCL', 'HML', 'HTL']:  # Exclude HMT
        return None
        if mark >= 90: return 1
        elif mark >= 85: return 2
        elif mark >= 80: return 3
        elif mark >= 75: return 4
        elif mark >= 65: return 5
        elif mark >= 45: return 6
        elif mark >= 20: return 7

                    al_to_numeric(row[f"{s}_AL"]) - np.mean(
                    ) >= 2), axis=1)



# Auto-hide subjects not taken by any selected students

def highlight_weak_subjects(row):
    if not al_numeric:
    avg_al = np.mean(al_numeric)
    styles = []
        col = f"{s}_AL"
        subject_al = al_to_numeric(row.get(col))
        if subject_al is None:
            styles.append('')
        elif subject_al - avg_al >= 2:
            styles.append('background-color: #ffcccc')
            styles.append('')
    return styles

    use_container_width=True
)
