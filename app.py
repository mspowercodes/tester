import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🔐 Interactive Coding Cipher Machine (Fixed import)")
st.caption("This version uses dynamic import for Pyodide to avoid srcdoc/module parsing issues.")

# Starter code
default_starter_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "defghijklmnopqrstuvwxyzabc")
    return message.translate(table)"""

# Layout
col_left, col_right = st.columns(2)

with col_left:
    st.header("1. Write Your Cipher Code")
    raw_code_input = st.text_area(
        "📝 Write Python Code:",
        value=default_starter_code,
        height=320
    )
    run_clicked = st.button("🚀 Run & Test Code", type="primary")

# session flag
if "engine_activated" not in st.session_state:
    st.session_state.engine_activated = False
if run_clicked:
    st.session_state.engine_activated = True

js_activation_flag = "true" if st.session_state.engine_activated else "false"

# Server-side debug info (visible on page)
st.write("SERVER DEBUG: engine_activated =", st.session_state.engine_activated)
st.write("SERVER DEBUG: raw_code length =", len(raw_code_input or ""))

# Escape-only the student code for safe insertion into JS template strings
safe_code = (raw_code_input or "").replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

# Simple test HTML (should always appear if components.html works)
simple_test_html = """
<div style="padding:10px;border:1px solid #ddd;border-radius:6px;background:#f8f8f8;">
  <strong>Simple test component</strong>
  <div id="simple-test">If you see this, components.html is rendering basic HTML.</div>
  <script>
    console.log("simple_test_html loaded");
  </script>
</div>
"""

# Complex interactive HTML template (placeholders __JS_FLAG__ and __SAFE_CODE__)
# NOTE: script is now a plain <script> and we do a dynamic import inside the async boot() function.
complex_html_template = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <style>
    body { font-family: sans-serif; background: transparent; color:#333; margin:6px; }
    .info { font-family: monospace; white-space: pre-wrap; margin-bottom:8px; }
    #notice-zone { margin-bottom:10px; }
    #interactive-suite.locked { opacity:0.5; pointer-events:none; }
    #output-box { margin-top:10px; padding:10px; border-radius:6px; border:1px solid #ddd; background:#fff; min-height:60px; white-space:pre-wrap; font-family:monospace; }
  </style>
</head>
<body>
  <div id="notice-zone"></div>

  <div id="interactive-suite" class="locked">
    <div>
      <label>📩 Enter message to encrypt:</label><br/>
      <input id="test-msg" value="hello world" style="width:90%;padding:8px;margin-top:6px;"/>&nbsp;
      <button id="encrypt-btn">🔒 Encrypt Message</button>
    </div>
    <div id="status" style="margin-top:8px;color:#666;font-style:italic;">⏳ Instantiating engine...</div>
    <div id="output-box">Your encrypted message will populate here.</div>
  </div>

  <script>
    // Global error capture so we can display runtime issues inside the notice-zone
    window.addEventListener('error', function (ev) {
      try {
        const n = document.getElementById('notice-zone');
        const d = document.createElement('div');
        d.className = 'info';
        d.innerText = 'FRAME ERROR: ' + (ev && ev.message ? ev.message : String(ev));
        n.appendChild(d);
      } catch(e){}
    });
    window.addEventListener('unhandledrejection', function (ev) {
      try {
        const n = document.getElementById('notice-zone');
        const d = document.createElement('div');
        d.className = 'info';
        d.innerText = 'UNHANDLED PROMISE REJECTION: ' + JSON.stringify(ev.reason);
        n.appendChild(d);
      } catch(e){}
    });

    (async function boot() {
      try {
        // Dynamic import of the pyodide module (avoids static `import { ... } from` in srcdoc)
        const module = await import("https://cdn.jsdelivr.net/pyodide/v0.26.1/full/pyodide.mjs");
        const loadPyodide = module.loadPyodide;

        const isUnlocked = __JS_FLAG__;
        const rawStudentCode = `__SAFE_CODE__`;

        function setStatus(s) { const el = document.getElementById('status'); if(el) el.innerText = s; }

        if (!isUnlocked) {
          const n = document.getElementById('notice-zone');
          const b = document.createElement('div');
          b.className = 'info';
          b.innerText = 'Workspace inactive — click Run & Test Code on the left to unlock.';
          n.appendChild(b);
          setStatus('🔒 Locked');
          return;
        }

        setStatus('Initializing Pyodide...');
        let pyEngine = null;
        try {
          pyEngine = await loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.1/full/" });
          setStatus('✅ Python Engine Active.');
        } catch(err){
          const n = document.getElementById('notice-zone');
          const d = document.createElement('div');
          d.className = 'info';
          d.innerText = 'Pyodide init failed: ' + (err && err.message ? err.message : String(err));
          n.appendChild(d);
          setStatus('❌ Pyodide init failed');
          return;
        }

        async function runStudentCode() {
          setStatus('⚡ Executing student cipher...');
          const userMessage = document.getElementById('test-msg').value;
          try {
            // pass as globals (avoids injection issues)
            pyEngine.globals.set('student_code', rawStudentCode);
            pyEngine.globals.set('test_msg', userMessage);
            const orchestration = `
import ast
def run_secure():
    try:
        parsed_ast = ast.parse(student_code)
        found_function_name = None
        for node in parsed_ast.body:
            if isinstance(node, ast.FunctionDef):
                found_function_name = node.name
                break
        if not found_function_name:
            return '❌ Error: No function definition found.'
        local_scope = {}
        exec(student_code, {}, local_scope)
        fn = local_scope.get(found_function_name)
        if fn is None:
            return '❌ Error: function not available after exec'
        return '🔒 Encrypted Output (' + str`

