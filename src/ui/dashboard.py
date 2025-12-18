import streamlit as st
import pandas as pd
import plotly.express as px
from src.log_config import logger  # Integrated Logger

class FluDashboardUI:
    def __init__(self):
       
        logger.info("FluDashboardUI Initialised - User session started.")
        st.set_page_config(
            page_title="National Flu Stress Monitor", 
            layout="wide",
            page_icon="🏥"
        )

    def get_risk_color(self, level):
        colors = {
            "Low": "green",
            "Moderate": "orange",
            "High": "red",
            "Critical": "darkred"
        }
        return colors.get(level, "gray")

    def render(self, df):
        logger.info(f"UI rendering started for {len(df)} records.")
        
        try:
            st.title("🏥 National Flu Hospitalisation Stress Monitor")
            
            # Methodology citation (Excellent for your report)
            st.markdown("""
                ---
                ### **Methodology & Burden Estimation**
                This dashboard utilizes a **1:15 Mortality-to-Admission ratio** derived from the **UKHSA 2024-25 Annual Epidemiological Report**. 
                Because mortality is a lagging indicator, this multiplier estimates total ICU/Hospital burden:
                - **Stress Index** = (Estimated Admissions / ICU Beds) × 100.
                - **Risk Tiers** are mapped to **CDC IRAT** impact categories.
                ---
            """)

            if df.empty:
                st.warning("⚠️ No data available. Please trigger a data fetch in the Admin panel.")
                logger.warning("Render attempted with empty DataFrame.")
                return

            # KPIs
            latest_date = df['date'].max()
            summary_df = df[df['date'] == latest_date]

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Latest Update", latest_date.strftime('%Y-%m-%d'))
            with col2:
                st.metric("Total Deaths", int(summary_df['flu_deaths'].sum()))
            with col3:
                avg_stress = round(summary_df['Stress_Index'].mean(), 1)
                st.metric("Avg. National Stress", f"{avg_stress}%")
            with col4:
                critical_count = len(summary_df[summary_df['Risk_Level'] == 'Critical'])
                st.metric("States in CRITICAL", critical_count)

            st.divider()

            # Visualisations
            tab1, tab2, tab3 = st.tabs(["📈 Trend Analysis", "🗺️ State Risk Table", "📄 Raw Historical Data"])

            with tab1:
                st.subheader("Historical Stress Index Trends")
                fig = px.line(
                    df, 
                    x='date', 
                    y='Stress_Index', 
                    color='state',
                    title="Estimated ICU Occupancy % Over Time",
                    labels={"Stress_Index": "Estimated Occupancy (%)", "date": "Report Date"},
                    markers=True
                )
                # Crisis Threshold Line
                fig.add_hline(y=70, line_dash="dot", line_color="red", 
                             annotation_text="Crisis Threshold (70%)", 
                             annotation_position="top left")
                
                st.plotly_chart(fig, use_container_width=True)


            with tab2:
                st.subheader("Current State Status")
                
                def apply_risk_styles(val):
                    color = self.get_risk_color(val)
                    return f'background-color: {color}; color: white; font-weight: bold;'

                status_cols = ['state', 'flu_deaths', 'ICU_Beds', 'Stress_Index', 'Risk_Level']
                display_df = summary_df[status_cols].sort_values(by='Stress_Index', ascending=False)
                
                st.table(display_df.style.applymap(apply_risk_styles, subset=['Risk_Level']))


            with tab3:
                st.subheader("Full Dataset")
                st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)

            logger.info("UI rendering completed successfully.")


        except Exception as e:
            logger.error(f"UI Rendering Failure: {e}", exc_info=True)
            st.error("An error occurred while displaying the dashboard. Please check the system logs.")