# pyrefly: ignore [missing-import]
import streamlit as st

def inject_global_css():
    st.html("""
        <link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
        <style>
        :root {
            --primary: #004e9f;
            --surface: #f9f9fb;
            --on-surface: #1a1c1d;
            --on-surface-variant: #414753;
            --surface-container-low: #f3f3f5;
            --surface-container-lowest: #ffffff;
            --outline-variant: #c1c6d5;
            --secondary-container: #6cf8bb;
            --on-secondary-container: #00714d;
            --primary-fixed: #d7e3ff;
            --tertiary-fixed: #ffdbcb;
            --on-tertiary-fixed: #341100;
        }
        
        html, body, .stApp, [data-testid="stHeader"], [class*="css-"] {
            font-family: 'Hanken Grotesk', sans-serif !important;
        }

        span.material-symbols-outlined, 
        i.material-symbols-outlined, 
        .material-symbols-outlined {
            font-family: 'Material Symbols Outlined' !important;
            font-weight: normal !important;
            font-style: normal !important;
            font-size: 24px !important;
            line-height: 1 !important;
            display: inline-block !important;
            direction: ltr !important;
            word-wrap: normal !important;
            white-space: nowrap !important;
            -webkit-font-smoothing: antialiased !important;
            text-rendering: optimizeLegibility !important;
            -moz-osx-font-smoothing: grayscale !important;
            font-feature-settings: 'liga' !important;
        }

        /* Force dark text on primary buttons for better contrast */
        .stButton > button[kind="primary"] {
            background-color: var(--primary) !important;
            color: #ffffff !important;
            border-radius: 9999px !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            border: none !important;
            box-shadow: 0px 4px 14px rgba(0,0,0,0.1) !important;
        }
        
        .stButton > button[kind="secondary"] {
            border-radius: 9999px !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            border: 1px solid var(--outline-variant) !important;
            background-color: var(--surface) !important;
            color: var(--on-surface) !important;
        }

        /* Inputs Styling */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div {
            background-color: #F5F5F7 !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 16px !important;
            color: var(--on-surface) !important;
            transition: border 0.2s ease !important;
        }
        
        .stTextInput > div > div > input:focus, 
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus-within {
            border: 1px solid var(--primary) !important;
            outline: none !important;
        }

        /* File Uploader Card */
        [data-testid="stFileUploadDropzone"] {
            background-color: #ffffff !important;
            border: 2px dashed #c1c6d5 !important;
            border-radius: 10px !important;
            min-height: 315px !important;
            padding: 48px 32px !important;
            box-shadow: 0px 18px 50px rgba(21, 37, 65, 0.06) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        [data-testid="stFileUploader"] {
            max-width: 820px;
            margin: 0 auto;
        }
        [data-testid="stFileUploader"] label {
            display: none !important;
        }
        [data-testid="stFileUploadDropzone"] svg {
            color: #b7becd !important;
            width: 54px !important;
            height: 54px !important;
        }
        [data-testid="stFileUploadDropzone"] button {
            background-color: #eceef2 !important;
            color: #0b1220 !important;
            border: 0 !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
        }
        [data-testid="stFileUploadDropzone"] div {
            color: #0b1220 !important;
        }

        /* Hero Section Styling */
        .hero-wrapper {
            padding: 60px 0;
            text-align: left;
        }
        .hero-title {
            font-size: 48px;
            font-weight: 700;
            line-height: 1.1;
            letter-spacing: -0.02em;
            margin-bottom: 24px;
            color: var(--on-surface);
        }
        .hero-subtitle {
            font-size: 17px;
            font-weight: 400;
            line-height: 1.5;
            color: var(--on-surface-variant);
            max-width: 600px;
            margin-bottom: 32px;
        }
        .hero-image-container {
            width: 100%;
            height: 400px;
            border-radius: 24px;
            overflow: hidden;
            position: relative;
            box-shadow: 0px 10px 40px rgba(0,0,0,0.04);
            background: linear-gradient(135deg, var(--primary-fixed), var(--secondary-container));
        }
        .hero-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0.9;
        }

        /* Features Bento Grid */
        .bento-grid {
            display: flex;
            gap: 24px;
            justify-content: center;
            margin-top: 60px;
            flex-wrap: wrap;
        }
        .bento-card {
            background-color: var(--surface-container-low);
            border-radius: 12px;
            padding: 32px;
            width: 320px;
            box-shadow: 0px 10px 40px rgba(0,0,0,0.04);
            text-align: left;
            transition: transform 0.3s ease;
        }
        .bento-card:hover {
            transform: translateY(-4px);
        }
        .bento-icon {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 16px;
        }
        .icon-1 { background-color: var(--primary-fixed); color: var(--primary); }
        .icon-2 { background-color: var(--secondary-container); color: var(--on-secondary-container); }
        .icon-3 { background-color: var(--tertiary-fixed); color: var(--on-tertiary-fixed); }

        .bento-title {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--on-surface);
            line-height: 1.3;
        }
        .bento-text {
            font-size: 15px;
            color: var(--on-surface-variant);
            line-height: 1.5;
        }

        /* Problem Section */
        .problem-section {
            padding: 64px 20px;
            background-color: var(--surface-container-lowest);
            text-align: center;
            margin-top: 40px;
        }
        .problem-headline {
            font-size: 32px;
            font-weight: 700;
            color: var(--on-surface);
            margin-bottom: 16px;
            letter-spacing: -0.01em;
        }
        .problem-subheadline {
            font-size: 17px;
            color: var(--on-surface-variant);
            max-width: 700px;
            margin: 0 auto 48px auto;
            line-height: 1.5;
        }
        .pain-points-grid {
            display: flex;
            gap: 24px;
            justify-content: center;
            flex-wrap: wrap;
            max-width: 1200px;
            margin: 0 auto;
        }
        .pain-point-card {
            background-color: var(--surface-container-low);
            border-radius: 12px;
            padding: 32px;
            width: 320px;
            text-align: left;
        }
        .pain-point-icon {
            color: var(--primary);
            font-size: 32px;
            margin-bottom: 16px;
        }
        .pain-point-title {
            font-size: 20px;
            font-weight: 600;
            color: var(--on-surface);
            margin-bottom: 8px;
        }
        .pain-point-desc {
            font-size: 15px;
            color: var(--on-surface-variant);
            line-height: 1.5;
        }

        /* Top Nav Bar replacement */
        .top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 28px;
            background-color: #ffffff;
            box-shadow: none;
            margin: 0 -10px 18px -10px;
            border-radius: 0;
        }
        .nav-brand {
            font-size: 24px;
            font-weight: 700;
            color: var(--on-surface);
        }
        .nav-links {
            display: flex;
            gap: 32px;
            font-size: 14px;
            font-weight: 700;
        }
        .nav-link {
            color: var(--on-surface-variant);
            text-decoration: none;
            cursor: pointer;
        }
        .nav-link.active {
            color: var(--primary);
            font-weight: 700;
            border-bottom: 3px solid var(--primary);
            padding-bottom: 8px;
        }
        .nav-actions {
            display: flex;
            align-items: center;
            gap: 18px;
            color: #5b6270;
        }
        .nav-actions .material-symbols-outlined {
            font-size: 25px;
        }
        
        /* Footer */
        .footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            padding: 32px 52px;
            margin: 80px -10px 0 -10px;
            background-color: #f4f5f7;
            border-top: 0;
            color: var(--on-surface-variant);
            font-size: 13px;
        }
        .footer-brand {
            color: #0b1220;
            font-weight: 800;
        }
        .footer-copy {
            color: #007f64;
        }
        .footer-links {
            display: flex;
            gap: 26px;
            color: #17213a;
            font-size: 13px;
            white-space: nowrap;
        }

        /* Metric cards for Upload Page */
        .metric-grid {
            display: flex;
            justify-content: center;
            gap: 16px;
            margin: 32px auto 40px auto;
            flex-wrap: wrap;
            max-width: 820px;
        }
        .metric-card {
            background-color: #f4f5f7;
            border-radius: 8px;
            padding: 20px 24px 18px 24px;
            text-align: center;
            min-width: 236px;
        }
        .metric-title {
            font-size: 13px;
            font-weight: 700;
            color: var(--on-surface);
            margin: 8px 0 4px 0;
        }
        .metric-val {
            font-size: 15px;
            color: var(--on-surface-variant);
        }
        .upload-title {
            padding-top: 12px;
            padding-bottom: 20px;
            text-align: center;
        }
        .upload-title .hero-title {
            font-size: 46px;
            margin: 0 auto 10px auto;
        }
        .upload-title .hero-subtitle {
            margin: 0 auto;
            color: #17213a;
        }
        .optimizer-action {
            max-width: 300px;
            margin: 0 auto;
        }
        .optimizer-action .stButton > button {
            min-height: 62px;
            font-size: 22px !important;
            border-radius: 9999px !important;
            box-shadow: 0px 10px 24px rgba(0, 78, 159, 0.28) !important;
        }
        .dashboard-shell {
            max-width: 1120px;
            margin: 0 auto;
        }
        .dashboard-kicker {
            color: var(--primary);
            font-size: 13px;
            font-weight: 700;
            margin: 8px 0 18px 0;
        }
        .dashboard-title {
            font-size: 42px;
            font-weight: 800;
            color: var(--on-surface);
            margin: 0 0 12px 0;
            letter-spacing: 0;
        }
        .dashboard-subtitle {
            max-width: 680px;
            color: var(--on-surface-variant);
            font-size: 17px;
            line-height: 1.5;
            margin: 0 0 44px 0;
        }
        .dashboard-grid,
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 22px;
        }
        .dashboard-grid {
            margin-bottom: 32px;
        }
        .feature-grid {
            margin: 16px 0 18px 0;
        }
        /* Feature Selection Sidebar Styles */
        .feature-selection-container {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .feature-selection-card {
            background-color: #f4f5f7;
            border-radius: 12px;
            padding: 24px;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.2s ease;
            text-align: left;
        }
        .feature-selection-card .card-icon {
            font-size: 32px;
            color: var(--on-secondary-container);
            margin-bottom: 12px;
        }
        .feature-selection-card h4 {
            margin: 0 0 4px 0;
            font-size: 16px;
            font-weight: 700;
            color: var(--on-surface);
        }
        .feature-selection-card p {
            margin: 0;
            font-size: 13px;
            color: var(--on-surface-variant);
            line-height: 1.4;
        }

        /* Target the feature selector radio specifically */
        [data-testid="stRadioSummary"] { display: none !important; }
        
        div[data-testid="stRadio"] > div[role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 16px;
            border: none !important;
            padding: 0 !important;
        }

        div[data-testid="stRadio"] > div[role="radiogroup"] label {
            background-color: #f4f5f7 !important;
            border-radius: 12px !important;
            padding: 20px 24px !important;
            cursor: pointer !important;
            border: 2px solid transparent !important;
            transition: all 0.2s ease !important;
            margin: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            width: 100% !important;
        }

        div[data-testid="stRadio"] > div[role="radiogroup"] label:hover {
            background-color: #eceef2 !important;
            transform: translateX(4px) !important;
        }

        div[data-testid="stRadio"] > div[role="radiogroup"] label[data-checked="true"] {
            background-color: #ffffff !important;
            border-color: var(--primary) !important;
            box-shadow: 0px 10px 30px rgba(0, 78, 159, 0.08) !important;
        }

        /* Hide the radio circle and its container */
        div[data-testid="stRadio"] > div[role="radiogroup"] label div[class*="st-"] {
            display: none !important;
        }

        /* Show only the label text container */
        div[data-testid="stRadio"] > div[role="radiogroup"] label div[data-testid="stWidgetLabel"] {
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="stRadio"] > div[role="radiogroup"] label div[data-testid="stWidgetLabel"] p {
            font-size: 17px !important;
            font-weight: 700 !important;
            color: var(--on-surface) !important;
            margin-bottom: 4px !important;
        }

        /* Add icons and descriptions via pseudo-elements based on child order */
        /* Card 1: Auto-Solver */
        div[data-testid="stRadio"] > div[role="radiogroup"] label:nth-child(1)::before {
            content: 'tune';
            font-family: 'Material Symbols Outlined' !important;
            font-size: 32px !important;
            color: #007f64 !important;
            margin-bottom: 12px;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] label:nth-child(1)::after {
            content: 'Optimasi diameter pipa otomatis berbasis EPyT.';
            font-size: 13px !important;
            color: var(--on-surface-variant) !important;
            line-height: 1.4;
        }

        /* Card 2: Pressure */
        div[data-testid="stRadio"] > div[role="radiogroup"] label:nth-child(2)::before {
            content: 'valve';
            font-family: 'Material Symbols Outlined' !important;
            font-size: 32px !important;
            color: #007f64 !important;
            margin-bottom: 12px;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] label:nth-child(2)::after {
            content: 'Analisis tekanan node & Triple PRV.';
            font-size: 13px !important;
            color: var(--on-surface-variant) !important;
            line-height: 1.4;
        }

        /* Card 3: Hardy Cross */
        div[data-testid="stRadio"] > div[role="radiogroup"] label:nth-child(3)::before {
            content: 'account_tree';
            font-family: 'Material Symbols Outlined' !important;
            font-size: 32px !important;
            color: #007f64 !important;
            margin-bottom: 12px;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] label:nth-child(3)::after {
            content: 'Analisis loop jaringan manual.';
            font-size: 13px !important;
            color: var(--on-surface-variant) !important;
            line-height: 1.4;
        }
        .status-card,
        .feature-card,
        .summary-card,
        .log-card {
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0px 18px 50px rgba(21, 37, 65, 0.06);
        }
        .status-card {
            padding: 24px;
            min-height: 120px;
        }
        .status-label {
            color: var(--on-surface-variant);
            font-size: 14px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
        }
        .status-value {
            font-size: 32px;
            font-weight: 800;
            color: var(--on-surface);
            margin-bottom: 6px;
        }
        .status-caption {
            color: var(--on-surface-variant);
            font-size: 14px;
        }
        .feature-card {
            padding: 24px;
            min-height: 150px;
            border: 1px solid #eef1f5;
        }
        .feature-card h3 {
            margin: 10px 0 8px 0;
            font-size: 19px;
            color: var(--on-surface);
        }
        .feature-card p {
            margin: 0;
            color: var(--on-surface-variant);
            font-size: 14px;
            line-height: 1.45;
        }
        .feature-icon {
            color: var(--primary);
            font-size: 28px;
        }
        .optimizer-workspace {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 22px;
            margin-top: 28px;
        }
        .summary-card {
            padding: 24px;
        }
        .summary-card h3,
        .log-card h3 {
            margin: 0 0 18px 0;
            font-size: 24px;
        }
        .summary-row {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #e7e9ee;
            padding: 13px 0;
            color: var(--on-surface-variant);
            font-size: 14px;
        }
        .summary-row strong {
            color: var(--on-surface);
            text-align: right;
        }
        .log-card {
            overflow: hidden;
        }
        .log-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px;
        }
        .engine-pill {
            background: #f4f5f7;
            border-radius: 6px;
            color: var(--on-surface-variant);
            font-size: 12px;
            font-weight: 800;
            padding: 8px 12px;
        }
        .log-console {
            background: #2f3332;
            color: #cfd6d4;
            font-family: Consolas, monospace;
            font-size: 13px;
            line-height: 1.8;
            min-height: 260px;
            padding: 24px;
        }
        .log-good {
            color: #66d39b;
            font-weight: 700;
        }
        @media (max-width: 900px) {
            .dashboard-grid,
            .feature-grid,
            .optimizer-workspace {
                grid-template-columns: 1fr;
            }
        }
        @media (max-width: 760px) {
            .top-nav, .footer {
                flex-direction: column;
                align-items: flex-start;
            }
            .footer-links {
                flex-wrap: wrap;
                gap: 14px;
            }
            .metric-card {
                width: 100%;
            }
            .upload-title .hero-title {
                font-size: 34px;
            }
        }
        </style>
    """)

def inject_landing_styles():
    st.html("""
        <style>
        /* Hide sidebar and header on landing page */
        [data-testid="collapsedControl"] {display: none;}
        header {display: none !important;}
        section[data-testid="stSidebar"] {display: none !important;}
        </style>
    """)

def inject_optimizer_styles():
    st.html("""
        <style>
        [data-testid="collapsedControl"] {display: none;}
        section[data-testid="stSidebar"] {display: none !important;}
        </style>
    """)
