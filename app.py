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

# Escaping backslashes and quotes for the HTML injection safely
safe_code = raw_code_input.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
safe_message = test_message.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

# 3. The Pyodide Sandbox (Runs completely in the user's browser)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <!-- Load Pyodide from a secure public CDN -->
    <script src="https://jsdelivr.net"></script>
    <style>
        body {{ font-family: sans-serif; background-color: #f9f9f9; color: #333; margin: 10px; }}
        #output-box {{ padding: 15px; border-radius: 8px; background: #ffffff; border: 1px solid #ddd; min-height: 50px; font-family: monospace; white-space: pre-wrap; }}
        .status {{ font-size: 0.9em; color: #666; margin-bottom: 8px; }}
    </style>
</head>
<body>
    <div class="status" id="status">⏳ Loading Python environment in browser...</div>
    <div id="output-box">Your encrypted message will appear here...</div>

    <script>
        async function main() {{
            // 1. Initialize Pyodide
            let pyodide = await loadPyodide();
            document.getElementById('status').innerText = "✅ Python Engine Ready! Running your code...";
            
            // 2. Define the Python wrapper to safely parse, find, and run the student's function
            let pythonWrapper = `
import ast

def run_secure():
    student_code = \"\"\"{safe_code}\"\"\"
    test_msg = \"\"\"{safe_message}\"\"\"
    
    try:
        # Parse the code to automatically find the function name
        parsed_ast = ast.parse(student_code)
        found_function_name = None
        for node in parsed_ast.body:
            if isinstance(node, ast.FunctionDef):
                found_function_name = node.name
                break
                
        if not found_function_name:
            return "❌ Error: Could not find any function definition (def your_function)."
            
        # Execute the user's code block safely in a local dict
        local_scope = {{}}
        exec(student_code, {{}}, local_scope)
        
        # Grab and run the function
        cipher_func = local_scope[found_function_name]
        result = cipher_func(test_msg)
        return f"🔒 Encrypted Output ({found_function_name}):\\n{{result}}"
        
    except Exception as e:
        return f"❌ Python Runtime Error:\\n{{str(e)}}"

run_secure()
`;
            try {{
                // 3. Execute the wrapper and display results
                let result = await pyodide.runPythonAsync(pythonWrapper);
                document.getElementById('output-box').innerText = result;
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

# Render the safe HTML container inside Streamlit
with col_right:
    st.subheader("3. Execution Results")
    components.html(html_code, height=250)
