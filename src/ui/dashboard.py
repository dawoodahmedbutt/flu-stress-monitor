import streamlit as st
import pandas as pd
import plotly.express as px
from src.log_config import logger

class FluDashboardUI:
    def __init__(self):
        logger.info("FluDashboardUI Initialized.")
        st.set_page_config(page_title="National Flu Stress Monitor", layout="wide", page_icon="🏥")

    def get_risk_color(self, level):
        colors = {"Low": "green", "Moderate": "orange", "High": "red", "Critical": "darkred"}
        return colors.get(level, "gray")
    

    def render(self, df):
        try:
            #  Data prep
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            if df.empty:
                st.warning("⚠️ No data available. Please go to the Admin Panel and Click 'Trigger Data Sync'.")
                return

            min_avail_date = df['date'].min()
            max_avail_date = df['date'].max()

            # filters
            st.sidebar.header("🔍 Filter View")
            
            all_states = sorted(df['state'].unique())
            default_states = ["California", "Texas", "New York"] if "California" in all_states else all_states[:3]
            selected_states = st.sidebar.multiselect("Select States", options=all_states, default=default_states)

            date_range = st.sidebar.slider(
                "Select Date Range", 
                min_value=min_avail_date.date(), 
                max_value=max_avail_date.date(), 
                value=(min_avail_date.date(), max_avail_date.date())
            )
            
            # Apply Filters
            filtered_df = df[
                (df['state'].isin(selected_states)) & 
                (df['date'].dt.date >= date_range[0]) & 
                (df['date'].dt.date <= date_range[1])
            ]

            st.title("🏥 National Flu Hospitalization Stress Monitor")
            st.markdown("---")

            if filtered_df.empty:
                st.warning("No data matches the selected filters.")
                return

            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            # Reporting Period
            col1.metric("Reporting Period Ends", date_range[1].strftime('%d-%m-%y'))
            
            # Cumulative Deaths 
            total_period_deaths = int(filtered_df['flu_deaths'].sum())
            col2.metric("Cumulative Deaths", f"{total_period_deaths:,}")
            
            #  Peak Stress 
            peak_stress = filtered_df['Stress_Index'].max()
            col3.metric("Peak Stress Index", f"{round(peak_stress, 1)}%" if pd.notna(peak_stress) else "0.0%")
            
            # Critical Instances
            critical_count = len(filtered_df[filtered_df['Risk_Level'] == 'Critical'])
            col4.metric("Weeks at Critical Risk", critical_count)

            st.divider()

            # tabs
            tab1, tab2, tab3 = st.tabs(["📈 Trend Analysis", "🗺️ Risk Table", "⚙️ Admin Info"])

            with tab1:
                st.subheader(f"ICU Stress Trends ({date_range[0].strftime('%d-%m-%y')} to {date_range[1].strftime('%d-%m-%y')})")
                if not filtered_df.empty:
                    chart_data = filtered_df.sort_values(by='date')
                    fig = px.line(chart_data, x='date', y='Stress_Index', color='state', markers=True)
                    fig.add_hline(y=70, line_dash="dot", line_color="red", annotation_text="Crisis Threshold")
                    st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("Detailed Data Log")
                display_df = filtered_df[['state', 'date', 'flu_deaths', 'Stress_Index', 'Risk_Level']].copy()
                display_df['date'] = display_df['date'].dt.strftime('%d-%m-%y')
                display_df = display_df.sort_values(by='date', ascending=False)
                
                def color_risk(val):
                    return f'background-color: {self.get_risk_color(val)}; color: white; font-weight: bold;'
                
                st.dataframe(display_df.style.applymap(color_risk, subset=['Risk_Level']))

            with tab3:
                st.info("Please use the 'Admin Panel' in the sidebar for CRUD operations.")

        except Exception as e:
            logger.error(f"UI Error: {e}")
            st.error(f"An error occurred: {e}")