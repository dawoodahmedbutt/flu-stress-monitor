import streamlit as st
from src.log_config import logger

def render_dashboard(service):
    """
    Render the main dashboard view: metrics, charts, and data table.
    """
    st.header("📊 Public Health Overview")
    
    # load data
    with st.spinner('Fetching latest analytics...'):
        df = service.get_dashboard_data()

    if df.empty:
        st.error("No data available.")
        return

    # filters
    st.sidebar.header("Filter Data")
    all_states = sorted(df['state'].unique())
    selected_states = st.sidebar.multiselect("Select States", all_states, default=all_states[:5])

    if selected_states:
        df_view = df[df['state'].isin(selected_states)]
    else:
        df_view = df

    # metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("States Monitored", len(df_view))
    col2.metric("Total Flu Deaths", f"{df_view['flu_deaths'].sum():,}")
    col3.metric("Avg Stress Index", f"{df_view['Stress_Index'].mean():.2f}")

    st.divider()

    # vis
    tab1, tab2 = st.tabs(["📈 Stress Index Chart", "📄 Raw Data"])
    
    with tab1:
        st.subheader("Hospital Stress Index by State")
        st.bar_chart(df_view.set_index('state')['Stress_Index'], color="#FF4B4B")

    with tab2:
        st.dataframe(df_view.style.format({"Stress_Index": "{:.2f}", "date": "{:%Y-%m-%d}"}))

    # 5. export functions
    csv = df_view.to_csv(index=False).encode('utf-8')
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='flu_report.csv',
        mime='text/csv',
        on_click=lambda: logger.info("User exported dashboard data")
    )