import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
from datetime import datetime, timedelta
import numpy as np

# ---------------------- 1. 页面配置与全局CSS样式 ----------------------
st.set_page_config(
    page_title="WGQ物流数据分析",
    page_icon="📊",
    layout="wide"
)

# 添加全局CSS样式
st.markdown("""
<style>
    /* 全局字体设置 */
    html, body, [class*="css"] {
        font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    
    /* 主标题 */
    h1 {
        font-size: 36px !important;
        font-weight: 800 !important;
        color: #1E3A8A;
        margin-bottom: 25px;
        text-align: center !important;
        padding-bottom: 15px;
        border-bottom: 3px solid #3B82F6;
    }
    
    /* 二级标题 */
    h2, h3, h4 {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #1E40AF !important;
        margin-top: 25px;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 2px solid #E5E7EB !important;
    }
    
    /* 按钮文字 */
    .stButton > button {
        font-size: 18px !important;
        font-weight: 700 !important;
    }
    
    /* 数据表格文字 */
    .stDataFrame {
        font-size: 17px !important;
        font-weight: 600 !important;
    }
    
    /* 表格表头样式 */
    .dataframe-container {
        background-color: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    .dataframe-header {
        background-color: #1E3A8A !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        padding: 12px !important;
    }
    
    .dataframe-content {
        font-size: 17px !important;
        font-weight: 600 !important;
        padding: 10px !important;
    }
    
    /* 扁长倒计时样式 */
    .flat-countdown-container {
        background-color: #F0F9FF;
        border-radius: 12px;
        padding: 15px 30px;
        margin-bottom: 20px;
        border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 120px;
    }
    
    .countdown-main {
        flex-grow: 1;
        text-align: center;
    }
    
    .countdown-left {
        flex: 0 0 200px;
        text-align: left;
    }
    
    .countdown-right {
        flex: 0 0 200px;
        text-align: right;
    }
    
    .flat-countdown-timer {
        font-size: 42px !important;
        font-weight: 900 !important;
        color: #DC2626 !important;
        text-align: center !important;
        margin: 5px 0 !important;
        font-family: 'Courier New', monospace !important;
        letter-spacing: 2px;
    }
    
    .flat-countdown-label {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #1E40AF !important;
        margin-bottom: 5px;
    }
    
    .flat-countdown-subtext {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #6B7280 !important;
    }
    
    .countdown-icon {
        font-size: 32px;
        margin-right: 10px;
    }
    
    /* 卡片样式 */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3B82F6;
    }
    
    /* 到达时间小方格样式 */
    .arrival-time-box {
        background-color: #F0F9FF;
        border: 2px solid #3B82F6;
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #1E40AF !important;
        text-align: center;
        margin-right: 10px;
        display: inline-block;
        min-width: 60px;
    }
    
    .arrival-time-label {
        font-size: 12px !important;
        color: #6B7280 !important;
        font-weight: 600 !important;
        margin-right: 5px;
    }
    
    /* 自定义表格样式 */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 17px !important;
        font-weight: 600 !important;
    }
    
    .custom-table th {
        background-color: #1E3A8A !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        padding: 12px !important;
        text-align: left;
        border: 1px solid #ddd;
    }
    
    .custom-table td {
        font-size: 17px !important;
        font-weight: 600 !important;
        padding: 10px !important;
        border: 1px solid #ddd;
        background-color: white !important;
    }
    
    .custom-table tr:nth-child(even) {
        background-color: #f9f9f9 !important;
    }
    
    .custom-table tr:hover {
        background-color: #f0f0f0 !important;
    }
    
    /* 状态指示器 */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #10B981;
    }
    
    .status-offline {
        background-color: #EF4444;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = datetime.now()
if 'auto_refresh_enabled' not in st.session_state:
    st.session_state.auto_refresh_enabled = True
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 10  # 默认10分钟
if 'page_load_time' not in st.session_state:
    st.session_state.page_load_time = datetime.now()

# ---------------------- 2. 定义文件路径 ----------------------
file_paths = {
    "承运商列表": r"C:\Users\te589492\TE Connectivity\WGQ DC OPREATION TEAM - General\Pick wave\WGQ承运商.xlsx",
    "运单数据": r"C:\Users\te589492\OneDrive - TE Connectivity\桌面\WGQ_shipment_processed.xlsx",
    "车辆到达时间": r"C:\Users\te589492\TE Connectivity\WGQ DC OPREATION TEAM - General\Pick wave\每日车辆到达时间表.xlsx",
    "预测结果": r"C:\Users\te589492\TE Connectivity\WGQ DC OPREATION TEAM - General\Pick wave\processed_results.xlsx",
    "Pick效率数据": r"C:\Users\te589492\TE Connectivity\WGQ DC OPREATION TEAM - General\Pick wave\093_统计结果.xlsx",
    "堆积天数数据": r"C:\Users\te589492\TE Connectivity\WGQ DC OPREATION TEAM - General\Pick wave\VT12.xlsx"
}

# ---------------------- 3. 安全读取Excel函数 ----------------------
def read_excel_safe(file_path, sheet_name=0, required_cols=None):
    """安全读取Excel，返回DataFrame或None"""
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path, engine="openpyxl", sheet_name=sheet_name)
        if required_cols:
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                return None
        return df
    except Exception as e:
        return None

# ---------------------- 4. 侧边栏配置 ----------------------
with st.sidebar:
    # 侧边栏标题
    st.markdown("<h3 style='color:#1E3A8A;'>控制面板</h3>", unsafe_allow_html=True)
    
    # 手动刷新按钮
    if st.button("🔄 手动刷新数据", type="primary"):
        st.session_state.page_load_time = datetime.now()
        st.rerun()
    
    st.divider()
    
    # 自动刷新设置
    st.markdown("### ⚙️ 自动刷新设置")
    st.session_state.auto_refresh_enabled = st.checkbox(
        "启用自动刷新", 
        value=st.session_state.auto_refresh_enabled,
        help="启用后，系统将按照设定的间隔自动刷新数据"
    )
    
    st.session_state.refresh_interval = st.slider(
        "刷新间隔（分钟）", 
        min_value=1, 
        max_value=60, 
        value=st.session_state.refresh_interval,
        help="设置自动刷新的时间间隔"
    )
    
    st.divider()
    
    # 文件状态检查
    st.markdown("<h4>📁 文件状态检查</h4>", unsafe_allow_html=True)
    for name, path in file_paths.items():
        exists = os.path.exists(path)
        status_icon = "✅" if exists else "❌"
        status_text = "正常" if exists else "异常"
        color = "green" if exists else "red"
        st.markdown(f"<span style='color:{color}'><strong>{status_icon} {name}:</strong> {status_text}</span>", unsafe_allow_html=True)
    
    st.divider()
    
    # 系统状态
    st.markdown("<h4>📊 系统状态</h4>", unsafe_allow_html=True)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"**当前时间:** {current_time}")
    st.markdown(f"**自动刷新:** {'已启用' if st.session_state.auto_refresh_enabled else '已禁用'}")

# ---------------------- 5. 主页面内容 ----------------------
st.markdown("<h1>📈 WGQ物流数据分析面板</h1>", unsafe_allow_html=True)

# 计算倒计时时间
refresh_seconds = st.session_state.refresh_interval * 60
current_time = datetime.now()
time_since_page_load = (current_time - st.session_state.page_load_time).total_seconds()
remaining_seconds = max(0, refresh_seconds - time_since_page_load)

# 加载所有数据
df_carrier = read_excel_safe(file_paths["承运商列表"])
df_shipment = read_excel_safe(file_paths["运单数据"], required_cols=["Carrier Name", "status"])
df_arrival = read_excel_safe(file_paths["车辆到达时间"], required_cols=["承运商", "到达时间"])
df_forecast = read_excel_safe(file_paths["预测结果"], sheet_name="Final Results", required_cols=["Date", "NonPGI", "PGI", "Forecast"])
df_pick_efficiency = read_excel_safe(file_paths["Pick效率数据"], sheet_name="统计结果")
df_accumulation = read_excel_safe(file_paths["堆积天数数据"])

# ---------------------- 6. 倒计时模块（使用Streamlit原生组件实现） ----------------------
if st.session_state.auto_refresh_enabled:
    # 初始显示的时间
    minutes = int(remaining_seconds // 60)
    seconds = int(remaining_seconds % 60)
    
    # 计算下次刷新时间
    next_refresh_time = st.session_state.page_load_time + timedelta(minutes=st.session_state.refresh_interval)
    
    # 使用Streamlit容器和列创建扁长倒计时
    with st.container():
        # 创建一个扁长的容器
        countdown_container = st.container()
        with countdown_container:
            # 使用三列布局
            col_left, col_center, col_right = st.columns([1, 2, 1])
            
            with col_left:
                st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
                st.markdown(f"<div class='flat-countdown-label'>🔄 自动刷新系统</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='flat-countdown-subtext'>刷新间隔: {st.session_state.refresh_interval}分钟</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='flat-countdown-subtext'>最后刷新: {st.session_state.page_load_time.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col_center:
                st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                st.markdown(f"<div class='flat-countdown-label'>刷新倒计时</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='flat-countdown-timer' id='flat-countdown-timer'>{minutes:02d}:{seconds:02d}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col_right:
                st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
                st.markdown(f"<div class='flat-countdown-label'>下次刷新时间</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='flat-countdown-subtext'>{next_refresh_time.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='flat-countdown-subtext'>当前时间: {current_time.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    
    # 添加JavaScript代码实现动态倒计时
    st.markdown(f"""
    <script>
        // 初始剩余时间（秒）
        let remainingSeconds = {int(remaining_seconds)};
        
        // 更新倒计时函数
        function updateFlatCountdown() {{
            // 如果倒计时结束，刷新页面
            if (remainingSeconds <= 0) {{
                // 显示刷新提示
                document.getElementById('flat-countdown-timer').innerHTML = '刷新中...';
                document.getElementById('flat-countdown-timer').style.color = '#10B981';
                document.getElementById('flat-countdown-timer').style.fontSize = '36px';
                
                // 延迟1秒后刷新
                setTimeout(function() {{
                    window.location.reload();
                }}, 1000);
                return;
            }}
            
            // 计算分钟和秒
            const minutes = Math.floor(remainingSeconds / 60);
            const seconds = remainingSeconds % 60;
            
            // 更新显示
            const timerElement = document.getElementById('flat-countdown-timer');
            timerElement.innerHTML = 
                minutes.toString().padStart(2, '0') + ':' + 
                seconds.toString().padStart(2, '0');
            
            // 根据剩余时间改变颜色
            if (remainingSeconds < 60) {{
                timerElement.style.color = '#EF4444';
                timerElement.style.fontWeight = '900';
            }} else if (remainingSeconds < 300) {{
                timerElement.style.color = '#F59E0B';
            }}
            
            // 减少剩余时间
            remainingSeconds--;
            
            // 每秒更新一次
            setTimeout(updateFlatCountdown, 1000);
        }}
        
        // 延迟启动倒计时，确保DOM完全加载
        setTimeout(updateFlatCountdown, 100);
    </script>
    """, unsafe_allow_html=True)
else:
    # 显示手动刷新状态
    st.info("ℹ️ 自动刷新已禁用，如需刷新请点击侧边栏的手动刷新按钮")

st.markdown("---")

# ---------------------- 7. 图表展示 ----------------------
# 创建两列用于并排显示图表
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # 图表1：横向堆积图 - 各承运商运单状态统计（包含到达时间）
    if df_shipment is not None and not df_shipment.empty and df_carrier is not None and not df_carrier.empty:
        # 获取承运商顺序
        carrier_order = df_carrier[df_carrier.columns[1]].tolist() if len(df_carrier.columns)>=2 else []
        
        # 获取到达时间映射 - 修复时间格式问题
        arrival_time_map = {}
        if df_arrival is not None and not df_arrival.empty:
            for _, row in df_arrival.iterrows():
                carrier = row["承运商"]
                if pd.notna(row["到达时间"]):
                    try:
                        # 尝试将时间转换为datetime对象
                        if isinstance(row["到达时间"], (datetime, pd.Timestamp)):
                            arrival_time_map[carrier] = row["到达时间"].strftime("%H:%M")
                        elif isinstance(row["到达时间"], str):
                            # 尝试解析字符串格式的时间
                            try:
                                dt = pd.to_datetime(row["到达时间"])
                                arrival_time_map[carrier] = dt.strftime("%H:%M")
                            except:
                                arrival_time_map[carrier] = row["到达时间"]
                        else:
                            # 其他格式，直接转换为字符串
                            arrival_time_map[carrier] = str(row["到达时间"])
                    except Exception as e:
                        arrival_time_map[carrier] = str(row["到达时间"])
        
        # 按照承运商顺序统计状态
        status_count = df_shipment.groupby(["Carrier Name", "status"]).size().reset_index(name="计数")
        
        # 确保承运商顺序与承运商列表一致
        status_count["Carrier Name"] = pd.Categorical(
            status_count["Carrier Name"], 
            categories=carrier_order, 
            ordered=True
        )
        status_count = status_count.sort_values("Carrier Name")
        
        # 状态颜色映射
        color_map = {
            "PGI": "#32CD32",
            "Picked": "#FF4500",
            "Packed": "#DC143C",
            "Not Picked": "#FF8C00",
            "Not Created": "#FFA500"
        }
        
        # 创建图表
        fig1 = px.bar(
            status_count,
            x="计数",
            y="Carrier Name",
            color="status",
            barmode="stack",
            color_discrete_map=color_map,
            title="各承运商运单状态统计",
            labels={"Carrier Name": "", "status": "运单状态", "计数": "数量"}  # 去掉y轴标题
        )
        
        # 更新图表字体和样式
        fig1.update_layout(
            title_font=dict(size=22, family="Microsoft YaHei", color="#000000", weight="bold"),
            font=dict(size=16, family="Microsoft YaHei", color="#000000", weight="bold"),
            margin=dict(l=10, r=10, t=50, b=30),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title_font=dict(size=18, color="#000000", weight="bold"),
                tickfont=dict(size=14, color="#000000", weight="bold"),
                gridcolor='lightgrey'
            ),
            yaxis=dict(
                title_text="",  # 去掉y轴标题
                title_font=dict(size=18, color="#000000", weight="bold"),
                tickfont=dict(size=14, color="#000000", weight="bold"),
                categoryorder='array',
                categoryarray=carrier_order[::-1]  # 反转顺序以匹配显示
            ),
            legend=dict(
                title_font=dict(size=16, color="#000000", weight="bold"),
                font=dict(size=14, color="#000000", weight="bold")
            )
        )
        
        # 为每个承运商添加到达时间注释
        for i, carrier in enumerate(carrier_order):
            if carrier in arrival_time_map:
                arrival_time = arrival_time_map[carrier]
                y_pos = len(carrier_order) - i - 1  # 反转索引以匹配图表顺序
                
                # 添加到达时间标注
                fig1.add_annotation(
                    x=-0.5,  # 在y轴左侧显示
                    y=y_pos,
                    text=arrival_time,
                    showarrow=False,
                    xref="x",
                    yref="y",
                    font=dict(size=12, color="#1E40AF", weight="bold"),
                    bgcolor="#F0F9FF",
                    bordercolor="#3B82F6",
                    borderwidth=2,
                    borderpad=6,
                    align="center",
                    xanchor="right",
                    yanchor="middle"
                )
        
        # 添加到达时间标题
        fig1.add_annotation(
            x=-0.5,
            y=len(carrier_order) + 0.5,
            text="到达时间",
            showarrow=False,
            xref="x",
            yref="y",
            font=dict(size=14, color="#1E40AF", weight="bold"),
            align="center",
            xanchor="right",
            yanchor="middle"
        )
        
        # 调整布局，为到达时间留出空间
        fig1.update_layout(
            margin=dict(l=120, r=10, t=50, b=30)  # 增加左侧边距以显示到达时间
        )
        
        st.plotly_chart(fig1, width='stretch')

with chart_col2:
    # 图表2：纵向堆积柱状图
    if df_forecast is not None and not df_forecast.empty:
        df_forecast_display = df_forecast.head(3).copy()
        df_forecast_display["Date"] = df_forecast_display["Date"].astype(str)
        
        df_forecast_long = df_forecast_display.melt(
            id_vars=["Date"],
            value_vars=["NonPGI", "PGI", "Forecast"],
            var_name="类型",
            value_name="数值"
        )
        
        forecast_color_map = {
            "PGI": "#32CD32",
            "NonPGI": "#FFA500",
            "Forecast": "#FF8C00"
        }
        
        fig2 = px.bar(
            df_forecast_long,
            x="Date",
            y="数值",
            color="类型",
            barmode="stack",
            color_discrete_map=forecast_color_map,
            title="近3日Forecast/PGI/NonPGI分布"
        )
        
        # 添加目标线
        fig2.add_hline(
            y=2333,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text="目标值: 2333",
            annotation_position="top right"
        )
        
        # 更新图表字体和样式
        fig2.update_layout(
            title_font=dict(size=22, family="Microsoft YaHei", color="#000000", weight="bold"),
            font=dict(size=16, family="Microsoft YaHei", color="#000000", weight="bold"),
            margin=dict(l=10, r=10, t=50, b=30),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title_font=dict(size=18, color="#000000", weight="bold"),
                tickfont=dict(size=14, color="#000000", weight="bold"),
                gridcolor='lightgrey'
            ),
            yaxis=dict(
                title_font=dict(size=18, color="#000000", weight="bold"),
                tickfont=dict(size=14, color="#000000", weight="bold"),
                gridcolor='lightgrey'
            ),
            legend=dict(
                title_font=dict(size=16, color="#000000", weight="bold"),
                font=dict(size=14, color="#000000", weight="bold")
            )
        )
        
        st.plotly_chart(fig2, width='stretch')

# ---------------------- 8. 效率数据表格 ----------------------
# 创建两列用于并排显示效率表格
accum_col, pick_col = st.columns(2)

with accum_col:
    # 堆积天数表格 - 使用自定义样式
    if df_accumulation is not None and not df_accumulation.empty:
        st.markdown("<h4>📆 堆积天数详情</h4>", unsafe_allow_html=True)
        
        # 只显示前8行数据
        df_accumulation_display = df_accumulation.head(8)
        
        # 使用自定义HTML表格确保样式一致
        accum_html = "<table class='custom-table'>"
        
        # 添加表头
        accum_html += "<thead><tr>"
        for col in df_accumulation_display.columns:
            accum_html += f"<th>{col}</th>"
        accum_html += "</tr></thead>"
        
        # 添加表格内容
        accum_html += "<tbody>"
        for _, row in df_accumulation_display.iterrows():
            accum_html += "<tr>"
            for col in df_accumulation_display.columns:
                cell_value = row[col]
                accum_html += f"<td>{cell_value}</td>"
            accum_html += "</tr>"
        accum_html += "</tbody></table>"
        
        st.markdown(accum_html, unsafe_allow_html=True)

with pick_col:
    # Pick效率表格 - 使用自定义样式
    if df_pick_efficiency is not None and not df_pick_efficiency.empty:
        st.markdown("<h4>📦 Pick效率统计</h4>", unsafe_allow_html=True)
        
        # 准备显示数据
        if '操作员' in df_pick_efficiency.columns:
            df_pick_display = df_pick_efficiency[df_pick_efficiency['操作员'] != '总计'].copy()
        elif '工号' in df_pick_efficiency.columns:
            df_pick_display = df_pick_efficiency[df_pick_efficiency['工号'] != '总计'].copy()
        else:
            df_pick_display = df_pick_efficiency.copy()
        
        # 只显示前8行数据
        if len(df_pick_display) > 8:
            df_pick_display = df_pick_display.head(8)
        
        # 使用自定义HTML表格确保样式一致
        pick_html = "<table class='custom-table'>"
        
        # 添加表头
        pick_html += "<thead><tr>"
        for col in df_pick_display.columns:
            pick_html += f"<th>{col}</th>"
        pick_html += "</tr></thead>"
        
        # 添加表格内容
        pick_html += "<tbody>"
        for _, row in df_pick_display.iterrows():
            pick_html += "<tr>"
            for col in df_pick_display.columns:
                cell_value = row[col]
                pick_html += f"<td>{cell_value}</td>"
            pick_html += "</tr>"
        pick_html += "</tbody></table>"
        
        st.markdown(pick_html, unsafe_allow_html=True)

# ---------------------- 9. 页面底部信息 ----------------------
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown(f"<div style='font-size: 16px; font-weight: 600;'>📅 页面加载时间：{st.session_state.page_load_time.strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 16px; font-weight: 600;'>⏰ 最后刷新时间：{st.session_state.last_refresh_time.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

with footer_col2:
    if st.session_state.auto_refresh_enabled:
        st.markdown(f"<div style='font-size: 16px; font-weight: 600;'>🔄 自动刷新间隔：{st.session_state.refresh_interval}分钟</div>", unsafe_allow_html=True)
        next_refresh_time = st.session_state.page_load_time + timedelta(minutes=st.session_state.refresh_interval)
        st.markdown(f"<div style='font-size: 16px; font-weight: 600;'>⏳ 预计下次刷新：{next_refresh_time.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size: 16px; font-weight: 600;'>❌ 自动刷新：已禁用</div>", unsafe_allow_html=True)

with footer_col3:
    st.markdown("<div style='font-size: 16px; font-weight: 600;'>📊 WGQ物流数据分析系统</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 14px; font-weight: 500; color: #6B7280;'>Version 2.0 | 数据更新时间: {}</div>".format(
        datetime.now().strftime("%Y-%m-%d")
    ), unsafe_allow_html=True)

# ---------------------- 10. 自动刷新检查 ----------------------
# 如果时间到了，刷新页面
if remaining_seconds <= 0 and st.session_state.auto_refresh_enabled:
    st.session_state.page_load_time = datetime.now()
    time.sleep(1)
    st.rerun()