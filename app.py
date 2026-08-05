import streamlit as st
import subprocess
import tempfile
import os
import re
import sys
from streamlit_ace import st_ace  # Safe editor with line numbers

st.set_page_config(page_title="Function Tester Sandbox", layout="wide", page_icon="💻")
st.title("💻 Live Function Validator & Tester")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 1. Write Your Python Function")
    
    starter_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "defghijklmnopqrstuvwxyzabc")
    return message.translate(table)
"""
    
    # st_ace provides real line numbers and code highlighting.
    # The output 'user_code' remains raw Python code without line numbers inside the string.
    user_code = st_ace(
        value=starter_code,
        language="python",
        theme="monokai",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        height=380,
        show_gutter=True,  # This explicitly enables line numbers on the left side
        wrap=True
    )

with col2:
    st.subheader("⚙️ 2. Dynamic Test Inputs")
    
    # Safely scan the clean user string for the function name
    match = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", user_code)
    detected_function = match.group(1) if match else "caesar_shift3"
    st.info(f"🔄 Detected Function Name: `{detected_function}`")
    
    user_message = st.text_input("Enter a message to pass into your function:", value="hello world")
    run_button = st.button("🚀 Run My Function", type="primary", use_container_width=True)
    
    st.divider()
    st.subheader("🖥️ 3. Live Encrypted Output")

    if run_button:
        # Create temporary file and close it to avoid OS system locks
        temp_file = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
        temp_path = temp_file.name
        
        harness_logic = f"""
import sys
try:
    result = {detected_function}("{user_message}")
    print(f"[FUNCTION_RETURN]{{result}}")
except NameError:
    print("[HARNESS_ERROR] Could not find a function named '{detected_function}'.", file=sys.stderr)
except Exception as e:
    import traceback
    print(traceback.format_exc(), file=sys.stderr)
"""
        full_executable_script = user_code + "\n" + harness_logic
        temp_file.write(full_executable_script.encode('utf-8'))
        temp_file.close() 

        try:
            # Safely pass the script to the background subprocess execution layer
            process = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            stdout = process.stdout
            stderr = process.stderr
            
            if "[FUNCTION_RETURN]" in stdout:
                for line in stdout.split("\n"):
                    if line.startswith("[FUNCTION_RETURN]"):
                        final_encrypted_text = line.replace("[FUNCTION_RETURN]", "")
                        st.success("🎉 Function successfully verified!")
                        st.markdown(f"**📥 Sent to `{detected_function}`:**")
                        st.code(user_message, language="text")
                        st.markdown("**📤 Encrypted Result Return:**")
                        st.code(final_encrypted_text, language="text")
                        break
            elif stderr:
                st.error("❌ Runtime Error Found inside your script:")
                st.code(stderr.replace(temp_path, "your_script.py"), language="python")
            else:
                st.warning(f"⚠️ Did you forget `return message` inside `{detected_function}`?")

        except subprocess.TimeoutExpired:
            st.error("🐢 CPU Timeout! Infinite loop detected.")
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        st.info("The output screen is resting. Click 'Run My Function' above to see it update.")
