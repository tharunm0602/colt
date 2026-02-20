"""
Terraform Generator - Streamlit Frontend
=========================================

UI Features:
- Orange sidebar with Terraform Generator title and About section
- TDA Name dropdown (from directory)
- Environment dropdown (dev/qa/prod)
- Technology Stack dropdown (from parsed document)
- Tab-based file viewer
- Save to Local functionality
"""

import os
import sys
import glob
import zipfile
from pathlib import Path
from datetime import datetime
from io import BytesIO

import streamlit as st

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from parser import parse_docx, InfrastructureSpec
from templates import generate_all, GeneratedFiles
from config import DEFAULT_REGION

# Page configuration
st.set_page_config(
    page_title="Terraform Generator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Orange sidebar, visible text everywhere
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Orange Sidebar - full width */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f7931e 0%, #ff6b35 100%);
        min-width: 250px;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 1rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] span {
        color: white !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.3);
        margin: 1rem 0;
    }
    
    /* Sidebar radio buttons - full width */
    [data-testid="stSidebar"] .stRadio > div {
        width: 100%;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        width: 100%;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: white !important;
        background: rgba(255,255,255,0.15);
        border-radius: 5px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        width: 100%;
        display: block;
        cursor: pointer;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: rgba(255,255,255,0.25);
    }
    
    /* MAIN CONTENT - ensure dark text */
    .main .block-container {
        color: #333;
    }
    
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #333 !important;
    }
    
    .main p, .main li, .main td, .main th {
        color: #333 !important;
    }
    
    .main [data-testid="stMarkdownContainer"] {
        color: #333 !important;
    }
    
    .main [data-testid="stMarkdownContainer"] p,
    .main [data-testid="stMarkdownContainer"] li,
    .main [data-testid="stMarkdownContainer"] h1,
    .main [data-testid="stMarkdownContainer"] h2,
    .main [data-testid="stMarkdownContainer"] h3 {
        color: #333 !important;
    }
    
    /* Tables in main content */
    .main table {
        color: #333 !important;
    }
    
    .main table th, .main table td {
        color: #333 !important;
        border-color: #ddd;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
        background: white;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .main-header h1 {
        color: #333;
        font-size: 2rem;
        font-weight: 400;
        margin: 0;
    }
    
    .main-header .highlight {
        color: #f7931e;
        font-weight: 600;
    }
    
    /* Form labels */
    .stSelectbox label {
        color: #333 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.25rem;
    }
    
    /* Dropdown text visibility */
    .stSelectbox [data-baseweb="select"] {
        background-color: white;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background-color: white;
        color: #333 !important;
    }
    
    .stSelectbox [data-baseweb="select"] span {
        color: #333 !important;
    }
    
    [data-baseweb="menu"] {
        background-color: white;
    }
    
    [data-baseweb="menu"] li {
        color: #333 !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background-color: #f0f0f0;
    }
    
    /* Generate button */
    .stButton > button[kind="primary"] {
        background-color: #f7931e !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        border-radius: 5px !important;
        font-weight: 500 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #e8851a !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #f8f8f8;
        border-radius: 5px 5px 0 0;
        border-bottom: 1px solid #ddd;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: #666;
        padding: 0.75rem 1.25rem;
        font-size: 0.9rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #333;
        font-weight: 600;
        border-bottom: 3px solid #f7931e;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #f7931e !important;
        color: white !important;
        border: none !important;
    }
    
    /* About section in sidebar */
    .about-section {
        background: rgba(255,255,255,0.15);
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        width: 100%;
    }
    
    .about-section h4, .about-section p {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


def find_docx_files(directory: str = ".") -> list:
    """Find all .docx files in the specified directory."""
    files = glob.glob(os.path.join(directory, "*.docx"))
    return [os.path.basename(f) for f in files]


def get_tech_stacks_from_spec(spec: InfrastructureSpec) -> list:
    """Extract available technology stacks from the parsed specification."""
    stacks = []
    
    if spec.vpc_name:
        stacks.append("VPC")
    if spec.subnet_cidr:
        stacks.append("SUBNET")
    if spec.service_account_name:
        stacks.append("SERVICE ACCOUNT")
    if spec.bucket_names:
        stacks.append("GCS BUCKET")
    if spec.artifact_registry_name:
        stacks.append("ARTIFACT REGISTRY")
    if spec.workbench_name:
        stacks.append("WORKBENCH")
    
    return stacks if stacks else ["No resources found"]


def create_zip_from_files(files_dict: dict) -> BytesIO:
    """Create a zip file from generated files."""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in files_dict.items():
            zip_file.writestr(filename, content)
    
    zip_buffer.seek(0)
    return zip_buffer


def write_files_to_output(output_dir: Path, resource_path: str, files: GeneratedFiles):
    """Write Terraform files to the output directory."""
    resource_dir = output_dir / resource_path
    resource_dir.mkdir(parents=True, exist_ok=True)
    
    (resource_dir / "main.tf").write_text(files.main_tf)
    (resource_dir / "variables.tf").write_text(files.variables_tf)
    (resource_dir / "terraform.tfvars").write_text(files.terraform_tfvars)
    (resource_dir / "provider.tf").write_text(files.provider_tf)
    
    return resource_dir


def render_sidebar():
    """Render the orange sidebar."""
    with st.sidebar:
        st.markdown("## Terraform Generator")
        st.markdown("---")
        st.markdown("Generate Terraform configs from TDA documents.")


def render_generator_page():
    """Render the main generator page."""
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>Terraform <span class="highlight">Generator</span></h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'spec' not in st.session_state:
        st.session_state.spec = None
    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = {}
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    
    # Get available documents
    script_dir = Path(__file__).parent
    docx_files = find_docx_files(str(script_dir))
    
    # Main form container
    with st.container():
        # Three column layout for dropdowns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_file = st.selectbox(
                "TDA Name",
                options=[""] + docx_files,
                format_func=lambda x: "Select TDA Document..." if x == "" else x.replace(".docx", "")
            )
        
        with col2:
            environment = st.selectbox(
                "Environment",
                options=["Select Environment", "dev", "prod"]
            )
        
        with col3:
            # Parse document to get tech stacks if file selected
            tech_stacks = ["Select Technology Stack"]
            if selected_file and selected_file != "":
                try:
                    docx_path = script_dir / selected_file
                    spec = parse_docx(str(docx_path))
                    st.session_state.spec = spec
                    tech_stacks = ["Select Technology Stack", "ALL"] + get_tech_stacks_from_spec(spec)
                except Exception as e:
                    st.error(f"Error parsing document: {e}")
            
            selected_stack = st.selectbox(
                "Technology Stack",
                options=tech_stacks
            )
        
        # Project ID input (required)
        project_id = st.text_input(
            "GCP Project ID",
            placeholder="Enter your GCP Project ID (e.g., my-project-123)"
        )
        
        # Generate button (centered)
        st.write("")
        col_btn = st.columns([1, 1, 1])
        with col_btn[1]:
            generate_clicked = st.button(
                "Generate Terraform",
                type="primary",
                use_container_width=True,
                disabled=(
                    not selected_file or 
                    selected_file == "" or 
                    environment == "Select Environment" or
                    selected_stack == "Select Technology Stack" or
                    not project_id or project_id.strip() == ""
                )
            )
        
        # Handle generation
        if generate_clicked and st.session_state.spec and project_id:
            spec = st.session_state.spec
            
            generated = generate_all(spec, project_id.strip(), DEFAULT_REGION)
            
            if generated:
                all_files = {}
                for resource_path, files in generated.items():
                    prefix = resource_path.replace("/", "_")
                    all_files[f"{prefix}/main.tf"] = files.main_tf
                    all_files[f"{prefix}/variables.tf"] = files.variables_tf
                    all_files[f"{prefix}/terraform.tfvars"] = files.terraform_tfvars
                    all_files[f"{prefix}/provider.tf"] = files.provider_tf
                
                st.session_state.generated_files = all_files
                st.session_state.show_results = True
                
                output_dir = script_dir / "output"
                for resource_path, files in generated.items():
                    write_files_to_output(output_dir, resource_path, files)
                
                # Show toast notification instead of inline success message
                st.toast(f"Generated {len(generated)} resource configurations!", icon="✅")
        
        # Display results
        if st.session_state.show_results and st.session_state.generated_files:
            st.markdown("---")
            
            files = st.session_state.generated_files
            resources = sorted(list(set([k.split("/")[0] for k in files.keys()])))
            
            # Format resource names for readability
            # e.g., "vpc_sbx-colt-vpc" → "VPC: sbx-colt-vpc"
            def format_resource_name(raw_name):
                parts = raw_name.split("_", 1)
                if len(parts) == 2:
                    resource_type = parts[0].upper()
                    resource_name = parts[1]
                    return f"{resource_type}: {resource_name}"
                return raw_name
            
            resource_display_map = {r: format_resource_name(r) for r in resources}
            
            # Tabs and resource selector on same line
            col_tabs, col_resource = st.columns([3, 1])
            
            with col_resource:
                selected_display = st.selectbox(
                    "Resource",
                    options=[resource_display_map[r] for r in resources],
                    label_visibility="collapsed"
                )
                # Get back the original key
                selected_resource = [k for k, v in resource_display_map.items() if v == selected_display][0]
            
            # Tabs for the 4 file types generated
            tabs = st.tabs(["main.tf", "variables.tf", "terraform.tfvars", "provider.tf"])
            
            with tabs[0]:
                main_key = f"{selected_resource}/main.tf"
                if main_key in files:
                    st.code(files[main_key], language="hcl")
            
            with tabs[1]:
                var_key = f"{selected_resource}/variables.tf"
                if var_key in files:
                    st.code(files[var_key], language="hcl")
            
            with tabs[2]:
                tfvars_key = f"{selected_resource}/terraform.tfvars"
                if tfvars_key in files:
                    st.code(files[tfvars_key], language="hcl")
            
            with tabs[3]:
                provider_key = f"{selected_resource}/provider.tf"
                if provider_key in files:
                    st.code(files[provider_key], language="hcl")
            
            # Save button
            st.write("")
            col_save, col_spacer2 = st.columns([1, 3])
            
            with col_save:
                zip_buffer = create_zip_from_files(files)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                st.download_button(
                    label="Save To Local",
                    data=zip_buffer,
                    file_name=f"terraform_files_{timestamp}.zip",
                    mime="application/zip"
                )


def main():
    """Main application entry point."""
    render_sidebar()
    render_generator_page()


if __name__ == "__main__":
    main()

