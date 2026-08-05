import streamlit as st
import sys
import io
import traceback

# 1. Configure the page setup
st.set_page_config(
    page_title="Interactive Python Executor",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Interactive Python Script Runner")
st.markdown("Type your Python code below and click **Run Script** to see the console output.")

# 2. Define a default starter script for the user
default_code = """# Write your Python code here
def greet(name):
    return f"Hello, {name}!"

print(greet("Streamlit User"))

# Try printing a loop
for i in range(3):
    print(f"Processing item {i}...")
"""

# 3. Create a layout with two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Python Script")
    # Use form to prevent the app from refreshing on every keystroke
    with st.form(key="code_form"):
        user_code = st.text_area(
            label="Write or paste your code here:",
            value=default_code,
            height=400,
            help="Note: Execution runs in the host environment. Avoid calling blocking loops."
        )
        submit_button = st.form_submit_button(label="▶ Run Script")

with col2:
    st.subheader("Console Output")
    
    if submit_button:
        # Redirect standard output to catch print statements
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        
        try:
            # Execute the user code in a dedicated global dictionary scope
            # Using an explicit dictionary protects the local app namespace
            exec_globals = {}
            exec(user_code, exec_globals)
            
            # Revert standard output back to system default
            sys.stdout = sys.__stdout__
            
            # Retrieve the captured string print statements
            captured_output = output_buffer.getvalue()
            
            # Display results
            if captured_output:
                st.code(captured_output, language="text")
            else:
                st.info("Script executed successfully, but returned no print output.")
                
        except Exception as e:
            # Safely revert standard output even if an error hits
            sys.stdout = sys.__stdout__
            
            # Capture the exact line location and message of the error
            error_msg = traceback.format_exc()
            st.error("An error occurred during execution:")
            st.code(error_msg, language="python")
    else:
        st.caption("Waiting for script execution...")
