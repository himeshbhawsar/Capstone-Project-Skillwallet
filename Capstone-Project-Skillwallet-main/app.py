"""
Multimodal Construction Intelligence Platform
Platform ID: 6ac4c98d1dcde6d7857c1642
Skill Wallet Capstone Project 1
Production-Ready Streamlit Application
"""

import os
import json
import io
import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Local Modules
from config import (
    PLATFORM_META,
    AVAILABLE_MODELS,
    LOCATION_TIERS,
    STRUCTURE_TYPES,
    STANDARDS,
    CRACK_TYPES
)
from ai_engine import (
    analyze_ppe_image,
    analyze_crack_image,
    generate_chat_response,
    get_demo_ppe_analysis,
    get_demo_crack_analysis
)
from valuation_engine import (
    calculate_project_valuation,
    generate_architectural_render_url,
    format_inr
)
from weather_engine import (
    WEATHER_PROFILES,
    get_weather_protocol
)
from utils import (
    load_custom_css,
    render_platform_header,
    render_metric_card
)

# Set page configuration
st.set_page_config(
    page_title="Multimodal Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom Industrial Engineering CSS
load_custom_css()

# Session State Initialization
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "👋 Hello Site Team! I am **SiteIntel AI**, your chartered construction engineering assistant. "
                "I am equipped to advise on **IS 456:2000**, **OSHA 1926**, structural crack remediation, "
                "concrete mix designs (M20 to M50), and Indian real estate cost audits. How can I assist you today?"
            )
        }
    ]
if "ppe_results" not in st.session_state:
    st.session_state.ppe_results = None
if "crack_results" not in st.session_state:
    st.session_state.crack_results = None
if "selected_sample_ppe" not in st.session_state:
    st.session_state.selected_sample_ppe = None
if "selected_sample_crack" not in st.session_state:
    st.session_state.selected_sample_crack = None
if "architectural_render_data" not in st.session_state:
    st.session_state.architectural_render_data = None


# ==============================================================================
# SIDEBAR: API KEY, MODEL SELECTION & PLATFORM ARCHITECTURE
# ==============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Engine Configuration")
    
    # API Key Input
    user_key = st.text_input(
        "Google Gemini API Key",
        value=st.session_state.gemini_api_key,
        type="password",
        help="Enter your Google Gemini API Key. If left empty, high-fidelity Demonstration Fallback Mode will activate automatically."
    )
    if user_key != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = user_key
        
    # Execution Mode Indicator
    has_api_key = bool(st.session_state.gemini_api_key.strip())
    demo_mode_toggle = st.toggle("Force Interactive Demo Mode", value=not has_api_key)
    
    effective_demo_mode = demo_mode_toggle or not has_api_key
    
    if effective_demo_mode:
        st.info("💡 **Mode**: Demonstration Fallback Mode (Full interactivity enabled without API key)")
    else:
        st.success("🟢 **Mode**: Live Gemini Multimodal API Active")

    # Model Selection
    selected_model = st.selectbox(
        "Active Multimodal LLM",
        AVAILABLE_MODELS,
        index=0,
        help="Gemini 2.5 Flash offers optimal latency and multimodal reasoning precision."
    )
    
    st.markdown("---")
    
    # Quick Sample Photo Pre-loader
    st.markdown("### 📂 Quick Sample Test Loader")
    st.caption("Test the multimodal engines instantly with pre-packaged construction specimens:")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("👷 Worker PPE Sample", use_container_width=True):
            st.session_state.selected_sample_ppe = "samples/ppe_site_worker.jpg"
            st.toast("Loaded Sample: Worker Scaffolding PPE Site", icon="👷")
    with col_s2:
        if st.button("🧱 Shear Crack Sample", use_container_width=True):
            st.session_state.selected_sample_crack = "samples/concrete_shear_crack.jpg"
            st.toast("Loaded Sample: Structural 45° Shear Crack", icon="🧱")

    st.markdown("---")

    # Architecture Overview
    st.markdown("### 🏛️ Platform Architecture")
    with st.expander("System Specs & Standards", expanded=False):
        st.markdown(f"""
        - **Platform ID**: `{PLATFORM_META['platform_id']}`
        - **Version**: `{PLATFORM_META['version']}`
        - **Safety Codes**: OSHA 1926, IS 2925, IS 3521, IS 15809
        - **Structural Codes**: IS 456:2000, IS 13920, ACI 224R
        - **Costing Engine**: Tier 1/2/3 Indian Metro Benchmarks
        - **Image Synthesis**: Pollinations / Flux 3D Engine
        - **Database**: Zero-dependency stateless cloud architecture
        """)

    st.markdown(
        "<div style='text-align: center; color: #64748B; font-size: 11px; margin-top: 20px;'>"
        "Multimodal Construction Intelligence • Skill Wallet Capstone"
        "</div>",
        unsafe_allow_html=True
    )


# ==============================================================================
# MAIN APPLICATION INTERFACE
# ==============================================================================

# Render Top Banner
render_platform_header()

# Main Navigation Tabs
tab_ppe, tab_crack, tab_valuation, tab_weather = st.tabs([
    "🦺 Site Safety & PPE Audit (Epic 2)",
    "🔬 Crack Diagnostics & Structural Integrity (Epic 2)",
    "📊 Planning & Real Estate Valuation (Epic 3)",
    "🌦️ Daily Site Assistant & Weather Advisory (Epic 5)"
])


# ==============================================================================
# TAB 1: SITE SAFETY & PPE AUDIT (EPIC 2)
# ==============================================================================

with tab_ppe:
    st.markdown("### 🦺 Multimodal PPE Compliance & Workplace Hazard Audit")
    st.caption("Automated visual compliance verification governed by OSHA 1926 and Indian Standard IS 456 / IS 3786 / IS 2925.")
    
    col_upload, col_preview = st.columns([1, 1], gap="medium")
    
    with col_upload:
        st.markdown("#### 1. Upload or Select Site Photo")
        uploaded_ppe_file = st.file_uploader(
            "Upload Construction Site Photo (JPG / PNG)",
            type=["jpg", "jpeg", "png"],
            key="ppe_uploader",
            help="Upload an image showing workers, scaffolding, lifting operations, or site excavations."
        )
        
        # Check if sample was triggered
        active_ppe_image = None
        if uploaded_ppe_file is not None:
            active_ppe_image = Image.open(uploaded_ppe_file)
        elif st.session_state.selected_sample_ppe and os.path.exists(st.session_state.selected_sample_ppe):
            active_ppe_image = Image.open(st.session_state.selected_sample_ppe)
            st.info("📌 Using preloaded sample: **Scaffolding Worker Safety Audit**")

        st.markdown("#### 2. Audit Execution")
        run_audit = st.button("🚀 Run AI Safety & PPE Compliance Audit", key="btn_run_ppe", use_container_width=True)

    with col_preview:
        st.markdown("#### Site Photo Preview")
        if active_ppe_image:
            st.image(active_ppe_image, caption="Active Site Inspection Specimen", use_container_width=True)
        else:
            st.info("👈 Upload a photo or click '**Worker PPE Sample**' in the sidebar to begin.")

    # Execute Analysis
    if run_audit:
        if active_ppe_image is None:
            st.warning("⚠️ Please upload a construction site photo or load a sample first.")
        else:
            with st.spinner("Analyzing worker PPE compliance, safety clearances, and fall risks..."):
                results = analyze_ppe_image(
                    image=active_ppe_image,
                    api_key=st.session_state.gemini_api_key,
                    model_name=selected_model,
                    force_demo=effective_demo_mode
                )
                st.session_state.ppe_results = results
                st.success("✅ Audit completed successfully!")

    # Display Audit Results
    if st.session_state.ppe_results:
        res = st.session_state.ppe_results
        st.markdown("---")
        st.markdown("### 📋 Executive Safety Audit Findings")
        
        # Top KPI Metric Cards
        score = res.get("safety_score", 0)
        status = res.get("overall_status", "UNKNOWN")
        worker_count = res.get("worker_count_detected", 0)
        hazards = res.get("identified_hazards", [])
        
        # Status color
        if score >= 85:
            score_color = "#10B981"
            badge_class = "badge-compliant"
        elif score >= 60:
            score_color = "#F59E0B"
            badge_class = "badge-medium"
        else:
            score_color = "#EF4444"
            badge_class = "badge-critical"

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(render_metric_card(
                "Safety Score",
                f"{score}/100",
                "OSHA / IS Weighting",
                color=score_color
            ), unsafe_allow_html=True)
        with c2:
            st.markdown(render_metric_card(
                "Workers Detected",
                f"{worker_count}",
                "Active in Frame"
            ), unsafe_allow_html=True)
        with c3:
            st.markdown(render_metric_card(
                "Identified Hazards",
                f"{len(hazards)}",
                "Action Items Logged"
            ), unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="site-metric-card">
                <div class="site-metric-label">Overall Site Status</div>
                <div style="margin-top: 8px;">
                    <span class="{badge_class}">{status}</span>
                </div>
                <div class="site-metric-hint">Source: {res.get('_source', 'Gemini Vision')}</div>
            </div>
            """, unsafe_allow_html=True)

        # PPE Detection Checklist Grid
        st.markdown("#### 🛡️ Personal Protective Equipment (PPE) Checklist")
        ppe_data = res.get("ppe_detection", {})
        if ppe_data:
            checklist_cols = st.columns(len(ppe_data))
            for idx, (item_name, item_info) in enumerate(ppe_data.items()):
                with checklist_cols[idx % len(checklist_cols)]:
                    disp_name = item_name.replace("_", " ").title()
                    status_pill = item_info.get("status", "VIOLATION")
                    badge = "badge-compliant" if "COMPLIANT" in status_pill or status_pill == "OK" else "badge-critical"
                    comp_pct = item_info.get("compliance_pct", 0)
                    
                    st.markdown(f"""
                    <div class="site-metric-card" style="padding: 14px;">
                        <div style="font-weight: 700; font-size: 13px; color: #F8FAFC;">{disp_name}</div>
                        <div style="margin: 6px 0;">
                            <span class="{badge}">{status_pill}</span>
                        </div>
                        <div style="font-size: 12px; color: #94A3B8;">
                            Compliance: <b>{comp_pct}%</b> ({item_info.get('detected', 0)}/{item_info.get('total_workers', 0)})
                        </div>
                        <div style="font-size: 10px; color: #64748B; margin-top: 4px;">
                            {item_info.get('standard', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Identified Site Hazards Table
        st.markdown("#### 🚨 Identified Workplace Hazards & Corrective Remedies")
        if hazards:
            hazard_rows = []
            for h in hazards:
                sev = h.get("severity", "Medium")
                badge_style = "badge-critical" if sev == "Critical" else ("badge-high" if sev == "High" else "badge-medium")
                hazard_rows.append({
                    "Severity": sev,
                    "Hazard Description": h.get("hazard", ""),
                    "Location": h.get("location", "Site perimeter"),
                    "Standard Citation": f"{h.get('osha_violation', '')} | {h.get('indian_standard', '')}",
                    "Corrective Action": h.get("corrective_remedy", "")
                })
            
            df_hazards = pd.DataFrame(hazard_rows)
            st.dataframe(
                df_hazards,
                use_container_width=True,
                column_config={
                    "Severity": st.column_config.TextColumn("Severity", width="small"),
                    "Hazard Description": st.column_config.TextColumn("Hazard Description", width="large"),
                    "Location": st.column_config.TextColumn("Location", width="medium"),
                    "Standard Citation": st.column_config.TextColumn("Standard Citation", width="medium"),
                    "Corrective Action": st.column_config.TextColumn("Corrective Action", width="large"),
                },
                hide_index=True
            )

        # Executive Summary
        summary = res.get("executive_summary", "")
        if summary:
            st.info(f"**Site Auditor Executive Note**: {summary}")

        # Download Report Buttons
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            json_str = json.dumps(res, indent=2)
            st.download_button(
                label="📥 Download JSON Audit Report",
                data=json_str,
                file_name="ppe_safety_audit_report.json",
                mime="application/json",
                use_container_width=True
            )
        with col_d2:
            md_report = f"""# CONSTRUCTION PPE & SITE SAFETY AUDIT REPORT
**Platform ID**: {PLATFORM_META['platform_id']}  
**Overall Status**: {status}  
**Safety Score**: {score}/100  
**Workers Detected**: {worker_count}  

## Identified Hazards & Actions
"""
            for h in hazards:
                md_report += f"\n- **[{h.get('severity', '').upper()}]** {h.get('hazard', '')}\n  - Location: {h.get('location', '')}\n  - Regulation: {h.get('osha_violation', '')} / {h.get('indian_standard', '')}\n  - Remedy: {h.get('corrective_remedy', '')}\n"
            st.download_button(
                label="📄 Download Formatted Markdown Report",
                data=md_report,
                file_name="ppe_safety_audit_summary.md",
                mime="text/markdown",
                use_container_width=True
            )


# ==============================================
# TAB 2: CRACK DIAGNOSTICS & STRUCTURAL INTEGRITY
# ==============================================

with tab_crack:
    st.markdown("### 🔬 Concrete Crack Diagnostics & Structural Integrity Assessment")
    st.caption("Multimodal concrete defect classification, crack width estimation, root-cause forensics, and repair specifications (IS 456 / ACI 224R).")
    
    col_c_upload, col_c_preview = st.columns([1, 1], gap="medium")
    
    with col_c_upload:
        st.markdown("#### 1. Upload Concrete / Masonry Image")
        uploaded_crack_file = st.file_uploader(
            "Upload Concrete Surface Photo (JPG / PNG)",
            type=["jpg", "jpeg", "png"],
            key="crack_uploader",
            help="Upload high-resolution photo of beam, column, slab, or masonry fracture."
        )
        
        active_crack_image = None
        if uploaded_crack_file is not None:
            active_crack_image = Image.open(uploaded_crack_file)
        elif st.session_state.selected_sample_crack and os.path.exists(st.session_state.selected_sample_crack):
            active_crack_image = Image.open(st.session_state.selected_sample_crack)
            st.info("📌 Using preloaded sample: **45° Structural Shear Fracture**")

        st.markdown("#### 2. Diagnostic Execution")
        run_crack_diag = st.button("🔬 Run AI Structural Crack Diagnostics", key="btn_run_crack", use_container_width=True)

    with col_c_preview:
        st.markdown("#### Specimen Photo Preview")
        if active_crack_image:
            st.image(active_crack_image, caption="Active Concrete Specimen", use_container_width=True)
        else:
            st.info("👈 Upload a photo or click '**Shear Crack Sample**' in the sidebar to begin.")

    # Execute Crack Analysis
    if run_crack_diag:
        if active_crack_image is None:
            st.warning("⚠️ Please upload a concrete surface photo or load a sample first.")
        else:
            with st.spinner("Classifying concrete defect, measuring fracture geometry, and checking IS 456 limits..."):
                c_results = analyze_crack_image(
                    image=active_crack_image,
                    api_key=st.session_state.gemini_api_key,
                    model_name=selected_model,
                    force_demo=effective_demo_mode
                )
                st.session_state.crack_results = c_results
                st.success("✅ Diagnostic assessment completed!")

    # Display Diagnostic Findings
    if st.session_state.crack_results:
        c_res = st.session_state.crack_results
        st.markdown("---")
        st.markdown("### 📋 Forensic Structural Assessment")
        
        defect = c_res.get("defect_type", "Structural Crack")
        conf = c_res.get("confidence_score", 0.90) * 100
        sev = c_res.get("severity_level", "Medium")
        urgency = c_res.get("urgency_rating", "Monitor")
        width_mm = c_res.get("estimated_crack_width_mm", "2.0 mm")
        cost_inr = c_res.get("estimated_repair_cost_inr", "₹50,000")
        
        badge_style = "badge-critical" if sev == "Critical" else ("badge-high" if sev == "High" else "badge-medium")

        # Top Diagnostic Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(render_metric_card("Defect Classification", defect, f"Confidence: {conf:.1f}%"), unsafe_allow_html=True)
        with m2:
            st.markdown(render_metric_card("Estimated Crack Width", width_mm, "IS 456 Max Limit: 0.3mm", color="#EF4444"), unsafe_allow_html=True)
        with m3:
            st.markdown(render_metric_card("Est. Repair Cost (INR)", cost_inr, "Labor + Chemical Grout"), unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="site-metric-card">
                <div class="site-metric-label">Urgency Rating</div>
                <div style="margin-top: 8px;">
                    <span class="{badge_style}">{sev.upper()} SEVERITY</span>
                </div>
                <div class="site-metric-hint">{urgency}</div>
            </div>
            """, unsafe_allow_html=True)

        # Geometric & Physical Characteristics
        st.markdown("#### 📐 Fracture Characteristics & Depth Profile")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown(f"""
            <div class="eng-card">
                <div style="color: #94A3B8; font-size: 12px; text-transform: uppercase; font-weight: 600;">Crack Orientation & Propagation</div>
                <div style="color: #F8FAFC; font-size: 15px; margin-top: 8px;">{c_res.get('orientation_propagation', 'Diagonal shear trajectory')}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_g2:
            st.markdown(f"""
            <div class="eng-card">
                <div style="color: #94A3B8; font-size: 12px; text-transform: uppercase; font-weight: 600;">Depth & Rebar Penetration</div>
                <div style="color: #F8FAFC; font-size: 15px; margin-top: 8px;">{c_res.get('crack_depth_estimate', 'Through-member fracture')}</div>
            </div>
            """, unsafe_allow_html=True)

        # Root Causes
        st.markdown("#### 🔍 Forensic Root Cause Hypotheses")
        causes = c_res.get("root_causes", [])
        for c in causes:
            st.markdown(f"- ⚠️ **{c}**")

        # Repair Protocol
        st.markdown("#### 🛠️ Recommended Engineering Repair Protocol")
        repair_steps = c_res.get("engineering_repair_protocol", [])
        for step in repair_steps:
            st.markdown(f"1. {step}")

        # Citation
        citation = c_res.get("is_456_citation", "IS 456:2000 Clause 40")
        st.info(f"🏛️ **Regulatory Standard Reference**: {citation}")

        # Download Report
        col_cd1, col_cd2 = st.columns(2)
        with col_cd1:
            st.download_button(
                label="📥 Download Crack Diagnostic JSON",
                data=json.dumps(c_res, indent=2),
                file_name="structural_crack_diagnostic_report.json",
                mime="application/json",
                use_container_width=True
            )
        with col_cd2:
            diag_summary = f"""# STRUCTURAL CONCRETE CRACK FORENSIC REPORT
**Defect Classification**: {defect}  
**Severity**: {sev}  
**Urgency**: {urgency}  
**Estimated Crack Width**: {width_mm}  
**Repair Estimate**: {cost_inr}  
**Code Reference**: {citation}  

## Repair Protocol:
""" + "\n".join([f"- {s}" for s in repair_steps])
            st.download_button(
                label="📄 Download Diagnostic Summary",
                data=diag_summary,
                file_name="structural_crack_summary.md",
                mime="text/markdown",
                use_container_width=True
            )


# ==============================================================================
# TAB 3: PLANNING & REAL ESTATE VALUATION (EPIC 3)
# ==============================================================================

with tab_valuation:
    st.markdown("### 📊 Construction Cost Planning & Real Estate Valuation (INR)")
    st.caption("Financial decision support: CapEx tracking, valuation forecasting, material consumption benchmarks, and 3D architectural AI rendering.")
    
    # Input Parameters
    st.markdown("#### 🏗️ Project Parameters & Site Geometry")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        v_structure = st.selectbox("Structure Type", STRUCTURE_TYPES, index=0)
        v_tier = st.selectbox("Location Tier", list(LOCATION_TIERS.keys()), index=0)
    with col_p2:
        v_sqft = st.number_input(
            "Built-up Area (Sq. Ft)",
            min_value=1000,
            max_value=1_000_000,
            value=45000,
            step=2500,
            help="Total built-up gross floor area including stilt/basements."
        )
        v_grade = st.selectbox(
            "Specification Grade",
            ["Budget / Standard", "Premium Quality", "Ultra-Luxury / High-Rise"],
            index=1
        )
    with col_p3:
        v_completion = st.slider(
            "Current Milestone Completion (%)",
            min_value=0,
            max_value=100,
            value=48,
            step=1,
            help="Percentage of construction works completed to date."
        )
        st.markdown(f"**Stage**: {'Early Substructure' if v_completion < 20 else ('Superstructure RCC' if v_completion < 65 else ('Finishing & Commissioning' if v_completion < 95 else 'Ready for Handover'))}")

    # Compute Project Valuation
    v_data = calculate_project_valuation(
        structure_type=v_structure,
        built_up_sqft=v_sqft,
        location_tier_name=v_tier,
        specification_grade=v_grade,
        completion_percentage=v_completion
    )

    st.markdown("---")
    st.markdown("#### 💰 Financial Valuation & CapEx Metrics (INR)")
    
    # Financial KPI Cards
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(render_metric_card(
            "Total Construction Budget",
            v_data["total_construction_budget_formatted"],
            f"@{format_inr(v_data['rate_per_sqft'])} / sq.ft"
        ), unsafe_allow_html=True)
    with f2:
        st.markdown(render_metric_card(
            "CapEx Incurred to Date",
            v_data["capex_incurred_formatted"],
            f"{v_completion}% Works Certified",
            color="#F59E0B"
        ), unsafe_allow_html=True)
    with f3:
        st.markdown(render_metric_card(
            "Remaining Cost to Complete",
            v_data["cost_to_complete_formatted"],
            f"{100 - v_completion}% Outstanding Work"
        ), unsafe_allow_html=True)

    f4, f5, f6 = st.columns(3)
    with f4:
        st.markdown(render_metric_card(
            "Current Asset Valuation",
            v_data["current_asset_valuation_formatted"],
            "Land Equity + Work-in-Progress",
            color="#10B981"
        ), unsafe_allow_html=True)
    with f5:
        st.markdown(render_metric_card(
            "Projected GDV (Completion)",
            v_data["projected_gdv_formatted"],
            f"Gross Development Value @ {format_inr(v_data['sale_rate_sqft'])}/sqft"
        ), unsafe_allow_html=True)
    with f6:
        st.markdown(render_metric_card(
            "Unrealized Equity Value",
            v_data["unrealized_equity_formatted"],
            "Current Value Minus CapEx Invested",
            color="#3B82F6"
        ), unsafe_allow_html=True)

    # Interactive Charts
    st.markdown("---")
    st.markdown("#### 📈 Financial Trajectory & Milestone Cost Allocation")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Donut Chart: Milestone Cost Distribution
        ms_labels = [m["stage"] for m in v_data["milestones"]]
        ms_values = [m["budget_inr"] for m in v_data["milestones"]]
        
        fig_donut = px.pie(
            names=ms_labels,
            values=ms_values,
            hole=0.45,
            title="Budget Allocation by Construction Stage",
            color_discrete_sequence=px.colors.sequential.Sunsetdark
        )
        fig_donut.update_layout(
            template="plotly_dark",
            margin=dict(t=40, b=20, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_chart2:
        # Valuation Trajectory over Completion Curve
        percentages = list(range(0, 101, 10))
        capex_curve = [v_data["total_construction_budget"] * (p / 100.0) / 10_000_000 for p in percentages]
        val_curve = [
            ((v_data["imputed_land_value"] + (v_data["total_construction_budget"] * (p / 100.0) * 1.25)) * (0.85 + 0.15 * (p / 100.0))) / 10_000_000
            for p in percentages
        ]
        
        fig_traj = go.Figure()
        fig_traj.add_trace(go.Scatter(
            x=percentages, y=val_curve,
            mode='lines+markers',
            name='Asset Valuation (Cr)',
            line=dict(color='#10B981', width=3)
        ))
        fig_traj.add_trace(go.Scatter(
            x=percentages, y=capex_curve,
            mode='lines',
            name='Cumulative CapEx (Cr)',
            line=dict(color='#F59E0B', width=2, dash='dot')
        ))
        fig_traj.add_vline(x=v_completion, line_width=2, line_dash="dash", line_color="#EF4444", annotation_text=f"Current ({v_completion}%)")
        fig_traj.update_layout(
            title="Valuation vs CapEx Incurred Trajectory (₹ Crores)",
            xaxis_title="Construction Completion (%)",
            yaxis_title="Value in ₹ Crores",
            template="plotly_dark",
            margin=dict(t=40, b=20, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_traj, use_container_width=True)

    # Material Requirement Estimation (IS 456 Benchmarks)
    st.markdown("---")
    st.markdown("#### 🧱 Material Consumption Estimates (IS 456 Norms)")
    mats = v_data["materials"]
    
    mat1, mat2, mat3, mat4, mat5 = st.columns(5)
    with mat1:
        st.markdown(render_metric_card("Structural Steel", f"{mats['steel_mt']:,.1f} MT", "Fe500D Reinforcement"), unsafe_allow_html=True)
    with mat2:
        st.markdown(render_metric_card("Cement", f"{mats['cement_bags']:,} Bags", f"~{mats['cement_mt']:,.1f} MT (PPC/OPC)"), unsafe_allow_html=True)
    with mat3:
        st.markdown(render_metric_card("M-Sand", f"{mats['sand_cum']:,.0f} m³", f"{mats['sand_cft']:,.0f} CFT"), unsafe_allow_html=True)
    with mat4:
        st.markdown(render_metric_card("Coarse Aggregate", f"{mats['coarse_agg_cum']:,.0f} m³", "20mm & 10mm Stone"), unsafe_allow_html=True)
    with mat5:
        st.markdown(render_metric_card("Water Requirement", f"{mats['water_kl']:,.0f} kL", "Mixing & 28-day Curing"), unsafe_allow_html=True)

    # Milestone Stages Table
    st.markdown("---")
    st.markdown("#### 🏗️ Milestone Construction Stages & Progress")
    ms_table = []
    for ms in v_data["milestones"]:
        ms_table.append({
            "Milestone Stage": ms["stage"],
            "Budget Share": f"{ms['share_pct']}%",
            "Allocated Budget": ms["budget_formatted"],
            "Spent to Date": ms["spent_formatted"],
            "Stage Progress": f"{ms['progress_pct']}%",
            "Status": ms["status"],
            "Scope Description": ms["description"]
        })
    df_ms = pd.DataFrame(ms_table)
    st.dataframe(df_ms, use_container_width=True, hide_index=True)

    # 3D Architectural AI Rendering Generator
    st.markdown("---")
    st.markdown("#### 🖼️ Conceptual 3D Architectural AI Rendering (Pollinations Engine)")
    st.caption("Generate instant photorealistic architectural concept visualisations based on project type and aesthetic parameters.")
    
    col_r_opt, col_r_btn = st.columns([2, 1])
    with col_r_opt:
        arch_style = st.selectbox(
            "Architectural Aesthetic Style",
            [
                "Futuristic Modern Biophilic with Hanging Gardens & Glass",
                "Brutalist Exposed Architectural Concrete & Bronze Finishes",
                "Contemporary Indo-Modern Luxury with Terracotta Louvers",
                "Minimalist Glass Curtain High-Rise with Kinetic Facade",
                "Industrial Loft Steel & Glass Frame with Atrium"
            ],
            index=0
        )
    with col_r_btn:
        st.write("")
        st.write("")
        gen_render_btn = st.button("🎨 Generate 3D Concept Render", use_container_width=True)

    if gen_render_btn or st.session_state.architectural_render_data is None:
        render_payload = generate_architectural_render_url(
            structure_type=v_structure,
            architectural_style=arch_style,
            location_tier=v_tier
        )
        st.session_state.architectural_render_data = render_payload

    if st.session_state.architectural_render_data:
        r_data = st.session_state.architectural_render_data
        st.image(
            r_data["image_url"],
            caption=f"AI Architectural Concept: {v_structure} ({arch_style})",
            use_container_width=True
        )
        with st.expander("🔍 View AI Synthesis Prompt"):
            st.code(r_data["prompt"])


# ==============================================================================
# TAB 4: DAILY SITE ASSISTANT & WEATHER-AWARE ADVISORY (EPIC 5)
# ==============================================================================

with tab_weather:
    st.markdown("### 🌦️ Daily Weather-Aware Site Advisory & Engineering Chatbot")
    st.caption("Real-time weather mitigation protocols, crane operational limits, IS 456 concreting precautions, and multi-turn engineering assistant.")
    
    col_w_sel, col_w_card = st.columns([1, 2], gap="large")
    
    with col_w_sel:
        st.markdown("#### 1. Select Prevailing Site Weather")
        weather_choice = st.selectbox(
            "Weather Condition Selector",
            list(WEATHER_PROFILES.keys()),
            index=1,
            help="Select the current site weather condition to load calibrated safety protocols."
        )
        protocol = get_weather_protocol(weather_choice)
        
        st.markdown(f"""
        <div style="background: {protocol['bg_color']}; border: 1px solid {protocol['badge_color']}; border-radius: 12px; padding: 18px; margin-top: 14px;">
            <div style="color: {protocol['badge_color']}; font-weight: 800; font-size: 13px; text-transform: uppercase;">
                {protocol['status_level']}
            </div>
            <div style="color: #F8FAFC; font-size: 14px; margin-top: 8px;">
                Wind Speed Range: <b>{protocol['wind_speed_range']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_w_card:
        st.markdown("#### 2. Actionable Operational Directives")
        
        tab_crane, tab_height, tab_concrete, tab_elec = st.tabs([
            "🏗️ Crane & Lifting",
            "🪜 Scaffolding & Height",
            "🧱 Concrete (IS 456/7861)",
            "⚡ Electrical Safety"
        ])
        
        with tab_crane:
            st.markdown(f"**Status**: `{protocol['crane_status']}`")
            st.markdown(protocol['crane_details'])
            st.caption("Standard: OSHA 1926.1400 Cranes and Derricks in Construction")
            
        with tab_height:
            st.markdown(f"**Status**: `{protocol['height_work_status']}`")
            st.markdown(protocol['height_work_details'])
            st.caption("Standard: OSHA 1926.451 / IS 2750 Steel Scaffoldings")
            
        with tab_concrete:
            st.markdown("**Concreting & Curing Protocol**:")
            st.markdown(protocol['concrete_protocol'])
            st.caption("Standard: IS 456:2000 & IS 7861 (Part 1 Extreme Hot Weather, Part 2 Cold Weather)")
            
        with tab_elec:
            st.markdown("**Electrical & Trench Mitigation**:")
            st.markdown(protocol['electrical_safety'])
            st.caption("Standard: OSHA 1926.404 / 30mA ELCB Protection")

    # Pre-Shift Supervisor Checklist
    st.markdown("---")
    st.markdown("#### ✅ Pre-Shift Site Supervisor Safety Checklist")
    chk_cols = st.columns(2)
    completed_checks = []
    for idx, item in enumerate(protocol["checklist"]):
        col_target = chk_cols[idx % 2]
        with col_target:
            checked = st.checkbox(f"**Item {idx+1}**: {item}", key=f"chk_{weather_choice}_{idx}")
            if checked:
                completed_checks.append(item)
                
    if st.button("📋 Export Daily Shift Safety Briefing Log"):
        log_text = f"""=======================================================
DAILY SITE SAFETY BRIEFING LOG & WEATHER PROTOCOL
=======================================================
Weather Condition: {weather_choice}
Status Level: {protocol['status_level']}
Platform ID: {PLATFORM_META['platform_id']}

COMPLETED SUPERVISOR CHECKS:
""" + "\n".join([f"[X] {c}" for c in completed_checks]) + "\n\nPending Checks:\n" + "\n".join([f"[ ] {c}" for c in protocol["checklist"] if c not in completed_checks])
        
        st.download_button(
            label="📥 Download Signed Shift Log (.txt)",
            data=log_text,
            file_name="daily_site_safety_briefing_log.txt",
            mime="text/plain"
        )
        st.success(f"Verified {len(completed_checks)} of {len(protocol['checklist'])} checks.")

    # Multi-Turn Construction Assistant Chatbot
    st.markdown("---")
    st.markdown("### 💬 SiteIntel AI: Construction Engineering Assistant")
    st.caption("Interactive multi-turn engineering advisor powered by Gemini multimodal civil knowledge base.")
    
    # Prompt Chip Shortcuts
    st.markdown("**Quick Technical Inquiries:**")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    quick_query = None
    with q_col1:
        if st.button("📐 IS 456 Concrete Cover", use_container_width=True):
            quick_query = "What are the IS 456 concrete cover requirements for mild, moderate, and severe exposure?"
    with q_col2:
        if st.button("🦺 OSHA Fall Protection", use_container_width=True):
            quick_query = "Explain OSHA 1926.502 personal fall arrest system (safety harness) requirements and anchor ratings."
    with q_col3:
        if st.button("🌡️ Hot Weather Concreting", use_container_width=True):
            quick_query = "How does high ambient temperature affect M30 concrete slump and what are IS 7861 curing guidelines?"
    with q_col4:
        if st.button("🛑 Stop-Work Notice Draft", use_container_width=True):
            quick_query = "Draft a formal Stop-Work Notice for an unsafe scaffolding tier missing safety harnesses."

    # Render Chat History
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # User Chat Input
    user_prompt = st.chat_input("Ask about IS 456, OSHA standards, concrete mix design, crack repairs, or cost estimation...")
    active_prompt = quick_query if quick_query else user_prompt

    if active_prompt:
        # Append User Message
        st.session_state.chat_messages.append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)

        # Generate Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing civil engineering regulations and project parameters..."):
                resp = generate_chat_response(
                    messages=st.session_state.chat_messages,
                    api_key=st.session_state.gemini_api_key,
                    model_name=selected_model,
                    force_demo=effective_demo_mode
                )
                st.markdown(resp)
                st.session_state.chat_messages.append({"role": "assistant", "content": resp})

    # Clear chat option
    if len(st.session_state.chat_messages) > 1:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_messages = [st.session_state.chat_messages[0]]
            st.rerun()
