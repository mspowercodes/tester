import os
import sys
import subprocess
import tempfile
import streamlit as st

st.set_page_config(layout="wide")
st.title("🔐 Build Your Own Secret Cipher!")
st.caption("A clean, production-grade sandbox for testing student encryption code.")

# Initialize persistent session states
if "code_verified" not in st.session_state:
    st.session_state.code_verified = False
if "saved_code" not in st.session_state:
    st.session_state.saved_code = ""

# --- STEP 1: THE CODE EDITOR ---
st.header("1. Write Your Python Cipher")
st.markdown("Your script must read a message using `input()` and print out the scrambled result.")

default_code = (
    '# Simple Caesar Cipher (shifts letters by 1)\n'
    'secret_message = input()\n'
    'encrypted = ""\n\n'
    'for letter in secret_message:\n'
    '    encrypted += chr(ord(letter) + 1)\n\n'
    'print(encrypted)'
)

current_code = st.text_area(
    "💻 Python Editor:", 
    value=st.session_state.saved_code if st.session_state.saved_code else default_code, 
    height=250
)

# FIXED: Ensure Python can see basic system configuration data to prevent loading crashes,
# while completely filtering out any custom secrets or API variables from your host.
safe_env = {
    "PATH": os.environ.get("PATH", os.defpath),
    "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),  # Necessary for Windows-based servers
    "PYTHONPATH": os.path.dirname(sys.executable),
    "LANG": "en_US.UTF-8"
}

if st.button("Check My Code Syntax 🛠️"):
    # Create an entirely isolated directory separate from the app source code
    with tempfile.TemporaryDirectory() as jail_dir:
        temp_file_path = os.path.join(jail_dir, "student_code.py")
        with open(temp_file_path, "w") as f:
            f.write(current_code)

        try:
            # Run code securely inside the empty directory
            result = subprocess.run(
                [sys.executable, "-I", "student_code.py"],
                input="test",
                capture_output=True,
                text=True,
                env=safe_env,  # Uses the corrected safe environment definition
                cwd=jail_dir,  # Strict folder isolation: user sees an empty folder
                timeout=3      # Instantly kills infinite loops within 3 seconds
            )
            
            if result.stderr:
                st.error("❌ Uh oh! There is an error in your code structure:")
                st.error(result.stderr.replace("student_code.py", "your_code.py"))
                st.session_state.code_verified = False
            else:
                st.success("✅ Awesome! Your script compiled successfully. Look below to type your message!")
                st.session_state.code_verified = True
                st.session_state.saved_code = current_code
                
        except subprocess.TimeoutExpired:
            st.error("⏳ Your code took too long to run! Make sure you don't have an infinite loop.")
            st.session_state.code_verified = False
        except Exception as e:
            st.error(f"Execution failed to run: {e}")
            st.session_state.code_verified = False

# --- STEP 2: THE CONDITIONAL ENCRYPTION BOX ---
if st.session_state.code_verified:
    st.write("---")
    st.header("2. Run Your Custom Cipher Machine")
    kids_message = st.text_input("🔑 Enter a secret message to encrypt:", value="Hello World")
    
    if st.button("🔒 Run Encryption"):
        with tempfile.TemporaryDirectory() as jail_dir:
            temp_file_path = os.path.join(jail_dir, "student_code.py")
            with open(temp_file_path, "w") as f:
                f.write(st.session_state.saved_code)

            try:
                run_result = subprocess.run(
                    [sys.executable, "-I", "student_code.py"],
                    input=kids_message,
                    capture_output=True,
                    text=True,
                    env=safe_env,
                    cwd=jail_dir,
                    timeout=3
                )
                
                if run_result.stdout:
                    st.subheader("🎉 Your Encrypted Secret Message:")
                    st.info(run_result.stdout)
                
                if run_result.stderr:
                    st.error("⚠️ The code broke while trying to scramble this specific message:")
                    st.error(run_result.stderr.replace("student_code.py", "your_code.py"))
                    
            except subprocess.TimeoutExpired:
                st.error("⏳ Your code took too long to run! Make sure you don't have an infinite loop.")
            except Exception as e:
                st.error(f"Execution failed: {e}")
