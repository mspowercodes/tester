# app.py - copy this whole file into your repo
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🔐 Interactive Coding Cipher Machine (Stable)")
st.caption("Write your custom function on the left, click run, and test messages on the right!")

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

# Use boolean for JSON emission
js_flag_bool = bool(st.session_state.engine_activated)

# Server-side debug info (visible on page)
st.write("SERVER DEBUG: engine_activated =", st.session_state.engine_activated)
st.write("SERVER DEBUG: raw_code length =", len(raw_code_input or ""))

# JSON-escape values to inject into the iframe safely
safe_code_json = json.dumps(raw_code_input or "")
js_flag_json = json.dumps(js_flag_bool)  # yields true/false (without quotes) in JS

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
    // Inserted JSON-safe values:
    const isUnlocked = __JS_FLAG_JSON__;
    const rawStudentCode = __SAFE_CODE_JSON__;

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

    (async function boot
"""
