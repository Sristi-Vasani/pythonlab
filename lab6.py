import streamlit as st
import pandas as pd
import plotly.express as px
import uuid
from datetime import datetime, date
import os
import json

st.set_page_config(page_title="Crime Unit Management System", layout="wide", initial_sidebar_state="expanded", page_icon="🚓")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f4e79; text-align: center; margin-bottom: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin: 0.5rem 0; }
    .success-message { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 0.75rem; border-radius: 0.375rem; margin: 1rem 0; }
    .warning-message { background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 0.75rem; border-radius: 0.375rem; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🚓 Crime Unit Management System</h1>', unsafe_allow_html=True)

def initialize_session_state():
    if "crimes" not in st.session_state:
        st.session_state.crimes = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = {}
    if "officers" not in st.session_state:
        st.session_state.officers = ["Officer Smith", "Officer Johnson", "Officer Brown", "Officer Davis", "Officer Wilson"]

initialize_session_state()

CRIME_TYPES = ["Theft", "Murder", "Assault", "Cybercrime", "Fraud", "Burglary", "Drug Offense", "Vandalism", "Domestic Violence", "Other"]
STATUSES = ["Open", "Under Investigation", "Closed", "Cold Case", "Pending Review"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]

def generate_crime_id():
    return f"CASE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

def validate_form_data(crime_type, location, officer, description):
    errors = []
    if not crime_type:
        errors.append("Crime type is required")
    if not location or len(location.strip()) < 2:
        errors.append("Location must be at least 2 characters long")
    if not officer:
        errors.append("Officer assignment is required")
    if not description or len(description.strip()) < 10:
        errors.append("Description must be at least 10 characters long")
    return errors

def export_to_csv(data):
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.drop(columns=["File"], errors='ignore')
    return df.to_csv(index=False).encode('utf-8')

with st.sidebar:
    st.header("🎛️ Navigation & Filters")
    total_cases = len(st.session_state.crimes)
    if total_cases > 0:
        df_temp = pd.DataFrame(st.session_state.crimes)
        open_cases = len(df_temp[df_temp['Status'] == 'Open'])
        closed_cases = len(df_temp[df_temp['Status'] == 'Closed'])
        st.markdown("### 📊 Quick Stats")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cases", total_cases)
        with col2:
            st.metric("Open Cases", open_cases)
        with col3:
            st.metric("Closed Cases", closed_cases)
    
    st.markdown("### 👮 Officer Management")
    new_officer = st.text_input("Add New Officer")
    if st.button("➕ Add Officer") and new_officer:
        if new_officer not in st.session_state.officers:
            st.session_state.officers.append(new_officer)
            st.success(f"Officer {new_officer} added!")
        else:
            st.warning("Officer already exists!")
        

def add_crime():
    st.subheader("📝 Register a New Crime Case")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("crime_form", clear_on_submit=True):
            st.markdown("**📋 Case Information**")
            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                crime_type = st.selectbox("Crime Type *", CRIME_TYPES)
                location = st.text_input("Location *", placeholder="Enter incident location")
            with row1_col2:
                priority = st.selectbox("Priority Level", PRIORITIES, index=1)
                officer = st.selectbox("Assigned Officer *", st.session_state.officers)
            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                status = st.selectbox("Case Status", STATUSES)
            with row2_col2:
                incident_date = st.date_input("Incident Date", value=date.today())
            st.markdown("**📄 Case Details**")
            description = st.text_area("Description *", placeholder="Provide detailed description of the incident (minimum 10 characters)", height=100)
            st.markdown("**📎 Evidence & Documentation**")
            file_upload = st.file_uploader("Attach Evidence or Reports", type=["pdf", "jpg", "jpeg", "png", "docx", "txt"], accept_multiple_files=True)
            notes = st.text_area("Additional Notes", placeholder="Any additional information or notes")
            submitted = st.form_submit_button("🚀 Submit Case", use_container_width=True)
            
            if submitted:
                errors = validate_form_data(crime_type, location, officer, description)
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    crime_id = generate_crime_id()
                    uploaded_files = []
                    if file_upload:
                        os.makedirs("uploads", exist_ok=True)
                        for uploaded_file in file_upload:
                            file_name = f"uploads/{crime_id}_{uploaded_file.name}"
                            with open(file_name, "wb") as f:
                                f.write(uploaded_file.read())
                            uploaded_files.append(file_name)
                        st.session_state.uploaded_files[crime_id] = uploaded_files
                    
                    crime_record = {
                        "ID": crime_id,
                        "Type": crime_type,
                        "Location": location,
                        "Officer": officer,
                        "Status": status,
                        "Priority": priority,
                        "Description": description,
                        "Notes": notes,
                        "Date_Registered": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Incident_Date": incident_date.strftime("%Y-%m-%d"),
                        "Files": len(uploaded_files) if uploaded_files else 0
                    }
                    
                    st.session_state.crimes.append(crime_record)
                    st.success(f"✅ Case successfully registered with ID: **{crime_id}**")
    
    with col2:
        st.markdown("**📋 Form Guidelines**")
        st.info("""
        **Required Fields:**
        - Crime Type
        - Location (min 2 chars)
        - Assigned Officer
        - Description (min 10 chars)
        
        **File Upload:**
        - Supported: PDF, JPG, PNG, DOCX, TXT
        - Multiple files allowed
        
        **Tips:**
        - Be detailed in descriptions
        - Include relevant dates
        - Upload all available evidence
        """)

def view_crimes():
    st.subheader("📋 View & Manage Crime Cases")
    
    if not st.session_state.crimes:
        st.warning("📭 No cases found. Add some cases to get started!")
        return
    
    df = pd.DataFrame(st.session_state.crimes)
    
    with st.expander("🔍 Advanced Search & Filters", expanded=True):
        search_col1, search_col2, search_col3 = st.columns(3)
        
        with search_col1:
            search_text = st.text_input("🔍 Search Text", placeholder="Search in any field...")
            crime_type_filter = st.multiselect("Crime Type", CRIME_TYPES, default=[])
        
        with search_col2:
            status_filter = st.multiselect("Status", STATUSES, default=[])
            priority_filter = st.multiselect("Priority", PRIORITIES, default=[])
        
        with search_col3:
            officer_filter = st.multiselect("Officer", st.session_state.officers, default=[])
            date_range = st.date_input("Date Range", value=[], help="Select start and end dates")
    
    filtered_df = df.copy()
    
    if search_text:
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_text, case=False, na=False)).any(axis=1)
        filtered_df = filtered_df[mask]
    
    if crime_type_filter:
        filtered_df = filtered_df[filtered_df['Type'].isin(crime_type_filter)]
    
    if status_filter:
        filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
    
    if priority_filter:
        filtered_df = filtered_df[filtered_df['Priority'].isin(priority_filter)]
    
    if officer_filter:
        filtered_df = filtered_df[filtered_df['Officer'].isin(officer_filter)]
    
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df['Incident_Date'] = pd.to_datetime(filtered_df['Incident_Date'])
        filtered_df = filtered_df[
            (filtered_df['Incident_Date'] >= pd.to_datetime(start_date)) &
            (filtered_df['Incident_Date'] <= pd.to_datetime(end_date))
        ]
    
    st.markdown(f"**📊 Showing {len(filtered_df)} of {len(df)} cases**")
    
    if not filtered_df.empty:
        csv_data = export_to_csv(filtered_df.to_dict('records'))
        st.download_button(
            label="📥 Export to CSV",
            data=csv_data,
            file_name=f"crime_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv'
        )
    
        display_df = filtered_df[['ID', 'Type', 'Location', 'Officer', 'Status', 'Priority', 'Incident_Date']].copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("### 📋 Case Details")
        for idx, row in filtered_df.iterrows():
            with st.expander(f"🔎 {row['ID']} - {row['Type']} | {row['Status']}", expanded=False):
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.markdown(f"**📍 Location:** {row['Location']}")
                    st.markdown(f"**👮 Officer:** {row['Officer']}")
                    st.markdown(f"**📊 Status:** {row['Status']}")
                    st.markdown(f"**⚡ Priority:** {row['Priority']}")
                
                with detail_col2:
                    st.markdown(f"**📅 Incident Date:** {row['Incident_Date']}")
                    st.markdown(f"**📝 Registered:** {row['Date_Registered']}")
                    st.markdown(f"**📎 Files:** {row['Files']} attached")
                
                st.markdown(f"**📄 Description:**")
                st.write(row['Description'])
                
                if row.get('Notes'):
                    st.markdown(f"**📋 Notes:**")
                    st.write(row['Notes'])
                
                if row['ID'] in st.session_state.uploaded_files:
                    st.markdown("**📎 Evidence Files:**")
                    for file_path in st.session_state.uploaded_files[row['ID']]:
                        file_name = os.path.basename(file_path)
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as file:
                                st.download_button(
                                    f"📄 {file_name}",
                                    file.read(),
                                    file_name=file_name,
                                    key=f"download_{row['ID']}_{file_name}"
                                )
    else:
        st.info("🔍 No cases match your current filters. Try adjusting your search criteria.")

def crime_statistics():
    st.subheader("📊 Crime Analytics Dashboard")
    
    if not st.session_state.crimes:
        st.warning("📭 No data available for analysis. Add some cases first.")
        return
    
    df = pd.DataFrame(st.session_state.crimes)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cases", len(df))
    with col2:
        open_cases = len(df[df['Status'] == 'Open'])
        st.metric("Open Cases", open_cases, delta=f"{open_cases/len(df)*100:.1f}%")
    with col3:
        high_priority = len(df[df['Priority'] == 'High'])
        st.metric("High Priority", high_priority)
    with col4:
        avg_cases_per_officer = len(df) / len(df['Officer'].unique()) if len(df['Officer'].unique()) > 0 else 0
        st.metric("Avg Cases/Officer", f"{avg_cases_per_officer:.1f}")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### 📊 Case Status Distribution")
        status_counts = df['Status'].value_counts()
        fig_status = px.pie(values=status_counts.values, names=status_counts.index, title="Case Status Distribution", color_discrete_sequence=px.colors.qualitative.Set3)
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_status, use_container_width=True)
        
        st.markdown("### ⚡ Priority Level Analysis")
        priority_counts = df['Priority'].value_counts()
        fig_priority = px.bar(x=priority_counts.index, y=priority_counts.values, title="Cases by Priority Level", color=priority_counts.index, color_discrete_map={'Low': '#90EE90', 'Medium': '#FFD700', 'High': '#FF8C00', 'Critical': '#FF0000'})
        fig_priority.update_layout(showlegend=False)
        st.plotly_chart(fig_priority, use_container_width=True)
    
    with chart_col2:
        st.markdown("### 🔵 Crime Type Distribution")
        type_counts = df['Type'].value_counts()
        fig_type = px.bar(x=type_counts.values, y=type_counts.index, orientation='h', title="Crime Types Frequency", color=type_counts.values, color_continuous_scale='viridis')
        fig_type.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_type, use_container_width=True)
        
        st.markdown("### 👮 Officer Workload")
        officer_counts = df['Officer'].value_counts()
        fig_officer = px.bar(x=officer_counts.index, y=officer_counts.values, title="Cases per Officer", color=officer_counts.values, color_continuous_scale='blues')
        fig_officer.update_layout(coloraxis_showscale=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_officer, use_container_width=True)
    
    st.markdown("### 📅 Timeline Analysis")
    df['Incident_Date'] = pd.to_datetime(df['Incident_Date'])
    df['Month_Year'] = df['Incident_Date'].dt.to_period('M').astype(str)
    
    timeline_data = df.groupby(['Month_Year', 'Type']).size().reset_index(name='Count')
    
    if not timeline_data.empty:
        fig_timeline = px.line(timeline_data, x='Month_Year', y='Count', color='Type', title='Crime Trends Over Time', markers=True)
        fig_timeline.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    with st.expander("📋 Detailed Statistics", expanded=False):
        st.markdown("### 📊 Summary Statistics")
        
        summary_stats = {
            'Crime Type': df['Type'].value_counts().to_dict(),
            'Status': df['Status'].value_counts().to_dict(),
            'Priority': df['Priority'].value_counts().to_dict(),
            'Officer': df['Officer'].value_counts().to_dict()
        }
        
        for category, stats in summary_stats.items():
            st.markdown(f"**{category}:**")
            stats_df = pd.DataFrame(list(stats.items()), columns=[category, 'Count'])
            st.dataframe(stats_df, hide_index=True)

tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Case", "📄 View Cases", "📈 Analytics", "⚙️ Settings"])

with tab1:
    add_crime()

with tab2:
    view_crimes()

with tab3:
    crime_statistics()

with tab4:
    st.subheader("⚙️ System Settings")
    
    st.markdown("### 💾 Data Management")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Data", type="secondary"):
            if st.checkbox("I understand this will delete all cases"):
                st.session_state.crimes = []
                st.session_state.uploaded_files = {}
                st.success("All data cleared successfully!")
                st.rerun()
    
    with col2:
        if st.session_state.crimes:
            backup_data = {
                'crimes': st.session_state.crimes,
                'officers': st.session_state.officers,
                'export_date': datetime.now().isoformat()
            }
            backup_json = json.dumps(backup_data, indent=2)
            st.download_button(
                "💾 Backup Data (JSON)",
                backup_json,
                file_name=f"crime_system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    st.markdown("### ℹ️ System Information")
    st.info(f"""
    **System Status:** ✅ Active  
    **Total Cases:** {len(st.session_state.crimes)}  
    **Registered Officers:** {len(st.session_state.officers)}  
    **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
    "🚓 Crime Unit Management System | Enhanced Version | Built with Streamlit"
    "</div>", 
    unsafe_allow_html=True
)
