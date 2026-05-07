
import os
import json
import time
import glob
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_extras.metric_cards import style_metric_cards
from PIL import Image
import html

from agent_engine import ReceiptAgent

APP_VERSION = "3.2.9"
DEFAULT_DATA_PATH = "D:/Agentic_OCR/data/sroie"
DEFAULT_REPORT_PATH = "D:/Agentic_OCR/master_report.csv"
DEFAULT_LOG_PATH = "D:/Agentic_OCR/agent_trace.log"
DEFAULT_ORGANIZED_PATH = "D:/Agentic_OCR/organized_receipts"
HISTORY_FILE = "D:/Agentic_OCR/run_history.json"

st.set_page_config(
    page_title="Neural OCR | Premium Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;800&family=Manrope:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

    /* UNIVERSAL STYLES */
    * {
        font-family: 'Manrope', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: 0.02em;
        font-weight: 800;
    }

    code {
        font-family: 'JetBrains Mono', monospace;
    }

    /* LIGHT THEME (Default) - Clean & Bright */
    :root {
        --bg-primary: #f5f3ee;
        --bg-secondary: #ebe7de;
        --text-primary: #0f0d0a;
        --button-text: #0f0d0a;
        --text-secondary: #3a3530;
        --accent-1: #a0684e;
        --accent-2: #6d8b6f;
        --accent-3: #d4ad80;
        --success: #2d5a38;
        --danger: #8b2e2b;
        --warning: #b87a04;
        --border: rgba(45, 42, 34, 0.2);
        --input-bg: #ffffff;
        --input-text: #0f0d0a;
        --card-bg: rgba(255, 255, 255, 0.95);
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    }

    #MainMenu {
        display: none !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    body, p, span, div, label {
        color: var(--text-primary) !important;
    }

    /* Keep toolbar for sidebar toggle */
    [data-testid="stToolbar"] {
        display: flex !important;
        background: transparent !important;
    }

    [data-testid="stToolbar"] button {
        background: linear-gradient(135deg, rgba(208,163,118,0.9), rgba(160,104,78,0.9)) !important;
        color: #ffffff !important;
        border: 2px solid rgba(160, 104, 78, 0.5) !important;
        fill: #000000 !important;
    }

    [data-testid="stToolbar"] button:hover {
        background: linear-gradient(135deg, rgba(208,163,118,1), rgba(160,104,78,1)) !important;
        box-shadow: 0 4px 12px rgba(160, 104, 78, 0.3) !important;
    }

    [data-testid="stToolbar"] button svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    /* Shared button feel for all interactive controls */
    .stButton > button,
    [data-testid="stToolbar"] button,
    button[data-testid="stDownloadButton"],
    .stExpander button,
    [data-testid="stExpander"] button,
    button[aria-label*="fullscreen"],
    button[aria-label*="expand"],
    button[title*="fullscreen"],
    button[title*="expand"],
    .vega-embed button,
    .plotly-graph-div button {
        cursor: pointer !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease, background 0.18s ease !important;
        transform: translateY(0);
        will-change: transform;
        border-radius: 12px !important;
    }

    .stButton > button:hover,
    [data-testid="stToolbar"] button:hover,
    button[data-testid="stDownloadButton"]:hover,
    .stExpander button:hover,
    [data-testid="stExpander"] button:hover,
    button[aria-label*="fullscreen"]:hover,
    button[aria-label*="expand"]:hover,
    button[title*="fullscreen"]:hover,
    button[title*="expand"]:hover,
    .vega-embed button:hover,
    .plotly-graph-div button:hover {
        transform: translateY(-1px) scale(1.01);
        filter: brightness(1.05);
    }

    .stButton > button:active,
    [data-testid="stToolbar"] button:active,
    button[data-testid="stDownloadButton"]:active,
    .stExpander button:active,
    [data-testid="stExpander"] button:active,
    button[aria-label*="fullscreen"]:active,
    button[aria-label*="expand"]:active,
    button[title*="fullscreen"]:active,
    button[title*="expand"]:active,
    .vega-embed button:active,
    .plotly-graph-div button:active {
        transform: translateY(1px) scale(0.99);
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.14) !important;
    }

    .stButton > button:focus-visible,
    [data-testid="stToolbar"] button:focus-visible,
    button[data-testid="stDownloadButton"]:focus-visible,
    .stExpander button:focus-visible,
    [data-testid="stExpander"] button:focus-visible,
    button[aria-label*="fullscreen"]:focus-visible,
    button[aria-label*="expand"]:focus-visible,
    button[title*="fullscreen"]:focus-visible,
    button[title*="expand"]:focus-visible,
    .vega-embed button:focus-visible,
    .plotly-graph-div button:focus-visible {
        outline: 3px solid rgba(245, 236, 224, 0.9) !important;
        outline-offset: 2px !important;
    }

    .stButton > button:disabled,
    [data-testid="stToolbar"] button:disabled,
    button[data-testid="stDownloadButton"]:disabled,
    .stExpander button:disabled,
    [data-testid="stExpander"] button:disabled,
    button[aria-label*="fullscreen"]:disabled,
    button[aria-label*="expand"]:disabled,
    button[title*="fullscreen"]:disabled,
    button[title*="expand"]:disabled,
    .vega-embed button:disabled,
    .plotly-graph-div button:disabled {
        cursor: not-allowed !important;
        opacity: 0.6 !important;
        transform: none !important;
    }

    /* Hide specific toolbar items but keep sidebar toggle */
    button[kind="header"] {
        display: none !important;
    }

    /* DARK THEME */
    [data-theme="dark"], [data-theme="dark"] body, [data-theme="dark"] .stApp {
        --bg-primary: #0f0d0a;
        --bg-secondary: #1a1714;
        --text-primary: #f5f3ee;
        --button-text: #f5f3ee;
        --text-secondary: #d4cfc3;
        --accent-1: #d9a66f;
        --accent-2: #8fb398;
        --accent-3: #f0d9b5;
        --success: #5fa368;
        --danger: #d4615f;
        --warning: #e6c228;
        --border: rgba(245, 243, 238, 0.2);
        --input-bg: #2d2a22;
        --input-text: #f5f3ee;
        --card-bg: rgba(45, 42, 34, 0.95);
    }

    [data-theme="dark"] {
        background: linear-gradient(135deg, #0f0d0a 0%, #1a1714 100%);
    }

    [data-theme="dark"] body, [data-theme="dark"] p, [data-theme="dark"] span, [data-theme="dark"] div, [data-theme="dark"] label {
        color: #f5f3ee !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-primary) 0%, var(--accent-3) 100%);
        border-right: 2px solid var(--border);
    }

    [data-theme="dark"] section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, #3a3530 100%);
    }

    .hero-card {
        background: linear-gradient(135deg, var(--accent-3) 0%, var(--accent-1) 100%);
        border: 3px solid var(--accent-1);
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 24px 64px rgba(0, 0, 0, 0.18);
        animation: slideInDown 0.6s ease-out;
    }

    .hero-card h1, .hero-card h2, .hero-card p {
        color: #0f0d0a !important;
        text-shadow: 0 2px 4px rgba(255, 255, 255, 0.4);
    }

    .hero-card h1 { font-size: 2.8rem; margin-bottom: 0.5rem; }

    @keyframes slideInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .metric-card {
        background: var(--card-bg);
        border: 3px solid var(--accent-2);
        border-radius: 18px;
        padding: 1.5rem;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.12);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.5s ease-out;
    }

    @keyframes floatUp {
        0% { opacity: 0; transform: translateY(20px) scale(0.97); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    .glass-panel,
    .metric-card,
    .stDataFrame,
    [data-testid="stMetric"],
    .stAlert,
    .stVegaLiteChart,
    .stPlotlyChart,
    .stImage,
    .stTabs [role="tab"] {
        animation: floatUp 520ms ease both;
    }

    .stButton > button {
        animation: floatUp 420ms ease both;
    }

    .metric-card:hover {
        border-color: var(--accent-1);
        transform: translateY(-6px);
        box-shadow: 0 20px 48px rgba(0, 0, 0, 0.16);
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.92); }
        to { opacity: 1; transform: scale(1); }
    }

    .glass-panel {
        background: var(--card-bg);
        border: 3px solid var(--border);
        border-radius: 18px;
        padding: 2rem;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.1);
    }

    .status-badge {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        border-radius: 14px;
        font-size: 0.9rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        border: 2px solid;
        text-transform: uppercase;
    }

    .badge-verified {
        background: rgba(61, 107, 71, 0.2);
        color: var(--success);
        border-color: var(--success);
    }

    .badge-pending {
        background: rgba(200, 154, 14, 0.2);
        color: var(--warning);
        border-color: var(--warning);
    }

    .badge-error {
        background: rgba(155, 56, 53, 0.2);
        color: var(--danger);
        border-color: var(--danger);
    }

    /* BUTTONS - BRILLIANT & ACCESSIBLE */
    .stButton > button {
        border-radius: 14px;
        border: 3px solid rgba(0,0,0,0.06);
        background: linear-gradient(135deg, rgba(208,163,118,1) 0%, rgba(160,104,78,1) 100%);
        color: var(--button-text) !important;
        font-weight: 800;
        letter-spacing: 0.03em;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        text-transform: none;
        font-size: 0.98rem;
        line-height: 1.25;
        min-height: 44px;
        padding: 0.7rem 1.4rem;
        box-shadow: 0 10px 30px rgba(160,104,78,0.18), inset 0 1px 0 rgba(255,255,255,0.08);
        backdrop-filter: blur(6px);
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }

    /* Dark theme buttons: slightly lighter accent with white text */
    [data-theme="dark"] .stButton > button {
        background: linear-gradient(135deg, rgba(240,217,181,1) 0%, rgba(217,166,111,1) 100%);
        color: #1a1512 !important;
        box-shadow: 0 10px 28px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.03);
    }

    .stButton > button:hover {
        transform: translateY(-4px);
        box-shadow: 0 22px 48px rgba(160,104,78,0.32);
        filter: saturate(1.08) brightness(1.02);
    }

    .stButton > button:active {
        transform: translateY(-1px) scale(0.998);
    }

    /* SELECT / DROPDOWN */
    .stSelectbox > div > div > select,
    .stSelectbox > div > div > div {
        background: linear-gradient(180deg, var(--input-bg), rgba(255,255,255,0.96)) !important;
        color: var(--input-text) !important;
        border: 2px solid rgba(0,0,0,0.06) !important;
        border-radius: 10px !important;
        padding: 0.6rem 0.9rem !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
        min-height: 40px !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06) !important;
    }

    /* Force dropdown list panels and options to inherit theme colors and remain readable */
    div[role="listbox"], ul[role="listbox"], div[role="option"], li[role="option"], select, option {
        background: var(--card-bg) !important;
        color: var(--input-text) !important;
        border-color: var(--border) !important;
        line-height: 1.25 !important;
    }

    /* Specific Streamlit popover/listbox containers */
    .stSelectbox [role="listbox"], .stMultiSelect [role="listbox"], .stRadio [role="listbox"], .stCheckbox [role="listbox"] {
        background: var(--card-bg) !important;
        color: var(--input-text) !important;
    }

    /* Ensure option highlight has clear contrast */
    .stSelectbox [role="option"]:hover, .stSelectbox [role="option"][aria-selected="true"], .stMultiSelect [role="option"][aria-selected="true"] {
        background: linear-gradient(90deg, rgba(160,104,78,0.14), rgba(109,139,111,0.06)) !important;
        color: var(--text-primary) !important;
    }

    [data-theme="dark"] .stSelectbox > div > div > select,
    [data-theme="dark"] .stSelectbox > div > div > div {
        background: linear-gradient(180deg, var(--input-bg), rgba(45,42,34,0.96)) !important;
        color: var(--input-text) !important;
        border: 2px solid rgba(255,255,255,0.04) !important;
    }

    /* Ensure option text visible in native selects */
    select option { color: inherit; background: inherit; }

    /* Give the caret / arrow a contrasting color */
    .stSelectbox select::-ms-expand { color: var(--accent-1); }
    .stSelectbox select { appearance: none; -webkit-appearance:none; -moz-appearance:none; }

    /* FORCE CONTRAST FOR ALL INTERACTIVE CONTROLS */
    .stApp button, .stApp select, .stApp option, .stApp input, .stApp textarea, .stApp label, .stApp div[role="button"], .stApp [role="option"] {
        color: var(--input-text) !important;
    }

    /* Sidebar specific controls */
    section[data-testid="stSidebar"] button, section[data-testid="stSidebar"] select, section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] label {
        color: var(--text-primary) !important;
    }

    /* Force option panels/listboxes to use readable colors */
    div[role="listbox"], ul[role="listbox"], div[role="option"], li[role="option"] {
        background: var(--card-bg) !important;
        color: var(--input-text) !important;
        border-color: var(--border) !important;
    }

    /* Ensure highlighted option has clear contrast */
    .stSelectbox [role="option"]:hover, .stSelectbox [role="option"][aria-selected="true"] {
        background: linear-gradient(90deg, rgba(160,104,78,0.16), rgba(109,139,111,0.06)) !important;
        color: var(--text-primary) !important;
    }

    .stTabs [role="tablist"] {
        border-bottom: 4px solid var(--border);
    }

    .stTabs [role="tab"] {
        border-radius: 12px 12px 0 0;
        font-weight: 800;
        letter-spacing: 0.05em;
        transition: all 0.25s ease;
        color: var(--text-secondary);
        padding: 0.8rem 1.5rem;
        text-transform: uppercase;
        font-size: 0.9rem;
    }

    .stTabs [role="tab"]:hover {
        color: var(--accent-1);
        border-color: var(--accent-1);
        background: rgba(160, 104, 78, 0.1);
    }

    .stTabs [role="tab"][aria-selected="true"] {
        border-color: var(--accent-1);
        color: var(--accent-1);
        border-bottom: 4px solid var(--accent-1);
    }

    /* INPUT FIELDS - CRITICAL FIX */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > div,
    input[type="text"],
    input[type="number"],
    select,
    textarea {
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--input-text) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput > div > div > input::placeholder,
    input[type="text"]::placeholder {
        color: var(--text-secondary) !important;
        opacity: 0.7 !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    input[type="text"]:focus,
    input[type="number"]:focus,
    select:focus,
    textarea:focus {
        border-color: var(--accent-1) !important;
        box-shadow: 0 0 0 4px rgba(160, 104, 78, 0.2) !important;
        outline: none !important;
    }

    .streamlit-expanderContent {
        background: var(--card-bg);
        border-left: 5px solid var(--accent-1);
        border-radius: 0 12px 12px 0;
        color: var(--text-primary);
    }

    .vega-embed {
        border-radius: 14px;
        overflow: hidden;
        border: 2px solid var(--border);
    }

    .stDataFrame {
        font-size: 0.95rem;
    }

    .stDataFrame thead {
        background-color: rgba(160, 104, 78, 0.3) !important;
    }

    .stDataFrame thead th {
        color: #ffffff !important;
        background-color: rgba(160, 104, 78, 0.7) !important;
        font-weight: 800 !important;
        border-color: rgba(160, 104, 78, 0.9) !important;
    }

    .stDataFrame tbody td,
    .stDataFrame [role="gridcell"] {
        border-color: rgba(160, 104, 78, 0.2);
        color: var(--text-primary) !important;
        background-color: transparent !important;
    }

    .stDataFrame tbody tr {
        background-color: transparent !important;
    }

    .stDataFrame tbody tr:hover {
        background-color: rgba(160, 104, 78, 0.08) !important;
    }

    /* Table cell buttons and icon buttons - make SVGs white */
    .stDataFrame tbody td button svg,
    .stDataFrame [role="gridcell"] button svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    /* Regular table text stays dark and visible */
    .stDataFrame tbody td,
    .stDataFrame [role="gridcell"] {
        color: var(--text-primary) !important;
    }

    /* Chart & Vega-Lite text contrast - use accent colors for visibility */
    .vega-embed {
        background: transparent !important;
    }

    .vega-embed text,
    .vega-embed tspan {
        fill: var(--accent-1) !important;
        color: var(--accent-1) !important;
        font-weight: 600;
    }

    .vega-embed .mark-text {
        fill: var(--accent-1) !important;
        font-weight: 600;
    }

    .vega-embed .axis text {
        fill: var(--accent-1) !important;
        font-size: 12px;
        font-weight: 500;
    }

    .vega-embed line,
    .vega-embed path {
        stroke: var(--accent-2) !important;
    }

    /* Plotly chart text and elements */
    .plotly-graph-div .xtick,
    .plotly-graph-div .ytick,
    .plotly-graph-div .xticklabel,
    .plotly-graph-div .yticklabel {
        color: var(--accent-1) !important;
        fill: var(--accent-1) !important;
    }

    svg text {
        fill: var(--accent-1) !important;
        color: var(--accent-1) !important;
        font-weight: 500;
    }

    /* Ensure all chart backgrounds are transparent */
    .stVegaLiteChart,
    .stPlotlyChart {
        background: transparent !important;
    }

    /* Hide download button icons but keep text */
    button[data-testid="stDownloadButton"] {
        background: linear-gradient(135deg, rgba(208,163,118,0.85), rgba(160,104,78,0.85)) !important;
        color: #ffffff !important;
        border: 2px solid rgba(160, 104, 78, 0.5) !important;
        gap: 0.6rem !important;
        font-weight: 700 !important;
    }

    button[data-testid="stDownloadButton"]:hover {
        background: linear-gradient(135deg, rgba(208,163,118,1), rgba(160,104,78,1)) !important;
        box-shadow: 0 6px 16px rgba(160, 104, 78, 0.35) !important;
    }

    button[data-testid="stDownloadButton"] svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    /* Expander/Expand buttons */
    .stExpander button,
    [data-testid="stExpander"] button {
        background: linear-gradient(135deg, rgba(208,163,118,0.85), rgba(160,104,78,0.85)) !important;
        color: #ffffff !important;
        border: 2px solid rgba(160, 104, 78, 0.5) !important;
        font-weight: 700 !important;
    }

    .stExpander button:hover,
    [data-testid="stExpander"] button:hover {
        background: linear-gradient(135deg, rgba(208,163,118,1), rgba(160,104,78,1)) !important;
        box-shadow: 0 6px 16px rgba(160, 104, 78, 0.35) !important;
    }

    .stExpander button svg,
    [data-testid="stExpander"] button svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    /* Chart fullscreen and expand buttons */
    button[aria-label*="fullscreen"],
    button[aria-label*="expand"],
    button[title*="fullscreen"],
    button[title*="expand"],
    .vega-embed button,
    .plotly-graph-div button {
        background: linear-gradient(135deg, rgba(208,163,118,0.85), rgba(160,104,78,0.85)) !important;
        color: #ffffff !important;
        border: 2px solid rgba(160, 104, 78, 0.5) !important;
    }

    button[aria-label*="fullscreen"]:hover,
    button[aria-label*="expand"]:hover,
    button[title*="fullscreen"]:hover,
    button[title*="expand"]:hover,
    .vega-embed button:hover,
    .plotly-graph-div button:hover {
        background: linear-gradient(135deg, rgba(208,163,118,1), rgba(160,104,78,1)) !important;
        box-shadow: 0 6px 16px rgba(160, 104, 78, 0.35) !important;
    }

    button[aria-label*="fullscreen"] svg,
    button[aria-label*="expand"] svg,
    button[title*="fullscreen"] svg,
    button[title*="expand"] svg,
    .vega-embed button svg,
    .plotly-graph-div button svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    .stSpinner {
        color: var(--accent-1) !important;
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-1), var(--accent-2)) !important;
        height: 10px !important;
        border-radius: 5px !important;
    }

    /* Explicit dark backgrounds need light text */
    [data-testid="stDataFrame"] {
        background: transparent;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--accent-1) !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
    }

    /* All button text must be visible */
    button {
        fill: currentColor !important;
    }

    button svg {
        fill: currentColor !important;
        stroke: currentColor !important;
    }

    .stButton > button svg,
    .stExpander button svg,
    [data-testid="stExpander"] button svg {
        fill: currentColor !important;
        stroke: currentColor !important;
    }

    /* Force light text on all dark backgrounds */
    .stTabs [role="tabpanel"] {
        color: var(--text-primary) !important;
    }

    /* Ensure all expandable content is readable */
    .streamlit-expanderContent {
        background: var(--card-bg) !important;
        color: var(--text-primary) !important;
    }

    .stSuccess {
        background-color: rgba(61, 107, 71, 0.55);
        border: 3px solid var(--success);
        border-radius: 12px;
        color: #ffffff;
        padding: 1.2rem;
        font-weight: 600;
    }

    .stWarning {
        background-color: rgba(200, 154, 14, 0.55);
        border: 3px solid var(--warning);
        border-radius: 12px;
        color: #ffffff;
        padding: 1.2rem;
        font-weight: 600;
    }

    .stError {
        background-color: rgba(155, 56, 53, 0.55);
        border: 3px solid var(--danger);
        border-radius: 12px;
        color: #ffffff;
        padding: 1.2rem;
        font-weight: 600;
    }

    .stInfo {
        background-color: rgba(109, 139, 111, 0.55);
        border: 3px solid var(--accent-2);
        border-radius: 12px;
        color: #ffffff;
        padding: 1.2rem;
        font-weight: 600;
    }

    /* Dark theme alerts */
    [data-theme="dark"] .stSuccess {
        background-color: rgba(61, 107, 71, 0.65);
        color: #ffffff;
    }

    [data-theme="dark"] .stWarning {
        background-color: rgba(200, 154, 14, 0.65);
        color: #ffffff;
    }

    [data-theme="dark"] .stError {
        background-color: rgba(155, 56, 53, 0.65);
        color: #ffffff;
    }

    [data-theme="dark"] .stInfo {
        background-color: rgba(109, 139, 111, 0.65);
        color: #ffffff;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    .pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }

    @keyframes popIn {
        0% { opacity: 0; transform: translateY(18px) scale(0.92); }
        70% { opacity: 1; transform: translateY(-4px) scale(1.02); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 10px 30px rgba(160, 104, 78, 0.18); }
        50% { box-shadow: 0 14px 40px rgba(109, 139, 111, 0.35); }
    }

    .popup-card {
        animation: popIn 420ms cubic-bezier(0.17, 0.89, 0.32, 1.28), glowPulse 2.4s ease-in-out infinite;
        border-radius: 16px;
        border: 2px solid var(--accent-2);
        background: linear-gradient(120deg, rgba(255,255,255,0.86), rgba(235,231,222,0.85));
        color: var(--text-primary);
        padding: 0.85rem 1rem;
    }

    @keyframes countUp {
        from { opacity: 0; transform: scale(0.85); }
        to { opacity: 1; transform: scale(1); }
    }

    .stat-number { animation: countUp 0.6s ease-out; }

    /* CAPTION & LABEL STYLES */
    .stCaption, caption {
        color: var(--text-secondary) !important;
        font-weight: 600;
    }

    /* SUBHEADER */
    .stSubheader {
        color: var(--text-primary) !important;
        font-weight: 800;
        font-size: 1.4rem;
    }

    /* SCROLLBARS - BRILLIANT & THEMED */
    section[data-testid="stSidebar"] {
        max-height: 100vh;
        overflow-y: auto;
    }

    div[data-testid="stAppViewContainer"] > .main {
        max-height: 100vh;
        overflow-y: auto;
    }

    /* Light theme scrollbars */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--accent-1), var(--accent-2));
        border-radius: 10px;
        border: 2px solid var(--bg-secondary);
        transition: background 0.2s ease;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--accent-2), var(--accent-1));
        box-shadow: 0 0 12px rgba(160, 104, 78, 0.3);
    }

    ::-webkit-scrollbar-thumb:active {
        background: linear-gradient(180deg, var(--accent-2), var(--accent-3));
    }

    section[data-testid="stSidebar"].is-scrolling::-webkit-scrollbar-thumb,
    div[data-testid="stAppViewContainer"] > .main.is-scrolling::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--accent-2), var(--accent-1));
        box-shadow: 0 0 14px rgba(109, 139, 111, 0.45);
    }

    /* Firefox scrollbars */
    * {
        scrollbar-color: var(--accent-1) var(--bg-secondary);
        scrollbar-width: thin;
    }

    /* Slider styling (max workers, batch size, etc.) */
    .stSlider > div > div {
        background: var(--card-bg) !important;
    }

    .stSlider [role="slider"] {
        background: linear-gradient(90deg, var(--accent-1), var(--accent-2)) !important;
        box-shadow: 0 4px 12px rgba(160, 104, 78, 0.2) !important;
        border-radius: 8px !important;
    }

    .stSlider [role="slider"]:hover {
        box-shadow: 0 6px 18px rgba(160, 104, 78, 0.35) !important;
    }

    /* Range slider track */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, var(--accent-3), var(--accent-2)) !important;
        height: 6px !important;
        border-radius: 3px !important;
    }

    /* Toast Notifications - Better Contrast */
    .stToast {
        background: linear-gradient(135deg, rgba(160,104,78,0.95), rgba(109,139,111,0.85)) !important;
        color: #ffffff !important;
        border: 2px solid rgba(160, 104, 78, 0.8) !important;
        border-radius: 12px !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25) !important;
    }

    .stToast p, .stToast span, .stToast div {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Code Blocks - Improved Readability for Diagnostics */
    .stCode {
        background: linear-gradient(135deg, rgba(45,42,34,0.95), rgba(30,28,25,0.95)) !important;
        border: 2px solid rgba(160, 104, 78, 0.4) !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
    }

    .stCode > div > pre {
        background: transparent !important;
        color: #f0d9b5 !important;
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
    }

    .stCode > div > pre > code {
        color: #f0d9b5 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 500 !important;
    }

    /* Pre-formatted Text */
    pre {
        background: linear-gradient(135deg, rgba(45,42,34,0.95), rgba(30,28,25,0.95)) !important;
        color: #f0d9b5 !important;
        border: 2px solid rgba(160, 104, 78, 0.4) !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
    }

    [data-theme="dark"] .stCode {
        background: linear-gradient(135deg, rgba(60,55,48,0.95), rgba(45,42,34,0.95)) !important;
        border-color: rgba(217,166,111,0.4) !important;
    }

    [data-theme="dark"] .stCode > div > pre {
        color: #f0d9b5 !important;
    }

    [data-theme="dark"] .stCode > div > pre > code {
        color: #f0d9b5 !important;
    }

    [data-theme="dark"] pre {
        background: linear-gradient(135deg, rgba(60,55,48,0.95), rgba(45,42,34,0.95)) !important;
        color: #f0d9b5 !important;
        border-color: rgba(217,166,111,0.4) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Server-side theme override (ensures theme applies even if client JS/DOM resets)
current_theme = st.session_state.get("app_theme", "light")
if current_theme == "dark":
    st.markdown(
        """
        <style>
        :root {
            --bg-primary: #0f0d0a !important;
            --bg-secondary: #1a1714 !important;
            --text-primary: #f5f3ee !important;
            --input-bg: #2d2a22 !important;
            --input-text: #f5f3ee !important;
            --card-bg: rgba(45, 42, 34, 0.95) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
elif current_theme == "system":
    st.markdown(
        """
        <style>
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-primary: #0f0d0a !important;
                --bg-secondary: #1a1714 !important;
                --text-primary: #f5f3ee !important;
                --input-bg: #2d2a22 !important;
                --input-text: #f5f3ee !important;
                --card-bg: rgba(45, 42, 34, 0.95) !important;
            }
        }
        @media (prefers-color-scheme: light) {
            :root {
                --bg-primary: #f5f3ee !important;
                --bg-secondary: #ebe7de !important;
                --text-primary: #0f0d0a !important;
                --input-bg: #ffffff !important;
                --input-text: #0f0d0a !important;
                --card-bg: rgba(255,255,255,0.95) !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    # light
    st.markdown(
        """
        <style>
        :root {
            --bg-primary: #f5f3ee !important;
            --bg-secondary: #ebe7de !important;
            --text-primary: #0f0d0a !important;
            --input-bg: #ffffff !important;
            --input-text: #0f0d0a !important;
            --card-bg: rgba(255,255,255,0.95) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )



# ===== THEME APPLICATION SCRIPT =====
st.markdown(
    """
    <script>
    (function() {
        let scrollTimer = null;

        // Apply theme from session or localStorage
        function applyTheme(theme) {
            const isDark = theme === 'dark';
            document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
            localStorage.setItem('app-theme', isDark ? 'dark' : 'light');
        }

        function wireScrollState(selector) {
            const el = document.querySelector(selector);
            if (!el) {
                return;
            }
            el.addEventListener('scroll', () => {
                el.classList.add('is-scrolling');
                if (scrollTimer) {
                    clearTimeout(scrollTimer);
                }
                scrollTimer = setTimeout(() => el.classList.remove('is-scrolling'), 140);
            }, { passive: true });
        }
        
        // Get saved theme or default to light
        const savedTheme = localStorage.getItem('app-theme') || 'light';
        applyTheme(savedTheme);
        
        // Monitor DOM for theme attribute changes
        const observer = new MutationObserver(() => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            if (currentTheme !== localStorage.getItem('app-theme')) {
                localStorage.setItem('app-theme', currentTheme || 'light');
            }
        });
        
        observer.observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});

        // Left and right panel scrollbar activity styles.
        wireScrollState('section[data-testid="stSidebar"]');
        wireScrollState('div[data-testid="stAppViewContainer"] > .main');
    })();
    </script>
    """,
    unsafe_allow_html=True,
)

if "welcome_popup_shown" not in st.session_state:
    st.session_state.welcome_popup_shown = False

if not st.session_state.welcome_popup_shown:
    st.markdown(
        """
        <div class="popup-card" style="position: fixed; right: 22px; bottom: 22px; z-index: 9999; max-width: 320px;">
            <div style="font-weight: 800; font-family: 'Space Grotesk', sans-serif; margin-bottom: 0.2rem;">
                Neural OCR Ready
            </div>
            <div style="font-size: 0.9rem; opacity: 0.9;">
                Batch engine is online. Start processing with live progress and anti-stall protection.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.welcome_popup_shown = True


@st.cache_data(show_spinner=False)
def load_lottie_url(url: str):
    try:
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            return response.json()
    except Exception:
        return None
    return None


@st.cache_data(show_spinner=False)
def load_report(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)
    for col in ["subtotal", "tax", "total"]:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    for col in ["vendor", "date", "status", "filename", "new_name"]:
        if col not in df.columns:
            df[col] = ""

    return df


def notify(message: str, icon: str = ""):
    try:
        st.toast(message, icon=icon)
    except Exception:
        pass


@st.cache_resource(show_spinner=False)
def get_cached_agent(max_workers: int, ocr_engine: str, ocr_timeout_seconds: int) -> ReceiptAgent:
    return ReceiptAgent(
        max_workers=max_workers,
        ocr_engine=ocr_engine,
        ocr_timeout_seconds=ocr_timeout_seconds,
    )


def compute_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "median": 0.0,
            "p90": 0.0,
            "p10": 0.0,
            "std": 0.0,
            "cv": 0.0,
            "tax_ratio": 0.0,
            "vendor_concentration": 0.0,
            "daily_avg": 0.0,
        }

    totals = df["total"].astype(float)
    median = float(totals.median())
    p90 = float(totals.quantile(0.9))
    p10 = float(totals.quantile(0.1))
    std = float(totals.std() if len(totals) > 1 else 0.0)
    mean = float(totals.mean()) if len(totals) else 0.0
    cv = (std / mean * 100.0) if mean > 0 else 0.0

    total_sum = float(df["total"].sum())
    tax_sum = float(df["tax"].sum())
    tax_ratio = (tax_sum / total_sum * 100.0) if total_sum > 0 else 0.0

    vendor_share = (
        df.groupby("vendor")["total"].sum() / total_sum if total_sum > 0 else pd.Series(dtype=float)
    )
    hhi = float((vendor_share.pow(2).sum() * 100) if not vendor_share.empty else 0.0)

    dates = pd.to_datetime(df["date"], errors="coerce", dayfirst=True).dropna()
    days = (dates.max() - dates.min()).days + 1
    daily_avg = total_sum / days if days > 0 else 0.0

    return {
        "median": median,
        "p90": p90,
        "p10": p10,
        "std": std,
        "cv": cv,
        "tax_ratio": tax_ratio,
        "vendor_concentration": hhi,
        "daily_avg": daily_avg,
    }


def compute_health_signal(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    verified = df["status"].astype(str).str.contains("VERIFIED", case=False, na=False).mean() * 100
    math_valid = (df["total"] >= df["tax"]).mean() * 100
    return round((verified * 0.7) + (math_valid * 0.3), 2)


def highlight_status(value: str):
    safe = str(value).upper()
    if "VERIFIED" in safe:
        return "background-color: rgba(16, 185, 129, 0.18); color: #d1fae5; font-weight: 700"
    if "ERROR" in safe:
        return "background-color: rgba(239, 68, 68, 0.18); color: #fee2e2; font-weight: 700"
    return "background-color: rgba(245, 158, 11, 0.18); color: #fef3c7; font-weight: 700"


def load_run_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_run_history(history: list):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def get_image_files(org_path: str) -> list:
    verified_dir = os.path.join(org_path, "Verified")
    if not os.path.exists(verified_dir):
        return []
    return [f for f in os.listdir(verified_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]


def get_export_template(template_name: str, df: pd.DataFrame) -> str:
    if template_name == "Summary Report":
        summary = f"""
# RECEIPT AUDIT SUMMARY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- Total Documents: {len(df)}
- Total Revenue: RM {df['total'].sum():,.2f}
- Verified Rate: {(df['status'].str.contains('VERIFIED', case=False, na=False).mean() * 100):.1f}%

## Top Vendors
{df.groupby('vendor')['total'].sum().sort_values(ascending=False).head(5).to_string()}

## Key Metrics
- Average Receipt: RM {df['total'].mean():,.2f}
- Median Receipt: RM {df['total'].median():,.2f}
- Total Tax: RM {df['tax'].sum():,.2f}
"""
    elif template_name == "Detailed Audit":
        summary = df.to_string()
    else:
        summary = df.to_csv(index=False)

    return summary



if "last_run_time" not in st.session_state:
    st.session_state.last_run_time = "Not run yet"

if "selected_receipt" not in st.session_state:
    st.session_state.selected_receipt = None

if "app_theme" not in st.session_state:
    st.session_state.app_theme = "light"

if "accent" not in st.session_state:
    st.session_state.accent = "clay_brown"

if "density" not in st.session_state:
    st.session_state.density = "comfortable"

if "theme_select" not in st.session_state:
    st.session_state.theme_select = "Light"

if "accent_select" not in st.session_state:
    st.session_state.accent_select = "Clay Brown"

if "density_select" not in st.session_state:
    st.session_state.density_select = "Comfortable"

try:
    history_init = load_run_history()
    if history_init:
       
        try:
            latest_ts = max(history_init, key=lambda r: r.get("timestamp", ""))
            ts = latest_ts.get("timestamp")
            if ts:
                st.session_state.last_run_time = ts
        except Exception:
            pass
except Exception:
    pass

# ===== LOAD ANIMATIONS =====
lottie_ai = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_49rdyysj.json")
lottie_celebrate = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_s1rxcbsq.json")
lottie_chart = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_5hl3c9ja.json")

# ===== HEADER SECTION =====
with st.container():
    col_hero_left, col_hero_anim = st.columns([2, 1])

    with col_hero_left:
        st.markdown(
            f"""
            <div class="hero-card">
                <h1 style="color: var(--accent-1); margin: 0;">Neural OCR Platform</h1>
                <p style="color: var(--text-dim); margin: 0.5rem 0 0 0; font-size: 1.05rem;">
                    Human-centered OCR and ML for practical business automation.
                    Fast, accurate data extraction that integrates with your workflows.
                </p>
                <p style="color: var(--text-dim); margin: 0.4rem 0 0 0; font-size: 0.9rem;">
                    Built on a flexible stack: Tesseract, OpenCV, TensorFlow/PyTorch, and optional cloud OCR (Google, AWS, Azure, ABBYY).
                </p>
                <div style="margin-top: 0.8rem; display:flex; gap:0.5rem; align-items:center;">
                    <span class="status-badge badge-verified">
                        ✓ Production Ready
                    </span>
                    <span class="status-badge" style="margin-left: 0.5rem;">
                        v{APP_VERSION}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_hero_anim:
        if lottie_ai:
            st_lottie(lottie_ai, height=180, key="main_anim", speed=0.8)

# ===== SIDEBAR CONFIGURATION =====
with st.sidebar:
    st.header("Command Center")

    process_limit = st.slider("Batch size", 1, 100, 20, help="Number of documents to process")
    data_path = st.text_input("Dataset path", value=DEFAULT_DATA_PATH)
    report_path = st.text_input("Report file", value=DEFAULT_REPORT_PATH)

    st.divider()

    with st.expander("Performance", expanded=True):
        run_mode = st.selectbox(
            "Run mode",
            ["Turbo", "Balanced", "Precision"],
            index=1,
            help="Speed vs quality tradeoff",
        )
        max_workers = st.slider("Max workers", 1, 16, 6)
        ocr_timeout_seconds = st.slider("OCR timeout/file (sec)", 10, 120, 25)
        organize_after_run = st.checkbox("Organize files after", value=True)
        fast_ui = st.checkbox("Fast UI mode", value=True)
        incremental_run = st.checkbox("Incremental (skip already processed)", value=True)
        image_width = st.slider("Image width (px)", 100, 800, 320)
        chart_width = st.slider("Chart width (px)", 300, 1400, 700)
        table_width = st.slider("Table width (px)", 600, 1600, 1000)

        with st.expander("Advanced engine", expanded=False):
            auto_refresh = st.checkbox("Auto-refresh after run", value=True)
            write_report = st.checkbox("Write report file", value=True)

    with st.expander("Analytics", expanded=False):
        top_vendor_limit = st.slider("Top vendors to show", 5, 30, 12)
        rolling_window = st.slider("Trend window", 2, 14, 5)
        anomaly_sigma = st.slider("Anomaly threshold (σ)", 1.0, 4.0, 2.0)
    ocr_engine = st.selectbox("OCR Engine", ["Docling (default)", "Tesseract", "Google Vision", "AWS Textract", "Azure OCR", "ABBYY"], index=0)

    with st.expander("Appearance", expanded=False):
        # Theme selector callback - updates immediately without lag
        def on_theme_change():
            theme_val = st.session_state.theme_select.lower()
            st.session_state.app_theme = theme_val
            
            st.markdown(
                f"""
                <script>
                document.documentElement.setAttribute('data-theme', '{theme_val}');
                localStorage.setItem('app-theme', '{theme_val}');
                </script>
                """,
                unsafe_allow_html=True,
            )

        theme_idx = 0 if st.session_state.app_theme == "light" else 1
        new_theme = st.selectbox(
            "Theme",
            ["Light", "Dark"],
            index=theme_idx,
            key="theme_select",
            on_change=on_theme_change,
        )

        # Accent selector callback
        def on_accent_change():
            st.session_state.accent = st.session_state.accent_select.lower().replace(" ", "_")

        accent = st.selectbox(
            "Accent Color",
            ["Clay Brown", "Olive Green", "Sand", "Custom"],
            index=0,
            key="accent_select",
            on_change=on_accent_change,
        )

        # Density selector callback
        def on_density_change():
            st.session_state.density = st.session_state.density_select.lower()

        density = st.selectbox(
            "Layout Density",
            ["Comfortable", "Compact"],
            index=0,
            key="density_select",
            on_change=on_density_change,
        )

        
        theme_val = st.session_state.app_theme.lower()
        st.markdown(
            f"""
            <script>
            (function(){{
                document.documentElement.setAttribute('data-theme', '{theme_val}');
                localStorage.setItem('app-theme', '{theme_val}');
            }})();
            </script>
            """,
            unsafe_allow_html=True,
        )

        
        accent_styles = {
            "clay_brown": ("#a0684e", "#6d4b3a", "#d4ad80"),
            "olive_green": ("#6d8b6f", "#4f6b5a", "#bfc9b7"),
            "sand": ("#d4ad80", "#b38a5d", "#efe1c8"),
        }
        a1, a2, a3 = accent_styles.get(st.session_state.accent, accent_styles["clay_brown"])

        
        st.markdown(
            f"""
            <style>
            :root {{
                --accent-1: {a1} !important;
                --accent-2: {a2} !important;
                --accent-3: {a3} !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        
        density_css = ""
        if st.session_state.density == "compact":
            density_css = """
            :root { --density-scale: 0.86; }
            .stButton > button { padding: 0.45rem 0.9rem !important; font-size: 0.88rem !important; }
            .stTextInput > div > div > input, .stSelectbox > div > div > select { padding: 0.45rem 0.7rem !important; font-size: 0.9rem !important; }
            """
        else:
            density_css = ":root { --density-scale: 1.0; }"

        st.markdown(f"<style>{density_css}</style>", unsafe_allow_html=True)

    st.divider()
    st.caption("� Model: Docling-V2 | OCR: Rapid-Torch | Audit: Heuristic-GST-6")
    
    last_run_iso = st.session_state.get("last_run_time", "Not run yet")
    if last_run_iso and last_run_iso != "Not run yet":
        
        last_run_attr = last_run_iso
    else:
        last_run_attr = ""

    html_content = (
        """
        <div style="display:flex; gap:0.6rem; align-items:center;">
            <div>Last run:</div>
        """
        + f"<div id=\"last-run\" data-last-run=\"{last_run_attr}\">{last_run_attr or 'Not run yet'}</div>"
        + """
            <div id="clock" style="color:var(--text-secondary); font-size:0.9rem; margin-left:0.8rem;"></div>
        </div>
        <script>
        (function(){
            function pad(n){return n<10? '0'+n : n}
            function updateClock(){
                var d = new Date();
                var s = pad(d.getDate())+"/"+pad(d.getMonth()+1)+"/"+d.getFullYear()+" "+pad(d.getHours())+":"+pad(d.getMinutes())+":"+pad(d.getSeconds());
                var el = document.getElementById('clock'); if(el) el.innerText = s;
                // update relative last run if provided
                var lr = document.getElementById('last-run');
                if(lr){
                    var attr = lr.getAttribute('data-last-run');
                    if(attr){
                        try{
                            var t = new Date(attr);
                            if(!isNaN(t)){
                                var diff = Math.floor((Date.now()-t.getTime())/1000);
                                var text = '';
                                if(diff<60) text = diff+ 's ago';
                                else if(diff<3600) text = Math.floor(diff/60)+'m ago';
                                else if(diff<86400) text = Math.floor(diff/3600)+'h ago';
                                else text = Math.floor(diff/86400)+'d ago';
                                lr.innerText = t.toLocaleString() + ' ('+text+')';
                            }
                        }catch(e){}
                    }
                }
            }
            updateClock(); setInterval(updateClock, 1000);
        })();
        </script>
        """
    )
    st.markdown(html_content, unsafe_allow_html=True)


st.markdown(
    """<div style="padding:0.5rem 1rem; background:rgba(160,104,78,0.08); border-left:3px solid var(--accent-2); border-radius:6px; margin-bottom:1rem; font-size:0.9rem;">
    <strong>💡 Tip:</strong> Use the hamburger menu (☰) at top-left to toggle the sidebar anytime.
    </div>""",
    unsafe_allow_html=True,
)

(
    tab_dashboard,
    tab_processor,
    tab_receipt_viewer,
    tab_explorer,
    tab_insights,
    tab_history,
    tab_exports,
    tab_ops,
) = st.tabs(
    [
        "Dashboard",
        "Processor",
        "Receipt Viewer",
        "Explorer",
        "Insights",
        "History",
        "Exports",
        "Ops",
    ]
)


df = load_report(report_path)
stats = compute_stats(df)
health = compute_health_signal(df)

mode_defaults = {
    "Turbo": {"workers": min(16, max_workers + 4), "organize": False},
    "Balanced": {"workers": max_workers, "organize": organize_after_run},
    "Precision": {"workers": max(1, max_workers - 2), "organize": organize_after_run},
}
effective_workers = mode_defaults[run_mode]["workers"]
effective_organize = mode_defaults[run_mode]["organize"]


with tab_dashboard:
    st.subheader("Executive Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="color: var(--text-dim); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em;">
                    Documents Processed
                </div>
                <div style="font-size: 2.2rem; font-weight: 800; color: var(--accent-1); margin-top: 0.5rem;" class="stat-number">
                    {len(df)}
                </div>
                <div style="color: var(--text-dim); font-size: 0.8rem; margin-top: 0.3rem;">
                    {max(0, len(df) - 1)} since last refresh
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        verified_count = (df["status"].astype(str).str.contains("VERIFIED", case=False, na=False).sum()) if not df.empty else 0
        verified_pct = (verified_count / len(df) * 100) if len(df) else 0
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="color: var(--text-dim); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em;">
                    Verification Rate
                </div>
                <div style="font-size: 2.2rem; font-weight: 800; color: var(--success); margin-top: 0.5rem;" class="stat-number">
                    {verified_pct:.1f}%
                </div>
                <div style="color: var(--text-dim); font-size: 0.8rem; margin-top: 0.3rem;">
                    {verified_count} verified
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="color: var(--text-dim); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em;">
                    Health Score
                </div>
                <div style="font-size: 2.2rem; font-weight: 800; color: var(--accent-2); margin-top: 0.5rem;" class="stat-number">
                    {health:.1f}
                </div>
                <div style="color: var(--text-dim); font-size: 0.8rem; margin-top: 0.3rem;">
                    Overall system
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Revenue", f"RM {df['total'].sum():,.2f}")
    k2.metric("Tax Collected", f"RM {df['tax'].sum():,.2f}")
    k3.metric("Median Receipt", f"RM {stats['median']:,.2f}")
    k4.metric("P90 Receipt", f"RM {stats['p90']:,.2f}")
    k5.metric("Volatility", f"{stats['cv']:.1f}%")
    k6.metric("Daily Avg", f"RM {stats['daily_avg']:,.2f}")
    style_metric_cards(background_color="rgba(255,255,255,0.06)", border_left_color="#00d9ff")

    st.divider()

    if not df.empty:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("Status Distribution")
            status_counts = df["status"].fillna("Unknown").value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            st.bar_chart(status_counts.set_index("status"), width=chart_width)

        with chart_col2:
            st.subheader("Top 8 Vendors")
            vendor_totals = (
                df.groupby("vendor", as_index=False)["total"].sum().sort_values("total", ascending=False).head(8).set_index("vendor")
            )
            st.bar_chart(vendor_totals, width=chart_width)
    else:
        st.info("No data yet. Run a batch to populate the dashboard.")


with tab_processor:
    st.subheader("Batch Processing Engine")

    st.markdown(
        f"""
        <div class="glass-panel">
            <h4 style="margin-top: 0;">Configuration Summary</h4>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; font-size: 0.95rem;">
                <div><strong>Run Mode:</strong> {run_mode}</div>
                <div><strong>Workers:</strong> {effective_workers}</div>
                <div><strong>Batch Size:</strong> {process_limit}</div>
                <div><strong>Organization:</strong> {'Enabled' if effective_organize else 'Disabled'}</div>
                <div><strong>Report Write:</strong> {'Yes' if write_report else 'No'}</div>
                <div><strong>Auto-refresh:</strong> {'Yes' if auto_refresh else 'No'}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_run, col_refresh = st.columns([3, 1])

    with col_run:
        if st.button("EXECUTE BATCH PROCESSING"):
            notify("Batch started. Initializing engine...", icon="⚙️")
            agent = get_cached_agent(
                max_workers=effective_workers,
                ocr_engine=ocr_engine,
                ocr_timeout_seconds=ocr_timeout_seconds,
            )
            progress_bar = st.progress(0)
            status_text = st.empty()
            time_text = st.empty()

            start_time = time.time()
            progress_bar.progress(5)
            status_text.info("Initializing batch engine...")

            if not fast_ui:
                for i in range(0, 40, 8):
                    elapsed = time.time() - start_time
                    status_text.info(f"Warming up pipeline: {i}%")
                    time_text.caption(f"Elapsed: {elapsed:.1f}s")
                    progress_bar.progress(i)
                    time.sleep(0.05)

            with st.spinner("Neural extraction in progress..."):
                def on_progress(done: int, total: int, filename: str):
                    elapsed_now = time.time() - start_time
                    ratio = (done / total) if total else 1.0
                    progress_bar.progress(min(90, max(10, int(10 + (ratio * 80)))))
                    status_text.info(f"Processing {done}/{total}: {filename}")
                    time_text.caption(f"Elapsed: {elapsed_now:.1f}s")

                # remember choice for history
                st.session_state['last_incremental'] = incremental_run
                results = agent.bulk_process(
                    data_path,
                    limit=process_limit,
                    report_path=report_path,
                    write_report=write_report,
                    incremental=incremental_run,
                    progress_callback=on_progress,
                )
                progress_bar.progress(85)

                if effective_organize:
                    status_text.info("Organizing receipt library...")
                    agent.organize_files(results)
                    progress_bar.progress(95)
                    notify("Library organization finished.", icon="📂")

            elapsed = time.time() - start_time
            progress_bar.progress(100)

            st.session_state.last_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            history = load_run_history()
            history.append(
                {
                    "timestamp": st.session_state.last_run_time,
                    "documents": len(results),
                    "duration": elapsed,
                    "mode": run_mode,
                    "workers": effective_workers,
                    "engine": ocr_engine,
                    "incremental": bool(st.session_state.get('last_incremental', True)),
                }
            )
            save_run_history(history[-50:])  # Keep last 50 runs

            throughput = len(results) / elapsed if elapsed > 0 else 0

            if len(results) == 0 and incremental_run:
                st.info("No new files needed processing (incremental mode).")
                notify("No new files in incremental mode.", icon="")
            else:
                st.success(
                    f"**Completed!** Processed {len(results)} docs in {elapsed:.1f}s ({throughput:.1f} docs/sec)"
                )
                notify(
                    f"Done: {len(results)} files in {elapsed:.1f}s ({throughput:.1f}/s)",
                    icon="",
                )
                st.balloons()

            if auto_refresh:
                st.cache_data.clear()
                st.rerun()

    with col_refresh:
        if st.button("Reload"):
            notify("Refreshing dashboards and cached data...", icon="")
            st.cache_data.clear()
            st.rerun()

# ===== TAB: RECEIPT VIEWER =====
with tab_receipt_viewer:
    st.subheader("Receipt Preview Gallery")

    image_files = get_image_files(DEFAULT_ORGANIZED_PATH)

    if not image_files:
        st.info("No organized receipts found. Run batch processing first.")
    else:
        view_mode = st.selectbox("View mode", ["Gallery", "Single Detailed"])

        if view_mode == "Gallery":
            cols_per_row = st.slider("Images per row", 2, 6, 4)
            max_images = st.slider("Max images to show", 4, 48, 12)
            cols = st.columns(cols_per_row)

            for idx, img_file in enumerate(image_files[:max_images]):
                col = cols[idx % cols_per_row]
                img_path = os.path.join(DEFAULT_ORGANIZED_PATH, "Verified", img_file)

                try:
                    img = Image.open(img_path)
                    col.image(img, width=image_width, caption=img_file[:20])
                except Exception:
                    col.warning(f"Cannot load: {img_file}")
        else:
            selected_img = st.selectbox("Select receipt", image_files[:20])
            img_path = os.path.join(DEFAULT_ORGANIZED_PATH, "Verified", selected_img)

            try:
                img = Image.open(img_path)
                st.image(img, width=image_width)

                matching_rows = df[df["new_name"] == selected_img]
                if not matching_rows.empty:
                    st.subheader("Extracted Data")
                    row = matching_rows.iloc[0]
                    col_data1, col_data2 = st.columns(2)

                    with col_data1:
                        st.metric("Vendor", row["vendor"])
                        st.metric("Date", row["date"])
                        st.metric("Subtotal", f"RM {row['subtotal']:,.2f}")

                    with col_data2:
                        st.metric("Tax", f"RM {row['tax']:,.2f}")
                        st.metric("Total", f"RM {row['total']:,.2f}")
                        st.metric("Status", row["status"])

            except Exception as e:
                st.error(f"Error loading image: {e}")

# ===== TAB: EXPLORER =====
with tab_explorer:
    st.subheader("Interactive Report Explorer")

    if df.empty:
        st.info("Report not available yet.")
    else:
        exp_col1, exp_col2, exp_col3 = st.columns(3)

        with exp_col1:
            status_filter = st.multiselect(
                "Filter by status",
                options=sorted(df["status"].astype(str).unique().tolist()),
                default=[],
            )

        with exp_col2:
            vendor_filter = st.text_input("Vendor contains")

        with exp_col3:
            min_total = st.number_input("Min total", min_value=0.0, value=0.0, step=1.0)

        date_col1, date_col2 = st.columns(2)
        with date_col1:
            date_from = st.date_input("Date from", value=None)
        with date_col2:
            date_to = st.date_input("Date to", value=None)

        filtered = df.copy()

        if status_filter:
            filtered = filtered[filtered["status"].isin(status_filter)]

        if vendor_filter.strip():
            filtered = filtered[
                filtered["vendor"].astype(str).str.contains(vendor_filter.strip(), case=False, na=False)
            ]

        filtered = filtered[filtered["total"] >= min_total]

        if date_from is not None or date_to is not None:
            date_col_parsed = pd.to_datetime(filtered["date"], errors="coerce", dayfirst=True)
            if date_from is not None:
                filtered = filtered[date_col_parsed >= pd.to_datetime(date_from)]
                date_col_parsed = pd.to_datetime(filtered["date"], errors="coerce", dayfirst=True)
            if date_to is not None:
                filtered = filtered[date_col_parsed <= pd.to_datetime(date_to)]

        st.caption(f"Showing {len(filtered)} of {len(df)} records")

        st.dataframe(
            filtered.style.map(highlight_status, subset=["status"]),
            width=table_width,
            height=450,
            hide_index=True,
        )

        exp_d1, exp_d2, exp_d3 = st.columns(3)

        with exp_d1:
            st.download_button(
                "Export CSV",
                data=filtered.to_csv(index=False),
                file_name="filtered_audit_report.csv",
                mime="text/csv",
            )

        with exp_d2:
            st.download_button(
                "Export JSON",
                data=filtered.to_json(orient="records", indent=2),
                file_name="filtered_audit_report.json",
                mime="application/json",
            )

        with exp_d3:
            st.download_button(
                "Export Excel",
                data=filtered.to_csv(index=False).encode("utf-8-sig"),
                file_name="filtered_audit_report.xlsx",
                mime="application/vnd.ms-excel",
            )

# ===== TAB: INSIGHTS =====
with tab_insights:
    st.subheader("Deep Analytics & Insights")

    if df.empty:
        st.info("Insights available after first batch run.")
    else:
        timeline = (
            df.assign(date_parsed=pd.to_datetime(df["date"], errors="coerce", dayfirst=True))
            .dropna(subset=["date_parsed"])
            .groupby("date_parsed", as_index=False)["total"]
            .sum()
            .sort_values("date_parsed")
        )

        if not timeline.empty:
            timeline["rolling_avg"] = timeline["total"].rolling(rolling_window, min_periods=1).mean()

        chart1, chart2, chart3 = st.columns([1.5, 1.5, 1])

        with chart1:
            st.subheader("Daily Spend Trend")
            if not timeline.empty:
                st.line_chart(timeline.set_index("date_parsed")["total"], width=chart_width)
            else:
                st.info("No date data available")

        with chart2:
            st.subheader("Smoothed Trend")
            if not timeline.empty:
                st.area_chart(timeline.set_index("date_parsed")["rolling_avg"], width=chart_width)
            else:
                st.info("No trend data")

        with chart3:
            st.subheader("Key Stats")
            mean_total = df["total"].mean()
            std_total = df["total"].std() if len(df) > 1 else 0.0
            threshold = mean_total + (anomaly_sigma * std_total)
            anomalies = df[df["total"] > threshold] if std_total > 0 else df.head(0)

            st.metric("Average", f"RM {mean_total:,.2f}")
            st.metric("Threshold", f"RM {threshold:,.2f}")
            st.metric("Anomalies", f"{len(anomalies)}")

        st.divider()

        anom_col1, anom_col2 = st.columns([2, 1])

        with anom_col1:
            if len(anomalies) > 0:
                    st.subheader(f"High-Value Outliers ({len(anomalies)})")
                    st.dataframe(
                        anomalies[["filename", "vendor", "date", "total", "status"]],
                        width=table_width,
                    )
            else:
                st.success("No anomalies detected!")

        with anom_col2:
            st.subheader("Distribution Stats")
            st.metric("Median", f"RM {stats['median']:,.2f}")
            st.metric("P10", f"RM {stats['p10']:,.2f}")
            st.metric("P90", f"RM {stats['p90']:,.2f}")
            st.metric("Std Dev", f"RM {stats['std']:,.2f}")
            st.metric("CV", f"{stats['cv']:.2f}%")

# ===== TAB: HISTORY =====
with tab_history:
    st.subheader("Run History & Benchmarks")

    history = load_run_history()

    if not history:
        st.info("No run history yet.")
    else:
        history_df = pd.DataFrame(history)
        history_df["timestamp"] = pd.to_datetime(history_df["timestamp"])
        history_df = history_df.sort_values("timestamp", ascending=False)

        st.dataframe(history_df, width=table_width)

        st.divider()

        perf1, perf2, perf3 = st.columns(3)

        with perf1:
            st.subheader("Total Runs")
            st.metric("Count", len(history))

        with perf2:
            st.subheader("Total Documents")
            st.metric("Processed", int(history_df["documents"].sum()))

        with perf3:
            st.subheader("Avg Throughput")
            avg_throughput = (history_df["documents"].sum() / history_df["duration"].sum()) if history_df["duration"].sum() > 0 else 0
            st.metric("Docs/sec", f"{avg_throughput:.2f}")

        st.divider()

        st.subheader("Performance Timeline")
        history_df["throughput"] = history_df["documents"] / history_df["duration"]
        st.line_chart(history_df.set_index("timestamp")["throughput"], width=chart_width)

# ===== TAB: EXPORTS =====
with tab_exports:
    st.subheader("Export Builder")

    if df.empty:
        st.info("No data to export.")
    else:
        export_template = st.selectbox(
            "Export template",
            ["Summary Report", "Detailed Audit", "CSV Data", "Financial Summary"],
        )

        export_format = st.selectbox("Format", ["Markdown", "Plain Text", "HTML"])

        if st.button("Generate Export"):
            notify("Preparing export package...", icon="")
            content = get_export_template(export_template, df)

            if export_format == "Markdown":
                st.download_button(
                    "Download Markdown",
                    data=content.encode("utf-8"),
                    file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                )
                st.markdown(content)
                notify("Markdown export ready.", icon="")

            elif export_format == "Plain Text":
                st.download_button(
                    "Download Text",
                    data=content.encode("utf-8"),
                    file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                )
                st.text(content)
                notify("Text export ready.", icon="")

            else:
                html_content = f"<pre>{content}</pre>"
                st.download_button(
                    "Download HTML",
                    data=html_content.encode("utf-8"),
                    file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                )
                st.html(html_content)
                notify("HTML export ready.", icon="")

# ===== TAB: OPERATIONS =====
with tab_ops:
    st.subheader("Operations & Maintenance")

    ops_col_a, ops_col_b = st.columns(2)

    with ops_col_a:
        st.markdown("### Health Check")

        checks = {
            "Dataset": data_path,
            "Report": report_path,
            "Logs": DEFAULT_LOG_PATH,
            "Organized": DEFAULT_ORGANIZED_PATH,
        }

        for name, path in checks.items():
            exists = os.path.exists(path)
            status = "OK" if exists else "Missing"
            st.write(f"{name}: {status}")

    with ops_col_b:
        st.markdown("### Maintenance")

        if st.button("Re-run File Organizer"):
            if df.empty:
                st.warning("No report found.")
            else:
                notify("Organizer started...", icon="")
                with st.spinner("Organizing..."):
                    agent = ReceiptAgent(max_workers=effective_workers, ocr_engine=ocr_engine)
                    agent.organize_files(df.to_dict(orient="records"))
                st.success("Organization complete!")
                notify("Organization complete.", icon="")

        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
            notify("Cache cleared.", icon="")

    st.divider()

    st.markdown("###Recent Agent Logs")

    if os.path.exists(DEFAULT_LOG_PATH):
        with open(DEFAULT_LOG_PATH, "r", encoding="utf-8", errors="ignore") as log_f:
            lines = log_f.readlines()[-100:]
            
            escaped = html.escape("".join(lines))
            st.markdown(
                f"""
                <div class="glass-panel" style="padding:0.8rem;">
                    <pre style="white-space: pre-wrap; margin:0; font-family: 'JetBrains Mono', monospace; font-size:0.9rem; color:var(--text-primary); background: transparent;">
{escaped}
                    </pre>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("📭 Log file not found.")

    st.divider()

    st.markdown("### Support & Diagnostics")

    if st.button("Generate Diagnostics Report"):
        notify("Building diagnostics snapshot...", icon="🩺")
        diag = f"""
# SYSTEM DIAGNOSTICS
Generated: {datetime.now().isoformat()}

## Versions
- App Version: {APP_VERSION}
- Python: {__import__('sys').version}

## Paths
- Dataset: {os.path.exists(data_path)} ({data_path})
- Report: {os.path.exists(report_path)} ({report_path})
- Logs: {os.path.exists(DEFAULT_LOG_PATH)} ({DEFAULT_LOG_PATH})

## Data Summary
- Total Documents: {len(df)}
- Verified: {(df['status'].str.contains('VERIFIED', case=False, na=False).sum()) if not df.empty else 0}
- Health Score: {health}

## Run History
- Total Runs: {len(history)}
- Last Run: {st.session_state.last_run_time}
"""
        st.code(diag, language="text")
        st.download_button(
            "Download Diagnostics",
            data=diag.encode("utf-8"),
            file_name=f"diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )

st.markdown("---")
st.caption(f"Neural OCR v{APP_VERSION} • Built for enterprise receipt intelligence • Last updated: May 2026")

