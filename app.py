import streamlit as st
import subprocess
import tempfile
import os

st.set_page_config(page_title="Kids Coding Sandbox", layout="wide", page_icon="🔓")
st.title("🔏 Caesar Cipher Coding Sandbox")
st.caption("Write your Python code on the left, use the kid-friendly tools on the right to test it!")

# Setup UI Columns
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📝 Write Your Code Here")
    
    # Starter template designed for kids learning a Caesar Cipher
    starter_code = """# Kids! Your inputs are already created for you as variables:
# 'message' = the text you want to hide
# 'shift' = the secret jump number

secret_message = ""

for letter in message:
    if letter.isalpha():
        # Move the letter forward by the shift amount
        new_letter = chr(ord(letter) + shift)
        secret_message += new_letter
    else:
        # Keep spaces and punctuation the same
        secret_message += letter

# Show your final hidden message using st.write!
st.write("🔒 Encrypted Result:", secret_message)
"""
    user_code = st.text_area("Python Editor", value=starter_code, height=450)

with col2:
    st.subheader("⚙️ Test & Run Your Code")
    
    # Simple input fields for the kids to interact with
    test_message = st.text_input("1. Message to Encrypt:", value="hello world")
    test_shift = st.number_input("2. Secret Shift Number:", min_value=1, max_value=25, value=3)
    
    run_button = st.button("🚀 Run My Code!", type="primary", use_container_width=True)
    
    st.divider()
    st.subheader("🖥️ App Output Screen")

    if run_button:
        # We append a visual "mock" header to their code.
        # This makes st.write and st.success print beautiful text block wrappers instantly.
        mock_header = f"""
import sys

class MockStreamlit:
    def write(self, *args):
        text = " ".join(str(x) for x in args)
        print(f"[ST_WRITE] {{text}}")
    def success(self, *args):
        text = " ".join(str(x) for x in args)
        print(f"[ST_SUCCESS] {{text}}")

st = MockStreamlit()
message = "{test_message}"
shift = {test_shift}

# --- KIDS CODE STARTS HERE ---
"""
        full_code_to_run = mock_header + user_code
        
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_script:
            temp_script.write(full_code_to_run.encode('utf-8'))
            temp_script_path = temp_script.name

        try:
            # Execute with a 3-second timeout to stop infinite loops if a kid makes a mistake
            result = subprocess.run(
                ["python", temp_script_path], 
                capture_output=True, 
                text=True, 
                timeout=3
            )
            
            # Parse outputs and display them as Streamlit UI blocks
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if line.startswith("[ST_WRITE]"):
                        st.info(line.replace("[ST_WRITE]", "").strip())
                    elif line.startswith("[ST_SUCCESS]"):
                        st.success(line.replace("[ST_SUCCESS]", "").strip())
                    else:
                        # Standard python print() statements
                        st.code(line, language="text")
                        
            if result.stderr:
                st.error("⚠️ Oh no! Your code has a small bug:")
                # Clean up error path to avoid confusing kids with ugly file routes
                clean_error = result.stderr.replace(temp_script_path, "your_code.py")
                st.code(clean_error, language="python")

        except subprocess.TimeoutExpired:
            st.error("🐢 Timeout! Your code is stuck in an infinite loop. Check your loops!")
            
        finally:
            if os.path.exists(temp_script_path):
                os.remove(temp_script_path)
    else:
        st.info("Your app results will appear here after you press 'Run My Code!'")
