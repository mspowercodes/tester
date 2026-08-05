import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🔐 Interactive Coding Cipher Machine")
st.caption("Write your custom function on the left, click run, and test messages on the right!")

# 1. Default starter code template for students
default_starter_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "defghijklmnopqrstuvwxyzabc")
    return message.translate(table)"""

# 2. Split interface layouts
col_left, col_right = st.columns(2)

with col_left:
    st.header("1. Write Your Cipher Code")
    raw_code_input = st.text_area(
        "📝 Write Python Code:",
        value=default_starter_code,
        height=320
    )
    # The initial engine button
    run_clicked = st.button("🚀 Run & Test Code", type="primary")

# Persist execution unlock states seamlessly across the session
if "has_run" not in st.session_state:
    st.session_state.has_run = False

if run_clicked:
    st.session_state.has_run = True

# 3. Handle the right-side sandboxed UI structure safely
with col_right:
    if st.session_state.has_run:
        st.header("2. Test Your Workspace")
        
        # Protect code block payloads from breaking JavaScript string arrays
        safe_code = raw_code_input.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

        # Complete JavaScript Sandbox Injection
        # Uses an updated, highly stable version of Pyodide
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://jsdelivr.net"></script>
            <style>
                body {{ font-family: sans-serif; background-color: transparent; color: #333; margin: 0; padding: 5px; }}
                .input-group {{ margin-bottom: 15px; }}
                label {{ font-size: 0.9em; font-weight: bold; color: #555; display: block; margin-bottom: 5px; }}
                input[type="text"] {{ width: 95%; padding: 10px; border-radius: 6px; border: 1px solid #ccc; font-size: 14px; margin-bottom: 10px; }}
                button {{ background-color: #ff4b4b; color: white; border: none; padding: 10px 15px; font-size: 14px; border-radius: 6px; cursor: pointer; font-weight: bold; }}
                button:hover {{ background-color: #e03e3e; }}
                #output-box {{ margin-top: 15px; padding: 15px; border-radius: 8px; background: #ffffff; border: 1px solid #ddd; min-height: 60px; font-family: monospace; white-space: pre-wrap; }}
                .status {{ font-size: 0.9em; color: #777; margin-bottom: 8px; font-style: italic; }}
            </style>
        </head>
        <body>
            <div class="input-group">
                <label>📩 Enter message to encrypt:</label>
                <input type="text" id="test-msg" value="hello world">
                <button id="encrypt-btn" onclick="executeCipher()">🔒 Encrypt Message</button>
            </div>
            
            <div class="status" id="status">⏳ Instantiating secure browser engine...</div>
            <div id="output-box">Your encrypted message will populate here.</div>

            <script>
                let pyEngine = null;
                const rawStudentCode = `{safe_code}`;

                async function initPyodide() {{
                    try {{
                        pyEngine = await loadPyodide();
                        document.getElementById('status').innerText = "✅ Python Engine Active. Ready to encrypt!";
                    }} catch(err) {{
                        document.getElementById('status').innerText = "💥 Engine initialization failed.";
                        document.getElementById('output-box').innerText = err.message;
                    }}
                }}

                async function executeCipher() {{
                    if(!pyEngine) {{
                        alert("Please wait for the environment to finish loading.");
                        return;
                    }}

                    document.getElementById('status').innerText = "⚡ Executing custom cipher logic...";
                    const userMessage = document.getElementById('test-msg').value;
                    
                    // Direct target translation escaping inside the execution routine
                    const safeMessage = userMessage.replace(/\\\\/g, '\\\\\\\\').replace(/`/g, '\\\\`').replace(/\\$/g, '\\\\$');

                    // Pure Python validation program executed inside Pyodide assembly
                    const orchestrationScript = `
import ast
def run_secure():
    student_code = r\"\"\"${{rawStudentCode}}\"\"\"
    test_msg = \"\"\"${{safeMessage}}\"\"\"
    try:
        parsed_ast = ast.parse(student_code)
        found_function_name = None
        for node in parsed_ast.body:
            if isinstance(node, ast.FunctionDef):
                found_function_name = node.name
                break
        if not found_function_name:
            return '❌ Error: Could not find any function definition (def your_function).'
        
        local_scope = {{}}
        exec(student_code, {{}}, local_scope)
        cipher_func = local_scope[found_function_name]
        result = cipher_func(test_msg)
        return '🔒 Encrypted Output (' + str(found_function_name) + '):\\n' + str(result)
    except Exception as e:
        return '❌ Python Runtime Error:\\n' + str(e)

run_secure()
`;
                    try {{
                        let outText = await pyEngine.runPythonAsync(orchestrationScript);
                        document.getElementById('output-box').innerText = outText;
                        document.getElementById('status').innerText = "🏁 Execution finished successfully.";
                    }} catch (err) {{
                        document.getElementById('output-box').innerText = "❌ Fatal error during run: " + err.message;
                        document.getElementById('status').innerText = "💥 Crashed.";
                    }}
                }}

                // Run bootloader automatically on activation
                initPyodide();
            </script>
        </body>
        </html>
        """
        # Render the integrated container cleanly
        components.html(html_code, height=350)
    else:
        st.info("💡 Write your function on the left and click 'Run & Test Code' to open the testing suite here.")
