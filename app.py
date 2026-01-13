"""
MASLD vs Healthy Ultrasound ML - Premium Results Viewer
A polished, interactive dashboard for presenting model performance and explainability results.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from typing import Optional

from data_loader import (
    load_all_data,
    validate_results_structure,
    filter_dataframe,
    get_explainability_image_path
)
from ui import (
    render_hero_banner,
    render_demo_banner,
    render_sidebar_brand_header,
    render_sidebar_nav_pills,
    render_sidebar_status_card,
    render_connection_status,
    render_kpi_card_clickable,
    render_global_filter_bar,
    render_artifact_cards,
    render_case_detail_card
)

# Page configuration
st.set_page_config(
    page_title="MASLD vs Healthy Ultrasound ML - Results Viewer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and inject CSS
def load_css():
    """Load CSS from styles.css file."""
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        with open(css_path, 'r') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


@st.cache_data
def cached_load_data(results_root: Path, demo_mode: bool = False):
    """Cached data loading."""
    return load_all_data(results_root, demo_mode)


def get_folder_name(results_root: Path) -> Optional[str]:
    """Get folder name without exposing full path."""
    try:
        name = results_root.name
        # Only return if it's a simple name (no path separators)
        if name and '/' not in name and '\\' not in name and ':' not in name:
            return name
        return None
    except:
        return None


def sidebar_setup():
    """Premium sidebar setup with branded header and navigation."""
    # Brand header
    render_sidebar_brand_header()
    
    # Connect Results section
    st.sidebar.markdown('<div class="sidebar-connect-section">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-section-header">Connect Results</div>', unsafe_allow_html=True)
    
    # Results path input (relative path only - NEVER show absolute)
    default_path = "../results"
    results_path = st.sidebar.text_input(
        "Results Folder",
        value=default_path,
        help="Relative path to results folder",
        label_visibility="visible"
    )
    
    results_root = Path(results_path).resolve()
    
    # Demo mode
    demo_mode = st.sidebar.checkbox(
        "Demo Mode",
        value=False,
        help="Use synthetic demo data"
    )
    
    # Connection status (NO PATH EXPOSURE)
    if not demo_mode:
        is_valid, missing = validate_results_structure(results_root)
        if is_valid:
            folder_name = get_folder_name(results_root)
            render_connection_status(True, folder_name)
        else:
            render_connection_status(False)
            if missing:
                st.sidebar.warning(f"Missing {len(missing)} required file(s)")
    else:
        render_connection_status(True, "DEMO")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    st.sidebar.markdown('<div class="sidebar-section-header">Navigation</div>', unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Select Page",
        ["📊 Dashboard", "🔍 Case Explorer", "📈 Performance & Run Info"],
        label_visibility="collapsed"
    )
    
    # Remove emoji for routing
    page = page.split(" ", 1)[1] if " " in page else page
    
    # Render nav pills (visual only, radio handles selection)
    render_sidebar_nav_pills(page)
    
    return results_root, demo_mode, page


def apply_global_filters(index_df, filters):
    """Apply global filters to dataframe."""
    return filter_dataframe(
        index_df,
        risk_bands=filters.get('risk_bands'),
        y_true_values=filters.get('y_true'),
        folds=filters.get('folds'),
        prob_min=filters.get('prob_range', (0.0, 1.0))[0],
        prob_max=filters.get('prob_range', (0.0, 1.0))[1],
        uncert_min=filters.get('uncert_range', (0.0, 1.0))[0],
        uncert_max=filters.get('uncert_range', (0.0, 1.0))[1]
    )


def page_dashboard(data: dict, results_root: Path):
    """Dashboard page with hero banner, KPIs, and interactive charts."""
    # Hero Banner
    render_hero_banner()
    
    # Demo banner if active
    if data.get('is_demo', False):
        render_demo_banner()
    
    index_df = data['index_df']
    artifacts = data['artifacts']
    run_config = data.get('run_config')
    
    if index_df is None or index_df.empty:
        st.warning("No data available. Enable Demo Mode or check your results folder.")
        return
    
    # Show note if explainability reports are subset of total patients
    if run_config and run_config.get('n_patients'):
        total_patients = run_config.get('n_patients', 0)
        n_cases_in_index = len(index_df)
        if total_patients > n_cases_in_index:
            st.info(f"ℹ️ **Note:** This dashboard shows {n_cases_in_index} explainability reports. The full dataset contains {total_patients} patients. Explainability reports were generated for a subset of cases.")
    
    # Artifacts as cards
    st.markdown("### Available Artifacts", unsafe_allow_html=True)
    render_artifact_cards(artifacts)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Global Filter Bar (collapsible)
    filters = render_global_filter_bar(index_df, key_prefix="dashboard")
    filtered_df = apply_global_filters(index_df, filters)
    
    st.info(f"Showing {len(filtered_df)} of {len(index_df)} cases")
    
    # Compute metrics
    n_cases = len(filtered_df)
    n_high_risk = len(filtered_df[filtered_df['risk_band'] == 'HIGH']) if 'risk_band' in filtered_df.columns else 0
    pct_high = (n_high_risk / n_cases * 100) if n_cases > 0 else 0
    avg_prob = filtered_df['p_calibrated'].mean() if 'p_calibrated' in filtered_df.columns else 0
    avg_uncert = filtered_df['uncertainty_std'].mean() if 'uncertainty_std' in filtered_df.columns else 0
    n_images = artifacts.get('case_image_count', 0)
    
    # KPI Cards
    st.markdown("### Key Metrics", unsafe_allow_html=True)
    kpi_cols = st.columns(5)
    
    with kpi_cols[0]:
        # Show total cases with note if subset
        subtitle = ""
        if run_config and run_config.get('n_patients'):
            total_patients = run_config.get('n_patients', 0)
            if total_patients > n_cases:
                subtitle = f"of {total_patients} patients"
        render_kpi_card_clickable("Cases with Reports", str(n_cases), "📋", subtitle=subtitle, color="blue", clickable=False)
    with kpi_cols[1]:
        render_kpi_card_clickable("High Risk", f"{pct_high:.1f}%", "⚠️", f"{n_high_risk} cases", color="pink", clickable=False)
    with kpi_cols[2]:
        render_kpi_card_clickable("Avg Risk", f"{avg_prob:.3f}", "📊", color="yellow", clickable=False)
    with kpi_cols[3]:
        render_kpi_card_clickable("Avg Uncertainty", f"{avg_uncert:.3f}", "🔍", color="green", clickable=False)
    with kpi_cols[4]:
        render_kpi_card_clickable("Images Available", str(n_images), "🖼️", color="default", clickable=False)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Top N Cases
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("### 🔴 Top High-Risk Cases", unsafe_allow_html=True)
        if 'p_calibrated' in filtered_df.columns:
            top_high = filtered_df.nlargest(5, 'p_calibrated')[['case_id', 'risk_band', 'p_calibrated']].copy()
            top_high['p_calibrated'] = top_high['p_calibrated'].round(3)
            top_high.columns = ['Case ID', 'Risk Band', 'Probability']
            st.dataframe(top_high, use_container_width=True, hide_index=True)
            
            if len(top_high) > 0:
                selected_high = st.selectbox("View Case", options=top_high['Case ID'].tolist(), key="view_high")
                if st.button("🔍 View in Case Explorer", key="goto_high", use_container_width=True):
                    st.session_state.case_selector = selected_high
                    st.session_state.page_switch = "Case Explorer"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Top Most Uncertain Cases", unsafe_allow_html=True)
        if 'uncertainty_std' in filtered_df.columns:
            top_uncert = filtered_df.nlargest(5, 'uncertainty_std')[['case_id', 'risk_band', 'uncertainty_std']].copy()
            top_uncert['uncertainty_std'] = top_uncert['uncertainty_std'].round(3)
            top_uncert.columns = ['Case ID', 'Risk Band', 'Uncertainty']
            st.dataframe(top_uncert, use_container_width=True, hide_index=True)
            
            if len(top_uncert) > 0:
                selected_uncert = st.selectbox("View Case", options=top_uncert['Case ID'].tolist(), key="view_uncert")
                if st.button("🔍 View in Case Explorer", key="goto_uncert", use_container_width=True):
                    st.session_state.case_selector = selected_uncert
                    st.session_state.page_switch = "Case Explorer"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    chart_cols = st.columns(2)
    
    with chart_cols[0]:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### Risk Distribution", unsafe_allow_html=True)
        if 'p_calibrated' in filtered_df.columns:
            fig = px.histogram(
                filtered_df,
                x='p_calibrated',
                nbins=25,
                color_discrete_sequence=['#667eea'],
                labels={'p_calibrated': 'Calibrated Probability', 'count': 'Cases'}
            )
            fig.update_layout(
                showlegend=False,
                height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(gridcolor='#e2e8f0'),
                yaxis=dict(gridcolor='#e2e8f0'),
                font=dict(size=11)
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_cols[1]:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### Risk Band Counts", unsafe_allow_html=True)
        if 'risk_band' in filtered_df.columns:
            risk_counts = filtered_df['risk_band'].value_counts().reset_index()
            risk_counts.columns = ['Risk Band', 'Count']
            
            fig = px.bar(
                risk_counts,
                x='Risk Band',
                y='Count',
                color='Risk Band',
                color_discrete_map={
                    'LOW': '#48BB78',
                    'LOW-MOD': '#F6E05E',
                    'MODERATE': '#F6AD55',
                    'HIGH': '#FC8181'
                }
            )
            fig.update_layout(
                showlegend=False,
                height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(gridcolor='#e2e8f0'),
                yaxis=dict(gridcolor='#e2e8f0'),
                font=dict(size=11)
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Scatter plot
    if 'p_calibrated' in filtered_df.columns and 'uncertainty_std' in filtered_df.columns:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### Uncertainty vs Risk", unsafe_allow_html=True)
        fig = px.scatter(
            filtered_df,
            x='p_calibrated',
            y='uncertainty_std',
            color='risk_band',
            hover_data=['case_id'],
            color_discrete_map={
                'LOW': '#48BB78',
                'LOW-MOD': '#F6E05E',
                'MODERATE': '#F6AD55',
                'HIGH': '#FC8181'
            },
            labels={
                'p_calibrated': 'Calibrated Probability',
                'uncertainty_std': 'Uncertainty (Std)',
                'case_id': 'Case ID'
            }
        )
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#e2e8f0'),
            yaxis=dict(gridcolor='#e2e8f0'),
            font=dict(size=11)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


def page_case_explorer(data: dict, results_root: Path):
    """Case Explorer page with interactive case selection and detail view."""
    index_df = data['index_df']
    if index_df is None or index_df.empty:
        st.warning("No data available. Enable Demo Mode or check your results folder.")
        return
    
    # Apply global filters
    filters = render_global_filter_bar(index_df, key_prefix="explorer")
    filtered_df = apply_global_filters(index_df, filters)
    
    # Two column layout
    left_col, right_col = st.columns([1, 1.2])
    
    with left_col:
        st.markdown("### Case List", unsafe_allow_html=True)
        
        # Search
        search_term = st.text_input("🔍 Search Case ID", key="case_search")
        if search_term:
            filtered_df = filtered_df[filtered_df['case_id'].str.contains(search_term, case=False, na=False)]
        
        # Display table (Case ID only, no patient_id)
        display_cols = ['case_id', 'risk_band', 'p_calibrated', 'uncertainty_std', 'y_true']
        available_cols = [c for c in display_cols if c in filtered_df.columns]
        display_df = filtered_df[available_cols].copy()
        
        # Format for display
        if 'y_true' in display_df.columns:
            display_df['y_true'] = display_df['y_true'].map({0: 'Healthy', 1: 'MASLD'})
            display_df = display_df.rename(columns={'y_true': 'Class'})
        if 'p_calibrated' in display_df.columns:
            display_df['p_calibrated'] = display_df['p_calibrated'].round(3)
        if 'uncertainty_std' in display_df.columns:
            display_df['uncertainty_std'] = display_df['uncertainty_std'].round(3)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Case selection
        case_ids = sorted(filtered_df['case_id'].unique().tolist())
        if not case_ids:
            st.warning("No cases match filters")
            selected_case = None
        else:
            if 'case_selector' not in st.session_state:
                st.session_state.case_selector = case_ids[0]
            
            selected_case = st.selectbox(
                "Select Case",
                options=case_ids,
                index=case_ids.index(st.session_state.case_selector) if st.session_state.case_selector in case_ids else 0,
                key="case_selector"
            )
    
    with right_col:
        if selected_case:
            case_data = filtered_df[filtered_df['case_id'] == selected_case].iloc[0].to_dict()
            image_path = get_explainability_image_path(results_root, selected_case)
            render_case_detail_card(case_data, image_path, results_root)
        else:
            st.info("Select a case from the list to view details")


def page_performance(data: dict, results_root: Path):
    """Performance & Run Info page with tabs."""
    metrics_summary = data['metrics_summary']
    run_config = data['run_config']
    artifacts = data['artifacts']
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Metrics", "📈 Calibration", "📁 Artifacts"])
    
    with tab1:
        st.markdown("### Model Performance Metrics", unsafe_allow_html=True)
        
        if metrics_summary is not None and not metrics_summary.empty:
            if len(metrics_summary) > 0:
                model_row = metrics_summary.iloc[0]
                metric_cols = st.columns(4)
                
                with metric_cols[0]:
                    if 'AUC' in model_row:
                        render_kpi_card_clickable("AUC", f"{model_row['AUC']:.3f}", "📈", color="blue", clickable=False)
                with metric_cols[1]:
                    if 'PR_AUC' in model_row:
                        render_kpi_card_clickable("PR-AUC", f"{model_row['PR_AUC']:.3f}", "📊", color="green", clickable=False)
                with metric_cols[2]:
                    if 'Accuracy' in model_row:
                        render_kpi_card_clickable("Accuracy", f"{model_row['Accuracy']:.3f}", "✅", color="yellow", clickable=False)
                with metric_cols[3]:
                    if 'F1' in model_row:
                        render_kpi_card_clickable("F1 Score", f"{model_row['F1']:.3f}", "🎯", color="pink", clickable=False)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            display_cols = ['model', 'AUC', 'PR_AUC', 'Sensitivity', 'Specificity', 'Accuracy', 'F1']
            available_cols = [c for c in display_cols if c in metrics_summary.columns]
            if available_cols:
                st.dataframe(
                    metrics_summary[available_cols].style.format({
                        'AUC': '{:.3f}',
                        'PR_AUC': '{:.3f}',
                        'Sensitivity': '{:.3f}',
                        'Specificity': '{:.3f}',
                        'Accuracy': '{:.3f}',
                        'F1': '{:.3f}'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No metrics summary available")
    
    with tab2:
        st.markdown("### Calibration Plots", unsafe_allow_html=True)
        
        plot_cols = st.columns(2)
        
        if artifacts.get('roc_curves', False):
            with plot_cols[0]:
                roc_path = results_root / "roc_curves_patient_level.png"
                if roc_path.exists():
                    st.image(str(roc_path), use_container_width=True, caption="ROC Curves")
        
        if artifacts.get('pr_curves', False):
            with plot_cols[1]:
                pr_path = results_root / "pr_curves_patient_level.png"
                if pr_path.exists():
                    st.image(str(pr_path), use_container_width=True, caption="PR Curves")
        
        if artifacts.get('confusion_matrix', False):
            cm_path = results_root / "confusion_matrices_patient_level.png"
            if cm_path.exists():
                st.image(str(cm_path), use_container_width=True, caption="Confusion Matrix")
        
        if not any([artifacts.get('roc_curves'), artifacts.get('pr_curves'), artifacts.get('confusion_matrix')]):
            st.info("No calibration plots available")
    
    with tab3:
        st.markdown("### Available Artifacts", unsafe_allow_html=True)
        render_artifact_cards(artifacts)
        
        # Run Summary
        if run_config:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Run Summary", unsafe_allow_html=True)
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            
            info_cols = st.columns(3)
            with info_cols[0]:
                st.markdown(f"""
                **Timestamp:** {run_config.get('timestamp', 'N/A')[:10] if run_config.get('timestamp') else 'N/A'}  
                **Patients:** {run_config.get('n_patients', 'N/A')}  
                **Folds:** 3-fold CV
                """)
            with info_cols[1]:
                st.markdown(f"""
                **MASLD Cases:** {run_config.get('n_masld', 'N/A')}  
                **Healthy Cases:** {run_config.get('n_healthy', 'N/A')}  
                **Batch Size:** {run_config.get('batch_size', 'N/A')}
                """)
            with info_cols[2]:
                st.markdown(f"""
                **CNN Epochs:** {run_config.get('cnn_epochs', 'N/A')}  
                **Learning Rate:** {run_config.get('cnn_lr', 'N/A')}  
                **Calibration Bins:** {run_config.get('calibration_bins', 'N/A')}
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main application entry point."""
    # Sidebar setup
    results_root, demo_mode, page = sidebar_setup()
    
    # Handle page switching from buttons
    if 'page_switch' in st.session_state:
        page = st.session_state.page_switch
        del st.session_state.page_switch
    
    # Load data
    data = cached_load_data(results_root, demo_mode=demo_mode)
    
    # Render status card in sidebar
    render_sidebar_status_card(data)
    
    # Route to page
    if page == "Dashboard":
        page_dashboard(data, results_root)
    elif page == "Case Explorer":
        page_case_explorer(data, results_root)
    elif page == "Performance & Run Info":
        page_performance(data, results_root)
    
    # Footer
    st.sidebar.markdown("""
    <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0; text-align: center; color: #718096; font-size: 0.75rem;">
        <div style="font-weight: 600; color: #2d3748; margin-bottom: 0.3rem;">MASLD Results Viewer</div>
        <div>Research Use Only</div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
