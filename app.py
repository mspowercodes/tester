import streamlit as st
import sys
import io
import traceback

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
    return message.translate(table)

text = "hello world"
shifted = caesar_shift3(text)

print(f"Original text: {text}")
print(f"Shifted output: {shifted}")
"""

# Persistent memory states
if "user_code_string" not in st.session_state:
    st.session_state.user_code_string = default_code

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

        // Safe component value communication with Streamlit
        runBtn.addEventListener('click', () => {{
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: codeEditor.value
            }}, '*');
        }});

        updateLines();
    </script>
    """
        
    # Render the native web container component safely
    editor_response = st.components.v1.html(custom_editor_html, height=360, scrolling=False)
    
    # FIXED: Extract data safely and trigger a rerun if a new value arrives
    if editor_response is not None:
        # Check if the internal value contains a string element from the frame
        if hasattr(editor_response, 'value'):
            new_code = editor_response.value
        else:
            new_code = str(editor_response)
            
        if new_code != st.session_state.user_code_string:
            st.session_state.user_code_string = new_code
            st.rerun()

with col_right:
    st.subheader("🧪 Live Output Testing")
        
    # Process script parameters directly whenever data updates
    if st.session_state.user_code_string:
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Safely cast string type for exec requirement
            exec(str(st.session_state.user_code_string), current_env)
            
            # Restore standard output system safely
            sys.stdout = old_stdout
            
            # Fetch the captured printed items
            printed_output = output_buffer.getvalue()
            
            st.success("🎉 Code executed successfully!")
            
            st.write("**Console Output (stdout):**")
            if printed_output.strip():
                st.code(printed_output, language="plaintext")
            else:
                st.caption("Script completed but did not print any output. Use print() to display results here.")
                    
        except Exception as e:
            # Restore standard output system safely during a failure
            sys.stdout = old_stdout
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")
    else:
        st.caption("Awaiting successful code submission from the left panel...")
