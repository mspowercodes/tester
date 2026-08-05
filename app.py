import streamlit as st
import sys
import io
import traceback

st.set_page_config(
    page_title="Instant Python Output",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Instant Auto-Print Python Runner")
st.markdown("Type any Python script here. All results and created variables will display automatically below.")

# Standard default code
default_code = """# Write your calculations, functions, or variables below
secret_message = "hello world"
shifted_amount = 3

# Math equations evaluate automatically
50 * 3
"""

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Python Script")
    with st.form(key="code_form"):
        user_code = st.text_area(
            label="Your Python Script:",
            value=default_code,
            height=350
        )
        submit_button = st.form_submit_button(label="▶ Run Script")

with col2:
    st.subheader("Output View")
    
    if submit_button:
        # 1. Setup execution tracking environment
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        
        # Isolate the user workspace dictionary
        exec_globals = {}
        
        try:
            # Clean up trailing spaces and break the script down by line entries
            raw_lines = user_code.strip().split('\n')
            clean_lines = [line for line in raw_lines if line.strip() and not line.strip().startswith('#')]
            
            if clean_lines:
                # Group all configuration setup lines together
                setup_block = '\n'.join(clean_lines[:-1])
                last_active_line = clean_lines[-1].strip()
                
                # Execute all background code lines first
                if setup_block:
                    exec(setup_block, exec_globals)
                
                # Try evaluating the final active line as a raw math equation/expression
                try:
                    final_eval = eval(last_active_line, exec_globals)
                except Exception:
                    # If it's a structural assignment line instead (like x = 5), run it as a statement
                    exec(last_active_line, exec_globals)
                    final_eval = None
            else:
                final_eval = None

            # 2. Revert back the system console default state
            sys.stdout = sys.__stdout__
            console_prints = output_buffer.getvalue()
            
            # 3. AUTO-PRINT LOGIC: Display everything found to the screen
            has_displayed_content = False
            
            # Display explicitly typed print() commands if present
            if console_prints.strip():
                st.write("**Console Output:**")
                st.code(console_prints, language="text")
                has_displayed_content = True
                
            # Display raw evaluations (e.g. 50 * 3 or variable reads)
            if final_eval is not None:
                st.success(f"**Result:** `{final_eval}`")
                has_displayed_content = True
                
            # Automatically find and display any new variables created by the user
            user_variables = {
                k: v for k, v in exec_globals.items() 
                if k != '__builtins__' and not k.startswith('__')
            }
            
            if user_variables:
                st.write("**Created Variables:**")
                for name, val in user_variables.items():
                    st.info(f"👉 `{name}` = `{val}`")
                has_displayed_content = True
                
            # Fallback guard check if they left absolutely everything blank
            if not has_displayed_content:
                st.warning("⚠️ Script ran fine, but found no text, expressions, or variables to display.")
                
        except Exception as e:
            # Safely restore console layout during runtime execution errors
            sys.stdout = sys.__stdout__
            error_msg = traceback.format_exc()
            st.error("❌ Python Execution Error:")
            st.code(error_msg, language="python")
    else:
        st.caption("Waiting for script execution...")
