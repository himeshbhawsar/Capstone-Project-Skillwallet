"""
UI Styling, Image Utilities, and Report Exporters
"""

import streamlit as st
import json
import base64
from io import BytesIO
from PIL import Image

def load_custom_css():
    """Injects high-end, responsive industrial engineering design aesthetics."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    /* Global Typography & Palette */
    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    code, pre, .font-mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1300px !important;
    }

    /* Header Banner Styling */
    .platform-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 20px -5px rgba(245, 158, 11, 0.15);
        position: relative;
        overflow: hidden;
    }

    .platform-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(180deg, #F59E0B 0%, #EF4444 100%);
    }

    .platform-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .platform-subtitle {
        color: #94A3B8;
        font-size: 14px;
        margin-top: 6px;
        margin-bottom: 0;
    }

    .meta-tag {
        display: inline-block;
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Metric Cards */
    .metric-card-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 20px;
    }

    .site-metric-card {
        background: rgba(30, 41, 59, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 20px;
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .site-metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(245, 158, 11, 0.4);
        box-shadow: 0 8px 20px -6px rgba(0, 0, 0, 0.4);
    }

    .site-metric-label {
        font-size: 12px;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .site-metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.2;
    }

    .site-metric-hint {
        font-size: 11px;
        color: #64748B;
        margin-top: 4px;
    }

    /* Status Badges */
    .badge-critical {
        background: rgba(239, 68, 68, 0.2);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .badge-high {
        background: rgba(249, 115, 22, 0.2);
        color: #FB923C;
        border: 1px solid rgba(249, 115, 22, 0.4);
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .badge-medium {
        background: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .badge-compliant {
        background: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Tab Custom Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 14px;
        padding: 0 16px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(239, 68, 68, 0.15) 100%) !important;
        color: #FBBF24 !important;
        border: 1px solid rgba(245, 158, 11, 0.35) !important;
    }

    /* Engineering Card */
    .eng-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }

    /* Table styling */
    .table-responsive {
        width: 100%;
        overflow-x: auto;
    }

    /* Button accents */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: #0F172A;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        transition: all 0.2s ease;
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%);
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.35);
        transform: translateY(-1px);
        color: #0F172A;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_platform_header():
    """Renders top hero banner."""
    header_html = """
    <div class="platform-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <h1 class="platform-title">
                    <span>🏗️ Multimodal Construction Intelligence Platform</span>
                </h1>
                <p class="platform-subtitle">
                    Safety PPE Audits (OSHA / IS 456) • Concrete Structural Crack Diagnostics • INR Valuation & CapEx Engine • Weather Risk Advisory
                </p>
            </div>
            <div style="text-align: right;">
                <span class="meta-tag">Platform ID: 6ac4c98d1dcde6d7857c1642</span>
                <div style="color: #64748B; font-size: 11px; margin-top: 4px; font-weight: 500;">
                    Skill Wallet Capstone Project 1 • Production Ready v2.4
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, hint: str = "", delta: str = None, color: str = None):
    """HTML metric card snippet."""
    val_style = f"color: {color};" if color else ""
    hint_html = f'<div class="site-metric-hint">{hint}</div>' if hint else ""
    return f"""
    <div class="site-metric-card">
        <div class="site-metric-label">{label}</div>
        <div class="site-metric-value" style="{val_style}">{value}</div>
        {hint_html}
    </div>
    """

def image_to_base64(image: Image.Image) -> str:
    """Converts PIL image to base64 string for embedding."""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()
