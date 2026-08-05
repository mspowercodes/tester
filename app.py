import streamlit as st
import sys
import io
import traceback
import inspect
import pandas as pd

st.set_page_config(
    page_title="Line-Numbered Sandbox",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Python Sandbox with True Line Numbers")
st.markdown("Double-click any row to edit or add code lines. Use the **[ + ]** button at the bottom of the grid to add new lines!")

# 1. Provide a starter script broken down by line rows
if "code_rows" not in st.session_state:
    st.session_state.code_rows = [
        "def caesar_shift3(message):",
        "    table = str.maketrans('abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZABC')",
        "    return message.translate(table)"
    ]

if "exec_env" not in st.session_state:
    st.session_state.exec_env = {}
if "detected_functions" not in st.session_state:
    st.session_state.detected_functions = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Python Script")
    
    # Format current rows into a clean Pandas DataFrame for the grid editor
    df = pd.DataFrame({"Python Code": st.session_state.code_rows})
    df.index = df.index + 1  # Force line numbers to start at 1 instead of 0
    
    # Render the interactive data editor grid
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",  # Allows users to add or delete rows live
        column_config={
            "Python Code": st.column_config.TextColumn(
                "Python Code (Edit lines below)",
                width="large",
                required=True
            )
        }
    )
    
    # Reassemble the individual table grid rows back into a single Python script block
    user_code = "\n".join(edited_df["Python Code"].tolist())
    
    # Save current lines to session state so they don't erase on page updates
    st.session_state.code_rows = edited_df["Python Code"].tolist()

with col2:
    st.subheader("Live Output Testing")
    
    # Automatically execute and monitor whenever lines in the data editor update
    if user_code.strip():
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            exec(user_code, current_env)
            
            found_funcs = [
                name for name, obj in current_env.items() 
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
            
            sys.stdout = sys.__stdout__
            st.session_state.exec_env = current_env
            st.session_state.detected_functions = found_funcs
            
        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error("❌ Python Syntax Error on Input:")
            st.code(traceback.format_exc(), language="python")

    # --- LIVE INTERACTION ZONE ---
    if st.session_state.detected_functions:
        target_func_name = st.session_state.detected_functions[0]
        target_func = st.session_state.exec_env[target_func_name]
        
        st.success(f"🎉 Active function ready: `{target_func_name}()`")
        st.write("---")
        st.write("### 🧪 Test Your Code Live")
        
        test_input = st.text_input("Enter text to pass into your function:", value="hello world")
        
        try:
            live_result = target_func(test_input)
            st.write("**Function Output:**")
            st.info(f"`{live_result}`")
        except Exception as e:
            st.error(f"Error running `{target_func_name}`: {e}")
    else:
        st.caption("Awaiting a valid function blueprint execution layout...")
