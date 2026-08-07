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
    # Escape backslashes, backticks and '${' so the embedded JS template/backtick strings are safer.
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
            .info-banner { background-color: #e7f3fe*

