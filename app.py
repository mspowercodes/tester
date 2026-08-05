import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🔐 Interactive Coding Cipher Machine")
st.caption("Write your custom function on the left, click run, and test messages on the right!")

# 1. Default starter code for the student
default_starter_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "defghijklmnopqrstuvwxyzabc")
    return message.translate(table)"""

# 2. Build the side-by-side layout
col_left, col_right = st.columns(2)

with col_left:
    st.header("1. Write Your Cipher Code")
    raw_code_input = st.text_area(
        "📝 Write Python Code:",
        value=default_starter_code,
        height=250
    )

with col_right:
    st.header("2. Test Your Cipher")
    test_message = st.text_input("📩 Enter message to encrypt:", value="hello world")
    
    # The Run Button to trigger execution on demand
    run_clicked = st.button("🚀 Run Cipher", type="primary")

# Escaping backslashes and quotes to make the code string safe for JavaScript insertion
safe_code = raw_code_input.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
safe_message = test_message.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

# 3. Pure Python block for the browser (Separated to avoid f-string NameErrors on the server)
python_payload = (
    "import ast\n"
    "def run_secure():\n"
    f"    student_code = r\"\"\"{safe_code}\"\"\"\n"
    f"    test_msg = \"\"\"{safe_message}\"\"\"\n"
    "    try:\n"
    "        parsed_ast = ast.parse(student_code)\n"
    "        found_function_name = None\n"
    "        for node in parsed_ast.body:\n"
    "            if isinstance(node, ast.FunctionDef):\n"
    "                found_function_name = node.name\n"
    "                break\n"
    "        if not found_function_name:\n"
    "            return '❌ Error: Could not find any function definition (def your_function).'\n"
    "        local_scope = {}\n"
    "        exec(student_code, {}, local_scope)\n"
    "        cipher_func = local_scope[found_function_name]\n"
    "        result = cipher_func(test_msg)\n"
    "        return '🔒 Encrypted Output (' + str(found_function_name) + '):\\n' + str(result)\n"
    "    except Exception as e:\n"
    "        return '❌ Python Runtime Error:\\n' + str(e)\n"
    "print(run_secure())"
)

# 4. The HTML Container that hosts Pyodide
# We pass an extra variable 'shouldRun' into JS to control execution
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://jsdelivr.net"></script>
    <style>
        body {{ font-family: sans-serif; background-color: #f9f9f9; color: #333; margin: 10px; }}
        #output-box {{ padding: 15px; border-radius: 8px; background: #ffffff; border: 1px solid #ddd; min-height: 60px; font-family: monospace; white-space: pre-wrap; }}
        .status {{ font-size: 0.9em; color: #666; margin-bottom: 8px; }}
    </style>
</head>
<body>
    <div class="status" id="status">💤 Waiting for you to click 'Run Cipher'...</div>
    <div id="output-box">Your encrypted message will appear here...</div>

    <script>
        async function main() {{
            const shouldRun = {str(run_clicked).lower()};
            
            if (!shouldRun) {{
                return;
            }}

            document.getElementById('status').innerText = "⏳ Loading Python environment in browser...";
            let pyodide = await loadPyodide();
            document.getElementById('status').innerText = "✅ Python Engine Ready! Running your code...";
            
            // Capture standard output from the Python execution
            pyodide.setStdout({{ batched: (text) => {{
                document.getElementById('output-box').innerText = text;
            }}}});

            try {{
                // Run the compiled payload block completely locally
                await pyodide.runPythonAsync(`{python_payload}`);
                document.getElementById('status').innerText = "🏁 Execution finished successfully.";
            }} catch (err) {{
                document.getElementById('output-box').innerText = "❌ Fatal execution error: " + err.message;
                document.getElementById('status').innerText = "💥 Crashed.";
            }}
        }}
        main();
    </script>
</body>
</html>
"""

# Render the container
with col_right:
    st.subheader("3. Execution Results")
    components.html(html_code, height=250)
