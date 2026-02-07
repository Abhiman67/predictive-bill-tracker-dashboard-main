import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import os

# Import data fetch functions
from data_fetch import fetch_comprehensive_bill_data

# Page configuration
st.set_page_config(
    page_title="Indian Parliament Bill Tracker - Predictive Dashboard",
    page_icon="🇮🇳",
    layout="wide"
)

st.title('🇮🇳 Indian Parliament Bill Tracker & Analytics')
st.markdown("### AI-Driven Insights for Lok Sabha & Rajya Sabha Legislation")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📖 About This System")
    st.markdown("""
    ### Indian Legislative Analytics
    
    **Scope:**
    - Tracks bills in **Lok Sabha** & **Rajya Sabha**
    - Predictions based on historical patterns of Indian legislation
    
    ### Prediction Logic (Prototype)
    
    **🏛️ Government Bills**
    - Historically high passage rate
    - Backed by ruling coalition
    
    **👤 Private Member Bills**
    - Historically very low passage rate
    - Often used to raise awareness rather than enact law
    
    **Understanding Scores:**
    - **Viability**: Likelihood of being taken up for discussion
    - **Passage**: Probability of receiving Presidential Assent
    """)

# Main input
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    bill_input = st.text_input('Enter Bill ID / Number', placeholder='e.g., 123 (Try 127 for Waqf Bill)')
with col2:
    house = st.selectbox('House', ['Lok Sabha', 'Rajya Sabha'])
with col3:
    session = st.text_input('Session/Year', value='2024')

# Display options
with st.expander("📊 Display Options"):
    col1, col2 = st.columns(2)
    with col1:
        show_confidence = st.checkbox("Show confidence intervals", value=True)
    with col2:
        show_timeline = st.checkbox("Show activity timeline", value=True)

if bill_input:
    try:
        # Fetch bill data
        with st.spinner('Fetching bill information from Indian legislative database...'):
            comprehensive_data = fetch_comprehensive_bill_data(
                bill_input, congress=None, bill_type=house
            )
            
            if not comprehensive_data or comprehensive_data['bill_info'].empty:
                st.error("Could not fetch bill data. Please check the bill number (Try ID 123-132).")
                st.stop()
            
            df = comprehensive_data['bill_info']
            actions_df = comprehensive_data['actions']
            metrics = comprehensive_data['metrics']
        
        # Calculate temporal metrics
        days_active = 0
        if not actions_df.empty:
            actions_df['date'] = pd.to_datetime(actions_df['date'], errors='coerce')
            valid_dates = actions_df['date'].dropna()
            if not valid_dates.empty:
                first_action = valid_dates.min()
                days_active = (datetime.now() - first_action).days
        else:
            days_active = 1
        
        # Bill header
        bill_title = df['title'].values[0]
        st.subheader(f"📄 {bill_title}")
        
        # Add bill verification info
        with st.expander("📋 Bill Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Bill ID:** {bill_input}")
                st.write(f"**House:** {df['house'].values[0] if 'house' in df.columns else house}")
                st.markdown(f"**Ministry/Sponsor:** {df['sponsor'].values[0]}")
                st.markdown(f"**Introduction Date:** {df['introduced_date'].values[0]}")
                st.markdown(f"**Status:** {df['status'].values[0]}")
                st.markdown(f"**Year:** {df['year'].values[0]}")
                
                is_amend = "Yes" if df['is_amendment'].values[0] == 1 else "No"
                st.markdown(f"**Is Amendment:** {is_amend}")
            with col2:
                st.write(f"**Type:** {df['type'].values[0]}")
                st.write(f"**Sponsor:** {df['sponsor'].values[0]}")
                st.write(f"**Introduced:** {df['introduced_date'].values[0]}")

        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Days Active", days_active)
        with col2:
            st.metric("Total Actions", metrics.get('total_actions', 0))
        with col3:
            st.metric("Ministry", df['sponsor'].values[0])
        with col4:
            st.metric("Bill Type", df['type'].values[0])
        
        # Activity timeline as table
        if show_timeline and not actions_df.empty:
            st.subheader("📅 Legislative Timeline")
            
            timeline_data = []
            for _, action in actions_df.iterrows():
                # Clean and truncate action text
                action_text = str(action['text']).strip()
                
                timeline_data.append({
                    'Date': action['date'].strftime('%d %B %Y') if pd.notnull(action['date']) else 'N/A',
                    'Action': action_text,
                })
            
            st.dataframe(pd.DataFrame(timeline_data), use_container_width=True, hide_index=True)
            
        st.markdown("---")
        
        # --- HEURISTIC PREDICTION LOGIC FOR INDIA ---
        st.header("🔮 AI Prediction Logic")
        
        # --- ML PREDICTION LOGIC FOR INDIA ---
        st.header("🔮 AI Prediction Logic")
        
        @st.cache_resource
        def load_model():
            try:
                import joblib
                model = joblib.load('data/indian_bill_model.pkl')
                columns = joblib.load('data/model_columns.pkl')
                return model, columns
            except Exception as e:
                st.error(f"Error loading model: {e}")
                return None, None

        model, model_cols = load_model()

        def calculate_indian_probability(bill_row, local_actions):
            """
            ML mode prediction with heuristic fallback
            """
            status = str(bill_row['status'].values[0]).lower()
            
            # 1. Deterministic States
            if 'Assented' in status or 'Passed' in status:
                return 1.0, 0.0, "Bill has likely passed or been enacted based on historical data."
            if 'Lapsed' in status or 'Withdrawn' in status or 'Negatived' in status:
                return 0.0, 0.0, "Bill has failed (Lapsed/Withdrawn)."
            
            # 2. ML Prediction
            if model and model_cols:
                try:
                    # Prepare input vector
                    input_data = {col: 0 for col in model_cols}
                    
                    # Fill features
                    # Numeric
                    input_data['year'] = float(bill_row['year'].values[0])
                    input_data['is_amendment'] = int(bill_row['is_amendment'].values[0])
                    input_data['is_appropriation'] = int(bill_row['is_appropriation'].values[0])
                    input_data['is_finance'] = int(bill_row['is_finance'].values[0])
                    
                    # Ministry
                    b_ministry = str(bill_row['ministry'].values[0]) 
                    min_col = f"ministry_clean_{b_ministry}"
                    if min_col in input_data:
                        input_data[min_col] = 1
                    
                    # Convert to DF
                    input_df = pd.DataFrame([input_data])
                    
                    # Predict
                    prob_array = model.predict_proba(input_df)
                    prob = prob_array[0][1] # Probability of Class 1 (Passed)
                    
                    explanation = f"ML Model Prediction (v2) based on: Year {int(input_data['year'])}, Ministry '{b_ministry}'."
                    if input_data['is_amendment']:
                        explanation += " Identifed as Amendment Bill."
                        
                    return prob, 0.15, explanation
                    
                except Exception as e:
                    st.warning(f"ML Model failed ({e}), falling back to heuristic.")
            
            # 3. Heuristic Fallback
            prob = 0.5
            explanation = "Uncertain status (Heuristic)."
            return prob, 0.3, explanation


        # Calculate prediction
        probability, spread, reason = calculate_indian_probability(df, actions_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Passage Probability")
            
            # Gauge Chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = probability * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Probability"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgray"},
                        {'range': [30, 70], 'color': "gray"},
                        {'range': [70, 100], 'color': "lightblue"}],
                }
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Analysis")
            if probability > 0.7:
                st.success(f"✅ **High Probability**: {reason}")
            elif probability < 0.3:
                st.error(f"❌ **Low Probability**: {reason}")
            else:
                st.warning(f"⚠️ **Moderate Probability**: {reason}")
                
            st.info("ℹ️ **Confidence Interval**: Predictions are based on bill type and current legislative stage.")

        # Recommendations
        st.markdown("---")
        st.subheader("💡 Strategic Recommendations")
        
        if probability < 0.5:
            if 'government' in str(df['type'].values[0]).lower():
                st.markdown("- **Floor Management**: Ensure coalition MPs are present for voting.")
                st.markdown("- **Opposition Consensus**: Engage with opposition leaders to reduce disruption.")
            else:
                st.markdown("- **Ministry Support**: Try to get the relevant Ministry to adopt the bill's objectives.")
                st.markdown("- **Public Awareness**: Use the bill to generate public debate on the issue.")
        else:
            st.markdown("- **Press ahead**: Schedule for passing in the remaining House immediately.")
            st.markdown("- **Gazette Notification**: Prepare for immediate notification after Assent.")

    except Exception as e:
        st.error(f"❗ An error occurred: {str(e)}")
        with st.expander("🐛 Debug Information"):
            import traceback
            st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.caption("Indian Parliament Bill Tracker | Adapted for Lok Sabha & Rajya Sabha | Prototype Version")