"""
UI components for MASLD Results Viewer.
Provides reusable components: cards, badges, hero banner, filter bar, sidebar components.
"""

import streamlit as st
from pathlib import Path
from typing import Optional, Dict
import json
import plotly.graph_objects as go
from datetime import datetime


def render_hero_banner():
    """Render premium hero banner for dashboard."""
    st.markdown("""
    <div class="hero-banner">
        <div style="position: relative; z-index: 1;">
            <h1 class="hero-title">MASLD Results Dashboard</h1>
            <p class="hero-subtitle">Interactive analysis and explainability viewer for ultrasound classification results</p>
        </div>
        <div class="hero-illustration">🩺</div>
    </div>
    """, unsafe_allow_html=True)


def render_demo_banner():
    """Render demo mode banner."""
    st.markdown("""
    <div class="demo-banner">
        🔶 DEMO MODE ACTIVE — Using synthetic data for UI preview only
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_brand_header():
    """Render premium branded sidebar header."""
    st.sidebar.markdown("""
    <div class="sidebar-brand-header">
        <div class="sidebar-brand-title">
            <div class="sidebar-brand-icon">🩺</div>
            <div>MASLD Viewer</div>
        </div>
        <p class="sidebar-brand-subtitle">Ultrasound ML Results</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_nav_pills(current_page: str):
    """Render premium navigation pills."""
    pages = [
        ("📊", "Dashboard", "Dashboard"),
        ("🔍", "Case Explorer", "Case Explorer"),
        ("📈", "Performance & Run Info", "Performance & Run Info"),
    ]
    
    st.sidebar.markdown('<div class="sidebar-nav-container">', unsafe_allow_html=True)
    
    for icon, label, page_key in pages:
        is_active = current_page == page_key
        active_class = "active" if is_active else ""
        st.sidebar.markdown(f"""
        <div class="sidebar-nav-pill {active_class}" style="position: relative;">
            <span class="sidebar-nav-icon">{icon}</span>
            <span>{label}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)


def render_sidebar_status_card(data: dict):
    """Render status summary card in sidebar."""
    index_df = data.get('index_df')
    artifacts = data.get('artifacts', {})
    
    if index_df is None or index_df.empty:
        return
    
    n_cases = len(index_df)
    n_high_risk = len(index_df[index_df['risk_band'] == 'HIGH']) if 'risk_band' in index_df.columns else 0
    pct_high = (n_high_risk / n_cases * 100) if n_cases > 0 else 0
    n_images = artifacts.get('case_image_count', 0)
    
    st.sidebar.markdown("""
    <div class="sidebar-status-card">
        <div class="sidebar-status-title">
            <span>📊</span>
            <span>Status & Summary</span>
        </div>
        <div class="sidebar-status-metric">
            <span class="sidebar-status-label">Cases Loaded</span>
            <span class="sidebar-status-value">{}</span>
        </div>
        <div class="sidebar-status-metric">
            <span class="sidebar-status-label">High Risk</span>
            <span class="sidebar-status-value">{:.1f}%</span>
        </div>
        <div class="sidebar-status-metric">
            <span class="sidebar-status-label">Images Available</span>
            <span class="sidebar-status-value">{}</span>
        </div>
        <div class="sidebar-status-metric" style="margin-top: 0.5rem; padding-top: 0.75rem; border-top: 1px solid #e2e8f0;">
            <span class="sidebar-status-label" style="font-size: 0.75rem; color: #a0aec0;">Last Loaded</span>
            <span class="sidebar-status-value" style="font-size: 0.75rem; color: #718096;">{}</span>
        </div>
    </div>
    """.format(n_cases, pct_high, n_images, datetime.now().strftime("%H:%M")), unsafe_allow_html=True)


def render_connection_status(connected: bool, folder_name: str = None):
    """Render connection status without exposing paths."""
    if connected:
        folder_display = f" ({folder_name})" if folder_name else ""
        st.sidebar.markdown(f"""
        <div class="connection-status">
            ✅ Connected{folder_display}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div class="connection-status error">
            ❌ Not Connected
        </div>
        """, unsafe_allow_html=True)


def render_kpi_card_clickable(title: str, value: str, icon: str = "", subtitle: str = "", 
                               color: str = "default", key: str = None, clickable: bool = False):
    """Render a premium KPI card."""
    color_map = {
        "default": "linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)",
        "blue": "linear-gradient(135deg, #E5F5FF 0%, #F0F9FF 100%)",
        "green": "linear-gradient(135deg, #E5FFE5 0%, #F0FFF0 100%)",
        "yellow": "linear-gradient(135deg, #FFF4E5 0%, #FFFBF0 100%)",
        "pink": "linear-gradient(135deg, #FFE5E5 0%, #FFF0F5 100%)",
    }
    bg = color_map.get(color, color_map["default"])
    
    click_class = "kpi-card" if clickable else "premium-card"
    
    st.markdown(f"""
    <div class="{click_class}" style="background: {bg};">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
            <div style="font-size: 0.85rem; color: #718096; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">
                {title}
            </div>
            {f'<div style="font-size: 1.5rem; opacity: 0.6;">{icon}</div>' if icon else ''}
        </div>
        <div class="kpi-value">{value}</div>
        {f'<div style="font-size: 0.8rem; color: #a0aec0; margin-top: 0.3rem;">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_risk_gauge(value: float, case_id: str = ""):
    """Render plotly gauge for risk level."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Risk Level{(' - ' + case_id) if case_id else ''}", 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "#C6F6D5"},
                {'range': [30, 50], 'color': "#FEFCBF"},
                {'range': [50, 75], 'color': "#FED7AA"},
                {'range': [75, 100], 'color': "#FED7D7"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    return fig


def render_uncertainty_meter(value: float, max_value: float = 0.2):
    """Render horizontal uncertainty meter."""
    percent = min((value / max_value) * 100, 100)
    color = "#48BB78" if percent < 33 else "#F6E05E" if percent < 66 else "#FC8181"
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-size: 0.9rem; color: #718096; font-weight: 500;">Uncertainty</span>
            <span style="font-size: 0.9rem; color: #1a202c; font-weight: 600;">{value:.3f}</span>
        </div>
        <div style="background: #e2e8f0; height: 10px; border-radius: 5px; overflow: hidden;">
            <div style="background: {color};
                        width: {percent}%;
                        height: 100%;
                        transition: width 0.3s;
                        border-radius: 5px;">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_global_filter_bar(index_df, key_prefix="global"):
    """Render collapsible global filter bar with active filter chips."""
    if index_df is None or index_df.empty:
        return {}
    
    # Show active filters outside expander
    if f'{key_prefix}_risk_bands' in st.session_state and st.session_state[f'{key_prefix}_risk_bands']:
        st.markdown("**Active Filters:**", unsafe_allow_html=True)
        active_chips = st.container()
        with active_chips:
            for band in st.session_state[f'{key_prefix}_risk_bands']:
                st.markdown(f'<span class="filter-chip active">Risk: {band}</span>', unsafe_allow_html=True)
            if st.session_state.get(f'{key_prefix}_y_true'):
                labels = ["Healthy" if x == 0 else "MASLD" for x in st.session_state[f'{key_prefix}_y_true']]
                st.markdown(f'<span class="filter-chip active">Class: {", ".join(labels)}</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Collapsible filter controls
    with st.expander("🔧 Global Filters", expanded=False):
        # Initialize session state for filters
        if f'{key_prefix}_risk_bands' not in st.session_state:
            st.session_state[f'{key_prefix}_risk_bands'] = []
        if f'{key_prefix}_y_true' not in st.session_state:
            st.session_state[f'{key_prefix}_y_true'] = []
        if f'{key_prefix}_folds' not in st.session_state:
            st.session_state[f'{key_prefix}_folds'] = []
        if f'{key_prefix}_prob_range' not in st.session_state:
            st.session_state[f'{key_prefix}_prob_range'] = (0.0, 1.0)
        if f'{key_prefix}_uncert_range' not in st.session_state:
            uncert_max = index_df['uncertainty_std'].max() if 'uncertainty_std' in index_df.columns else 0.2
            st.session_state[f'{key_prefix}_uncert_range'] = (0.0, float(uncert_max))
        
        filter_cols = st.columns(5)
        
        with filter_cols[0]:
            risk_bands = st.multiselect(
                "Risk Band",
                options=sorted(index_df['risk_band'].unique()) if 'risk_band' in index_df.columns else [],
                default=st.session_state[f'{key_prefix}_risk_bands'],
                key=f"{key_prefix}_risk_select"
            )
            st.session_state[f'{key_prefix}_risk_bands'] = risk_bands
        
        with filter_cols[1]:
            y_true_options = st.multiselect(
                "Class",
                options=[0, 1],
                format_func=lambda x: "Healthy" if x == 0 else "MASLD",
                default=st.session_state[f'{key_prefix}_y_true'],
                key=f"{key_prefix}_class_select"
            )
            st.session_state[f'{key_prefix}_y_true'] = y_true_options
        
        with filter_cols[2]:
            folds = st.multiselect(
                "Fold",
                options=sorted(index_df['fold'].unique()) if 'fold' in index_df.columns else [],
                default=st.session_state[f'{key_prefix}_folds'],
                key=f"{key_prefix}_fold_select"
            )
            st.session_state[f'{key_prefix}_folds'] = folds
        
        with filter_cols[3]:
            if 'p_calibrated' in index_df.columns:
                prob_range = st.slider(
                    "Probability",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state[f'{key_prefix}_prob_range'],
                    step=0.01,
                    key=f"{key_prefix}_prob_slider"
                )
                st.session_state[f'{key_prefix}_prob_range'] = prob_range
            else:
                prob_range = (0.0, 1.0)
        
        with filter_cols[4]:
            if 'uncertainty_std' in index_df.columns:
                uncert_max = index_df['uncertainty_std'].max()
                uncert_range = st.slider(
                    "Uncertainty",
                    min_value=0.0,
                    max_value=float(uncert_max),
                    value=st.session_state[f'{key_prefix}_uncert_range'],
                    step=0.01,
                    key=f"{key_prefix}_uncert_slider"
                )
                st.session_state[f'{key_prefix}_uncert_range'] = uncert_range
            else:
                uncert_range = (0.0, 1.0)
        
        if st.button("🔄 Reset Filters", key=f"{key_prefix}_reset", use_container_width=True):
            st.session_state[f'{key_prefix}_risk_bands'] = []
            st.session_state[f'{key_prefix}_y_true'] = []
            st.session_state[f'{key_prefix}_folds'] = []
            st.session_state[f'{key_prefix}_prob_range'] = (0.0, 1.0)
            if 'uncertainty_std' in index_df.columns:
                uncert_max = index_df['uncertainty_std'].max()
                st.session_state[f'{key_prefix}_uncert_range'] = (0.0, float(uncert_max))
            st.rerun()
    
    return {
        'risk_bands': st.session_state.get(f'{key_prefix}_risk_bands', []),
        'y_true': st.session_state.get(f'{key_prefix}_y_true', []),
        'folds': st.session_state.get(f'{key_prefix}_folds', []),
        'prob_range': st.session_state.get(f'{key_prefix}_prob_range', (0.0, 1.0)),
        'uncert_range': st.session_state.get(f'{key_prefix}_uncert_range', (0.0, 1.0))
    }


def render_risk_badge(risk_band: str) -> str:
    """Get HTML for risk band badge."""
    # Map risk band to CSS class
    risk_class_map = {
        'LOW': 'low',
        'LOW-MOD': 'low-mod',
        'MODERATE': 'moderate',
        'HIGH': 'high'
    }
    risk_class = risk_class_map.get(risk_band.upper(), 'low')
    return f'<span class="risk-badge {risk_class}">{risk_band}</span>'


def render_artifact_cards(artifacts: dict):
    """Render artifacts as visual cards."""
    artifact_list = [
        ("📄", "Index CSV", artifacts.get('index_csv', False)),
        ("🗺️", "Case Mapping", artifacts.get('case_mapping', False)),
        ("🖼️", "Case Images", artifacts.get('case_images', False), artifacts.get('case_image_count', 0)),
        ("📊", "Metrics", artifacts.get('metrics_summary', False)),
        ("⚙️", "Config", artifacts.get('run_config', False)),
        ("📈", "Calibration", artifacts.get('calibration_plots', False)),
        ("📉", "ROC Curves", artifacts.get('roc_curves', False)),
        ("📊", "PR Curves", artifacts.get('pr_curves', False)),
    ]
    
    cols = st.columns(4)
    for idx, item in enumerate(artifact_list):
        with cols[idx % 4]:
            if len(item) == 4:
                icon, label, available, count = item
                detail = f"{count} images" if available and count > 0 else ("Available" if available else "Missing")
            else:
                icon, label, available = item
                detail = "Available" if available else "Missing"
            
            status_icon = "✅" if available else "❌"
            status_color = "#22543D" if available else "#742A2A"
            st.markdown(f"""
            <div class="artifact-card">
                <div class="artifact-icon">{icon}</div>
                <div class="artifact-label">{label}</div>
                <div class="artifact-status" style="color: {status_color};">{status_icon} {detail}</div>
            </div>
            """, unsafe_allow_html=True)


def render_case_detail_card(case_data: dict, image_path: Optional[Path], results_root: Path):
    """Render detailed case information card with gauges."""
    case_id = case_data.get('case_id', 'N/A')
    risk_band = case_data.get('risk_band', 'N/A')
    prob = case_data.get('p_calibrated', 0)
    uncert = case_data.get('uncertainty_std', 0)
    true_label = case_data.get('y_true', -1)
    label_text = "MASLD" if true_label == 1 else "Healthy"
    
    st.markdown(f"""
    <div class="premium-card">
        <div style="margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.8rem; font-weight: 700; color: #1a202c; margin: 0 0 0.5rem 0;">
                {case_id}
            </h2>
            {render_risk_badge(risk_band)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk Gauge
    st.markdown("### Risk Level", unsafe_allow_html=True)
    fig_gauge = render_risk_gauge(prob, case_id)
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Uncertainty Meter
    render_uncertainty_meter(uncert)
    
    # Label and Fold
    col1, col2 = st.columns(2)
    with col1:
        label_color = "#FED7D7" if true_label == 1 else "#C6F6D5"
        label_text_color = "#742A2A" if true_label == 1 else "#22543D"
        st.markdown(f"""
        <div style="background: {label_color};
                    padding: 1rem;
                    border-radius: 12px;
                    text-align: center;">
            <div style="font-size: 0.75rem; color: {label_text_color}; margin-bottom: 0.3rem; opacity: 0.8;">True Label</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: {label_text_color};">{label_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        fold = case_data.get('fold', 'N/A')
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E5F5FF 0%, #F0F9FF 100%);
                    padding: 1rem;
                    border-radius: 12px;
                    text-align: center;">
            <div style="font-size: 0.75rem; color: #718096; margin-bottom: 0.3rem; opacity: 0.8;">Fold</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #1a202c;">{fold}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Explainability image
    st.markdown("### Explainability Visualization", unsafe_allow_html=True)
    
    if image_path and image_path.exists():
        zoom_col1, zoom_col2 = st.columns([1, 4])
        with zoom_col1:
            full_width = st.checkbox("Full Width", key=f"zoom_{case_id}")
        
        st.image(str(image_path), use_container_width=full_width)
        
        col1, col2 = st.columns(2)
        with col1:
            with open(image_path, 'rb') as f:
                st.download_button(
                    label="📥 Download Image",
                    data=f.read(),
                    file_name=f"{case_id}.png",
                    mime="image/png",
                    use_container_width=True
                )
    else:
        st.markdown("""
        <div style="background: #f7fafc;
                    border: 2px dashed #cbd5e0;
                    border-radius: 12px;
                    padding: 4rem 2rem;
                    text-align: center;
                    color: #a0aec0;">
            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;">🖼️</div>
            <div style="font-size: 1.1rem; font-weight: 600; color: #718096; margin-bottom: 0.5rem;">
                Explainability Image Not Available
            </div>
            <div style="font-size: 0.9rem; color: #a0aec0;">
                Image would appear here if available
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Notes expander
    with st.expander("📝 Case Summary"):
        st.markdown(f"""
        **Case ID:** {case_id}  
        **Risk Band:** {risk_band}  
        **Calibrated Probability:** {prob:.3f}  
        **Uncertainty:** {uncert:.3f}  
        **True Label:** {label_text}  
        **Fold:** {case_data.get('fold', 'N/A')}
        
        *This summary is for research purposes only. Results should not be used for clinical decision-making.*
        """)
    
    # Download case summary JSON
    st.markdown("<br>", unsafe_allow_html=True)
    case_summary = {
        'case_id': case_id,
        'risk_band': risk_band,
        'calibrated_probability': float(prob),
        'uncertainty_std': float(uncert),
        'true_label': label_text,
        'fold': int(case_data.get('fold', -1))
    }
    json_str = json.dumps(case_summary, indent=2)
    st.download_button(
        label="📥 Download Case Summary (JSON)",
        data=json_str,
        file_name=f"{case_id}_summary.json",
        mime="application/json",
        use_container_width=True
    )
