"""
Enhanced GUI components for the Phone Intelligence Tool
Provides reusable UI components with consistent styling
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import pandas as pd

class PhoneIntelligenceUI:
    """Enhanced UI components for phone intelligence tool"""
    
    @staticmethod
    def render_header():
        """Render enhanced header with branding"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .header-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
        }
        .feature-badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            margin: 0.2rem;
            font-size: 0.9rem;
            backdrop-filter: blur(10px);
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="main-header">
            <div class="header-title">📱 Phone Intelligence Pro</div>
            <div class="header-subtitle">Advanced OSINT & Security Analysis Platform</div>
            <div style="margin-top: 1rem;">
                <span class="feature-badge">🔍 OSINT Analysis</span>
                <span class="feature-badge">🛡️ Security Scoring</span>
                <span class="feature-badge">🌍 Geolocation</span>
                <span class="feature-badge">📊 Batch Processing</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metric_card(title, value, icon, color="blue", delta=None):
        """Render enhanced metric card"""
        delta_html = ""
        if delta:
            delta_color = "green" if delta > 0 else "red"
            delta_symbol = "↗" if delta > 0 else "↘"
            delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem;">{delta_symbol} {abs(delta)}%</div>'
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 5px solid {color};
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
            transition: transform 0.2s ease;
        ">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">{icon} {title}</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #1e293b;">{value}</div>
                    {delta_html}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_risk_gauge(risk_score, title="Risk Assessment"):
        """Render interactive risk gauge"""
        colors = ["#10b981", "#f59e0b", "#ef4444"]
        color_idx = 0 if risk_score < 40 else 1 if risk_score < 70 else 2
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title, 'font': {'size': 20}},
            delta = {'reference': 50, 'increasing': {'color': "#ef4444"}, 'decreasing': {'color': "#10b981"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': colors[color_idx], 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': '#dcfce7'},
                    {'range': [40, 70], 'color': '#fef3c7'},
                    {'range': [70, 100], 'color': '#fee2e2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            font={'color': "darkblue", 'family': "Arial"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        return fig
    
    @staticmethod
    def render_security_indicators(security_data):
        """Render security indicators with enhanced styling"""
        st.markdown("### 🛡️ Security Indicators")
        
        indicators = [
            ("Spam Risk", security_data.get('is_spam_risk', False), "🚨", "#ef4444"),
            ("VoIP Number", security_data.get('is_voip', False), "📞", "#f59e0b"),
            ("Verified Carrier", security_data.get('verified_carrier', True), "✅", "#10b981"),
            ("Known Scammer", security_data.get('is_scammer', False), "🚫", "#ef4444")
        ]
        
        cols = st.columns(2)
        for i, (label, status, icon, color) in enumerate(indicators):
            with cols[i % 2]:
                status_text = "Yes" if status else "No"
                bg_color = color if status else "#e2e8f0"
                text_color = "white" if status else "#64748b"
                
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    color: {text_color};
                    padding: 1rem;
                    border-radius: 8px;
                    text-align: center;
                    margin: 0.5rem 0;
                    font-weight: 600;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                ">
                    {icon} {label}<br>
                    <span style="font-size: 1.2rem;">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def render_analysis_timeline():
        """Render analysis timeline"""
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        
        st.markdown("### 📈 Analysis Timeline")
        
        if st.session_state.analysis_history:
            # Create timeline chart
            df_history = pd.DataFrame(st.session_state.analysis_history)
            
            fig = px.line(
                df_history, 
                x='timestamp', 
                y='risk_score',
                title='Risk Score Trends',
                markers=True
            )
            
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Risk Score",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No analysis history available yet.")
    
    @staticmethod
    def render_export_section(results):
        """Enhanced export section with multiple formats"""
        st.markdown("### 📤 Export & Reporting")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # JSON export
            json_data = json.dumps(results, indent=2, default=str)
            st.download_button(
                label="📄 JSON",
                data=json_data,
                file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # CSV export
            df = pd.json_normalize(results)
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📊 CSV",
                data=csv_data,
                file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            # XML export
            xml_data = dict_to_xml(results)
            st.download_button(
                label="📋 XML",
                data=xml_data,
                file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml",
                mime="application/xml",
                use_container_width=True
            )
        
        with col4:
            # Report summary
            if st.button("📑 Generate Report", use_container_width=True):
                generate_analysis_report(results)

def dict_to_xml(data, root_name="analysis"):
    """Convert dictionary to XML format"""
    def dict_to_xml_recursive(d, parent_name):
        xml_str = f"<{parent_name}>"
        for key, value in d.items():
            if isinstance(value, dict):
                xml_str += dict_to_xml_recursive(value, key)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        xml_str += dict_to_xml_recursive(item, key)
                    else:
                        xml_str += f"<{key}>{item}</{key}>"
            else:
                xml_str += f"<{key}>{value}</{key}>"
        xml_str += f"</{parent_name}>"
        return xml_str
    
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{dict_to_xml_recursive(data, root_name)}'

def generate_analysis_report(results):
    """Generate comprehensive analysis report"""
    st.markdown("### 📑 Analysis Report Generated")
    
    report_content = f"""
    # Phone Number Intelligence Report
    
    **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ## Executive Summary
    - **Phone Number:** {results.get('formatted_number', 'N/A')}
    - **Risk Score:** {results.get('risk_score', 0)}/100
    - **Country:** {results.get('country', 'Unknown')}
    - **Carrier:** {results.get('carrier', 'Unknown')}
    
    ## Detailed Findings
    {json.dumps(results, indent=2, default=str)}
    """
    
    st.download_button(
        label="📥 Download Full Report",
        data=report_content,
        file_name=f"phone_intelligence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )
