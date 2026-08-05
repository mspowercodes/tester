import os
import sys
import subprocess
import tempfile
import streamlit as st

# Platform check for Linux/macOS resource management (Streamlit Cloud, Heroku, AWS, etc.)
if sys.platform != "win32":
    import resource

st.set_page_config(layout="wide")
st.title("🔐 Build Your Own Secret Cipher!")
st.caption("A secure sandbox for testing student encryption functions.")

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

def limit_resources():
    """Enforces strict kernel-level hardware restrictions on the spawned script."""
    if sys.platform != "win32":
        # Hard cap RAM usage to 100MB to stop memory exhaustion attacks
        max_memory = 100 * 1024 * 1024 
        resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
        # Hard cap raw CPU processing time to 2 seconds to instantly kill infinite loops
        resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
        # Prevent the script from spawning any sub-processes (blocks fork bombs)
        resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))

if st.button("Check My Code Syntax 🛠️"):
    # Clear out environment inheritance entirely to hide host secrets
    clean_env = {"PATH": os.defpath, "LANG": "en_US.UTF-8"}
    
    # SECURITY: Create a temporary jail directory separate from the app's source code
    with tempfile.TemporaryDirectory() as jail_dir:
        temp_file_path = os.path.join(jail_dir, "student_code.py")
        with open(temp_file_path, "w") as f:
            f.write(current_code)

        try:
            # Execute Python in Isolated mode (-I) inside the empty sandbox directory (cwd=jail_dir)
            result = subprocess.run(
                [sys.executable, "-I", "student_code.py"],
                input="test",
                capture_output=True,
                text=True,
                env=clean_env,
                preexec_fn=limit_resources,
                cwd=jail_dir,  # CRITICAL: Forces Python to see an empty folder as its root
                timeout=3
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
            st.error(f"Execution blocked by security policy: {e}")
            st.session_state.code_verified = False

# --- STEP 2: THE CONDITIONAL ENCRYPTION BOX ---
if st.session_state.code_verified:
    st.write("---")
    st.header("2. Run Your Custom Cipher Machine")
    kids_message = st.text_input("🔑 Enter a secret message to encrypt:", value="Hello World")
    
    if st.button("🔒 Run Encryption"):
        clean_env = {"PATH": os.defpath, "LANG": "en_US.UTF-8"}
        
        # SECURITY: Re-sandbox the environment for the active payload execution
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
                    env=clean_env,
                    preexec_fn=limit_resources,
                    cwd=jail_dir,  # CRITICAL: Ensures student code can't read your main project files
                    timeout=3
                )
                
                if run_result.stdout:
                    st.subheader("🎉 Your Encrypted Secret Message:")
                    st.info(run_result.stdout)
                
                if run_result.stderr:
                    st.error("⚠️ The code broke while trying to scramble this specific message:")
                    st.error(run_result.stderr.replace("student_code.py", "your_code.py"))
                    
            except Exception as e:
                st.error(f"Execution failed: {e}")

