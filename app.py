# app.py - server-side fetch of Streamlit internal endpoint, safe injection into iframe
import os
import json
import html as html_escape
import requests
import streamlit as st
import streamlit.components.v1 as components


app_url = None
try:
    app_url = st.secrets.get("app_url")
except Exception:
    app_url = None
app_url = app_url or os.environ.get("STREAMLIT_APP_URL")

st.write("DEBUG: app_url:", app_url)

if not app_url:
    st.warning("STREAMLIT_APP_URL not set. Set st.secrets['app_url'] or STREAMLIT_APP_URL env var.")


st.set_page_config(layout="wide")
st.title("🔐 Interactive Coding Cipher Machine (Server-side debug)")
st.caption("Server-side fetch of app internals is embedded into the iframe (safe).")

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

# Server-side: fetch internal endpoint if configured
# Priority: st.secrets['app_url'] -> env STREAMLIT_APP_URL
app_url = None
try:
    app_url = st.secrets.get("app_url")  # streamlit cloud secrets (preferred)
except Exception:
    app_url = None
if not app_url:
    app_url = os.environ.get("STREAMLIT_APP_URL")

# user_debug_result = None
# if app_url:
#     # Build absolute URL safely
#     endpoint = "/api/v2/user/details"
#     if app_url.endswith("/"):
#         target = app_url.rstrip("/") + endpoint
#     else:
#         target = app_url + endpoint
#     try:
#         r = requests.get(target, timeout=5)
#         body = r.text or ""
#         # truncate to 4000 chars to avoid huge payloads
#         summary = body[:4000]
#         if r.ok:
#             user_debug_result = f"HTTP {r.status_code} OK. Body (truncated 4k chars):\\n{summary}"
#         else:
#             user_debug_result = f"HTTP {r.status_code} {r.reason}. Body (truncated 4k chars):\\n{summary}"
#     except Exception as e:
#         user_debug_result = f"REQUEST ERROR: {str(e)}"
# else:
#     user_debug_result = "APP URL not configured. Set st.secrets['app_url'] or environment variable STREAMLIT_APP_URL to your app URL (e.g. https://tester-new.streamlit.app) to enable server-side diagnostics."

# # Server-side debug info (visible on page)
# st.write("SERVER DEBUG: engine_activated =", st.session_state.engine_activated)
# st.write("SERVER DEBUG: raw_code length =", len(raw_code_input or ""))
# st.write("SERVER DEBUG: server-side user debug length:", len(user_debug_result or ""))

# Prepare JSON-safe injection values
safe_code_json = json.dumps(raw_code_input or "")
js_flag_json = json.dumps(bool(st.session_state.engine_activated))
# Inject server-side debug as JSON string so client can display it via textContent (no HTML injection)
server_user_debug_json = json.dumps(user_debug_result)

# Simple test HTML (should always appear if components.html works)
simple_test_html = """
<div style="padding:10px;border:1px solid #ddd;border-radius:6px;background:#f8f8f8;">
  <strong>Simple test component</strong>
  <div id="simple-test">If you see this, components.html is rendering basic HTML.</div>
  <script>console.log("simple_test_html loaded");</script>
</div>
"""

# Complex interactive HTML template with placeholders that we'll replace with JSON values
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
    label { font-weight: bold; }
    pre.server-debug { background:#f4f4f4; padding:8px; border-radius:6px; border:1px solid #e0e0e0; max-height:240px; overflow:auto; }
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
    // Inserted JSON-safe values (replaced server-side)
    const isUnlocked = __JS_FLAG_JSON__;
    const rawStudentCode = __SAFE_CODE_JSON__;
    const serverUserDebug = __SERVER_USER_DEBUG_JSON__;

    // Show the server-side debug result (safe, uses textContent)
    (function showServerDebug() {
      const notice = document.getElementById('notice-zone');
      const wrapper = document.createElement('div');
      wrapper.className = 'info';
      const title = document.createElement('div');
      title.innerText = 'SERVER-SIDE DEBUG (fetched by Streamlit server):';
      const pre = document.createElement('pre');
      pre.className = 'server-debug';
      pre.textContent = serverUserDebug;
      wrapper.appendChild(title);
      wrapper.appendChild(pre);
      notice.appendChild(wrapper);
    })();

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
        try { d.innerText = 'UNHANDLED PROMISE REJECTION: ' + JSON.stringify(ev.reason); } catch(_) { d.innerText = 'UNHANDLED PROMISE REJECTION'; }
        n.appendChild(d);
      } catch(e){}
    });

    (async function boot() {
      try {
        // Dynamic import of the pyodide module to avoid static module parsing issues in srcdoc
        const module = await import("https://cdn.jsdelivr.net/pyodide/v0.26.1/full/pyodide.mjs");
        const loadPyodide = module.loadPyodide;

        function setStatus(s) { const el = document.getElementById('status'); if(el) el.innerText = s; }

        if (!isUnlocked) {
          setStatus('🔒 Locked');
          // still show the server-side debug above, but don't init pyodide
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
        return '🔒 Encrypted Output (' + str(found_function_name) + '):\\n' + str(fn(test_msg))
    except Exception as e:
        return '❌ Python Runtime Error:\\n' + str(e)

run_secure()
`;
            const out = await pyEngine.runPythonAsync(orchestration);
            document.getElementById('output-box').innerText = out;
            setStatus('🏁 Done');
          } catch (e) {
            const n = document.getElementById('notice-zone');
            const d = document.createElement('div');
            d.className = 'info';
            d.innerText = 'Run error: ' + (e && e.message ? e.message : String(e));
            n.appendChild(d);
            setStatus('💥 Execution error');
          } finally {
            try { pyEngine.globals.delete('student_code'); } catch(_){}
            try { pyEngine.globals.delete('test_msg'); } catch(_){}
          }
        }

        document.getElementById('encrypt-btn').addEventListener('click', runStudentCode);

        const n = document.getElementById('notice-zone');
        const ok = document.createElement('div');
        ok.className = 'info';
        ok.innerText = 'FRAME INFO: boot completed; event listeners attached.';
        n.appendChild(ok);

      } catch (err) {
        try {
          const n = document.getElementById('notice-zone');
          const d = document.createElement('div');
          d.className = 'info';
          d.innerText = 'BOOT ERROR: ' + (err && err.message ? err.message : String(err));
          n.appendChild(d);
        } catch(e){}
        console.error('BOOT ERROR', err);
      }
    })();
  </script>
</body>
</html>
"""

# Render simple test first (should always render if components.html works)
st.write("SERVER DEBUG: rendering simple test HTML below")
components.html(simple_test_html, height=110)

# Render the complex interactive iframe with placeholders replaced safely with JSON literals
html_code = complex_html_template.replace("__JS_FLAG_JSON__", js_flag_json).replace("__SAFE_CODE_JSON__", safe_code_json).replace("__SERVER_USER_DEBUG_JSON__", server_user_debug_json)
st.write("SERVER DEBUG: rendering complex interactive HTML below")
components.html(html_code, height=640, scrolling=True)
