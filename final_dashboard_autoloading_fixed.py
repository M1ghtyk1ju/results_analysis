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
    st.success(f"✅ Loaded '{sheet_used}' using header row {header_row + 1}")
else:
    st.info("Please upload a file to begin.")
    st.stop()
    st.info("Please upload a file to begin.")
    st.stop()

# --- Load and Preprocess ---
df['Name'] = df['Name'].fillna("Unknown")

subject_columns = ['EL', 'Maths', 'Sci', 'CL', 'ML', 'TL', 'HCL', 'HML', 'HTL',
                   'Fn EL', 'Fn Maths', 'Fn Sci', 'Fn CL', 'Fn ML', 'Fn TL']
for col in subject_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

available_subjects = [s for s in subject_columns if s in df.columns]
classes = df['Class'].dropna().unique().tolist()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
selected_class = st.sidebar.multiselect("Filter by class", classes, default=classes)
selected_subject = st.sidebar.selectbox("Select subject", available_subjects)
chart_type = "Stacked Bar"

df_filtered = df[df['Class'].isin(selected_class)]
sub_df = df_filtered[['Class', selected_subject]].dropna()
sub_df = sub_df[sub_df[selected_subject].notna()]
sub_df['Mark'] = sub_df[selected_subject].astype(float)
sub_df['Category'] = sub_df['Mark'].apply(lambda x: mark_to_al(selected_subject, x))

# --- Define Sort Order by Subject Type ---
if selected_subject.startswith("Fn "):
    sort_order = ['A', 'B', 'C']
elif selected_subject in ['HCL', 'HML', 'HTL']:
    sort_order = ['Distinction', 'Merit', 'Pass', 'Ungraded']
else:
    sort_order = ['AL1', 'AL2', 'AL3', 'AL4', 'AL5', 'AL6', 'AL7', 'AL8']

# --- Summary Insights ---
st.subheader(f"📊 Summary Insights for {selected_subject}")
total_students = len(sub_df)
if total_students > 0:
    quantity_passes = sub_df[sub_df['Mark'] >= 45].shape[0]
    quality_passes = sub_df[sub_df['Mark'] >= 75].shape[0]
    qty_pct = (quantity_passes / total_students) * 100
    qlt_pct = (quality_passes / total_students) * 100

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div style='font-size:48px; color:#2f4b7c'><b>{qty_pct:.1f}%</b></div>", unsafe_allow_html=True)
        st.markdown("**Quantity Pass (≥45 marks)**")
    with col2:
        st.markdown(f"<div style='font-size:48px; color:#003f5c'><b>{qlt_pct:.1f}%</b></div>", unsafe_allow_html=True)
        st.markdown("**Quality Pass (≥75 marks)**")
else:
    st.info("No students found for this subject and filters.")

# --- Class Summary Table ---
st.subheader("📋 Class Summary Table")
temp_df = sub_df.copy()
grouped = temp_df.groupby(['Class', 'Category']).size().unstack(fill_value=0)
for cat in sort_order:
    if cat not in grouped:
        grouped[cat] = 0
grouped = grouped[sort_order]
grouped['Total'] = grouped.sum(axis=1)
for cat in sort_order:
    grouped[f"{cat} (%)"] = (grouped[cat] / grouped['Total'] * 100).round(1)
grouped['Quantity Pass (%)'] = (temp_df[temp_df['Mark'] >= 45].groupby('Class').size() / grouped['Total'] * 100).round(1)
grouped['Quality Pass (%)'] = (temp_df[temp_df['Mark'] >= 75].groupby('Class').size() / grouped['Total'] * 100).round(1)
st.dataframe(grouped, use_container_width=True)

# --- Distribution Chart ---
st.subheader(f"{selected_subject} Distribution")
chart_data = sub_df.groupby(['Category', 'Class']).size().reset_index(name='Count')
x_axis = alt.X('Category:N', sort=sort_order, title="Category")
y_axis = alt.Y('Count:Q', title="No. of Students")
color = alt.Color('Class:N', title='Class')
chart = alt.Chart(chart_data).mark_bar().encode(
    x=x_axis,
    y=y_axis,
    color=color,
    tooltip=['Class', 'Category', 'Count']
).properties(height=400)
st.altair_chart(chart, use_container_width=True)
st.subheader(f"📊 Grade Distribution for {selected_subject}")
pie_data = sub_df.groupby('Category').size().reindex(sort_order).fillna(0).reset_index()
pie_data.columns = ['Category', 'Count']
pie_colors = ['#003f5c', '#2f4b7c', '#416c99', '#5b8bb4', '#77a7cf', '#a0c4e4', '#ff6347', '#d62728'][:len(sort_order)]
fig = px.pie(pie_data, names='Category', values='Count', title=f"{selected_subject} Breakdown")
fig.update_traces(marker=dict(colors=pie_colors), sort=False)
st.plotly_chart(fig, use_container_width=True)

# --- Individual Student Table ---
st.subheader("👤 Individual Student Table")
al_cols = []
for sub in subject_columns:
    if sub in df.columns:
        al_col = f"{sub}_AL"
        df[al_col] = df[sub].apply(lambda x: mark_to_al(sub, x))
        al_cols.append(al_col)

df['Total Marks'] = df[subject_columns].sum(axis=1, skipna=True)

# Recalculate Aggregate AL using only best 4 scores from standard + foundation
def map_to_al_for_agg(subject, mark):
    if pd.isna(mark): return None
    if subject.startswith("Fn "):  # Foundation
        if mark >= 75: return 6
        elif mark >= 30: return 7
        else: return 8
    elif subject in ['HCL', 'HML', 'HTL']:  # Exclude HMT
        return None
    else:  # Standard AL
        if mark >= 90: return 1
        elif mark >= 85: return 2
        elif mark >= 80: return 3
        elif mark >= 75: return 4
        elif mark >= 65: return 5
        elif mark >= 45: return 6
        elif mark >= 20: return 7
        else: return 8

df['Aggregate AL'] = df.apply(lambda row: sorted(
    [map_to_al_for_agg(sub, row[sub]) for sub in subject_columns if sub in df.columns and pd.notna(row[sub]) and sub not in ['HCL','HML','HTL']]
)[:4], axis=1).apply(lambda x: sum(x) if len(x)==4 else None)
df['Weak Subjects'] = df.apply(
    lambda row: sum(1 for s in subject_columns if pd.notna(row.get(f"{s}_AL")) and
                    al_to_numeric(row[f"{s}_AL"]) - np.mean(
                        [al_to_numeric(row[f"{s}_AL"]) for s in subject_columns if pd.notna(row.get(f"{s}_AL"))]
                    ) >= 2), axis=1)

display_cols = ['Name', 'Class', 'Total Marks', 'Aggregate AL', 'Weak Subjects'] + [f"{s}_AL" for s in subject_columns if s in df.columns]

display_cols = ['Name', 'Class', 'Total Marks', 'Aggregate AL', 'Weak Subjects'] + [f"{s}_AL" for s in subject_columns if f"{s}_AL" in df.columns]
sort_option = st.selectbox("Sort students by:", ["Total Marks", "Aggregate AL", "Weak Subjects"])
ascending = st.checkbox("Sort ascending?", value=False)
df = df[df['Class'].isin(selected_class)]

# Auto-hide subjects not taken by any selected students
display_cols = ['Name', 'Class', 'Total Marks', 'Aggregate AL', 'Weak Subjects'] + [f"{s}_AL" for s in subject_columns if f"{s}_AL" in df.columns]
sorted_df = df[display_cols].sort_values(by=sort_option, ascending=ascending)

def highlight_weak_subjects(row):
    al_numeric = [al_to_numeric(row[f"{s}_AL"]) for s in subject_columns if f"{s}_AL" in row and pd.notna(row[f"{s}_AL"])]
    if not al_numeric:
        return [''] * len(subject_columns)
    avg_al = np.mean(al_numeric)
    styles = []
    for s in subject_columns:
        col = f"{s}_AL"
        subject_al = al_to_numeric(row.get(col))
        if subject_al is None:
            styles.append('')
        elif subject_al - avg_al >= 2:
            styles.append('background-color: #ffcccc')
        else:
            styles.append('')
    return styles

st.dataframe(
    sorted_df.style.apply(highlight_weak_subjects, axis=1, subset=[f"{s}_AL" for s in subject_columns if f"{s}_AL" in sorted_df.columns]),
    use_container_width=True
)
