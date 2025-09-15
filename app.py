import streamlit as st
import pandas as pd
import plotly.express as px


stage_map = {
    'Untouched': 1,
    'Prescheduled': 2,
    'Intro Discussions': 3,
    'Cost Discussions': 4,
    'Pitched': 5,
    'Pitched & Processed': 6,
    'Enrolled': 7,
    'Program Dead': 8
}

try:
    df = pd.read_excel('output/processed_leads.xlsx')
except FileNotFoundError:
    st.error("Run lead_tracker.py first to generate 'output/processed_leads.xlsx'.")
    st.stop()

st.sidebar.title("Filters")
selected_counselor = st.sidebar.multiselect("Select Counselor", df['Counselor'].unique(), default=df['Counselor'].unique())
selected_country = st.sidebar.multiselect("Select Country", df['Country'].unique(), default=df['Country'].unique())

filtered_df = df[df['Counselor'].isin(selected_counselor) & df['Country'].isin(selected_country)]

leads_per_stage = filtered_df.groupby('Sales Stage')['Lead ID'].count().reindex(list(stage_map.keys())).fillna(0).astype(int)
stuck_per_stage = filtered_df[filtered_df['Stuck']].groupby('Sales Stage')['Lead ID'].count().reindex(list(stage_map.keys())).fillna(0).astype(int)
counselor_stats = filtered_df.groupby('Counselor').agg(Total_Leads=('Lead ID', 'count'), Enrolled_Leads=('Sales Stage', lambda x: (x == 'Enrolled').sum()))
counselor_stats['Conversion %'] = (counselor_stats['Enrolled_Leads'] / counselor_stats['Total_Leads'] * 100).round(2)
country_stats = filtered_df.groupby('Country').agg(Total_Leads=('Lead ID', 'count'), Enrolled_Leads=('Sales Stage', lambda x: (x == 'Enrolled').sum()))
country_stats['Conversion %'] = (country_stats['Enrolled_Leads'] / country_stats['Total_Leads'] * 100).round(2)

st.title("Lead Movement Tracker Dashboard")

st.subheader("Total Leads per Stage (Funnel)")
fig_funnel = px.funnel(leads_per_stage.reset_index(), x=leads_per_stage.values, y=leads_per_stage.index)
st.plotly_chart(fig_funnel)

st.subheader("Stuck Leads (>7 days) per Stage")
fig_stuck = px.bar(stuck_per_stage.reset_index(), x='Sales Stage', y='Lead ID', color_discrete_sequence=['red'])
st.plotly_chart(fig_stuck)

st.subheader("Conversion % by Counselor")
fig_conv = px.bar(counselor_stats.reset_index(), x='Counselor', y='Conversion %')
st.plotly_chart(fig_conv)
st.dataframe(counselor_stats)

st.subheader("Conversion % by Country")
fig_country = px.bar(country_stats.reset_index(), x='Country', y='Conversion %')
st.plotly_chart(fig_country)
st.dataframe(country_stats)

st.subheader("Key Insights")
st.write("- Biggest leak: Cost Discussions -> Pitched (14.96% drop-off). Focus on cost/visa objections.")
st.write("- Effective Counselors: Cynthia, Deepak, Grace, Harsh")
st.write("- Ineffective Counselors: Brian")
st.write("- Total Stuck Leads: " + str(filtered_df['Stuck'].sum()))
st.write("- Common Objections: Visa (2 mentions), Placement (2), WhatsApp (2)")

st.subheader("Sample Lead Summaries (First 5)")
st.text("\n\n".join(filtered_df['Summary'].head(5)))
