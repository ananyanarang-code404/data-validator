import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io
import zipfile

# ----------------------------------------------------
# Constants & Default Configurations
# ----------------------------------------------------
DEFAULT_PHONE_RULES = [
    {"Country": "Singapore", "Prefix": "SG", "Digits": 8},
    {"Country": "India", "Prefix": "IN", "Digits": 10},
    {"Country": "United States", "Prefix": "US", "Digits": 10},
    {"Country": "United Kingdom", "Prefix": "UK", "Digits": 10},
]

DATE_FORMATS = {
    "YYYY-MM-DD HH:mm:ss": "%Y-%m-%d %H:%M:%S",
    "YYYY-MM-DD": "%Y-%m-%d",
    "DD/MM/YYYY": "%d/%m/%Y",
    "MM/DD/YYYY": "%m/%d/%Y",
}

VALID_PAYMENT_MODES = ["credit card", "debit card", "net banking", "upi", "paypal", "bank transfer", "cash"]
VALID_PAYMENT_STATUSES = ["success", "pending", "failed"]

# ----------------------------------------------------
# Helper Validation & Normalization Logic
# ----------------------------------------------------
def clean_phone(phone_str):
    """Removes all non-digit characters from a phone number."""
    if pd.isna(phone_str):
        return ""
    return re.sub(r'\D', '', str(phone_str))

def strip_prefix(digits, country_name_lower):
    """Strips country calling codes from digits if they are matched and length is extended."""
    if country_name_lower in ("india", "in") and digits.startswith("91") and len(digits) == 12:
        return digits[2:]
    if country_name_lower in ("singapore", "sg") and digits.startswith("65") and len(digits) == 10:
        return digits[2:]
    if country_name_lower in ("united states", "us", "usa") and digits.startswith("1") and len(digits) == 11:
        return digits[1:]
    if country_name_lower in ("united kingdom", "uk", "gb") and digits.startswith("44") and len(digits) == 12:
        return digits[2:]
    return digits

def validate_dataframe(df, phone_rules, date_format_pattern, date_format_label):
    """
    Validates the dataframe row by row.
    Returns:
        - List of statuses ('🟢 Valid', '🔴 Invalid', '🟡 Warning')
        - List of details (comma-separated validation descriptions)
    """
    statuses = []
    details_list = []
    
    # Pre-parse phone rules to lower-case dict for speed
    rules_dict = {}
    for r in phone_rules:
        c_name = str(r.get("Country", "")).strip().lower()
        c_pref = str(r.get("Prefix", "")).strip().lower()
        digits = int(r.get("Digits", 10))
        if c_name:
            rules_dict[c_name] = digits
        if c_pref:
            rules_dict[c_pref] = digits
            
    for idx, row in df.iterrows():
        errors = []
        warnings = []
        
        # 1. Order ID Validation
        order_id = str(row.get("Order ID", "")).strip()
        if pd.isna(row.get("Order ID")) or order_id == "" or order_id == "nan":
            errors.append("Missing Order ID")
            
        # 2. Customer ID Validation
        customer_id = str(row.get("Customer ID", "")).strip()
        if pd.isna(row.get("Customer ID")) or customer_id == "" or customer_id == "nan":
            errors.append("Missing Customer ID")
            
        # 3. Date & Time Validation
        order_date = str(row.get("Order Date", "")).strip()
        if pd.isna(row.get("Order Date")) or order_date == "" or order_date == "nan":
            errors.append("Missing Order Date")
        else:
            try:
                datetime.strptime(order_date, date_format_pattern)
            except ValueError:
                errors.append(f"Order Date format mismatch (expected {date_format_label})")
                
        # 4. Country & Phone Validation
        country = str(row.get("Customer Country", "")).strip().lower()
        phone = str(row.get("Customer Phone", "")).strip()
        
        if pd.isna(row.get("Customer Country")) or country == "" or country == "nan":
            errors.append("Missing Customer Country")
        elif pd.isna(row.get("Customer Phone")) or phone == "" or phone == "nan":
            errors.append("Missing Customer Phone")
        else:
            # Check phone rule
            digits_len = rules_dict.get(country)
            if digits_len is None:
                warnings.append(f"Phone validation skipped: Country '{row.get('Customer Country')}' not in configurations")
            else:
                cleaned = clean_phone(phone)
                stripped = strip_prefix(cleaned, country)
                if len(stripped) != digits_len:
                    errors.append(f"Customer Phone digits mismatch (expected {digits_len}, found {len(stripped)})")
                    
        # 5. Product Details Validation
        product_id = str(row.get("Product ID", "")).strip()
        product_name = str(row.get("Product Name", "")).strip()
        if pd.isna(row.get("Product ID")) or product_id == "" or product_id == "nan":
            errors.append("Missing Product ID")
        if pd.isna(row.get("Product Name")) or product_name == "" or product_name == "nan":
            errors.append("Missing Product Name")
            
        # 6. Quantity Validation
        qty = row.get("Quantity")
        try:
            if pd.isna(qty) or str(qty).strip() == "":
                errors.append("Missing Quantity")
            else:
                qty_val = int(float(str(qty).strip()))
                if qty_val <= 0:
                    errors.append("Quantity must be greater than 0")
        except ValueError:
            errors.append("Quantity must be a valid integer")
            
        # 7. Unit Price Validation
        price = row.get("Unit Price")
        try:
            if pd.isna(price) or str(price).strip() == "":
                errors.append("Missing Unit Price")
            else:
                price_val = float(str(price).strip())
                if price_val <= 0.0:
                    errors.append("Unit Price must be greater than 0")
        except ValueError:
            errors.append("Unit Price must be a valid decimal")
            
        # 8. Payment Mode Validation
        pay_mode = str(row.get("Payment Mode", "")).strip().lower()
        if pd.isna(row.get("Payment Mode")) or pay_mode == "" or pay_mode == "nan":
            errors.append("Missing Payment Mode")
        elif pay_mode not in VALID_PAYMENT_MODES:
            errors.append(f"Invalid Payment Mode '{row.get('Payment Mode')}'")
            
        # 9. Transaction ID Validation
        txn_id = str(row.get("Transaction ID", "")).strip()
        if pd.isna(row.get("Transaction ID")) or txn_id == "" or txn_id == "nan":
            errors.append("Missing Transaction ID")
            
        # 10. Payment Status Validation
        pay_status = str(row.get("Payment Status", "")).strip().lower()
        if pd.isna(row.get("Payment Status")) or pay_status == "" or pay_status == "nan":
            errors.append("Missing Payment Status")
        elif pay_status not in VALID_PAYMENT_STATUSES:
            errors.append(f"Invalid Payment Status '{row.get('Payment Status')}'")
            
        # Compile Row Status
        if len(errors) > 0:
            statuses.append("🔴 Invalid")
            details_list.append("; ".join(errors))
        elif len(warnings) > 0:
            statuses.append("🟡 Warning")
            details_list.append("; ".join(warnings))
        else:
            statuses.append("🟢 Valid")
            details_list.append("Data is clean")
            
    return statuses, details_list

# ----------------------------------------------------
# Main UI Presentation Function
# ----------------------------------------------------
def main():
    # Set Streamlit Page Configuration
    # Note: st.set_page_config must be called as the first Streamlit command
    # and only once per app run.
    
    # Custom Premium Styling
    st.markdown("""
    <style>
        /* Main Layout */
        .stApp {
            background: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                        radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 45%),
                        #0b0f19;
            color: #f8fafc;
        }
        
        /* Headers & Subtitles */
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }
        
        .glow-title {
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #6366f1, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px !important;
            padding-bottom: 5px !important;
        }
        
        .subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #0e1322 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }
        
        /* Config Panel Headers */
        .sidebar-header {
            font-size: 1.25rem;
            font-weight: 600;
            color: #6366f1;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 0.5rem;
        }
        
        /* Custom Card Design */
        .metric-card {
            background: rgba(22, 30, 49, 0.45);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s ease-in-out;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.3);
        }
        .metric-title {
            font-size: 0.85rem;
            color: #94a3b8;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            font-family: 'Outfit', sans-serif;
            line-height: 1.2;
            margin-top: 0.25rem;
        }
        .metric-val-total { color: #38bdf8; }
        .metric-val-valid { color: #34d399; }
        .metric-val-invalid { color: #f87171; }
        .metric-val-warning { color: #fbbf24; }
        
        /* Edit Tip */
        .editing-tip {
            font-size: 0.8rem;
            color: #64748b;
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='glow-title'>ValidatorAI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Real-time Transaction Data Validation, Processing & Chunk Splitting Hub</p>", unsafe_allow_html=True)

    # Initialize Session State
    if 'phone_rules' not in st.session_state:
        st.session_state.phone_rules = pd.DataFrame(DEFAULT_PHONE_RULES)

    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None

    # Sidebar Controls & Configurations
    with st.sidebar:
        st.markdown("<div class='sidebar-header'>⚙️ Configuration Controls</div>", unsafe_allow_html=True)
        
        # 1. Loading Demo Dataset (Instant UX)
        st.subheader("💡 Sandbox Helpers")
        if st.button("🚀 Load Demo Dataset", type="primary", use_container_width=True):
            st.session_state.df = pd.read_csv("sample_transactions.csv")
            st.session_state.file_name = "sample_transactions.csv"
            st.toast("Loaded sample dataset!", icon="🚀")

        st.markdown("---")
        
        # 2. Predefined Date/Time Formats
        st.subheader("📅 Date Validation Format")
        selected_date_label = st.selectbox(
            "Expected Date-Time Format:",
            list(DATE_FORMATS.keys()),
            index=0
        )
        date_pattern = DATE_FORMATS[selected_date_label]
        
        st.markdown("---")
        
        # 3. CSV File Chunking Config
        st.subheader("✂️ CSV Splitting Config")
        chunk_size = st.number_input(
            "Max Rows per CSV Chunk:",
            min_value=1,
            max_value=10000,
            value=3,
            step=1,
            help="The engine splits your validated CSV into smaller parts of this size."
        )
        
        st.markdown("---")
        
        # 4. Configurable Phone Length Rules (via editable table)
        st.subheader("📞 Phone validation rules")
        st.markdown("<span style='font-size:0.75rem; color:#94a3b8;'>Edit digit expectations by Country Name or Prefix:</span>", unsafe_allow_html=True)
        
        # Render an editable table for rules
        edited_rules = st.data_editor(
            st.session_state.phone_rules,
            num_rows="dynamic",
            use_container_width=True,
            key="rules_editor",
            column_config={
                "Country": st.column_config.TextColumn("Country", required=True),
                "Prefix": st.column_config.TextColumn("Prefix (Code)", required=True),
                "Digits": st.column_config.NumberColumn("Digits", min_value=4, max_value=15, step=1, required=True),
            }
        )
        # Save rules back to state
        st.session_state.phone_rules = edited_rules

    # Main Content Area: File Upload Widget
    uploaded_file = st.file_uploader(
        "Drag and drop your transaction CSV here",
        type=["csv"],
        help="CSVs containing columns like Order ID, Customer Phone, Product Name, Unit Price, etc."
    )

  if uploaded_file is not None:
    # If a new file is uploaded, reload it into session state
    if st.session_state.file_name != uploaded_file.name:

        df = pd.read_csv(uploaded_file)

        # Normalize column names
        df.columns = df.columns.str.strip()

        column_mapping = {
            "order_id": "Order ID",
            "customer_id": "Customer ID",
            "order_date": "Order Date",
            "country": "Customer Country",
            "customer_country": "Customer Country",
            "phone": "Customer Phone",
            "customer_phone": "Customer Phone",
            "product_id": "Product ID",
            "product_name": "Product Name",
            "quantity": "Quantity",
            "price": "Unit Price",
            "unit_price": "Unit Price",
            "payment_mode": "Payment Mode",
            "transaction_id": "Transaction ID",
            "payment_status": "Payment Status"
        }

        df.rename(columns=column_mapping, inplace=True)
        st.write("Detected Columns:")
        st.write(df.columns.tolist())

        st.session_state.df = df
        st.session_state.file_name = uploaded_file.name

        st.toast(
            f"Successfully uploaded: {uploaded_file.name}",
            icon="📁"
        )

    # Render UI based on whether data exists
    if st.session_state.df is not None:
        # Load rules list as list of dicts for validation
        current_rules = st.session_state.phone_rules.to_dict('records')
        
        # Filter validation columns if they were previously saved, so we don't duplicate them
        clean_base_df = st.session_state.df.copy()
        if 'Validation Status' in clean_base_df.columns:
            clean_base_df = clean_base_df.drop(columns=['Validation Status', 'Validation Details'])
        
        # Execute Validation Engine
        statuses, details = validate_dataframe(clean_base_df, current_rules, date_pattern, selected_date_label)
        
        # Attach Validation Columns
        clean_base_df.insert(0, 'Validation Status', statuses)
        clean_base_df.insert(1, 'Validation Details', details)
        
        # Calculate Metrics
        total_records = len(clean_base_df)
        valid_records = statuses.count("🟢 Valid")
        invalid_records = statuses.count("🔴 Invalid")
        warning_records = statuses.count("🟡 Warning")
        
        # Display Gorgeous Metrics Dashboard
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-title">📋 Total Records</span>
                <span class="metric-value metric-val-total">{total_records}</span>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-title">✅ Valid Records</span>
                <span class="metric-value metric-val-valid">{valid_records}</span>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-title">❌ Invalid Records</span>
                <span class="metric-value metric-val-invalid">{invalid_records}</span>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-title">⚠️ Warnings</span>
                <span class="metric-value metric-val-warning">{warning_records}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("### 🔍 Dataset Viewer & Live In-Place Editor")
        st.markdown("<div class='editing-tip'>💡 <b>Pro Tip:</b> Double-click any cellular detail (like customer phone, quantities, dates) to edit and fix errors instantly. The grid will re-validate dynamically.</div>", unsafe_allow_html=True)
        
        # Columns selector to filter preview rows
        filter_choice = st.radio(
            "Show Records:",
            ["All Records", "Valid Only", "Invalid Only", "Warnings Only"],
            horizontal=True
        )
        
        # Filter dataset for preview
        filtered_df = clean_base_df.copy()
        if filter_choice == "Valid Only":
            filtered_df = filtered_df[filtered_df['Validation Status'] == "🟢 Valid"]
        elif filter_choice == "Invalid Only":
            filtered_df = filtered_df[filtered_df['Validation Status'] == "🔴 Invalid"]
        elif filter_choice == "Warnings Only":
            filtered_df = filtered_df[filtered_df['Validation Status'] == "🟡 Warning"]
            
        # Render Data Editor
        # We disable editability on Validation columns to prevent logical overriding
        disabled_cols = ["Validation Status", "Validation Details"]
        
        edited_df = st.data_editor(
            filtered_df,
            use_container_width=True,
            num_rows="fixed",
            key="data_viewer",
            disabled=disabled_cols,
            column_config={
                "Validation Status": st.column_config.TextColumn("Status", width="small"),
                "Validation Details": st.column_config.TextColumn("Errors / Verification Notes", width="large"),
            }
        )
        
        # Sync edits back to the main session dataframe
        # If the user edited cell values, we replace modified rows in st.session_state.df
        if not edited_df.equals(filtered_df):
            # Merge edits back to base df using index
            for idx in edited_df.index:
                for col in clean_base_df.columns:
                    if col not in disabled_cols:
                        st.session_state.df.loc[idx, col] = edited_df.loc[idx, col]
            st.rerun()

        # Processing & Download Operations
        st.markdown("### 📥 Processing & Clean Exports")
        
        # Filter valid rows (cleaned output dataset)
        valid_rows_only = clean_base_df[clean_base_df['Validation Status'] == "🟢 Valid"].copy()
        # Remove validation-specific helper columns for download
        export_cleaned_df = valid_rows_only.drop(columns=['Validation Status', 'Validation Details'])
        
        # Build Error Report
        invalid_rows_only = clean_base_df[clean_base_df['Validation Status'] != "🟢 Valid"].copy()
        
        # Setup download button columns
        col_d1, col_d2, col_d3 = st.columns(3)
        
        # 1. Download Cleaned Dataset
        with col_d1:
            cleaned_csv_data = export_cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="✨ Download Cleaned CSV (Valid Only)",
                data=cleaned_csv_data,
                file_name="cleaned_transactions.csv",
                mime="text/csv",
                use_container_width=True,
                help="Downloads a file containing only the green/validated rows, formatted exactly like the input."
            )
            
        # 2. Download Error Report
        with col_d2:
            error_csv_data = invalid_rows_only.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📋 Download Validation Error Report",
                data=error_csv_data,
                file_name="validation_error_report.csv",
                mime="text/csv",
                use_container_width=True,
                help="Downloads a report containing all invalid and warned rows, including explanation columns.",
                disabled=len(invalid_rows_only) == 0
            )
            
        # 3. Download split chunks ZIP file
        with col_d3:
            if len(export_cleaned_df) == 0:
                st.button("📦 Download Split Chunks (.ZIP)", disabled=True, use_container_width=True)
            else:
                # Generate ZIP file in-memory
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    # Divide dataset into chunks of size `chunk_size`
                    num_chunks = (len(export_cleaned_df) + chunk_size - 1) // chunk_size
                    for i in range(num_chunks):
                        start_row = i * chunk_size
                        end_row = start_row + chunk_size
                        chunk_df = export_cleaned_df.iloc[start_row:end_row]
                        
                        chunk_csv = chunk_df.to_csv(index=False).encode('utf-8')
                        zip_file.writestr(f"cleaned_transactions_part_{i+1}.csv", chunk_csv)
                        
                zip_buffer.seek(0)
                
                st.download_button(
                    label=f"📦 Download Split Chunks ({num_chunks} parts ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="cleaned_split_chunks.zip",
                    mime="application/zip",
                    use_container_width=True,
                    help=f"Splits the cleaned dataset into chunks of {chunk_size} rows and downloads them bundled inside a single ZIP file."
                )
                
    else:
        # Empty state visual instructions
        st.markdown("---")
        st.info("👋 **Welcome to ValidatorAI!** Please upload a transaction CSV dataset in the panel above, or click the **'Load Demo Dataset'** button in the sidebar to test the validation features instantly.", icon="ℹ️")
        
        st.markdown("""
        ### Expected Data Schema Details:
        Your transaction dataset should contain columns covering these fields:
        * **Order Details**: `Order ID`, `Customer ID`, `Order Date`
        * **Customer Demographics**: `Customer Country` (e.g. Singapore, India), `Customer Phone`
        * **Product Attributes**: `Product ID`, `Product Name`, `Quantity`, `Unit Price`
        * **Payment Logistics**: `Payment Mode` (e.g. Credit Card, UPI), `Transaction ID`, `Payment Status` (Success, Pending, Failed)
        """)

if __name__ == "__main__":
    main()
