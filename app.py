with col_left:
    st.subheader("📝 Integrated Code Box")
         
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

        codeEditor.addEventListener('scroll', () => {{
            lineCounter.scrollTop = codeEditor.scrollTop;
        }});

        codeEditor.addEventListener('input', updateLines);
                 
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

        // FIXED: Streamlit uses Streamlit.setComponentValue via messaging protocol
        runBtn.addEventListener('click', () => {{
            window.parent.postMessage({{
                isStreamlitMessage: true,
                type: "streamlit:setComponentValue",
                value: codeEditor.value
            }}, "*");
        }});

        updateLines();
    </script>
    """
         
    # Capture the return value from the HTML component
    editor_response = st.components.v1.html(custom_editor_html, height=360, scrolling=False)

    # FIXED: Update session state if the component sent back new text
    if editor_response is not None:
        st.session_state.user_code_string = editor_response
        st.rerun()
