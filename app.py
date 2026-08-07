import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🔐 Interactive Coding Cipher Machine")
st.caption("Write your custom function on the left, click run, and test messages on the right!")

# 1. Default starter code template for students
default_starter_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "defghijklmnopqrstuvwxyzabc")
    return message.translate(table)"""

# 2. Permanent Split Column Interface Layout
col_left, col_right = st.columns(2)

with col_left:
    st.header("1. Write Your Cipher Code")
    raw_code_input = st.text_area(
        "📝 Write Python Code:",
        value=default_starter_code,
        height=320
    )
    # The action button
    run_clicked = st.button("🚀 Run & Test Code", type="primary")

# Safely track button updates across instances
if "engine_activated" not in st.session_state:
    st.session_state.engine_activated = False

if run_clicked:
    st.session_state.engine_activated = True

# Convert boolean to a clean, universal string flag for JavaScript
js_activation_flag = "true" if st.session_state.engine_activated else "false"

# 3. Always render the right side so it never disappears or crashes
with col_right:
    st.header("2. Test Your Workspace")
    
    # Protect raw student text configurations from breaking Javascript strings
    # Note: we escape backslashes, backticks and '${' so the embedded JS template/backtick strings are safer.
    safe_code = raw_code_input.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    # Use a plain triple-quoted string (not an f-string) with placeholders that we replace below.
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: sans-serif; background-color: transparent; color: #333; margin: 0; padding: 5px; }
            .input-group { margin-bottom: 15px; }
            label { font-size: 0.9em; font-weight: bold; color: #555; display: block; margin-bottom: 5px; }
            input[type="text"] { width: 95%; padding: 10px; border-radius: 6px; border: 1px solid #ccc; font-size: 14px; margin-bottom: 10px; }
            button { background-color: #ff4b4b; color: white; border: none; padding: 10px 15px; font-size: 14px; border-radius: 6px; cursor: pointer; font-weight: bold; }
            button:hover { background-color: #e03e3e; }
            #output-box { margin-top: 15px; padding: 15px; border-radius: 8px; background: #ffffff; border: 1px solid #ddd; min-height: 60px; font-family: monospace; white-space: pre-wrap; }
            .status { font-size: 0.9em; color: #777; margin-bottom: 8px; font-style: italic; }
            
            /* Dim treatment to visually lock UI elements before execution initiation */
            .locked { opacity: 0.4; pointer-events: none; }
            .info-banner { background-color: #e7f3fe; border-left: 6px solid #2196F3; padding: 10px; margin-bottom: 15px; border-radius: 4px; font-size: 0.95em; line-height: 1.4; }
        </style>
    </head>
    <body>
        <div id="notice-zone"></div>

        <div id="interactive-suite" class="locked">
            <div class="input-group">
                <label>📩 Enter message to encrypt:</label>
                <input type="text" id="test-msg" value="hello world">
                <button id="encrypt-btn">🔒 Encrypt Message</button>
            </div>
            
            <div class="status" id="status">⏳ Instantiating secure browser engine...</div>
            <div id="output-box">Your encrypted message will populate here.</div>
        </div>

        <script type="module">
            // Import Pyodide from the official CDN module entrypoint
            import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.26.1/full/pyodide.mjs";

            let pyEngine = null;
            const isUnlocked = __JS_FLAG__;
            const rawStudentCode = `__SAFE_CODE__`;

            function checkLockState() {
                const noticeZone = document.getElementById('notice-zone');
                const mainSuite = document.getElementById('interactive-suite');
                
                if (!isUnlocked) {
                    noticeZone.innerHTML = '<div class="info-banner">💡 <b>Workspace Inactive:</b> Write or review your function on the left, then click <b>"Run & Test Code"</b> to open the compiler and runtime. This page will automatically enable when you press run.</div>';
                } else {
                    noticeZone.innerHTML = '';
                    mainSuite.classList.remove('locked');
                    initPyodide();
                }

                // Kick off a lightweight diagnostic to surface Streamlit API routing issues
                debugStreamlitApi();
            }

            async function initPyodide() {
                try {
                    pyEngine = await loadPyodide({
                        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.1/full/"
                    });
                    document.getElementById('status').innerText = "✅ Python Engine Active. Ready to encrypt!";
                } catch(err) {
                    document.getElementById('status').innerText = "💥 Engine initialization failed.";
                    document.getElementById('output-box').innerText = err.message;
                }
            }

            async function executeCipher() {
                if(!pyEngine) {
                    alert("Please wait for the environment to finish loading.");
                    return;
                }

                document.getElementById('status').innerText = "⚡ Executing custom cipher logic...";
                const userMessage = document.getElementById('test-msg').value;
                
                // Escape backslashes and special string arrays inside evaluation wrappers
                const safeMessage = userMessage.replace(/\\\\/g, '\\\\\\\\').replace(/`/g, '\\\\`').replace(/\\$/g, '\\\\$');

                const orchestrationScript = `
import ast
def run_secure():
    student_code = r\"\"\"${rawStudentCode}\"\"\"
    test_msg = \"\"\"${safeMessage}\"\"\"
    try:
        parsed_ast = ast.parse(student_code)
        found_function_name = None
        for node in parsed_ast.body:
            if isinstance(node, ast.FunctionDef):
                found_function_name = node.name
                break
        if not found_function_name:
            return '❌ Error: Could not find any function definition (def your_function).'
        
        local_scope = {}
        exec(student_code, {}, local_scope)
        cipher_func = local_scope[found_function_name]
        result = cipher_func(test_msg)
        return '🔒 Encrypted Output (' + str(found_function_name) + '):\\n' + str(result)
    except Exception as e:
        return '❌ Python Runtime Error:\\n' + str(e)

run_secure()
`;
                try {
                    let outText = await pyEngine.runPythonAsync(orchestrationScript);
                    document.getElementById('output-box').innerText = outText;
                    document.getElementById('status').innerText = "🏁 Execution finished successfully.";
                } catch (err) {
                    document.getElementById('output-box').innerText = "❌ Fatal error during run: " + err.message;
                    document.getElementById('status').innerText = "💥 Crashed.";
                }
            }

            // Debug helper: try to fetch Streamlit's user/details endpoint and print the response
            async function debugStreamlitApi() {
                const noticeZone = document.getElementById('notice-zone');
                const origin = window.location.origin;
                const testPaths = [
                    '/api/v2/user/details',
                    '/api/v2/app/status',
                    '/api/v1/info'
                ];

                for (const p of testPaths) {
                    const url = origin + p;
                    try {
                        const res = await fetch(url, { credentials: 'include' });
                        const text = await res.text().catch(() => '<<no-body>>');
                        const msg = document.createElement('div');
                        msg.style.marginBottom = '8px';
                        msg.style.fontFamily = 'monospace';
                        msg.innerText = `DEBUG: GET ${url} -> ${res.status} ${res.statusText}\n${text}`;
                        noticeZone.appendChild(msg);
                    } catch (e) {
                        const msg = document.createElement('div');
                        msg.style.marginBottom = '8px';
                        msg.style.fontFamily = 'monospace';
                        msg.innerText = `DEBUG: GET ${url} -> NETWORK ERROR: ${e.message}`;
                        noticeZone.appendChild(msg);
                    }
                }
            }

            // Attach event listener natively to module-bound elements
            document.getElementById('encrypt-btn').addEventListener('click', executeCipher);

            // Start check boot process immediately
            checkLockState();
        </script>
    </body>
    </html>
    """

    # Inject the two dynamic values into the template safely
    html_code = html_template.replace("__JS_FLAG__", js_activation_flag).replace("__SAFE_CODE__", safe_code)

    # Render the permanent interface component frame
    components.html(html_code, height=380)
