import streamlit as st
import sys
import io
import traceback
import ast

st.set_page_config(
    page_title="Interactive Python Executor",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Interactive Python Script Runner")
st.markdown("Type your Python code below and click **Run Script** to see the output.")

# Default starter code that demonstrates both printing and expressions
default_code = """# Option 1: Use print statements
print("Hello from Streamlit Cloud!")

# Option 2: Write a function and call it
def add_numbers(a, b):
    return a + b

result = add_numbers(10, 5)
print(f"The result is: {result}")

# Option 3: Just type a raw value or calculation on the final line
2 + 2
"""

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
    st.subheader("Console Output")
    
    if submit_button:
        # 1. Setup execution environment and console redirect
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        exec_globals = {}
        
        try:
            # 2. Advanced Parsing: Separate the code body from the final line
            # This allows us to capture raw expressions (like "2+2") if there are no print statements
            cleaned_code = user_code.strip()
            lines = cleaned_code.split('\n')
            
            if lines:
                body = '\n'.join(lines[:-1])
                last_line = lines[-1]
                
                # Execute everything except the last line first
                if body:
                    exec(body, exec_globals)
                
                # Try to evaluate the last line as an expression to return a value
                try:
                    compiled_last = compile(last_line, '<string>', 'eval')
                    eval_result = eval(compiled_last, exec_globals)
                    # If it successfully evaluated and wasn't None, print it to the buffer
                    if eval_result is not None:
                        print(eval_result)
                except Exception:
                    # If the last line is a statement (like a loop or assignment), execute it normally
                    exec(last_line, exec_globals)
            else:
                exec(user_code, exec_globals)
                
            # 3. Reset console output back to system defaults
            sys.stdout = sys.__stdout__
            captured_output = output_buffer.getvalue()
            
            # 4. Display the gathered output to the user
            if captured_output.strip():
                st.code(captured_output, language="text")
            else:
                st.warning("⚠️ Script ran fine, but generated no output text. Make sure to use print() or put an expression on the final line!")
                
        except Exception as e:
            # Safety catch: Always restore stdout if the user's code crashes
            sys.stdout = sys.__stdout__
            error_msg = traceback.format_exc()
            st.error("❌ An error occurred during execution:")
            st.code(error_msg, language="python")
    else:
        st.caption("Waiting for script execution...")
