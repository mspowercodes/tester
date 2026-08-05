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
    <!-- Load Streamlit Component Library API connection asset -->
    <script src="https://jsdelivr.net"></script>

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

        // Component API handshake activation
        Streamlit.setFrameHeight(360);

        // Safe component value communication using the library API 
        runBtn.addEventListener('click', () => {{
            Streamlit.setComponentValue(codeEditor.value);
        }});

        updateLines();
    </script>
    """
        
    # Render the native web container component using a persistent key to prevent reload loops
    editor_response = st.components.v1.html(custom_editor_html, height=360, scrolling=False, key="editor_sandbox_instance")
    
    # Safely extract component returns and save directly into state without loops
    if editor_response is not None and editor_response != st.session_state.user_code_string:
        st.session_state.user_code_string = editor_response

with col_right:
    st.subheader("🧪 Live Output Testing")
        
    if st.session_state.user_code_string:
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Execute user script directly 
            exec(str(st.session_state.user_code_string), current_env)
            
            sys.stdout = old_stdout
            printed_output = output_buffer.getvalue()
            
            st.success("🎉 Code executed successfully!")
            st.write("**Console Output (stdout):**")
            
            if printed_output.strip():
                st.code(printed_output, language="plaintext")
            else:
                st.caption("Script completed but did not print any output. Use print() to display results here.")
                    
        except Exception as e:
            sys.stdout = old_stdout
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")
    else:
        st.caption("Awaiting successful code submission from the left panel...")
