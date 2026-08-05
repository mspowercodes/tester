import streamlit as st
import sys
import io
import traceback
import ast

st.set_page_config(
    page_title="Auto-Print Python Executor",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Auto-Print Python Script Runner")
st.markdown("Type your code below. The final calculation or variable will display automatically without typing `print()`.")

# Default starter code showing that raw calculations display instantly
default_code = """# Define variables or functions normally
subtotal = 50
tax_rate = 0.08
total_cost = subtotal * (1 + tax_rate)

# Just type the variable or calculation on the last line to see it!
total_cost"""

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Python Script")
    with st.form(key="code_form"):
        user_code = st.text_area(
            label="Write or paste your code here:",
            value=default_code,
            height=400
        )
        submit_button = st.form_submit_button(label="▶ Run Script")

with col2:
    st.subheader("Output")
    
    if submit_button:
        # Clear/setup standard text buffer for any standard print statements used
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        
        # Persistent global environment for this specific run
        exec_globals = {}
        
        try:
            # 1. Parse the user's code into an Abstract Syntax Tree (AST)
            cleaned_code = user_code.strip()
            tree = ast.parse(cleaned_code)
            
            # 2. Check if the very last line of code is a raw expression (like a variable or math)
            if tree.body and isinstance(tree.body[-1], ast.Expr):
                # Isolate the final line expression
                last_expr = tree.body.pop()
                
                # Compile and execute all lines leading up to the final expression
                if tree.body:
                    exec(compile(tree, filename="<ast>", mode="exec"), exec_globals)
                
                # Compile and explicitly evaluate the final line to extract its value
                expr_mode = ast.Expression(last_expr.value)
                final_result = eval(compile(expr_mode, filename="<ast>", mode="eval"), exec_globals)
            else:
                # If the last line is a statement (like a loop or function definition), execute normally
                exec(compile(tree, filename="<ast>", mode="exec"), exec_globals)
                final_result = None
            
            # 3. Restore standard system console output
            sys.stdout = sys.__stdout__
            captured_printed_output = output_buffer.getvalue()
            
            # 4. Display results to user
            # Show standard prints if they exist
            if captured_printed_output.strip():
                st.code(captured_printed_output, language="text")
            
            # Automatically show the final un-printed evaluation result
            if final_result is not None:
                st.metric(label="Evaluated Result:", value=str(final_result))
            elif not captured_printed_output.strip():
                st.info("Script executed successfully, but returned no value.")
                
        except Exception as e:
            # Emergency safety reset for system console
            sys.stdout = sys.__stdout__
            error_msg = traceback.format_exc()
            st.error("❌ Execution Error:")
            st.code(error_msg, language="python")
    else:
        st.caption("Waiting for script execution...")
