import streamlit as st
import sys
import io
import traceback
import ast

st.set_page_config(
    page_title="Instant Python Output",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Instant Auto-Print Python Runner")
st.markdown("Type any Python script below. All results, variables, and outputs will display automatically.")

# Default starter code showing a multi-line function assignment and execution
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)

# Run the function with a secret message
secret = caesar_shift3("hello world")
"""

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Python Script")
    with st.form(key="code_form"):
        user_code = st.text_area(
            label="Your Python Script:",
            value=default_code,
            height=400
        )
        submit_button = st.form_submit_button(label="▶ Run Script")

with col2:
    st.subheader("Output View")
    
    if submit_button:
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        
        # Track baseline environment keys to filter out later
        baseline_globals = set(globals().keys()) | {'baseline_globals', 'exec_globals'}
        exec_globals = {}
        
        try:
            # 1. Parse the entire script into a complete Abstract Syntax Tree structure
            cleaned_code = user_code.strip()
            tree = ast.parse(cleaned_code)
            final_eval = None
            
            # 2. Check if the very last structural block is a raw expression (like calling a function or variable)
            if tree.body and isinstance(tree.body[-1], ast.Expr):
                last_expr = tree.body.pop()
                
                # Execute all preceding code blocks together safely
                if tree.body:
                    exec(compile(tree, filename="<ast>", mode="exec"), exec_globals)
                
                # Explicitly evaluate only the final standalone expression line
                expr_mode = ast.Expression(last_expr.value)
                final_eval = eval(compile(expr_mode, filename="<ast>", mode="eval"), exec_globals)
            else:
                # If the last block is a statement (like an assignment 'secret = ...'), run the full tree safely
                exec(compile(tree, filename="<ast>", mode="exec"), exec_globals)
            
            # 3. Restore the server console defaults
            sys.stdout = sys.__stdout__
            console_prints = output_buffer.getvalue()
            
            # 4. AUTO-PRINT DISPLAY ENGINE
            has_displayed_content = False
            
            # Display any standard print() commands if the user used them
            if console_prints.strip():
                st.write("**Console Output:**")
                st.code(console_prints, language="text")
                has_displayed_content = True
                
            # Display raw trailing calculation or function execution results
            if final_eval is not None:
                st.success(f"**Returned Value:** `{final_eval}`")
                has_displayed_content = True
                
            # Automatically find and print all variables created anywhere in the script
            user_variables = {
                k: v for k, v in exec_globals.items() 
                if k not in baseline_globals and not k.startswith('__') and not callable(v)
            }
            
            if user_variables:
                st.write("**Created Variables (Auto-Printed):**")
                for name, val in user_variables.items():
                    st.info(f"👉 `{name}` = `{val}`")
                has_displayed_content = True
                
            if not has_displayed_content:
                st.warning("⚠️ Script completed successfully, but did not generate any variable outputs or text values.")
                
        except Exception as e:
            # Always ensure the server environment is restored even during structural errors
            sys.stdout = sys.__stdout__
            error_msg = traceback.format_exc()
            st.error("❌ Python Execution Error:")
            st.code(error_msg, language="python")
    else:
        st.caption("Waiting for script execution...")
