import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple
import hashlib

# Page configuration
st.set_page_config(
    page_title="MA Plan Design Simulator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional UI with better visibility
st.markdown("""
<style>
    /* Main app background - subtle gradient */
    .stApp {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Compact header */
    .main-header {
        background: linear-gradient(90deg, #2c5282 0%, #2d3748 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .main-header h1 {
        font-size: 1.5rem;
        margin: 0;
        color: white;
    }
    
    .main-header p {
        margin: 0;
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
    }
    
    /* KPI Cards with better contrast */
    .kpi-card {
        background: white;
        padding: 1.25rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        margin-bottom: 1rem;
        border-left: 4px solid #4299e1;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.25rem;
    }
    
    .kpi-label {
        font-size: 0.875rem;
        color: #4a5568;
        font-weight: 500;
    }
    
    /* Scenario cards */
    .scenario-card {
        background: white;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    .scenario-card h4 {
        color: #2d3748;
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    
    .scenario-card p {
        color: #4a5568;
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    
    /* Sidebar styling */
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    
    div[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    div[data-testid="stSidebar"] .stSelectbox label {
        color: white !important;
    }
    
    div[data-testid="stSidebar"] h2, 
    div[data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #f7fafc;
        padding: 4px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: #4a5568;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #2b6cb0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4299e1;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #3182ce;
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background-color: #2b6cb0;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #2c5282;
    }
    
    /* Data editor improvements */
    .stDataFrame {
        background: white;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Info boxes */
    .stAlert {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
    }
    
    /* Guidelines box */
    .guidelines-box {
        background: #f7fafc;
        border: 1px solid #cbd5e0;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .guidelines-box h4 {
        color: #2d3748;
        margin: 0 0 0.5rem 0;
        font-size: 0.95rem;
        font-weight: 600;
    }
    
    .guidelines-box ul {
        margin: 0;
        padding-left: 1.5rem;
        color: #4a5568;
        font-size: 0.875rem;
    }
    
    .guidelines-box li {
        margin: 0.25rem 0;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #718096;
        padding: 1rem;
        margin-top: 2rem;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = []
if 'current_scenario' not in st.session_state:
    st.session_state.current_scenario = None
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False

# Data Generation Functions
@st.cache_data
def generate_plan_master():
    """Generate realistic MA plan master data"""
    plans = []
    contracts = ['H0001', 'H5521', 'H6743', 'H3239', 'H4922']
    plan_types = ['HMO', 'Local PPO', 'Regional PPO', 'HMO-POS', 'MSA']
    regions = ['Northeast', 'Southeast', 'Midwest', 'Southwest', 'West']
    counties = ['Los Angeles', 'Cook', 'Harris', 'Maricopa', 'San Diego', 'Orange', 'Miami-Dade', 'Dallas']

    for i in range(15):
        contract = np.random.choice(contracts)
        plans.append({
            'plan_id': f'{contract}_{str(i+1).zfill(3)}_0',
            'scenario_id': 'baseline',
            'plan_name': f'MediAdvantage {np.random.choice(["Plus", "Select", "Choice", "Premier", "Essential"])} {np.random.choice(["HMO", "PPO", ""])}',
            'contract_id': contract,
            'plan_type': np.random.choice(plan_types),
            'ma_pd': np.random.choice([True, False], p=[0.8, 0.2]),
            'ma_region': np.random.choice(regions),
            'service_area_counties': ';'.join(np.random.choice(counties, size=np.random.randint(1, 4), replace=False)),
            'effective_year': 2025,
            'status': np.random.choice(['Draft', 'Published'], p=[0.3, 0.7])
        })

    return pd.DataFrame(plans)

@st.cache_data
def generate_benefit_definitions():
    """Generate benefit definitions"""
    benefits = [
        {'benefit_id': 'inpatient_hospital', 'benefit_name': 'Inpatient Hospital', 'category': 'Hospital', 'sub_category': 'Standard', 'unit_type': 'days', 'default_limit': 90},
        {'benefit_id': 'inpatient_psych', 'benefit_name': 'Inpatient Psychiatric', 'category': 'Hospital', 'sub_category': 'Mental Health', 'unit_type': 'days', 'default_limit': 190},
        {'benefit_id': 'skilled_nursing', 'benefit_name': 'Skilled Nursing Facility', 'category': 'Post-Acute', 'sub_category': 'Standard', 'unit_type': 'days', 'default_limit': 100},
        {'benefit_id': 'home_health', 'benefit_name': 'Home Health', 'category': 'Post-Acute', 'sub_category': 'Standard', 'unit_type': 'visits', 'default_limit': None},
        {'benefit_id': 'pcp_visit', 'benefit_name': 'Primary Care Visit', 'category': 'Physician', 'sub_category': 'Routine', 'unit_type': 'visits', 'default_limit': None},
        {'benefit_id': 'specialist_visit', 'benefit_name': 'Specialist Visit', 'category': 'Physician', 'sub_category': 'Specialty', 'unit_type': 'visits', 'default_limit': None},
        {'benefit_id': 'urgent_care', 'benefit_name': 'Urgent Care', 'category': 'Emergency', 'sub_category': 'Non-Emergency', 'unit_type': 'visits', 'default_limit': None},
        {'benefit_id': 'emergency_room', 'benefit_name': 'Emergency Room', 'category': 'Emergency', 'sub_category': 'Emergency', 'unit_type': 'visits', 'default_limit': None},
        {'benefit_id': 'ambulance', 'benefit_name': 'Ambulance', 'category': 'Emergency', 'sub_category': 'Transport', 'unit_type': 'trips', 'default_limit': None},
        {'benefit_id': 'dme', 'benefit_name': 'Durable Medical Equipment', 'category': 'Supplies', 'sub_category': 'Equipment', 'unit_type': 'items', 'default_limit': None},
        {'benefit_id': 'lab_tests', 'benefit_name': 'Laboratory Tests', 'category': 'Diagnostic', 'sub_category': 'Lab', 'unit_type': 'tests', 'default_limit': None},
        {'benefit_id': 'xray', 'benefit_name': 'X-rays', 'category': 'Diagnostic', 'sub_category': 'Imaging', 'unit_type': 'procedures', 'default_limit': None},
        {'benefit_id': 'physical_therapy', 'benefit_name': 'Physical Therapy', 'category': 'Therapy', 'sub_category': 'Rehabilitation', 'unit_type': 'visits', 'default_limit': None},
        {'benefit_id': 'mental_health', 'benefit_name': 'Mental Health Visits', 'category': 'Mental Health', 'sub_category': 'Outpatient', 'unit_type': 'visits', 'default_limit': None},
        {'benefit_id': 'dental_basic', 'benefit_name': 'Dental - Basic', 'category': 'Supplemental', 'sub_category': 'Preventive', 'unit_type': 'services', 'default_limit': None},
        {'benefit_id': 'vision', 'benefit_name': 'Vision - Routine', 'category': 'Supplemental', 'sub_category': 'Exam & Hardware', 'unit_type': 'services', 'default_limit': None},
        {'benefit_id': 'hearing', 'benefit_name': 'Hearing Aids', 'category': 'Supplemental', 'sub_category': 'Devices', 'unit_type': 'aids', 'default_limit': None},
        {'benefit_id': 'otc_benefit', 'benefit_name': 'OTC Allowance', 'category': 'Supplemental', 'sub_category': 'Allowance', 'unit_type': 'quarterly', 'default_limit': None},
        {'benefit_id': 'gym_membership', 'benefit_name': 'Fitness Benefit', 'category': 'Supplemental', 'sub_category': 'Wellness', 'unit_type': 'monthly', 'default_limit': None},
    ]
    return pd.DataFrame(benefits)

@st.cache_data
def generate_plan_cost_sharing(plan_id):
    """Generate cost sharing data for a specific plan"""
    benefits_df = generate_benefit_definitions()
    cost_sharing = []

    for _, benefit in benefits_df.iterrows():
        # Generate realistic copays based on benefit type
        if benefit['category'] == 'Hospital':
            copay = np.random.choice([275, 295, 315, 335, 350])
            coinsurance = 0
        elif benefit['category'] == 'Physician':
            if 'Primary' in benefit['benefit_name']:
                copay = np.random.choice([0, 5, 10, 15])
            else:
                copay = np.random.choice([30, 35, 40, 45, 50])
            coinsurance = 0
        elif benefit['category'] == 'Emergency':
            copay = np.random.choice([90, 110, 120, 135])
            coinsurance = 0
        elif benefit['category'] == 'Diagnostic':
            copay = np.random.choice([0, 20, 35, 50])
            coinsurance = np.random.choice([0, 10, 20])
        elif benefit['category'] == 'Supplemental':
            copay = 0
            coinsurance = np.random.choice([0, 20, 30])
        else:
            copay = np.random.choice([20, 30, 40])
            coinsurance = np.random.choice([0, 10, 20])

        # Generate utilization and costs
        util_rate = np.random.uniform(0.5, 15) if benefit['unit_type'] == 'visits' else np.random.uniform(0.1, 5)
        cost_per_unit = {
            'days': np.random.uniform(1800, 2500),
            'visits': np.random.uniform(75, 250),
            'procedures': np.random.uniform(500, 2000),
            'tests': np.random.uniform(50, 200),
            'items': np.random.uniform(100, 500),
            'trips': np.random.uniform(150, 300),
            'services': np.random.uniform(100, 300),
            'aids': 1500,
            'quarterly': 50,
            'monthly': 25
        }.get(benefit['unit_type'], 100)

        cost_sharing.append({
            'plan_id': plan_id,
            'benefit_id': benefit['benefit_id'],
            'benefit_name': benefit['benefit_name'],
            'category': benefit['category'],
            'sub_category': benefit['sub_category'],
            'unit_type': benefit['unit_type'],
            'limits_visits': benefit['default_limit'],
            'current_utilization_pct': util_rate,
            'projected_utilization_pct': util_rate,
            'cost_per_unit': cost_per_unit,
            'copay': copay,
            'coinsurance_pct': coinsurance,
        })

    return pd.DataFrame(cost_sharing)

@st.cache_data
def generate_enrollment_data(plan_id):
    """Generate enrollment data"""
    months = pd.date_range(start='2024-01-01', end='2025-12-01', freq='MS')
    enrollment = []
    base_enrollment = np.random.randint(2000, 10000)

    for month in months:
        # Add seasonal variation and trend
        seasonal = np.sin((month.month - 1) * 2 * np.pi / 12) * base_enrollment * 0.1
        trend = (month.year - 2024) * 12 + month.month
        growth = trend * np.random.uniform(10, 50)

        total = int(base_enrollment + seasonal + growth + np.random.normal(0, 100))

        enrollment.append({
            'plan_id': plan_id,
            'month': month.strftime('%Y-%m'),
            'enrollees_total': max(total, 0),
            'enrollees_65to69': int(total * 0.35),
            'enrollees_70to74': int(total * 0.30),
            'enrollees_75to79': int(total * 0.20),
            'enrollees_80plus': int(total * 0.15),
        })

    return pd.DataFrame(enrollment)

@st.cache_data
def generate_star_ratings(plan_id):
    """Generate star ratings"""
    return pd.DataFrame([{
        'plan_id': plan_id,
        'year': 2025,
        'overall_star_rating': round(np.random.uniform(3.0, 5.0), 1),
        'part_c_score': round(np.random.uniform(3.0, 5.0), 1),
        'part_d_score': round(np.random.uniform(3.0, 5.0), 1),
        'member_experience': round(np.random.uniform(3.0, 5.0), 1),
        'member_complaints': round(np.random.uniform(3.0, 5.0), 1),
        'health_plan_quality': round(np.random.uniform(3.0, 5.0), 1),
    }])

class MAPlanSimulator:
    """Medicare Advantage Plan Simulator Engine"""

    def __init__(self, plan_data, cost_sharing_data):
        self.plan_data = plan_data
        self.cost_sharing_data = cost_sharing_data
        self.risk_score = 1.05  # Average MA risk score

    def calculate_pmpm(self, cost_sharing_df):
        """Calculate PMPM costs"""
        pmpm_results = []

        for _, benefit in cost_sharing_df.iterrows():
            # Annual utilization per member
            annual_util = benefit['projected_utilization_pct'] / 100 * 12

            # Gross cost
            gross_cost = annual_util * benefit['cost_per_unit']

            # Member cost share
            member_copay = annual_util * benefit['copay']
            member_coinsurance = gross_cost * benefit['coinsurance_pct'] / 100
            member_cost_share = member_copay + member_coinsurance

            # Plan liability
            plan_liability = gross_cost - member_cost_share

            # PMPM
            pmpm = plan_liability / 12

            pmpm_results.append({
                'benefit_id': benefit['benefit_id'],
                'benefit_name': benefit['benefit_name'],
                'category': benefit['category'],
                'gross_pmpm': gross_cost / 12,
                'member_pmpm': member_cost_share / 12,
                'plan_pmpm': pmpm
            })

        pmpm_df = pd.DataFrame(pmpm_results)

        # Separate Medicare vs Supplemental
        medicare_benefits = pmpm_df[~pmpm_df['category'].isin(['Supplemental'])]
        supplemental_benefits = pmpm_df[pmpm_df['category'].isin(['Supplemental'])]

        return {
            'total_medicare_pmpm': medicare_benefits['plan_pmpm'].sum(),
            'total_supplemental_pmpm': supplemental_benefits['plan_pmpm'].sum(),
            'total_pmpm': pmpm_df['plan_pmpm'].sum(),
            'risk_adjusted_pmpm': pmpm_df['plan_pmpm'].sum() * self.risk_score,
            'details': pmpm_df
        }

    def calculate_enrollment_lift(self, baseline_pmpm, new_pmpm, star_change=0):
        """Calculate enrollment lift based on benefit changes"""
        # Simple elasticity model
        pmpm_reduction = baseline_pmpm - new_pmpm
        pmpm_elasticity = 0.02  # 2% lift per $10 PMPM reduction
        star_elasticity = 0.05  # 5% lift per 0.5 star increase

        pmpm_lift = (pmpm_reduction / 10) * pmpm_elasticity
        star_lift = (star_change / 0.5) * star_elasticity

        total_lift = pmpm_lift + star_lift
        return max(min(total_lift, 0.20), -0.20)  # Cap at ±20%

    def run_monte_carlo(self, cost_sharing_df, n_simulations=100):
        """Run Monte Carlo simulation"""
        results = []

        for _ in range(n_simulations):
            # Vary utilization ±20%
            sim_df = cost_sharing_df.copy()
            sim_df['projected_utilization_pct'] *= np.random.uniform(0.8, 1.2, len(sim_df))

            # Vary costs ±15%
            sim_df['cost_per_unit'] *= np.random.uniform(0.85, 1.15, len(sim_df))

            pmpm_result = self.calculate_pmpm(sim_df)
            results.append(pmpm_result['total_pmpm'])

        return {
            'mean': np.mean(results),
            'std': np.std(results),
            'ci_lower': np.percentile(results, 2.5),
            'ci_upper': np.percentile(results, 97.5),
            'results': results
        }

def create_waterfall_chart(baseline_pmpm, scenario_pmpm, details):
    """Create waterfall chart for PMPM changes"""
    categories = details.groupby('category')['plan_pmpm'].sum().to_dict()

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative"] * len(categories) + ["total"],
        x=list(categories.keys()) + ["Total"],
        text=[f"${v:.2f}" for v in categories.values()] + [f"${scenario_pmpm:.2f}"],
        y=list(categories.values()) + [scenario_pmpm],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#4299e1"}},
        decreasing={"marker": {"color": "#fc8181"}},
        totals={"marker": {"color": "#48bb78"}}
    ))

    fig.update_layout(
        title="PMPM Cost Breakdown by Category",
        yaxis_title="PMPM ($)",
        showlegend=False,
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2d3748')
    )

    return fig

def create_enrollment_trend_chart(enrollment_df):
    """Create enrollment trend chart"""
    fig = px.area(
        enrollment_df,
        x='month',
        y='enrollees_total',
        title='Enrollment Trend',
        labels={'enrollees_total': 'Total Enrollees', 'month': 'Month'},
        color_discrete_sequence=['#4299e1']
    )

    fig.update_layout(
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2d3748')
    )
    return fig

def create_comparison_chart(scenarios):
    """Create scenario comparison chart"""
    if not scenarios:
        return None

    comparison_data = []
    for scenario in scenarios:
        comparison_data.append({
            'Scenario': scenario['name'],
            'Medicare PMPM': scenario['medicare_pmpm'],
            'Supplemental PMPM': scenario['supplemental_pmpm'],
            'Total PMPM': scenario['total_pmpm']
        })

    df = pd.DataFrame(comparison_data)

    fig = go.Figure()

    for col in ['Medicare PMPM', 'Supplemental PMPM']:
        fig.add_trace(go.Bar(
            x=df['Scenario'],
            y=df[col],
            name=col,
            marker_color='#4299e1' if 'Medicare' in col else '#805ad5'
        ))

    fig.update_layout(
        title='Scenario Comparison',
        yaxis_title='PMPM ($)',
        barmode='stack',
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2d3748')
    )

    return fig

# Main App
def main():
    # Compact Header
    st.markdown("""
    <div class="main-header">
        <div>
            <h1>🏥 MA Plan Design Simulator</h1>
        </div>
        <div>
            <p>Design, simulate, and optimize Medicare Advantage plans</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Load data
    plans_df = generate_plan_master()

    # Sidebar
    with st.sidebar:
        st.markdown("## 📋 Plan Selection")
        selected_plan_id = st.selectbox(
            "Select Plan",
            options=plans_df['plan_id'].tolist(),
            format_func=lambda x: f"{x} - {plans_df[plans_df['plan_id']==x]['plan_name'].iloc[0]}"
        )

        selected_plan = plans_df[plans_df['plan_id'] == selected_plan_id].iloc[0]

        st.markdown("### Plan Details")
        st.info(f"""
        **Type:** {selected_plan['plan_type']}  
        **MA-PD:** {'Yes' if selected_plan['ma_pd'] else 'No'}  
        **Region:** {selected_plan['ma_region']}  
        **Status:** {selected_plan['status']}
        """)

        # Star Ratings
        star_ratings = generate_star_ratings(selected_plan_id)
        st.markdown("### ⭐ Star Ratings")
        st.metric("Overall Rating", f"{star_ratings.iloc[0]['overall_star_rating']} ★")

        st.markdown("---")

        # Simulation Controls
        st.markdown("## 🎯 Simulation Settings")

        risk_score = st.slider("Risk Score Adjustment", 0.8, 1.3, 1.05, 0.05)

        run_monte_carlo = st.checkbox("Run Monte Carlo Simulation")
        if run_monte_carlo:
            n_simulations = st.number_input("Number of Simulations", 50, 1000, 100, 50)

    # Main Content Area
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Benefit Design", "📈 Analysis", "🔄 Scenarios", "📑 Reports"])

    with tab1:
        # Guidelines Section
        st.markdown("""
        <div class="guidelines-box">
            <h4>📌 Quick Actions & Guidelines</h4>
            <ul>
                <li><strong>Edit Benefits:</strong> Click on any cell in the table below to modify copays, coinsurance, or utilization rates</li>
                <li><strong>Adjust Limits:</strong> Set visit/day limits for benefits to control utilization</li>
                <li><strong>Add/Remove Benefits:</strong> Use the category filter to focus on specific benefit types</li>
                <li><strong>Numbers Format:</strong> Enter copays as whole numbers (e.g., 45 for $45), percentages without % sign</li>
                <li><strong>Save Your Work:</strong> Use "Save Scenario" after calculating PMPM to preserve your design</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Benefit Cost Sharing Configuration")

        # Load cost sharing data
        if 'cost_sharing_df' not in st.session_state:
            st.session_state.cost_sharing_df = generate_plan_cost_sharing(selected_plan_id)

        cost_sharing_df = st.session_state.cost_sharing_df

        # Category filter for easier management
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_categories = st.multiselect(
                "Filter by Category",
                options=cost_sharing_df['category'].unique(),
                default=cost_sharing_df['category'].unique()
            )
        
        with col2:
            show_all = st.button("Show All Categories", use_container_width=True)
            if show_all:
                selected_categories = cost_sharing_df['category'].unique()

        # Filter dataframe
        filtered_df = cost_sharing_df[cost_sharing_df['category'].isin(selected_categories)]

        # Create editable dataframe with compact columns
        edited_df = st.data_editor(
            filtered_df,
            column_config={
                "benefit_name": st.column_config.TextColumn("Benefit", disabled=True, width="medium"),
                "category": st.column_config.TextColumn("Category", disabled=True, width="small"),
                "limits_visits": st.column_config.NumberColumn("Limit", min_value=0, width="small"),
                "projected_utilization_pct": st.column_config.NumberColumn("Util %", min_value=0, max_value=100, width="small"),
                "cost_per_unit": st.column_config.NumberColumn("Cost/Unit", min_value=0, format="$%.0f", width="small"),
                "copay": st.column_config.NumberColumn("Copay", min_value=0, format="$%.0f", width="small"),
                "coinsurance_pct": st.column_config.NumberColumn("Coins %", min_value=0, max_value=100, width="small"),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key="benefit_editor",
            height=400
        )

        # Merge edited values back to full dataframe
        for idx, row in edited_df.iterrows():
            mask = cost_sharing_df['benefit_id'] == row['benefit_id']
            for col in cost_sharing_df.columns:
                if col in row:
                    cost_sharing_df.loc[mask, col] = row[col]

        # Update session state
        st.session_state.cost_sharing_df = cost_sharing_df

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("💰 Calculate PMPM", type="primary", use_container_width=True):
                simulator = MAPlanSimulator(selected_plan, cost_sharing_df)
                simulator.risk_score = risk_score
                pmpm_results = simulator.calculate_pmpm(cost_sharing_df)
                st.session_state.pmpm_results = pmpm_results
                st.success("PMPM calculation completed!")

        with col2:
            if st.button("📊 Get Enrollment Lift", use_container_width=True):
                if 'pmpm_results' in st.session_state:
                    baseline_pmpm = 150  # Baseline assumption
                    new_pmpm = st.session_state.pmpm_results['total_pmpm']
                    simulator = MAPlanSimulator(selected_plan, cost_sharing_df)
                    lift = simulator.calculate_enrollment_lift(baseline_pmpm, new_pmpm)
                    st.session_state.enrollment_lift = lift
                    st.success(f"Enrollment lift: {lift:.2%}")
                else:
                    st.warning("Please calculate PMPM first")

        with col3:
            if st.button("💾 Save Scenario", use_container_width=True):
                if 'pmpm_results' in st.session_state:
                    scenario_name = st.text_input("Scenario Name", f"Scenario_{len(st.session_state.scenarios)+1}")
                    if scenario_name:
                        scenario = {
                            'name': scenario_name,
                            'plan_id': selected_plan_id,
                            'timestamp': datetime.now(),
                            'cost_sharing': cost_sharing_df.to_dict(),
                            'medicare_pmpm': st.session_state.pmpm_results['total_medicare_pmpm'],
                            'supplemental_pmpm': st.session_state.pmpm_results['total_supplemental_pmpm'],
                            'total_pmpm': st.session_state.pmpm_results['total_pmpm'],
                            'enrollment_lift': st.session_state.get('enrollment_lift', 0)
                        }
                        st.session_state.scenarios.append(scenario)
                        st.success(f"Scenario '{scenario_name}' saved!")
                else:
                    st.warning("Please calculate PMPM first")

        with col4:
            if st.button("🔄 Reset to Baseline", use_container_width=True):
                st.session_state.cost_sharing_df = generate_plan_cost_sharing(selected_plan_id)
                st.rerun()

    with tab2:
        st.markdown("### Plan Performance Analysis")

        # KPI Cards
        if 'pmpm_results' in st.session_state:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("""
                <div class="kpi-card">
                    <div class="kpi-value">${:.2f}</div>
                    <div class="kpi-label">Medicare PMPM</div>
                </div>
                """.format(st.session_state.pmpm_results['total_medicare_pmpm']), unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="kpi-card">
                    <div class="kpi-value">${:.2f}</div>
                    <div class="kpi-label">Supplemental PMPM</div>
                </div>
                """.format(st.session_state.pmpm_results['total_supplemental_pmpm']), unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div class="kpi-card">
                    <div class="kpi-value">${:.2f}</div>
                    <div class="kpi-label">Total PMPM</div>
                </div>
                """.format(st.session_state.pmpm_results['total_pmpm']), unsafe_allow_html=True)

            with col4:
                lift = st.session_state.get('enrollment_lift', 0)
                lift_color = "#48bb78" if lift > 0 else "#fc8181"
                st.markdown("""
                <div class="kpi-card">
                    <div class="kpi-value" style="color: {};">{:+.2%}</div>
                    <div class="kpi-label">Enrollment Lift</div>
                </div>
                """.format(lift_color, lift), unsafe_allow_html=True)

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                # Waterfall Chart
                fig = create_waterfall_chart(
                    150,  # baseline
                    st.session_state.pmpm_results['total_pmpm'],
                    st.session_state.pmpm_results['details']
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Enrollment Trend
                enrollment_df = generate_enrollment_data(selected_plan_id)
                fig = create_enrollment_trend_chart(enrollment_df)
                st.plotly_chart(fig, use_container_width=True)

            # Detailed Breakdown
            st.markdown("### Detailed Cost Breakdown")
            details_df = st.session_state.pmpm_results['details']
            details_df['gross_pmpm'] = details_df['gross_pmpm'].round(2)
            details_df['member_pmpm'] = details_df['member_pmpm'].round(2)
            details_df['plan_pmpm'] = details_df['plan_pmpm'].round(2)

            st.dataframe(
                details_df,
                column_config={
                    "benefit_name": st.column_config.TextColumn("Benefit"),
                    "category": st.column_config.TextColumn("Category"),
                    "gross_pmpm": st.column_config.NumberColumn("Gross PMPM", format="$%.2f"),
                    "member_pmpm": st.column_config.NumberColumn("Member PMPM", format="$%.2f"),
                    "plan_pmpm": st.column_config.NumberColumn("Plan PMPM", format="$%.2f"),
                },
                hide_index=True,
                use_container_width=True
            )

            # Monte Carlo Results
            if run_monte_carlo:
                st.markdown("### Monte Carlo Simulation Results")

                with st.spinner("Running Monte Carlo simulation..."):
                    simulator = MAPlanSimulator(selected_plan, st.session_state.cost_sharing_df)
                    mc_results = simulator.run_monte_carlo(st.session_state.cost_sharing_df, n_simulations)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Mean PMPM", f"${mc_results['mean']:.2f}")

                with col2:
                    st.metric("Std Deviation", f"${mc_results['std']:.2f}")

                with col3:
                    st.metric("95% CI", f"${mc_results['ci_lower']:.2f} - ${mc_results['ci_upper']:.2f}")

                # Distribution chart
                fig = px.histogram(
                    x=mc_results['results'],
                    nbins=30,
                    title="PMPM Distribution (Monte Carlo)",
                    labels={'x': 'PMPM ($)', 'y': 'Frequency'},
                    color_discrete_sequence=['#4299e1']
                )
                fig.add_vline(x=mc_results['mean'], line_dash="dash", line_color="red", annotation_text="Mean")
                fig.update_layout(
                    height=350,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#2d3748')
                )
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Please calculate PMPM in the Benefit Design tab to see analysis results.")

    with tab3:
        st.markdown("### Scenario Management")

        if st.session_state.scenarios:
            # Scenario comparison controls
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_scenarios = st.multiselect(
                    "Select scenarios to compare",
                    options=[s['name'] for s in st.session_state.scenarios],
                    default=[s['name'] for s in st.session_state.scenarios[:2]]
                )

            with col2:
                if st.button("🗑️ Clear All Scenarios", use_container_width=True):
                    st.session_state.scenarios = []
                    st.rerun()

            # Display selected scenarios
            if selected_scenarios:
                scenarios_to_compare = [s for s in st.session_state.scenarios if s['name'] in selected_scenarios]

                # Comparison chart
                fig = create_comparison_chart(scenarios_to_compare)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                # Scenario cards
                st.markdown("### Scenario Details")

                cols = st.columns(min(len(scenarios_to_compare), 3))
                for idx, scenario in enumerate(scenarios_to_compare[:3]):
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="scenario-card">
                            <h4>{scenario['name']}</h4>
                            <p><strong>Created:</strong> {scenario['timestamp'].strftime('%Y-%m-%d %H:%M')}</p>
                            <p><strong>Medicare PMPM:</strong> ${scenario['medicare_pmpm']:.2f}</p>
                            <p><strong>Supplemental PMPM:</strong> ${scenario['supplemental_pmpm']:.2f}</p>
                            <p><strong>Total PMPM:</strong> ${scenario['total_pmpm']:.2f}</p>
                            <p><strong>Enrollment Lift:</strong> {scenario['enrollment_lift']:.2%}</p>
                        </div>
                        """, unsafe_allow_html=True)

                # Detailed comparison table
                if len(scenarios_to_compare) == 2:
                    st.markdown("### Side-by-Side Comparison")

                    s1, s2 = scenarios_to_compare[0], scenarios_to_compare[1]

                    comparison_data = {
                        'Metric': ['Medicare PMPM', 'Supplemental PMPM', 'Total PMPM', 'Enrollment Lift'],
                        s1['name']: [
                            f"${s1['medicare_pmpm']:.2f}",
                            f"${s1['supplemental_pmpm']:.2f}",
                            f"${s1['total_pmpm']:.2f}",
                            f"{s1['enrollment_lift']:.2%}"
                        ],
                        s2['name']: [
                            f"${s2['medicare_pmpm']:.2f}",
                            f"${s2['supplemental_pmpm']:.2f}",
                            f"${s2['total_pmpm']:.2f}",
                            f"{s2['enrollment_lift']:.2%}"
                        ],
                        'Delta': [
                            f"${s2['medicare_pmpm'] - s1['medicare_pmpm']:.2f}",
                            f"${s2['supplemental_pmpm'] - s1['supplemental_pmpm']:.2f}",
                            f"${s2['total_pmpm'] - s1['total_pmpm']:.2f}",
                            f"{s2['enrollment_lift'] - s1['enrollment_lift']:.2%}"
                        ]
                    }

                    st.dataframe(pd.DataFrame(comparison_data), hide_index=True, use_container_width=True)
        else:
            st.info("No scenarios saved yet. Create scenarios in the Benefit Design tab.")

    with tab4:
        st.markdown("### Report Generation")

        report_type = st.selectbox(
            "Select Report Type",
            ["Executive Summary", "Detailed Benefit Analysis", "Scenario Comparison", "Compliance Report"]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            include_charts = st.checkbox("Include Charts", value=True)

        with col2:
            include_monte_carlo = st.checkbox("Include Monte Carlo Analysis", value=False)

        with col3:
            include_recommendations = st.checkbox("Include Recommendations", value=True)

        if st.button("📄 Generate Report", type="primary", use_container_width=True):
            with st.spinner("Generating report..."):
                # Simulate report generation
                import time
                time.sleep(2)

                st.success("Report generated successfully!")

                # Display sample report content
                st.markdown("---")
                st.markdown(f"## {report_type}")
                st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Plan:** {selected_plan['plan_name']} ({selected_plan_id})")

                if 'pmpm_results' in st.session_state:
                    st.markdown("### Key Metrics")
                    st.markdown(f"""
                    - **Medicare PMPM:** ${st.session_state.pmpm_results['total_medicare_pmpm']:.2f}
                    - **Supplemental PMPM:** ${st.session_state.pmpm_results['total_supplemental_pmpm']:.2f}
                    - **Total PMPM:** ${st.session_state.pmpm_results['total_pmpm']:.2f}
                    - **Risk-Adjusted PMPM:** ${st.session_state.pmpm_results['risk_adjusted_pmpm']:.2f}
                    """)

                    if 'enrollment_lift' in st.session_state:
                        st.markdown(f"- **Projected Enrollment Lift:** {st.session_state.enrollment_lift:.2%}")

                if include_recommendations:
                    st.markdown("### Recommendations")
                    st.markdown("""
                    1. **Optimize High-Cost Benefits:** Consider adjusting copays for specialist visits and diagnostic imaging to reduce PMPM by $3-5.
                    2. **Enhance Supplemental Benefits:** Adding dental and vision coverage could increase enrollment by 5-8% with minimal PMPM impact.
                    3. **Network Optimization:** Negotiate better rates with high-volume providers to reduce unit costs by 3-5%.
                    4. **Star Rating Improvement:** Focus on member experience metrics to improve star rating by 0.2-0.3 points.
                    """)

                # Download buttons
                col1, col2 = st.columns(2)

                with col1:
                    st.download_button(
                        label="📥 Download as PDF",
                        data=f"PDF Report Content for {selected_plan['plan_name']}",
                        file_name=f"MA_Plan_Report_{selected_plan_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )

                with col2:
                    if 'pmpm_results' in st.session_state:
                        csv_data = st.session_state.pmpm_results['details'].to_csv(index=False)
                        st.download_button(
                            label="📥 Download Data (CSV)",
                            data=csv_data,
                            file_name=f"MA_Plan_Data_{selected_plan_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )

    # Footer
    st.markdown("""
    <div class="footer">
        <p>Medicare Advantage Plan Design Simulator v1.0 | © 2025 Healthcare Analytics Platform</p>
        <p style="font-size: 0.875rem; color: #a0aec0;">Data is simulated for demonstration purposes only</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
