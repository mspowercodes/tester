import streamlit as st
import subprocess
import tempfile
import sys
import psutil
import platform

# 1. Page Configuration
st.set_page_config(
    page_title="Secure Python Runner",
    page_icon="🛡️",
    layout="wide"
)

# 2. Sidebar Layout - Environment Info & Limits
with st.sidebar:
    st.header("⚙️ Runner Configuration")
    
    # Execution Time Safety Limit
    timeout_limit = st.slider(
        "Maximum Execution Time (Seconds)", 
        min_value=1, 
        max_value=30, 
        value=5,
        help="Forces code to stop if it gets stuck in an infinite loop."
    )
    
    st.divider()
    st.subheader("🖥️ Host System Info")
    st.text(f"OS: {platform.system()} ({platform.release()})")
    st.text(f"Python Ver: {platform.python_version()}")
    
    # Live CPU / Memory usage tracking
    cpu_use = psutil.cpu_percent()
    mem_use = psutil.virtual_memory().percent
    st.progress(cpu_use / 100, text=f"Host CPU Usage: {cpu_use}%")
    st.progress(mem_use / 100, text=f"Host RAM Usage: {mem_use}%")

# 3. Main Dashboard Layout
st.title("🛡️ Secure Python Subprocess Runner")
st.caption("Runs code inside an isolated standalone process. State is wiped clean on every run.")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📝 Python Script Input")
    
    # Baseline instructional code pattern
    starter_code = """# Subprocess example script
import sys
import time

print("Hello from the subprocess environment!")
print(f"Running via interpreter: {sys.executable}")

# Let's count some numbers
squares = [x**2 for x in range(1, 6)]
print(f"Calculated squares: {squares}")
"""
    
    user_code = st.text_area(
        label="Code Input Box",
        value=starter_code,
        height=450,
        label_visibility="collapsed"
    )
    
    run_btn = st.button("▶ Run Script", type="primary", use_container_width=True)

with col2:
    st.subheader("🖥️ Execution Output console")
    
    if run_btn:
        # Create a temporary secure script file on the server file system
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as temp_file:
            temp_file.write(user_code)
            temp_file_path = temp_file.name
            
        with st.spinner("Executing script..."):
            try:
                # Capture terminal processes safely using sys.executable
                # This ensures the script utilizes the exact same python packages as Streamlit
                process_result = subprocess.run(
                    [sys.executable, temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout_limit
                )
                
                # Render Console Standard Prints (STDOUT)
                if process_result.stdout:
                    st.success("Execution Output:")
                    st.code(process_result.stdout, language="text")
                
                # Render Failures/Tracebacks cleanly (STDERR)
                if process_result.stderr:
                    st.error("Runtime Error or Traceback Raised:")
                    st.code(process_result.stderr, language="python")
                    
                if not process_result.stdout and not process_result.stderr:
                    st.info("Script executed successfully but generated no console outputs.")
                    
            except subprocess.TimeoutExpired:
                st.error(f"🚨 Execution Halted! Script exceeded your {timeout_limit} second time limit.")
                st.warning("Ensure your script does not contain unresolved `while True:` loops or stuck user inputs.")
            except Exception as system_err:
                st.error(f"Internal runner failure: {str(system_err)}")
    else:
        st.info("Write your Python script and click 'Run Script' to execute.")
