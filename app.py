import streamlit as st
import subprocess
import tempfile
import os
import re
import sys

st.set_page_config(page_title="Function Tester Sandbox", layout="wide", page_icon="💻")
st.title("💻 Live Function Validator & Tester")

starter_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "defghijklmnopqrstuvwxyzabc")
    return message.translate(table)
"""

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 1. Write Your Python Function")
    
    # CRITICAL FIX: The form stops Streamlit from rerunning on every keystroke
    with st.form("code_form"):
        num_col, code_col = st.columns([0.1, 1.9])
        
        with num_col:
            st.markdown(
                "<div style='text-align: right; color: gray; font-family: monospace; line-height: 2.15; padding-top: 5px; font-size: 14px;'>" + 
                "<br>".join(str(i) for i in range(1, 21)) + 
                "</div>", 
                unsafe_allow_html=True
            )
            
        with code_col:
            user_code = st.text_area(
                "Python Code Editor:", 
                value=starter_code, 
                height=465, 
                label_visibility="collapsed"
            )
            
        # The form submit button locks the text area data safely
        submit_code = st.form_submit_button("🔒 Lock Code Changes", type="secondary", use_container_width=True)

with col2:
    st.subheader("⚙️ 2. Dynamic Test Inputs")
    
    # Process the regex search safely now that user_code won't change mid-type
    match = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", user_code)
    detected_function = match.group(1) if match else "caesar_shift3"
    st.info(f"🔄 Detected Function Name: `{detected_function}`")
    
    user_message = st.text_input("Enter a message to pass into your function:", value="hello world")
    run_button = st.button("🚀 Run My Function", type="primary", use_container_width=True)
    
    st.divider()
    st.subheader("🖥️ 3. Live Encrypted Output")

    if run_button:
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
                st.warning(f"⚠️ Did you forget a `return` statement inside `{detected_function}`?")

        except subprocess.TimeoutExpired:
            st.error("🐢 CPU Timeout! Infinite loop detected inside code structure.")
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        st.info("The output screen is resting. Click 'Run My Function' above to see it update.")
