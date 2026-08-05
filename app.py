import streamlit as st
import sys
import io
import traceback
import inspect

st.set_page_config(
    page_title="Single Box Editor Sandbox",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Single Box Python Editor Sandbox")
st.markdown("Type code inside the single window below. Line numbers are fully integrated, and code runs instantly without copy-pasting!")

# Default starter code template
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)"""

# Persistent memory states
if "user_code_string" not in st.session_state:
    st.session_state.user_code_string = default_code
if "exec_env" not in st.session_state:
    st.session_state.exec_env = {}
if "detected_functions" not in st.session_state:
    st.session_state.detected_functions = []

# --- EXTRACT CODE DATA SUBMITTED FROM THE BROWSER ---
# Check url parameters safely without triggering parent window crash reloads
query_params = st.query_params
if "submitted_code" in query_params:
    st.session_state.user_code_string = query_params["submitted_code"]

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Integrated Code Box")
        
    # THE SINGLE-BOX EDITOR ENGINE: Unified code area with auto-compile broadcasting
    custom_editor_html = f"""
    <div style="font-family: monospace; position: relative; border: 1px solid #444; border-radius: 4px; background: #1e1e1e; padding: 0; display: flex; height: 300px;">
        <!-- Left Side Gutter Line Numbers -->
        <textarea id="lineCounter" readonly style="
            width: 35px; height: 100%; border: none; background: #1e1e1e; color: #888; 
            text-align: right; padding: 10px 5px; resize: none; overflow-y: hidden; 
            font-family: inherit; font-size: 14px; line-height: 20px; font-weight: bold;
            border-right: 1px solid #444; user-select: none; pointer-events: none; box-sizing: border-box;
        ">1</textarea>
                
        <!-- Right Side Typing Editor Area -->
        <textarea id="codeEditor" placeholder="Write your Python script here..." wrap="off" style="
            flex: 1; height: 100%; border: none; background: #1e1e1e; color: #fff; 
            padding: 10px; resize: none; font-family: inherit; font-size: 14px; line-height: 20px;
            outline: none; tab-size: 4; box-sizing: border-box; overflow-x: auto;
        ">{st.session_state.user_code_string}</textarea>
    </div>
        
    <!-- Unified Run Button inside the theme wrapper -->
    <button id="runBtn" style="
        margin-top: 15px; background-color: #ff4b4b; color: white; border: none; 
        padding: 8px 16px; font-size: 14px; border-radius: 4px; cursor: pointer; font-family: sans-serif;
    ">🚀 Run & Compile Code</button>

    <script>
        const codeEditor = document.getElementById('codeEditor');
        const lineCounter = document.getElementById('lineCounter');
        const runBtn = document.getElementById('runBtn');

        function updateLines() {{
            const lines = codeEditor.value.split('\\n');
            const lineCount = lines.length;
            let lineNumbers = '';
            for (let i = 1; i <= lineCount; i++) {{
                lineNumbers += i + '\\n';
            }}
            lineCounter.value = lineNumbers;
            lineCounter.scrollTop = codeEditor.scrollTop;
        }}

        // Keep scrolling sync active
        codeEditor.addEventListener('scroll', () => {{
            lineCounter.scrollTop = codeEditor.scrollTop;
        }});

        codeEditor.addEventListener('input', updateLines);
                
        // Handle Tab key indenting natively
        codeEditor.addEventListener('keydown', (e) => {{
            if (e.key === 'Tab') {{
                e.preventDefault();
                const start = codeEditor.selectionStart;
                const end = codeEditor.selectionEnd;
                codeEditor.value = codeEditor.value.substring(0, start) + "    " + codeEditor.value.substring(end);
                codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
                updateLines();
            }}
        }});

        // FIXED: Using postMessage safely to notify the parent application without window.href breakage
        runBtn.addEventListener('click', () => {{
            const codeContent = codeEditor.value;
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: codeContent
            }}, '*');
            
            // Set the URL search parameters through standard parent channel
            const url = new URL(window.parent.location.href);
            url.searchParams.set('submitted_code', codeContent);
            window.parent.location.assign(url.href);
        }});

        updateLines();
    </script>
    """
        
    # Render the native web container component safely
    editor_response = st.components.v1.html(custom_editor_html, height=360, scrolling=False)

with col_right:
    st.subheader("🧪 Live Output Testing")
        
    # Process script parameters directly whenever data updates
    if st.session_state.user_code_string:
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        current_env = {}
                
        try:
            exec(st.session_state.user_code_string, current_env)
                        
            found_funcs = [
                name for name, obj in current_env.items() 
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
                        
            sys.stdout = sys.__stdout__
            st.session_state.exec_env = current_env
            st.session_state.detected_functions = found_funcs
                    
        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")

    # --- LIVE TESTING INTERACTION ZONE ---
    if st.session_state.detected_functions:
        # FIXED: Correctly grab the first function item string out of the environment array list 
        target_func_name = st.session_state.detected_functions[0]
        target_func = st.session_state.exec_env[target_func_name]
                
        st.success(f"🎉 Active function ready: `{target_func_name}()`")
        st.write("---")
                
        # Editable message input block appears on the right panel
        test_input = st.text_input("Enter text to pass into your function:", value="hello world")
                
        try:
            # Process text input live through the custom encryption logic
            live_result = target_func(test_input)
            st.write("**Function Output:**")
            st.info(f"`{live_result}`")
        except Exception as e:
            st.error(f"Error running `{target_func_name}`: {e}")
    else:
        st.caption("Awaiting successful function build from the left panel...")
