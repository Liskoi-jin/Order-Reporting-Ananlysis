import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import os
from collections import defaultdict
import plotly.express as px
import plotly.graph_objects as go
import glob

# 设置页面配置
st.set_page_config(
    page_title="项目数据分析看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 高级CSS样式 - 完整统一的深色主题
st.markdown("""
<style>
:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #10b981;
    --accent: #8b5cf6;
    --warning: #f59e0b;
    --danger: #ef4444;

    /* 深色主题颜色 */
    --dark-bg: #0f172a;
    --darker-bg: #020617;
    --sidebar-bg: #1e293b;
    --card-bg: rgba(30, 41, 59, 0.95);
    --card-border: rgba(99, 102, 241, 0.3);
    --input-bg: rgba(15, 23, 42, 0.8);

    /* 文字颜色 - 高对比度 */
    --text-primary: #ffffff;
    --text-secondary: #e2e8f0;
    --text-muted: #94a3b8;

    /* 其他变量 */
    --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    --shadow-hover: 0 20px 40px rgba(0, 0, 0, 0.6);
    --transition: all 0.3s ease;

    /* 渐变色 */
    --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    --gradient-success: linear-gradient(135deg, #10b981 0%, #059669 100%);
    --gradient-warning: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    --gradient-danger: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

/* ===== 基础重置 ===== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Streamlit应用主体样式 */
.stApp {
    background: var(--dark-bg) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* 背景渐变效果 */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 0% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 100% 100%, rgba(16, 185, 129, 0.1) 0%, transparent 50%),
        linear-gradient(135deg, var(--dark-bg) 0%, #1e1b4b 100%);
    z-index: -2;
    opacity: 0.8;
}

/* ===== 文字样式 ===== */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    line-height: 1.3 !important;
}

h1 { 
    font-size: 2.5rem !important; 
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-top: 0 !important;
}

h2 { 
    font-size: 2rem !important; 
    border-left: 4px solid var(--primary);
    padding-left: 15px;
    margin-top: 2rem !important;
}

h3 { font-size: 1.75rem !important; }
h4 { font-size: 1.5rem !important; }
h5 { font-size: 1.25rem !important; }
h6 { font-size: 1.1rem !important; }

/* 所有文本元素 */
p, span, div, li, td, label, .stMarkdown, .stText, .stAlert {
    color: var(--text-secondary) !important;
    font-weight: 400 !important;
    font-size: 16px !important;
}

/* 强调文字 */
strong, b {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}

/* ===== 侧边栏修复 - 重点 ===== */
/* 侧边栏容器 */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.2) !important;
    padding: 20px 0 !important;
}

/* 侧边栏所有内容 */
[data-testid="stSidebar"] * {
    color: var(--text-secondary) !important;
    background-color: transparent !important;
}

/* 侧边栏标题 */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6 {
    color: var(--text-primary) !important;
}

/* 侧边栏分割线 */
[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.1) !important;
    margin: 1.5rem 0 !important;
}

/* ===== 侧边栏导航菜单样式 ===== */
.sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 20px;
}

.sidebar-nav-item {
    display: flex;
    align-items: center;
    padding: 14px 20px;
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 12px;
    color: var(--text-secondary) !important;
    text-decoration: none !important;
    transition: var(--transition) !important;
    cursor: pointer;
    font-weight: 500 !important;
    font-size: 16px !important;
}

.sidebar-nav-item:hover {
    background: rgba(99, 102, 241, 0.15) !important;
    border-color: var(--primary) !important;
    transform: translateX(5px) !important;
    box-shadow: 0 5px 15px rgba(99, 102, 241, 0.2) !important;
    color: var(--text-primary) !important;
}

.sidebar-nav-item.active {
    background: var(--gradient-primary) !important;
    border-color: var(--primary) !important;
    color: white !important;
    box-shadow: 0 5px 15px rgba(99, 102, 241, 0.3) !important;
    font-weight: 600 !important;
}

.sidebar-nav-icon {
    margin-right: 12px;
    font-size: 1.2rem;
    width: 24px;
    text-align: center;
}

/* ===== 表单控件样式 ===== */
/* 标签 */
.stText label, 
.stSelectbox label, 
.stSlider label, 
.stCheckbox label, 
.stRadio label,
.stDateInput label,
.stTimeInput label,
.stMultiSelect label {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    margin-bottom: 8px !important;
}

/* 文本输入框 */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--input-bg) !important;
    border: 2px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    transition: var(--transition) !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    outline: none !important;
}

/* 下拉选择框 */
.stSelectbox > div > div {
    background: var(--input-bg) !important;
    border: 2px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

.stSelectbox > div > div:hover {
    border-color: var(--primary) !important;
}

/* 滑块 */
.stSlider > div > div > div {
    background: rgba(99, 102, 241, 0.2) !important;
}

.stSlider > div > div > div > div {
    background: var(--gradient-primary) !important;
}

/* 复选框 */
.stCheckbox > label > div:first-child {
    background: var(--input-bg) !important;
    border: 2px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 6px !important;
}

.stCheckbox > label > div:first-child:hover {
    border-color: var(--primary) !important;
}

/* 单选按钮 */
.stRadio > div {
    background: var(--input-bg) !important;
    border: 2px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 10px !important;
    padding: 15px !important;
}

.stRadio > label {
    color: var(--text-primary) !important;
}

/* 文件上传器 */
.stFileUploader {
    background: var(--card-bg) !important;
    border: 2px dashed rgba(99, 102, 241, 0.4) !important;
    border-radius: 15px !important;
    padding: 25px !important;
}

.stFileUploader:hover {
    border-color: var(--primary) !important;
    background: rgba(99, 102, 241, 0.1) !important;
}

/* ===== 卡片样式 ===== */
.custom-card {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 15px !important;
    padding: 25px !important;
    margin-bottom: 20px !important;
    box-shadow: var(--shadow) !important;
    transition: var(--transition) !important;
    backdrop-filter: blur(10px) !important;
}

.custom-card:hover {
    transform: translateY(-5px) !important;
    box-shadow: var(--shadow-hover) !important;
    border-color: var(--primary) !important;
}

/* ===== 按钮样式 ===== */
/* 主要按钮 */
.stButton > button {
    background: var(--gradient-primary) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    padding: 14px 28px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    transition: var(--transition) !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    color: white !important;
}

/* 下载按钮 */
.stDownloadButton > button {
    background: var(--gradient-success) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    padding: 14px 28px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    transition: var(--transition) !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    width: 100% !important;
}

.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
}

/* ===== 表格样式 ===== */
/* Streamlit数据表格 */
.stDataFrame {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

.stDataFrame table {
    background: var(--card-bg) !important;
    color: var(--text-secondary) !important;
}

.stDataFrame thead th {
    background: rgba(99, 102, 241, 0.3) !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    padding: 15px !important;
    border-bottom: 2px solid rgba(99, 102, 241, 0.5) !important;
}

.stDataFrame tbody td {
    color: var(--text-secondary) !important;
    padding: 12px 15px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.stDataFrame tbody tr:hover {
    background: rgba(99, 102, 241, 0.1) !important;
}

/* Pandas数据表格 */
.dataframe {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

.dataframe thead th {
    background: rgba(99, 102, 241, 0.3) !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    padding: 15px !important;
    border-bottom: 2px solid rgba(99, 102, 241, 0.5) !important;
}

.dataframe tbody td {
    color: var(--text-secondary) !important;
    padding: 12px 15px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.dataframe tbody tr:hover {
    background: rgba(99, 102, 241, 0.1) !important;
}

/* ===== 选项卡样式 ===== */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
    padding: 5px !important;
    margin-bottom: 25px !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    margin: 0 2px !important;
    font-weight: 500 !important;
    font-size: 16px !important;
    transition: var(--transition) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(99, 102, 241, 0.1) !important;
    color: var(--text-primary) !important;
}

.stTabs [aria-selected="true"] {
    background: var(--gradient-primary) !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
}

/* ===== 进度条样式 ===== */
.stProgress > div > div > div > div {
    background: var(--gradient-primary) !important;
}

/* ===== 警告提示样式 ===== */
.stAlert {
    background: rgba(30, 41, 59, 0.9) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 12px !important;
    color: var(--text-secondary) !important;
    border-left: 4px solid !important;
    backdrop-filter: blur(10px) !important;
}

.stAlert [data-testid="stMarkdownContainer"] {
    color: var(--text-secondary) !important;
}

/* 不同类型的提示 */
div[data-testid="stAlert"] > div:first-child {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

/* ===== 展开器样式 ===== */
.streamlit-expanderHeader {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    padding: 15px 20px !important;
}

.streamlit-expanderContent {
    background: rgba(30, 41, 59, 0.8) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 0 0 10px 10px !important;
    border-top: none !important;
    padding: 20px !important;
}

/* ===== 滚动条样式 ===== */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(30, 41, 59, 0.5);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb {
    background: var(--primary);
    border-radius: 5px;
    border: 2px solid transparent;
    background-clip: padding-box;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary-dark);
}

/* ===== 统计卡片 ===== */
.stat-card {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 15px !important;
    padding: 25px !important;
    text-align: center !important;
    transition: var(--transition) !important;
    height: 100% !important;
    backdrop-filter: blur(10px) !important;
}

.stat-card:hover {
    transform: translateY(-5px) !important;
    box-shadow: var(--shadow-hover) !important;
    border-color: var(--primary) !important;
}

.stat-value {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    margin-bottom: 10px !important;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    font-size: 1rem !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
}

/* ===== 图标样式 ===== */
.icon-wrapper {
    width: 60px;
    height: 60px;
    background: rgba(99, 102, 241, 0.2);
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    border: 2px solid rgba(99, 102, 241, 0.3);
}

.icon-wrapper i {
    font-size: 1.5rem;
    color: var(--primary);
}

/* ===== 欢迎卡片 ===== */
.welcome-card {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.15)) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 20px !important;
    padding: 40px !important;
    margin-bottom: 40px !important;
    text-align: center !important;
    backdrop-filter: blur(20px) !important;
}

/* ===== 上传区域卡片 ===== */
.upload-card {
    background: var(--card-bg) !important;
    border: 2px dashed rgba(99, 102, 241, 0.4) !important;
    border-radius: 20px !important;
    padding: 40px 30px !important;
    text-align: center !important;
    cursor: pointer !important;
    transition: var(--transition) !important;
    height: 100% !important;
}

.upload-card:hover {
    border-color: var(--primary) !important;
    background: rgba(99, 102, 241, 0.1) !important;
    transform: translateY(-5px) !important;
}

/* ===== 时间卡片样式 ===== */
.time-card {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 15px !important;
    padding: 20px !important;
    margin-bottom: 20px !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: var(--shadow) !important;
    height: 100% !important;
}

.time-card:hover {
    border-color: var(--primary) !important;
    box-shadow: var(--shadow-hover) !important;
}

.time-card h4 {
    color: var(--text-primary) !important;
    font-size: 1.2rem !important;
    margin-bottom: 20px !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

.time-card h4::before {
    content: '';
    width: 4px;
    height: 20px;
    background: var(--gradient-primary);
    border-radius: 2px;
}

/* ===== 修复所有白色背景问题 ===== */
/* 主内容区域 */
.main .block-container {
    background: transparent !important;
    padding-top: 2rem !important;
}

/* 所有streamlit组件的背景 */
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"],
div[data-testid="stColumn"] {
    background: transparent !important;
}

/* 移除所有默认白色背景 */
div[style*="background-color: white"],
div[style*="background: white"],
.bg-white {
    background: transparent !important;
}

/* ===== 修复Plotly图表 ===== */
.js-plotly-plot .plotly {
    background: transparent !important;
}

.js-plotly-plot .modebar {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 8px !important;
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.75rem !important; }
    h3 { font-size: 1.5rem !important; }

    .stat-value {
        font-size: 2rem !important;
    }

    .custom-card,
    .welcome-card,
    .upload-card {
        padding: 20px !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        padding: 12px 20px !important;
        font-size: 15px !important;
    }
}

/* ===== 动画效果 ===== */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeIn 0.6s ease-out forwards;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
    100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
}

.pulse {
    animation: pulse 2s infinite;
}

/* ===== 工具类 ===== */
.text-gradient {
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.border-gradient {
    border: 2px solid transparent;
    background: linear-gradient(var(--card-bg), var(--card-bg)) padding-box,
                var(--gradient-primary) border-box;
}

.glass-effect {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* ===== 修复日期时间选择器 - 重要修复 ===== */
/* 日期输入框 */
.stDateInput > div > div > input {
    background: var(--input-bg) !important;
    border: 2px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    width: 100% !important;
}

.stDateInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    outline: none !important;
}

/* 日期选择器弹出框 */
div[data-baseweb="popover"] {
    background-color: var(--card-bg) !important;
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 10px !important;
}

/* 日历容器 - 深色背景 */
div[data-baseweb="calendar"] {
    background-color: var(--card-bg) !important;
    background: var(--card-bg) !important;
    color: var(--text-primary) !important;
}

/* 日历表格 */
div[data-baseweb="calendar"] table {
    background-color: transparent !important;
    background: transparent !important;
}

/* 日历单元格 */
div[data-baseweb="calendar"] td,
div[data-baseweb="calendar"] th {
    background-color: transparent !important;
    background: transparent !important;
    color: var(--text-primary) !important;
}

/* 日历按钮 */
div[data-baseweb="calendar"] button {
    background-color: transparent !important;
    background: transparent !important;
    color: var(--text-primary) !important;
}

div[data-baseweb="calendar"] button:hover {
    background-color: rgba(99, 102, 241, 0.2) !important;
    background: rgba(99, 102, 241, 0.2) !important;
}

div[data-baseweb="calendar"] button[aria-selected="true"] {
    background-color: var(--primary) !important;
    background: var(--primary) !important;
    color: white !important;
}

/* 日历头部 */
div[data-baseweb="calendar"] > div:first-child {
    background-color: rgba(99, 102, 241, 0.1) !important;
    background: rgba(99, 102, 241, 0.1) !important;
    border-bottom: 1px solid var(--card-border) !important;
    color: var(--text-primary) !important;
}

/* 时间选择器弹出框 */
.stTimeInput > div > div > input {
    background: var(--input-bg) !important;
    border: 2px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    width: 100% !important;
}

.stTimeInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    outline: none !important;
}

/* 时间选择器弹出框 */
.stTimeInput > div > div > div,
div[role="listbox"][data-baseweb="select"] {
    background-color: var(--card-bg) !important;
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
}

/* 时间选择器选项 */
div[role="listbox"][data-baseweb="select"] > div {
    background-color: transparent !important;
    background: transparent !important;
    color: var(--text-primary) !important;
}

div[role="listbox"][data-baseweb="select"] > div:hover {
    background-color: rgba(99, 102, 241, 0.1) !important;
    background: rgba(99, 102, 241, 0.1) !important;
}

div[role="listbox"][data-baseweb="select"] > div[aria-selected="true"] {
    background-color: rgba(99, 102, 241, 0.2) !important;
    background: rgba(99, 102, 241, 0.2) !important;
}

/* ===== 修复多选框 ===== */
.stMultiSelect > div > div {
    background: var(--input-bg) !important;
    border: 2px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

.stMultiSelect > div > div:hover {
    border-color: var(--primary) !important;
}

/* ===== 修复数字输入框 ===== */
input[type="number"] {
    color: var(--text-primary) !important;
}

/* ===== 修复占位符颜色 ===== */
::placeholder {
    color: var(--text-muted) !important;
    opacity: 0.7 !important;
}

/* ===== 修复链接颜色 ===== */
a {
    color: var(--primary) !important;
    text-decoration: none !important;
    transition: var(--transition) !important;
}

a:hover {
    color: #a78bfa !important;
    text-decoration: underline !important;
}

/* ===== 修复所有下拉菜单 ===== */
div[role="listbox"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 10px !important;
}

div[role="option"] {
    color: var(--text-primary) !important;
}

div[role="option"]:hover {
    background: rgba(99, 102, 241, 0.1) !important;
}

/* ===== 修复所有日期时间选择器的占位符 ===== */
.stDateInput input::placeholder,
.stTimeInput input::placeholder {
    color: var(--text-muted) !important;
    opacity: 0.7 !important;
}

/* ===== 修复日期时间选择器图标 ===== */
.stDateInput input + div svg,
.stTimeInput input + div svg {
    fill: var(--text-secondary) !important;
}

.stDateInput input:focus + div svg,
.stTimeInput input:focus + div svg {
    fill: var(--primary) !important;
}

/* ===== 时间选择器标签样式 ===== */
.time-label {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    margin-bottom: 8px !important;
    display: block !important;
}

/* ===== 强制修复白色背景 ===== */
/* 强制所有日历相关的白色背景改为深色 */
div[data-baseweb="calendar"] div[style*="background-color: white"],
div[data-baseweb="calendar"] div[style*="background: white"],
div[data-baseweb="popover"] div[style*="background-color: white"],
div[data-baseweb="popover"] div[style*="background: white"] {
    background-color: var(--card-bg) !important;
    background: var(--card-bg) !important;
}

/* 强制日历按钮白色背景改为透明 */
div[data-baseweb="calendar"] button[style*="background-color: white"],
div[data-baseweb="calendar"] button[style*="background: white"] {
    background-color: transparent !important;
    background: transparent !important;
}

/* 修复月份年份下拉菜单 */
div[data-baseweb="popover"] > div {
    background: var(--card-bg) !important;
}

/* 修复Streamlit默认的白色背景 */
div[style*="background: rgb(255, 255, 255)"],
div[style*="background-color: rgb(255, 255, 255)"],
div[style*="background: #ffffff"],
div[style*="background-color: #ffffff"] {
    background: var(--card-bg) !important;
    background-color: var(--card-bg) !important;
}

/* ===== 极端解决方案：强制覆盖所有可能的白色背景 ===== */
/* 使用!important强制覆盖 */
div[data-baseweb="popover"] *,
div[data-baseweb="calendar"] *,
div[role="listbox"] * {
    background-color: var(--card-bg) !important;
    background: var(--card-bg) !important;
}

/* 特定元素单独处理 */
div[data-baseweb="calendar"] button,
div[role="listbox"] > div {
    background-color: transparent !important;
    background: transparent !important;
}

/* 覆盖Streamlit的默认白色背景 */
div[style*="background"],
div[style*="background-color"] {
    background-color: var(--card-bg) !important;
    background: var(--card-bg) !important;
}

/* 月份年份选择器下拉菜单 */
div[data-baseweb="popover"] > div > div {
    background-color: var(--card-bg) !important;
    background: var(--card-bg) !important;
}
</style>

<script>
// 通过JavaScript强制设置日期时间选择器的背景色
document.addEventListener('DOMContentLoaded', function() {
    function forceDarkTheme() {
        // 查找所有日期时间选择器元素
        const popovers = document.querySelectorAll('[data-baseweb="popover"]');
        const calendars = document.querySelectorAll('[data-baseweb="calendar"]');
        const timePickers = document.querySelectorAll('[role="listbox"][data-baseweb="select"]');

        // 设置弹出框背景
        popovers.forEach(el => {
            el.style.backgroundColor = 'rgba(30, 41, 59, 0.95)';
            el.style.background = 'rgba(30, 41, 59, 0.95)';
        });

        // 设置日历背景
        calendars.forEach(el => {
            el.style.backgroundColor = 'rgba(30, 41, 59, 0.95)';
            el.style.background = 'rgba(30, 41, 59, 0.95)';
            el.style.color = '#ffffff';
        });

        // 设置时间选择器背景
        timePickers.forEach(el => {
            el.style.backgroundColor = 'rgba(30, 41, 59, 0.95)';
            el.style.background = 'rgba(30, 41, 59, 0.95)';
        });
    }

    // 初始执行
    forceDarkTheme();

    // 定时执行，确保新创建的元素也被设置
    setInterval(forceDarkTheme, 1000);
});
</script>
""", unsafe_allow_html=True)

# 应用标题
st.markdown("""
<div class="welcome-card fade-in">
    <h1>📊 项目数据分析看板</h1>
    <p style="font-size: 1.2rem; color: var(--text-secondary); margin-top: 10px;">
        专业的数据分析工具 | 提供完整的违规率分析和统计功能
    </p>
</div>
""", unsafe_allow_html=True)

# 初始化session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = '上传数据文件'
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'local_file_path' not in st.session_state:
    st.session_state.local_file_path = None
if 'show_raw_data' not in st.session_state:
    st.session_state.show_raw_data = False
if 'highlight_violations' not in st.session_state:
    st.session_state.highlight_violations = True
if 'show_charts' not in st.session_state:
    st.session_state.show_charts = True
if 'show_detailed_analysis' not in st.session_state:
    st.session_state.show_detailed_analysis = True
if 'high_violation_threshold' not in st.session_state:
    st.session_state.high_violation_threshold = 20
if 'medium_violation_threshold' not in st.session_state:
    st.session_state.medium_violation_threshold = 10

# 侧边栏配置
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0 10px 0;">
        <h2 style="color: var(--text-primary); margin-bottom: 30px; text-align: center;">📊 导航菜单</h2>
    </div>
    """, unsafe_allow_html=True)

    # 侧边栏导航菜单
    st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)

    # 上传数据文件按钮
    if st.button("📤 上传数据文件",
                 key="nav_upload",
                 use_container_width=True,
                 type="primary" if st.session_state.current_page == "上传数据文件" else "secondary"):
        st.session_state.current_page = "上传数据文件"
        st.rerun()

    # 违规率分析按钮
    if st.button("📈 违规率分析",
                 key="nav_analysis",
                 use_container_width=True,
                 type="primary" if st.session_state.current_page == "违规率分析" else "secondary"):
        st.session_state.current_page = "违规率分析"
        st.rerun()

    # 违规率统计按钮
    if st.button("📊 违规率统计",
                 key="nav_statistics",
                 use_container_width=True,
                 type="primary" if st.session_state.current_page == "违规率统计" else "secondary"):
        st.session_state.current_page = "违规率统计"
        st.rerun()

    # 分析设置按钮
    if st.button("⚙️ 分析设置",
                 key="nav_settings",
                 use_container_width=True,
                 type="primary" if st.session_state.current_page == "分析设置" else "secondary"):
        st.session_state.current_page = "分析设置"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 文件状态显示
    if st.session_state.uploaded_file is not None:
        st.success("✅ 已加载上传文件")
    elif st.session_state.local_file_path is not None:
        st.success(f"✅ 已加载本地文件: {os.path.basename(st.session_state.local_file_path)}")
    else:
        st.info("📁 请先上传或选择数据文件")


# 数据解析和清洗函数
def parse_date(date_str):
    """解析各种格式的日期字符串"""
    if not date_str or pd.isna(date_str) or str(date_str) == '1/1/1970 08:00:00':
        return None

    date_str = str(date_str).strip()

    # 尝试多种日期格式
    date_formats = [
        '%d/%m/%Y %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
        '%d/%m/%Y',
        '%Y-%m-%d',
        '%Y/%m/%d %H:%M:%S',
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue

    return None


def read_csv_safe(file_path):
    """安全读取CSV文件"""
    try:
        # 先尝试直接读取
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"❌ 直接读取失败: {e}")

    # 尝试不同编码
    encodings = ['gbk', 'gb2312', 'utf-8', 'latin1', 'utf-8-sig']
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding, engine='python')
            return df
        except Exception as e:
            continue

    return None


# ==================== 违规率分析页面函数 ====================
def analyze_complete_data(df):
    """使用完整计算逻辑分析数据（不应用时间筛选）"""
    try:
        # 检查必要的列是否存在
        required_columns = ['activity_name', 'project_name', 'channel_name', 'bonus_invalid_text', 'bonus_text']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"❌ 缺少必要的列: {missing_columns}")
            st.info(f"📊 文件中的列: {list(df.columns)}")
            return None

        # 检查是否有order_text列
        if 'order_text' not in df.columns:
            st.error("❌ 缺少order_text列，无法计算实际计佣GMV")
            st.info(f"📊 文件中的列: {list(df.columns)}")
            return None

        # 检查是否有estimate_cos_price和actual_cos_price列
        if 'estimate_cos_price' not in df.columns:
            st.error("❌ 缺少estimate_cos_price列，无法计算预估计佣GMV")
            st.info(f"📊 文件中的列: {list(df.columns)}")
            return None

        if 'actual_cos_price' not in df.columns:
            st.error("❌ 缺少actual_cos_price列，无法计算实际计佣GMV")
            st.info(f"📊 文件中的列: {list(df.columns)}")
            return None

        # 检查是否有project_code列用于排序
        if 'project_code' not in df.columns:
            use_project_code = False
        else:
            use_project_code = True

        # 确保estimate_cos_price和actual_cos_price是数值类型
        for col in ['estimate_cos_price', 'actual_cos_price']:
            if not pd.api.types.is_numeric_dtype(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    st.error(f"❌ 转换{col}为数值类型时出错: {e}")
                    return None

        # 如果使用project_code排序，我们需要获取每个项目的project_code
        if use_project_code:
            # 获取每个项目的project_code（取第一个非空值）
            project_code_map = {}
            for project_name in df['project_name'].unique():
                project_codes = df[df['project_name'] == project_name]['project_code'].dropna().unique()
                if len(project_codes) > 0:
                    project_code_map[project_name] = str(project_codes[0])
                else:
                    project_code_map[project_name] = project_name  # 如果没有project_code，使用项目名称

        # 计算项目级别的统计数据（用于项目违规率和项目违规GMV占比）
        project_stats = {}
        for project_name in df['project_name'].unique():
            project_group = df[df['project_name'] == project_name]

            # 项目总订单数
            project_total_count = len(project_group)

            # 项目总GMV（预估）
            project_estimate_gmv = project_group['estimate_cos_price'].sum()

            # 项目总GMV（实际） - 只计算bonus_text为"有效"且order_text为"已完成"的订单
            project_actual_gmv = project_group[
                (project_group['bonus_text'] == '有效') &
                (project_group['order_text'] == '已完成')
                ]['actual_cos_price'].sum()

            # 项目无效-违规订单数
            project_invalid_violation = (project_group['bonus_invalid_text'] == '无效-违规订单').sum()

            # 项目无效-风险订单数
            project_invalid_risk = (project_group['bonus_invalid_text'] == '无效-风险订单').sum()

            # 项目无效-违规订单GMV（预估）
            project_invalid_violation_gmv = project_group.loc[
                project_group['bonus_invalid_text'] == '无效-违规订单',
                'estimate_cos_price'
            ].sum()

            # 项目无效-风险订单GMV（预估）
            project_invalid_risk_gmv = project_group.loc[
                project_group['bonus_invalid_text'] == '无效    -风险订单',
                'estimate_cos_price'
            ].sum()

            # 项目违规率
            project_violation_rate = (
                                             project_invalid_violation + project_invalid_risk) / project_total_count if project_total_count > 0 else 0

            # 项目违规GMV占比（使用预估GMV）
            project_violation_gmv_ratio = (
                                                  project_invalid_violation_gmv + project_invalid_risk_gmv) / project_estimate_gmv if project_estimate_gmv > 0 else 0

            project_stats[project_name] = {
                'project_total_count': project_total_count,
                'project_estimate_gmv': project_estimate_gmv,
                'project_actual_gmv': project_actual_gmv,
                'project_invalid_violation': project_invalid_violation,
                'project_invalid_risk': project_invalid_risk,
                'project_invalid_violation_gmv': project_invalid_violation_gmv,
                'project_invalid_risk_gmv': project_invalid_risk_gmv,
                'project_violation_rate': project_violation_rate,
                'project_violation_gmv_ratio': project_violation_gmv_ratio
            }

        # 获取所有唯一的项目-渠道组合
        unique_combinations = df[['project_name', 'channel_name']].drop_duplicates()

        # 将组合转换为列表
        project_channel_combinations = []
        for _, row in unique_combinations.iterrows():
            project_channel_combinations.append((row['project_name'], row['channel_name']))

        # 用于存储结果的列表
        results = []

        # 按照数据中实际存在的项目名称和渠道名称组合处理
        for project_name, channel_name in project_channel_combinations:
            # 筛选对应项目名称和渠道名称的数据
            group = df[(df['project_name'] == project_name) & (df['channel_name'] == channel_name)]
            total_count = len(group)

            # 如果没有数据，跳过
            if total_count == 0:
                continue

            # 统计 bonus_invalid_text 中的各类无效原因
            invalid_violation_mask = (group['bonus_invalid_text'] == '无效-违规订单')
            invalid_risk_mask = (group['bonus_invalid_text'] == '无效-风险订单')
            invalid_cancel_mask = (group['bonus_invalid_text'] == '无效-取消')
            invalid_split_mask = (group['bonus_invalid_text'] == '无效-拆单')
            invalid_return_mask = (group['bonus_invalid_text'] == '无效-退货')

            invalid_violation = invalid_violation_mask.sum()
            invalid_risk = invalid_risk_mask.sum()
            invalid_cancel = invalid_cancel_mask.sum()
            invalid_split = invalid_split_mask.sum()
            invalid_return = invalid_return_mask.sum()

            # 其他无效原因
            invalid_other = (group['bonus_invalid_text'].notna() &
                             (group['bonus_invalid_text'] != '') &
                             (group['bonus_invalid_text'] != '无效-取消') &
                             (group['bonus_invalid_text'] != '无效-违规订单') &
                             (group['bonus_invalid_text'] != '无效-风险订单') &
                             (group['bonus_invalid_text'] != '无效-拆单') &
                             (group['bonus_invalid_text'] != '无效-退货')).sum()

            # 计算无效订单总数（所有无效原因的总和）
            total_invalid_orders = invalid_cancel + invalid_violation + invalid_risk + invalid_split + invalid_return + invalid_other

            # 计算预估计佣GMV - 使用estimate_cos_price
            estimate_commission_gmv = group['estimate_cos_price'].sum() if not group[
                'estimate_cos_price'].isna().all() else 0

            # 计算预估完成GMV - 只计算bonus_text为"有效"的订单
            valid_mask = (group['bonus_text'] == '有效')
            estimate_completed_gmv = group.loc[valid_mask, 'estimate_cos_price'].sum() if not group[
                'estimate_cos_price'].isna().all() else 0

            # 计算实际计佣GMV - 只计算bonus_text为"有效"且order_text为"已完成"的订单
            valid_completed_mask = (group['bonus_text'] == '有效') & (group['order_text'] == '已完成')
            actual_commission_gmv = group.loc[valid_completed_mask, 'actual_cos_price'].sum() if not group[
                'actual_cos_price'].isna().all() else 0

            # 计算无效-违规订单GMV - 使用estimate_cos_price
            invalid_violation_gmv = group.loc[invalid_violation_mask, 'estimate_cos_price'].sum() if not group[
                'estimate_cos_price'].isna().all() else 0

            # 计算无效-风险订单GMV - 使用estimate_cos_price
            invalid_risk_gmv = group.loc[invalid_risk_mask, 'estimate_cos_price'].sum() if not group[
                'estimate_cos_price'].isna().all() else 0

            # 计算GMV占比（占预估计佣GMV的比例）
            invalid_violation_gmv_ratio = invalid_violation_gmv / estimate_commission_gmv if estimate_commission_gmv > 0 else 0
            invalid_risk_gmv_ratio = invalid_risk_gmv / estimate_commission_gmv if estimate_commission_gmv > 0 else 0

            # 计算各类订单占比（占订单总数的比例）
            invalid_ratio_total = total_invalid_orders / total_count if total_count > 0 else 0
            violation_ratio_total = invalid_violation / total_count if total_count > 0 else 0
            risk_ratio_total = invalid_risk / total_count if total_count > 0 else 0

            # 计算渠道违规率（违规订单数占比）
            channel_violation_rate = (invalid_violation + invalid_risk) / total_count if total_count > 0 else 0

            # 计算渠道违规GMV占比
            channel_violation_gmv_ratio = (
                                                  invalid_violation_gmv + invalid_risk_gmv) / estimate_commission_gmv if estimate_commission_gmv > 0 else 0

            # 获取日期（假设使用数据中的最小日期或当前日期）
            date = pd.Timestamp.now().strftime('%Y-%m-%d')

            # 获取项目级别的统计数据
            project_stat = project_stats.get(project_name, {})

            # 创建结果字典
            result_dict = {
                '日期': date,
                '项目名称': project_name,
                '渠道名称': channel_name,
                '订单总数': total_count,
                '预估计佣GMV': f"{estimate_commission_gmv:.2f}",
                '预估完成': f"{estimate_completed_gmv:.2f}",
                '实际计佣GMV': f"{actual_commission_gmv:.2f}",
                '无效订单总数': total_invalid_orders,
                '无效订单占比': f"{invalid_ratio_total:.2%}",
                '无效-违规订单数': invalid_violation,
                '无效-违规订单占比': f"{violation_ratio_total:.2%}",
                '无效-违规订单GMV': f"{invalid_violation_gmv:.2f}",
                '无效-违规订单GMV占比': f"{invalid_violation_gmv_ratio:.2%}",
                '无效-风险订单数': invalid_risk,
                '无效-风险订单占比': f"{risk_ratio_total:.2%}",
                '无效-风险订单GMV': f"{invalid_risk_gmv:.2f}",
                '无效-风险订单GMV占比': f"{invalid_risk_gmv_ratio:.2%}",
                '违规率': f"{channel_violation_rate:.2%}",
                '违规GMV占比': f"{channel_violation_gmv_ratio:.2%}",
                '项目违规率': f"{project_stat.get('project_violation_rate', 0):.2%}",
                '项目违规GMV占比': f"{project_stat.get('project_violation_gmv_ratio', 0):.2%}"
            }

            # 如果有项目编号，添加到结果中
            if use_project_code:
                project_code = project_code_map.get(project_name, "")
                result_dict['项目编号'] = project_code

            results.append(result_dict)

        # 转换为 DataFrame
        result_df = pd.DataFrame(results)

        # 按照项目编号排序（如果有项目编号）
        if use_project_code:
            # 确保项目编号可以正确排序
            try:
                # 尝试将项目编号转换为整数进行排序
                result_df['项目编号_排序'] = pd.to_numeric(result_df['项目编号'], errors='coerce')
                result_df = result_df.sort_values('项目编号_排序', ascending=True)
                result_df = result_df.drop('项目编号_排序', axis=1)
            except:
                # 如果不能转换为数字，按字符串排序
                result_df = result_df.sort_values('项目编号', ascending=True)
        else:
            # 按项目名称排序
            result_df = result_df.sort_values('项目名称', ascending=True)

        # 按照要求的字段顺序重新排列
        required_columns_order = [
            '日期',
            '项目名称',
            '渠道名称',
            '订单总数',
            '预估计佣GMV',
            '预估完成',
            '实际计佣GMV',
            '无效订单总数',
            '无效订单占比',
            '无效-违规订单数',
            '无效-违规订单占比',
            '无效-违规订单GMV',
            '无效-违规订单GMV占比',
            '无效-风险订单数',
            '无效-风险订单占比',
            '无效-风险订单GMV',
            '无效-风险订单GMV占比',
            '违规率',
            '违规GMV占比',
            '项目违规率',
            '项目违规GMV占比'
        ]

        # 如果有项目编号，添加到列顺序中
        if use_project_code:
            # 在项目名称之后，渠道名称之前插入项目编号
            required_columns_order.insert(2, '项目编号')  # 位置2（0-based索引）

        # 确保只保留要求的列
        result_df = result_df[required_columns_order]

        return {
            'analysis_result': result_df,
            'filtered_data': df,
            'total_combinations': len(project_channel_combinations),
            'total_records': len(df),
            'use_project_code': use_project_code
        }

    except Exception as e:
        st.error(f"❌ 分析数据时出错: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None


# ==================== 违规率统计页面函数 ====================
def analyze_violation_statistics(df, order_start_dt, order_end_dt, finish_start_dt, finish_end_dt):
    """分析违规率统计"""
    try:
        # 检查必要的列是否存在
        required_columns = ['project_name', 'channel_name', 'bonus_invalid_text', 'bonus_text', 'order_time',
                            'finish_time']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"❌ 缺少必要的列: {missing_columns}")
            st.info(f"📊 文件中的列: {list(df.columns)}")
            return None

        # 解析日期列
        df['order_time_parsed'] = df['order_time'].apply(parse_date)
        df['finish_time_parsed'] = df['finish_time'].apply(parse_date)

        # 筛选下单时间在指定范围内的所有订单
        order_mask = df['order_time_parsed'].notna()

        if order_start_dt:
            order_mask = order_mask & (df['order_time_parsed'] >= order_start_dt)
        if order_end_dt:
            order_mask = order_mask & (df['order_time_parsed'] <= order_end_dt)

        order_filtered_df = df[order_mask].copy()

        if len(order_filtered_df) == 0:
            st.warning("⚠️ 没有符合下单时间筛选条件的订单")
            return None

        # 获取所有唯一的项目-渠道组合（基于下单时间筛选后的数据）
        unique_combinations = order_filtered_df[['project_name', 'channel_name']].drop_duplicates()

        # 将组合转换为列表
        project_channel_combinations = []
        for _, row in unique_combinations.iterrows():
            project_channel_combinations.append((row['project_name'], row['channel_name']))

        # 用于存储结果的列表
        results = []

        # 按照数据中实际存在的项目名称和渠道名称组合处理
        for project_name, channel_name in project_channel_combinations:
            # 筛选对应项目名称和渠道名称的数据（基于下单时间）
            order_group = order_filtered_df[
                (order_filtered_df['project_name'] == project_name) &
                (order_filtered_df['channel_name'] == channel_name)
                ]

            # 订单总数（基于下单时间）
            order_total_count = len(order_group)

            # 筛选完成时间在指定范围内的订单
            finish_group = order_group.copy()

            finish_mask = finish_group['finish_time_parsed'].notna()

            if finish_start_dt:
                finish_mask = finish_mask & (finish_group['finish_time_parsed'] >= finish_start_dt)
            if finish_end_dt:
                finish_mask = finish_mask & (finish_group['finish_time_parsed'] <= finish_end_dt)

            finish_filtered = finish_group[finish_mask]

            # 计算无效订单总数（基于完成时间）
            # bonus_text = '无效' 的订单
            invalid_orders = finish_filtered[finish_filtered['bonus_text'] == '无效']
            invalid_order_count = len(invalid_orders)

            # 计算违规订单数（基于完成时间）
            # bonus_invalid_text = '无效-风险订单' 或 '无效-违规订单'
            violation_orders = finish_filtered[
                (finish_filtered['bonus_invalid_text'] == '无效-风险订单') |
                (finish_filtered['bonus_invalid_text'] == '无效-违规订单')
                ]
            violation_order_count = len(violation_orders)

            # 计算违规率
            violation_rate = violation_order_count / order_total_count if order_total_count > 0 else 0

            # 创建结果字典
            result_dict = {
                '项目名称': project_name,
                '渠道名称': channel_name,
                '订单总数': order_total_count,  # 基于下单时间
                '无效订单总数': invalid_order_count,  # 基于完成时间
                '违规订单数': violation_order_count,  # 基于完成时间
                '违规率': f"{violation_rate:.2%}"
            }

            results.append(result_dict)

        # 转换为 DataFrame
        result_df = pd.DataFrame(results)

        # 按项目名称排序
        result_df = result_df.sort_values('项目名称', ascending=True)

        return {
            'analysis_result': result_df,
            'order_filtered_data': order_filtered_df,
            'total_combinations': len(project_channel_combinations),
            'order_total_count': len(order_filtered_df)
        }

    except Exception as e:
        st.error(f"❌ 分析违规率统计时出错: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None


# ==================== 页面1：上传数据文件 ====================
def page_upload_data():
    """上传数据文件页面"""
    st.markdown("""
    <div class="custom-card fade-in">
        <h2>📤 上传数据文件</h2>
        <p>请上传CSV格式的数据文件或从本地目录选择文件</p>
    </div>
    """, unsafe_allow_html=True)

    # 创建两列布局
    col1, col2 = st.columns(2)

    with col1:
        # 文件上传部分
        st.markdown("""
        <div class="upload-card">
            <div class="icon-wrapper" style="margin: 0 auto 20px auto;">
                <span style="font-size: 2rem;">📤</span>
            </div>
            <h3>上传数据文件</h3>
            <p>点击上传CSV格式的数据文件</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "选择CSV文件",
            type=["csv"],
            help="请上传包含项目数据的CSV文件",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            try:
                # 尝试读取文件
                with st.spinner("正在读取文件..."):
                    df = pd.read_csv(uploaded_file)
                    st.session_state.uploaded_file = df
                    st.session_state.local_file_path = None
                    st.success("✅ 文件上传成功！")

                    # 显示文件信息
                    st.info(f"📊 文件信息：{uploaded_file.name}")
                    st.info(f"📊 数据行数：{len(df):,}")
                    st.info(f"📊 数据列数：{len(df.columns)}")

                    # 显示列名预览
                    with st.expander("📋 查看数据列名", expanded=False):
                        st.write("数据列：", list(df.columns))

                    # 显示数据预览
                    with st.expander("👀 预览数据（前10行）", expanded=False):
                        st.dataframe(df.head(10), use_container_width=True)

            except Exception as e:
                st.error(f"❌ 读取文件失败: {e}")

    with col2:
        # 本地文件选择部分
        st.markdown("""
        <div class="upload-card">
            <div class="icon-wrapper" style="margin: 0 auto 20px auto;">
                <span style="font-size: 2rem;">📁</span>
            </div>
            <h3>选择本地文件</h3>
            <p>从本地目录选择已存在的文件</p>
        </div>
        """, unsafe_allow_html=True)

        # 获取当前目录的CSV文件
        current_dir = os.getcwd()
        csv_files = glob.glob(os.path.join(current_dir, "*.csv"))

        if csv_files:
            file_options = ["请选择..."] + [os.path.basename(f) for f in csv_files]
            selected_file = st.selectbox("选择本地CSV文件", file_options, key="local_file_select")

            if selected_file and selected_file != "请选择...":
                # 找到完整路径
                for file_path in csv_files:
                    if os.path.basename(file_path) == selected_file:
                        try:
                            with st.spinner(f"正在读取文件: {selected_file}"):
                                df = read_csv_safe(file_path)
                                if df is not None:
                                    st.session_state.local_file_path = file_path
                                    st.session_state.uploaded_file = None
                                    st.success(f"✅ 已加载: {selected_file}")

                                    # 显示文件信息
                                    st.info(f"📊 文件信息：{selected_file}")
                                    st.info(f"📊 数据行数：{len(df):,}")
                                    st.info(f"📊 数据列数：{len(df.columns)}")

                                    # 显示列名预览
                                    with st.expander("📋 查看数据列名", expanded=False):
                                        st.write("数据列：", list(df.columns))

                                    # 显示数据预览
                                    with st.expander("👀 预览数据（前10行）", expanded=False):
                                        st.dataframe(df.head(10), use_container_width=True)
                                else:
                                    st.error("❌ 读取文件失败")
                        except Exception as e:
                            st.error(f"❌ 读取文件失败: {e}")
                        break
        else:
            st.warning("⚠️ 当前目录未找到CSV文件")

    # 数据格式要求
    st.markdown("""
    <div class="custom-card" style="margin-top: 30px;">
        <h3>📋 数据格式要求</h3>
        <div style="overflow-x: auto; margin-top: 20px;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: rgba(99, 102, 241, 0.2);">
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid rgba(99, 102, 241, 0.5);">字段名</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid rgba(99, 102, 241, 0.5);">说明</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid rgba(99, 102, 241, 0.5);">示例</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                        <td style="padding: 12px;"><code>project_name</code></td>
                        <td style="padding: 12px;">项目名称</td>
                        <td style="padding: 12px;">Q4宠物</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                        <td style="padding: 12px;"><code>channel_name</code></td>
                        <td style="padding: 12px;">渠道名称</td>
                        <td style="padding: 12px;">清歌</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                        <td style="padding: 12px;"><code>bonus_invalid_text</code></td>
                        <td style="padding: 12px;">无效原因</td>
                        <td style="padding: 12px;">无效-违规订单</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                        <td style="padding: 12px;"><code>bonus_text</code></td>
                        <td style="padding: 12px;">奖金状态</td>
                        <td style="padding: 12px;">有效</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px;"><code>order_text</code></td>
                        <td style="padding: 12px;">订单状态</td>
                        <td style="padding: 12px;">已完成</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 导航按钮
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col2:
        if st.button("🚀 开始分析", use_container_width=True, type="primary"):
            if st.session_state.uploaded_file is not None or st.session_state.local_file_path is not None:
                st.session_state.current_page = "违规率分析"
                st.rerun()
            else:
                st.warning("请先上传或选择数据文件")


# ==================== 页面2：违规率分析 ====================
def page_violation_analysis():
    """违规率分析页面"""
    st.markdown("""
    <div class="custom-card fade-in">
        <h2>📈 违规率分析</h2>
        <p>完整数据分析，包含GMV、违规率等多维度分析</p>
    </div>
    """, unsafe_allow_html=True)

    # 检查是否有数据文件
    if st.session_state.uploaded_file is None and st.session_state.local_file_path is None:
        st.warning("⚠️ 请先上传或选择数据文件")
        if st.button("📤 前往上传数据文件", use_container_width=True):
            st.session_state.current_page = "上传数据文件"
            st.rerun()
        return

    # 确定使用哪个文件
    df = None
    try:
        if st.session_state.uploaded_file is not None:
            df = st.session_state.uploaded_file
        elif st.session_state.local_file_path is not None:
            df = read_csv_safe(st.session_state.local_file_path)
    except Exception as e:
        st.error(f"❌ 读取数据失败: {e}")
        return

    if df is None:
        st.error("❌ 无法读取数据文件")
        return

    # 显示原始数据预览
    if st.session_state.show_raw_data:
        with st.expander("📋 原始数据预览", expanded=False):
            st.dataframe(df.head(100), use_container_width=True)
            st.info(f"数据总行数: {len(df)}")
            st.info(f"数据列: {', '.join(df.columns.tolist())}")

    # 完整数据分析
    with st.spinner("正在进行完整数据分析..."):
        analysis_result = analyze_complete_data(df)

    if analysis_result is None:
        st.warning("⚠️ 数据分析失败，请检查数据格式")
        return

    result_df = analysis_result['analysis_result']
    filtered_df = analysis_result['filtered_data']
    total_combinations = analysis_result['total_combinations']
    total_records = analysis_result['total_records']
    use_project_code = analysis_result['use_project_code']

    if result_df.empty:
        st.info("没有符合条件的项目数据")
        return

    # 显示整体概览
    st.markdown("""
    <div class="custom-card">
        <h3>📈 完整数据分析概览</h3>
    </div>
    """, unsafe_allow_html=True)

    # 关键指标汇总
    total_orders = result_df['订单总数'].sum()
    total_estimate_gmv = sum([float(x) for x in result_df['预估计佣GMV']])
    total_actual_gmv = sum([float(x) for x in result_df['实际计佣GMV']])
    total_violation = result_df['无效-违规订单数'].sum() + result_df['无效-风险订单数'].sum()

    # 使用列布局显示指标卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_records:,}</div>
            <div class="stat-label">原始数据总行数</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_combinations:,}</div>
            <div class="stat-label">项目-渠道组合数</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">¥{total_estimate_gmv:,.0f}</div>
            <div class="stat-label">总预估计佣GMV</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_violation:,}</div>
            <div class="stat-label">总违规+风险订单</div>
        </div>
        """, unsafe_allow_html=True)

    # 显示排序信息
    if use_project_code:
        st.success("✅ 已按项目编号排序")
    else:
        st.info("ℹ️ 已按项目名称排序（未检测到项目编号列）")

    # 详细分析表格
    st.markdown("""
    <div class="custom-card">
        <h3>📊 详细分析表格</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.show_detailed_analysis:
        # 显示完整分析表格
        st.dataframe(
            result_df,
            use_container_width=True,
            height=500
        )

    # 创建选项卡查看不同部分
    tab1, tab2, tab3 = st.tabs(["📈 违规分析", "💰 GMV分析", "📊 项目汇总"])

    with tab1:
        st.markdown("### 违规分析概览")

        # 提取数值数据用于图表
        violation_data = []
        for _, row in result_df.iterrows():
            violation_rate = float(row['违规率'].replace('%', ''))
            violation_gmv_rate = float(row['违规GMV占比'].replace('%', ''))
            project_violation_rate = float(row['项目违规率'].replace('%', ''))

            violation_data.append({
                '项目': row['项目名称'],
                '渠道': row['渠道名称'],
                '违规率': violation_rate,
                '违规GMV占比': violation_gmv_rate,
                '项目违规率': project_violation_rate
            })

        violation_df = pd.DataFrame(violation_data)

        if not violation_df.empty and st.session_state.show_charts:
            col1, col2 = st.columns(2)

            with col1:
                # 违规率最高的项目
                top_violation = violation_df.nlargest(10, '违规率')
                fig1 = px.bar(
                    top_violation,
                    x='项目',
                    y='违规率',
                    color='渠道',
                    title='违规率最高的10个项目',
                    labels={'违规率': '违规率 (%)'}
                )
                fig1.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    legend=dict(
                        bgcolor='rgba(30, 41, 59, 0.8)',
                        bordercolor='rgba(99, 102, 241, 0.3)',
                        borderwidth=1
                    )
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                # 违规GMV占比
                top_violation_gmv = violation_df.nlargest(10, '违规GMV占比')
                fig2 = px.bar(
                    top_violation_gmv,
                    x='项目',
                    y='违规GMV占比',
                    color='渠道',
                    title='违规GMV占比最高的10个项目',
                    labels={'违规GMV占比': '违规GMV占比 (%)'}
                )
                fig2.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    legend=dict(
                        bgcolor='rgba(30, 41, 59, 0.8)',
                        bordercolor='rgba(99, 102, 241, 0.3)',
                        borderwidth=1
                    )
                )
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("### GMV分析概览")

        # 提取GMV数据
        gmv_data = []
        for _, row in result_df.iterrows():
            estimate_gmv = float(row['预估计佣GMV'])
            actual_gmv = float(row['实际计佣GMV'])
            violation_gmv = float(row['无效-违规订单GMV'])
            risk_gmv = float(row['无效-风险订单GMV'])

            gmv_data.append({
                '项目': row['项目名称'],
                '渠道': row['渠道名称'],
                '预估计佣GMV': estimate_gmv,
                '实际计佣GMV': actual_gmv,
                '无效-违规订单GMV': violation_gmv,
                '无效-风险订单GMV': risk_gmv
            })

        gmv_df = pd.DataFrame(gmv_data)

        if not gmv_df.empty and st.session_state.show_charts:
            # 预估vs实际GMV对比
            top_gmv = gmv_df.nlargest(10, '预估计佣GMV')
            fig1 = go.Figure(data=[
                go.Bar(name='预估计佣GMV', x=top_gmv['项目'], y=top_gmv['预估计佣GMV'],
                       marker_color='#6366f1'),
                go.Bar(name='实际计佣GMV', x=top_gmv['项目'], y=top_gmv['实际计佣GMV'],
                       marker_color='#10b981')
            ])
            fig1.update_layout(
                title='GMV最高的10个项目对比',
                height=400,
                barmode='group',
                yaxis_title='金额 (元)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                legend=dict(
                    bgcolor='rgba(30, 41, 59, 0.8)',
                    bordercolor='rgba(99, 102, 241, 0.3)',
                    borderwidth=1
                )
            )
            st.plotly_chart(fig1, use_container_width=True)

            # 违规和风险GMV
            violation_gmv_df = gmv_df.nlargest(10, '无效-违规订单GMV')
            if violation_gmv_df['无效-违规订单GMV'].sum() > 0:
                fig2 = px.bar(
                    violation_gmv_df,
                    x='项目',
                    y=['无效-违规订单GMV', '无效-风险订单GMV'],
                    title='违规和风险GMV最高的10个项目',
                    labels={'value': '金额 (元)', 'variable': '类型'},
                    color_discrete_sequence=['#ef4444', '#f59e0b']
                )
                fig2.update_layout(
                    height=400,
                    barmode='stack',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    legend=dict(
                        bgcolor='rgba(30, 41, 59, 0.8)',
                        bordercolor='rgba(99, 102, 241, 0.3)',
                        borderwidth=1
                    )
                )
                st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.markdown("### 项目汇总统计")

        # 按项目汇总
        if '项目编号' in result_df.columns:
            summary_df = result_df.groupby(['项目编号', '项目名称']).agg({
                '订单总数': 'sum',
                '预估计佣GMV': lambda x: sum([float(v) for v in x]),
                '实际计佣GMV': lambda x: sum([float(v) for v in x]),
                '无效-违规订单数': 'sum',
                '无效-风险订单数': 'sum',
                '违规率': lambda x: np.mean([float(str(v).replace('%', '')) for v in x])
            }).reset_index()

            summary_df['预估计佣GMV'] = summary_df['预估计佣GMV'].apply(lambda x: f"¥{x:,.2f}")
            summary_df['实际计佣GMV'] = summary_df['实际计佣GMV'].apply(lambda x: f"¥{x:,.2f}")
            summary_df['违规率'] = summary_df['违规率'].apply(lambda x: f"{x:.2f}%")

            st.dataframe(
                summary_df,
                use_container_width=True,
                height=300
            )

    # 导出功能
    st.markdown("---")
    st.markdown("""
    <div class="custom-card">
        <h3>💾 数据导出</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        # 导出详细分析报告
        csv_buffer = io.StringIO()
        result_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')

        st.download_button(
            label="📥 下载完整分析报告",
            data=csv_buffer.getvalue(),
            file_name=f"违规率分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        # 导出原始数据
        csv_buffer2 = io.StringIO()
        filtered_df.to_csv(csv_buffer2, index=False, encoding='utf-8-sig')

        st.download_button(
            label="📥 下载原始数据",
            data=csv_buffer2.getvalue(),
            file_name=f"原始数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col3:
        # 导出完整报告（Excel）
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='详细分析', index=False)
            filtered_df.to_excel(writer, sheet_name='原始数据', index=False)

            # 创建项目汇总
            if use_project_code and '项目编号' in result_df.columns:
                summary_df = result_df.groupby(['项目编号', '项目名称']).agg({
                    '订单总数': 'sum',
                    '预估计佣GMV': lambda x: sum([float(v) for v in x]),
                    '实际计佣GMV': lambda x: sum([float(v) for v in x]),
                    '无效-违规订单数': 'sum',
                    '无效-风险订单数': 'sum'
                }).reset_index()

                summary_df['预估计佣GMV'] = summary_df['预估计佣GMV'].apply(lambda x: f"¥{x:,.2f}")
                summary_df['实际计佣GMV'] = summary_df['实际计佣GMV'].apply(lambda x: f"¥{x:,.2f}")
                summary_df.to_excel(writer, sheet_name='项目汇总', index=False)

            # 添加统计信息
            total_stats = {
                '总项目-渠道组合数': len(result_df),
                '总订单数': result_df['订单总数'].sum(),
                '总预估计佣GMV': sum([float(x) for x in result_df['预估计佣GMV']]),
                '总实际计佣GMV': sum([float(x) for x in result_df['实际计佣GMV']]),
                '总无效-违规订单数': result_df['无效-违规订单数'].sum(),
                '总无效-风险订单数': result_df['无效-风险订单数'].sum(),
                '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '数据来源': '违规率分析'
            }
            stats_df = pd.DataFrame([total_stats])
            stats_df.to_excel(writer, sheet_name='统计汇总', index=False)

        excel_buffer.seek(0)

        st.download_button(
            label="📥 下载完整报告 (Excel)",
            data=excel_buffer.getvalue(),
            file_name=f"违规率分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # 计算公式说明
    with st.expander("📖 计算公式说明", expanded=False):
        st.markdown("""
        ### 📊 计算公式说明

        **基础指标：**
        - **订单总数** = 统计数据行数
        - **预估计佣GMV** = ∑所有订单的 `estimate_cos_price`
        - **实际计佣GMV** = ∑`actual_cos_price` (仅当 `bonus_text="有效"` 且 `order_text="已完成"`)
        - **预估完成** = ∑`estimate_cos_price` (仅当 `bonus_text="有效"`)

        **违规相关指标：**
        - **无效-违规订单数** = 统计 `bonus_invalid_text` = "无效-违规订单"
        - **无效-风险订单数** = 统计 `bonus_invalid_text` = "无效-风险订单"
        - **无效-违规订单GMV** = 违规订单的 `estimate_cos_price` 总和
        - **无效-风险订单GMV** = 风险订单的 `estimate_cos_price` 总和

        **衍生指标：**
        - **违规率** = (无效-违规订单数 + 无效-风险订单数) / 订单总数 × 100%
        - **违规GMV占比** = (无效-违规订单GMV + 无效-风险订单GMV) / 预估计佣GMV × 100%
        - **项目违规率** = (项目违规订单数 + 项目风险订单数) / 项目总订单数 × 100%
        - **项目违规GMV占比** = (项目违规GMV + 项目风险GMV) / 项目预估GMV × 100%
        """, unsafe_allow_html=True)


# ==================== 页面3：违规率统计 ====================
def page_violation_statistics():
    """违规率统计页面"""
    st.markdown("""
    <div class="custom-card fade-in">
        <h2>📊 违规率统计</h2>
        <p>按时间维度统计订单和违规情况</p>
    </div>
    """, unsafe_allow_html=True)

    # 检查是否有数据文件
    if st.session_state.uploaded_file is None and st.session_state.local_file_path is None:
        st.warning("⚠️ 请先上传或选择数据文件")
        if st.button("📤 前往上传数据文件", use_container_width=True):
            st.session_state.current_page = "上传数据文件"
            st.rerun()
        return

    # 确定使用哪个文件
    df = None
    try:
        if st.session_state.uploaded_file is not None:
            df = st.session_state.uploaded_file
        elif st.session_state.local_file_path is not None:
            df = read_csv_safe(st.session_state.local_file_path)
    except Exception as e:
        st.error(f"❌ 读取数据失败: {e}")
        return

    if df is None:
        st.error("❌ 无法读取数据文件")
        return

    # 显示原始数据预览
    with st.expander("📋 原始数据预览", expanded=False):
        st.dataframe(df.head(100), use_container_width=True)
        st.info(f"数据总行数: {len(df)}")
        st.info(f"数据列: {', '.join(df.columns.tolist())}")

    # 时间选择器部分
    st.markdown("""
    <div class="custom-card">
        <h3>⏰ 时间范围设置</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="time-card">
            <h4 style="color: var(--text-primary); margin-bottom: 15px;">📅 下单时间范围</h4>
        """, unsafe_allow_html=True)

        # 获取数据中的最小和最大下单时间
        df['order_time_parsed'] = df['order_time'].apply(parse_date)
        valid_order_times = df['order_time_parsed'].dropna()

        if not valid_order_times.empty:
            min_order_time = valid_order_times.min()
            max_order_time = valid_order_times.max()
        else:
            min_order_time = datetime.now() - timedelta(days=30)
            max_order_time = datetime.now()

        # 下单开始日期 - 使用自定义样式
        st.markdown('<div class="time-label">下单开始日期</div>', unsafe_allow_html=True)
        order_start_date = st.date_input(
            "",
            value=min_order_time.date(),
            min_value=min_order_time.date() - timedelta(days=365),
            max_value=max_order_time.date() + timedelta(days=365),
            key="order_start_date_stat",
            label_visibility="collapsed"
        )

        # 下单开始时间 - 使用自定义样式
        st.markdown('<div class="time-label" style="margin-top: 15px;">下单开始时间</div>', unsafe_allow_html=True)
        order_start_time = st.time_input(
            "",
            value=datetime.min.time(),
            key="order_start_time_stat",
            label_visibility="collapsed"
        )
        order_start_dt = datetime.combine(order_start_date, order_start_time)

        # 下单结束日期
        st.markdown('<div class="time-label" style="margin-top: 15px;">下单结束日期</div>', unsafe_allow_html=True)
        order_end_date = st.date_input(
            "",
            value=max_order_time.date(),
            min_value=min_order_time.date() - timedelta(days=365),
            max_value=max_order_time.date() + timedelta(days=365),
            key="order_end_date_stat",
            label_visibility="collapsed"
        )

        # 下单结束时间
        st.markdown('<div class="time-label" style="margin-top: 15px;">下单结束时间</div>', unsafe_allow_html=True)
        order_end_time = st.time_input(
            "",
            value=datetime.max.time(),
            key="order_end_time_stat",
            label_visibility="collapsed"
        )
        order_end_dt = datetime.combine(order_end_date, order_end_time)

        st.caption(
            f"下单时间范围: {order_start_dt.strftime('%Y-%m-%d %H:%M:%S')} 至 {order_end_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="time-card">
            <h4 style="color: var(--text-primary); margin-bottom: 15px;">✅ 完成时间范围</h4>
        """, unsafe_allow_html=True)

        # 获取数据中的最小和最大完成时间
        df['finish_time_parsed'] = df['finish_time'].apply(parse_date)
        valid_finish_times = df['finish_time_parsed'].dropna()

        if not valid_finish_times.empty:
            min_finish_time = valid_finish_times.min()
            max_finish_time = valid_finish_times.max()
        else:
            min_finish_time = datetime.now() - timedelta(days=30)
            max_finish_time = datetime.now()

        # 完成开始日期
        st.markdown('<div class="time-label">完成开始日期</div>', unsafe_allow_html=True)
        finish_start_date = st.date_input(
            "",
            value=min_finish_time.date(),
            min_value=min_finish_time.date() - timedelta(days=365),
            max_value=max_finish_time.date() + timedelta(days=365),
            key="finish_start_date_stat",
            label_visibility="collapsed"
        )

        # 完成开始时间
        st.markdown('<div class="time-label" style="margin-top: 15px;">完成开始时间</div>', unsafe_allow_html=True)
        finish_start_time = st.time_input(
            "",
            value=datetime.min.time(),
            key="finish_start_time_stat",
            label_visibility="collapsed"
        )
        finish_start_dt = datetime.combine(finish_start_date, finish_start_time)

        # 完成结束日期
        st.markdown('<div class="time-label" style="margin-top: 15px;">完成结束日期</div>', unsafe_allow_html=True)
        finish_end_date = st.date_input(
            "",
            value=max_finish_time.date(),
            min_value=min_finish_time.date() - timedelta(days=365),
            max_value=max_finish_time.date() + timedelta(days=365),
            key="finish_end_date_stat",
            label_visibility="collapsed"
        )

        # 完成结束时间
        st.markdown('<div class="time-label" style="margin-top: 15px;">完成结束时间</div>', unsafe_allow_html=True)
        finish_end_time = st.time_input(
            "",
            value=datetime.max.time(),
            key="finish_end_time_stat",
            label_visibility="collapsed"
        )
        finish_end_dt = datetime.combine(finish_end_date, finish_end_time)

        st.caption(
            f"完成时间范围: {finish_start_dt.strftime('%Y-%m-%d %H:%M:%S')} 至 {finish_end_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown('</div>', unsafe_allow_html=True)

    # 添加统计按钮
    if st.button("🚀 执行统计", use_container_width=True, type="primary"):
        with st.spinner("正在进行违规率统计..."):
            # 执行违规率统计
            analysis_result = analyze_violation_statistics(
                df,
                order_start_dt,
                order_end_dt,
                finish_start_dt,
                finish_end_dt
            )

        if analysis_result is not None:
            result_df = analysis_result['analysis_result']
            order_filtered_df = analysis_result['order_filtered_data']
            total_combinations = analysis_result['total_combinations']
            order_total_count = analysis_result['order_total_count']

            if result_df.empty:
                st.info("没有符合条件的项目数据")
                return

            # 显示统计结果概览
            st.markdown("""
            <div class="custom-card">
                <h3>📊 统计结果概览</h3>
            </div>
            """, unsafe_allow_html=True)

            # 关键指标汇总
            total_orders = result_df['订单总数'].sum()
            total_invalid = result_df['无效订单总数'].sum()
            total_violation = result_df['违规订单数'].sum()
            avg_violation_rate = (total_violation / total_orders * 100) if total_orders > 0 else 0

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{order_total_count:,}</div>
                    <div class="stat-label">符合下单时间订单数</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{total_combinations:,}</div>
                    <div class="stat-label">项目-渠道组合数</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{total_invalid:,}</div>
                    <div class="stat-label">无效订单总数</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{total_violation:,}</div>
                    <div class="stat-label">违规订单总数</div>
                </div>
                """, unsafe_allow_html=True)

            # 显示平均违规率
            st.markdown(f"""
            <div class="custom-card" style="margin-top: 20px;">
                <h4>📈 整体违规率统计</h4>
                <p>在符合下单时间范围的 <strong style="color: var(--primary);">{total_orders:,}</strong> 个订单中：</p>
                <ul style="margin-top: 10px;">
                    <li>无效订单总数：<strong style="color: var(--warning);">{total_invalid:,}</strong> 个</li>
                    <li>违规订单总数：<strong style="color: var(--danger);">{total_violation:,}</strong> 个</li>
                    <li>整体违规率：<strong style="color: var(--primary);">{avg_violation_rate:.2f}%</strong></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # 显示详细统计表格
            st.markdown("""
            <div class="custom-card">
                <h3>📋 详细统计表格</h3>
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(
                result_df,
                use_container_width=True,
                height=400
            )

            # 可视化图表
            st.markdown("""
            <div class="custom-card">
                <h3>📈 可视化分析</h3>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                # 违规率最高的项目
                result_df['违规率数值'] = result_df['违规率'].str.replace('%', '').astype(float)
                top_violation = result_df.nlargest(10, '违规率数值')

                if not top_violation.empty:
                    fig1 = px.bar(
                        top_violation,
                        x='项目名称',
                        y='违规率数值',
                        color='渠道名称',
                        title='违规率最高的10个项目',
                        labels={'违规率数值': '违规率 (%)', '项目名称': '项目名称', '渠道名称': '渠道名称'}
                    )
                    fig1.update_layout(
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        legend=dict(
                            bgcolor='rgba(30, 41, 59, 0.8)',
                            bordercolor='rgba(99, 102, 241, 0.3)',
                            borderwidth=1
                        )
                    )
                    st.plotly_chart(fig1, use_container_width=True)

            with col2:
                # 违规订单数最多的项目
                top_violation_count = result_df.nlargest(10, '违规订单数')

                if not top_violation_count.empty:
                    fig2 = px.bar(
                        top_violation_count,
                        x='项目名称',
                        y='违规订单数',
                        color='渠道名称',
                        title='违规订单数最多的10个项目',
                        labels={'违规订单数': '违规订单数', '项目名称': '项目名称', '渠道名称': '渠道名称'}
                    )
                    fig2.update_layout(
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        legend=dict(
                            bgcolor='rgba(30, 41, 59, 0.8)',
                            bordercolor='rgba(99, 102, 241, 0.3)',
                            borderwidth=1
                        )
                    )
                    st.plotly_chart(fig2, use_container_width=True)

            # 导出功能
            st.markdown("---")
            st.markdown("""
            <div class="custom-card">
                <h3>💾 导出统计结果</h3>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                # 导出统计报告
                csv_buffer = io.StringIO()
                result_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')

                st.download_button(
                    label="📥 下载统计报告",
                    data=csv_buffer.getvalue(),
                    file_name=f"违规率统计报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col2:
                # 导出筛选后的数据
                csv_buffer2 = io.StringIO()
                order_filtered_df.to_csv(csv_buffer2, index=False, encoding='utf-8-sig')

                st.download_button(
                    label="📥 下载筛选数据",
                    data=csv_buffer2.getvalue(),
                    file_name=f"筛选数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            # 统计逻辑说明
            with st.expander("📖 统计逻辑说明", expanded=False):
                st.markdown("""
                ### 📊 统计逻辑说明

                **时间筛选逻辑：**
                1. **下单时间筛选**：筛选 `order_time` 在指定范围内的所有订单
                2. **完成时间筛选**：在已筛选的下单订单中，进一步筛选 `finish_time` 在指定范围内的订单

                **统计指标说明：**
                - **订单总数**：基于下单时间筛选的订单数量
                - **无效订单总数**：基于完成时间筛选，且 `bonus_text` = "无效" 的订单数量
                - **违规订单数**：基于完成时间筛选，且 `bonus_invalid_text` = "无效-风险订单" 或 "无效-违规订单" 的订单数量
                - **违规率**：违规订单数 ÷ 订单总数 × 100%

                **示例说明：**
                - 下单时间：23/12/2025 00:00:00 - 24/12/2025 00:00:00
                - 完成时间：24/12/2025 00:00:00 - 25/12/2025 00:00:00

                1. 先找出所有在23-24日下单的订单
                2. 在这些订单中，找出在24-25日完成的订单
                3. 统计这些订单中的无效和违规情况
                """, unsafe_allow_html=True)

    else:
        st.info("👆 请设置时间范围并点击'执行统计'按钮开始分析")


# ==================== 页面4：分析设置 ====================
def page_analysis_settings():
    """分析设置页面"""
    st.markdown("""
    <div class="custom-card fade-in">
        <h2>⚙️ 分析设置</h2>
        <p>配置数据分析的各项参数和选项</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="custom-card">
            <h3>👁️ 显示选项</h3>
        """, unsafe_allow_html=True)

        # 显示选项
        st.session_state.highlight_violations = st.checkbox(
            "高亮显示违规率高的项目",
            value=st.session_state.highlight_violations,
            help="是否在表格中高亮显示违规率较高的项目"
        )

        st.session_state.show_charts = st.checkbox(
            "显示可视化图表",
            value=st.session_state.show_charts,
            help="是否显示数据可视化图表"
        )

        st.session_state.show_raw_data = st.checkbox(
            "显示原始数据预览",
            value=st.session_state.show_raw_data,
            help="是否显示原始数据的预览"
        )

        st.session_state.show_detailed_analysis = st.checkbox(
            "显示详细分析表格",
            value=st.session_state.show_detailed_analysis,
            help="是否显示详细的分析表格"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="custom-card">
            <h3>📊 阈值设置</h3>
        """, unsafe_allow_html=True)

        # 违规率阈值
        st.session_state.high_violation_threshold = st.slider(
            "高风险阈值（%）",
            min_value=0,
            max_value=100,
            value=st.session_state.high_violation_threshold,
            help="违规率高于此值将被标记为高风险",
            key="high_threshold_slider"
        )

        st.session_state.medium_violation_threshold = st.slider(
            "中等风险阈值（%）",
            min_value=0,
            max_value=100,
            value=st.session_state.medium_violation_threshold,
            help="违规率高于此值将被标记为中等风险",
            key="medium_threshold_slider"
        )

        # 显示阈值说明
        st.info(f"""
        **当前阈值设置：**
        - 高风险：≥ {st.session_state.high_violation_threshold}%
        - 中等风险：≥ {st.session_state.medium_violation_threshold}%
        - 低风险：< {st.session_state.medium_violation_threshold}%
        """)

        st.markdown("</div>", unsafe_allow_html=True)

    # 数据管理部分
    st.markdown("""
    <div class="custom-card" style="margin-top: 20px;">
        <h3>🗂️ 数据管理</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ 清除所有数据", use_container_width=True, type="secondary"):
            st.session_state.uploaded_file = None
            st.session_state.local_file_path = None
            st.success("✅ 已清除所有数据")

    with col2:
        if st.button("🔄 重新加载当前文件", use_container_width=True, type="secondary"):
            if st.session_state.local_file_path is not None:
                try:
                    df = read_csv_safe(st.session_state.local_file_path)
                    if df is not None:
                        st.session_state.uploaded_file = df
                        st.success("✅ 文件重新加载成功")
                    else:
                        st.error("❌ 重新加载失败")
                except Exception as e:
                    st.error(f"❌ 重新加载失败: {e}")
            elif st.session_state.uploaded_file is not None:
                st.info("ℹ️ 上传的文件已加载")
        if st.button("🔄 重新加载当前文件", use_container_width=True, type="secondary"):
            pass

    with col3:
        if st.button("💾 保存当前设置", use_container_width=True, type="primary"):
            st.success("✅ 设置已保存")

    # 帮助信息
    st.markdown("""
    <div class="custom-card" style="margin-top: 20px;">
        <h3>📖 使用说明</h3>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🚀 使用步骤", expanded=False):
        st.markdown("""
        **使用步骤**
        1. **上传数据文件**：在"上传数据文件"页面上传CSV数据文件或从本地目录选择
        2. **选择分析页面**：使用侧边栏导航选择"违规率分析"或"违规率统计"
        3. **查看分析结果**：系统将自动分析数据并显示结果
        4. **导出分析报告**：下载完整的分析报告和数据
        """)

    with st.expander("📋 数据要求", expanded=False):
        st.markdown("""
        **数据要求**
        文件必须是CSV格式，必须包含以下字段：
        - `project_name` - 项目名称
        - `channel_name` - 渠道名称
        - `bonus_invalid_text` - 无效原因
        - `bonus_text` - 奖金状态
        - `order_time` - 下单时间
        - `finish_time` - 完成时间
        - `estimate_cos_price` - 预估成本价格
        - `actual_cos_price` - 实际成本价格
        """)

    with st.expander("📑 页面说明", expanded=False):
        st.markdown("""
        **页面说明**
        - **违规率分析**：完整数据分析，包含GMV、违规率等多维度分析
        - **违规率统计**：按时间维度统计订单和违规情况
        - **分析设置**：配置分析参数和显示选项
        """)

    with st.expander("⚙️ 设置说明", expanded=False):
        st.markdown("""
        **设置说明**
        - **显示选项**：控制数据展示的方式和内容
        - **阈值设置**：定义违规率的风险等级
        - **数据管理**：管理已加载的数据文件
        """)


# ==================== 主应用逻辑 ====================
def main():
    # 根据当前页面显示不同内容
    if st.session_state.current_page == "上传数据文件":
        page_upload_data()
    elif st.session_state.current_page == "违规率分析":
        page_violation_analysis()
    elif st.session_state.current_page == "违规率统计":
        page_violation_statistics()
    elif st.session_state.current_page == "分析设置":
        page_analysis_settings()


# 运行应用
if __name__ == "__main__":
    main()