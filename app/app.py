import streamlit as st
from dashboard import *

# Page configuration
st.set_page_config(
    page_title="Real-time Groundwater Resource Evaluation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar instructions
st.sidebar.title("Groundwater Dashboard")
st.sidebar.markdown("""
Select a village, start and end dates for predictions, and the type of dashboard you want to view.
""")

# The dashboard.py handles:
# 1. Village selection
# 2. Dashboard type (Farmers / Policy Makers / Researchers)
# 3. Past 2, 5, 10 years graphs
# 4. Future predictions graph
# 5. Plotting all graphs using matplotlib
