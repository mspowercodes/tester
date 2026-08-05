import streamlit as st
import subprocess
import tempfile
import os
import re

# Page configuration
st.set_page_config(page_title="Function Tester Sandbox", layout="wide", page_icon="💻")
st.title("💻 Live Function Validator & Tester")
st.caption("Submit your custom python function on the left, then use the dynamic interface on the right to test it safely.")

# Split interface into input and testing sides
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 1. Write Your Python Function")
    
    # Pre-populate with the example format you requested
    starter_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "defghijklmnopqrstuvwxyzabc")
    return message.translate(table)
"""
    user_code = st.text_area(
        "Python Code Editor:", 
        value=starter_code, 
        height=350,
        help="Ensure your function accepts a string argument and returns the modified string."
    )

with col2:
    st.subheader("⚙️ 2. Dynamic Test Inputs")
    
    # Step 1: Detect the function name dynamically so the boxes adapt
    # Looks for 'def function_name(' using a simple regular expression
    match = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", user_code)
    detected_function = match.group(1) if match else "caesar_shift3"
    
    st.info(f"🔄 Detected Function Name: `{detected_function}`")
    
    # Step 2: Create interactive input boxes for the user
    user_message = st.text_input(
        "Enter a message to pass into your function:", 
        value="hello world",
        placeholder="Type something to encrypt..."
    )
    
    run_button = st.button("🚀 Run My Function", type="primary", use_container_width=True)
    
    st.divider()
    st.subheader("🖥️ 3. Live Encrypted Output")

    if run_button:
        # Create a temporary file on the hosting server to run the process
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_path = temp_file.name
            
            # This logic is appended to the bottom of the user's script file safely.
            # It cleanly captures the returned value and handles edge cases.
            harness_logic = f"""
import sys

try:
    # Dynamically invoke whatever function the user defined
    result = {detected_function}("{user_message}")
    
    # Print with an explicit wrapper token for identification
    print(f"[FUNCTION_RETURN]{{result}}")
    
except NameError:
    print("[HARNESS_ERROR] Could not find a function named '{detected_function}'. Check your spelling and syntax.", file=sys.stderr)
except Exception as e:
    import traceback
    print(traceback.format_exc(), file=sys.stderr)
"""
            # Combine code strings and write out as bytes
            full_executable_script = user_code + "\n" + harness_logic
            temp_file.write(full_executable_script.encode('utf-8'))

        try:
            # Safely execute the code as an entirely isolated terminal subprocess
            # Sets a strict 3-second limit to cut off infinite loops
            process = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            stdout = process.stdout
            stderr = process.stderr
            
            # Process and display output tokens
            if "[FUNCTION_RETURN]" in stdout:
                # Extract the line containing our execution token
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
                # Sanitize the backend directory paths so error windows look tidy and readable
                clean_err = stderr.replace(temp_path, "your_script.py")
                st.code(clean_err, language="python")
            else:
                st.warning(f"⚠️ Your code completed but did not return a value. Did you forget `return message` inside `{detected_function}`?")

        except subprocess.TimeoutExpired:
            st.error("🐢 CPU Timeout! Your function code took too long to finish executing. Verify your loops do not lock up.")
            
        finally:
            # Clean up the script file instantly to free environment memory
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        st.info("The output screen is resting. Click 'Run My Function' above to see it update.")

