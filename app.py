import streamlit as st
import sys
import io
import traceback
import inspect

st.set_page_config(
    page_title="Streamlit Python Sandbox",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Native Python Editor Sandbox")
st.markdown("Type any Python code or function on the left, then click the button to execute it and run live tests on the right panel.")

# Default starting code template
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)

# You can also run plain expressions or prints here:
print("Code template compiled successfully!")
"""

# Track application state across clicks
if "user_code" not in st.session_state:
    st.session_state.user_code = default_code
if "has_run" not in st.session_state:
    st.session_state.has_run = False

col_editor, col_output = st.columns(2)

with col_editor:
    st.subheader("📝 Integrated Code Box")
    
    # Calculate how many lines are currently in the code template
    num_lines = len(st.session_state.user_code.split("\n"))
    line_numbers_string = "\n".join(str(i) for i in range(1, num_lines + 1))
    
    # Visual Layout: Align line numbers directly next to the code text area
    gutter, textarea = st.columns([1, 15])
    
    with gutter:
        # Static tracking box displaying line integers cleanly
        st.text_area(
            label="Lines",
            value=line_numbers_string,
            height=300,
            disabled=True,
            label_visibility="collapsed"
        )
        
    with textarea:
        # Main input editor window where the user types
        code_input = st.text_area(
            label="Python Code Editor Input",
            value=st.session_state.user_code,
            height=300,
            label_visibility="collapsed"
        )
    
    # Trigger execution update
    if st.button("🚀 Run & Compile Code", type="primary"):
        st.session_state.user_code = code_input
        st.session_state.has_run = True
        st.rerun()

with col_output:
    st.subheader("🧪 Live Output Testing")
    
    if st.session_state.has_run:
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Safely compile whatever functions or statements the user provided
            exec(st.session_state.user_code, current_env)
            
            # Restore stdout standard stream mapping
            sys.stdout = old_stdout
            printed_logs = output_buffer.getvalue()
            
            st.success("🎉 Code compiled successfully!")
            
            # Display print logs if present
            if printed_logs.strip():
                st.write("**Console Output (stdout):**")
                st.code(printed_logs, language="plaintext")
            
            # Look for executable user-defined functions inside the environment
            found_functions = [
                name for name, obj in current_env.items()
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
            
            if found_functions:
                st.write("---")
                st.markdown("### 📥 Interactive Function Tester")
                
                # Pick the primary custom function found
                target_name = found_functions[0]
                target_func = current_env[target_name]
                
                st.caption(f"Testing active function: `{target_name}()`")
                
                # Dynamic text area generated right here for entering arguments
                test_message = st.text_input("Enter text to pass as a message argument:", value="hello world")
                
                if test_message:
                    try:
                        # Feed the live text input directly into the user's function
                        result = target_func(test_message)
                        st.markdown("**Function Result Output:**")
                        st.info(f"`{result}`")
                    except Exception as func_err:
                        st.error(f"Execution error inside `{target_name}`: {func_err}")
                        
        except Exception as e:
            # Revert stream output safely during a compilation failure
            sys.stdout = old_stdout
            st.error("❌ Python Execution/Syntax Error:")
            st.code(traceback.format_exc(), language="python")
    else:
        st.caption("Awaiting successful code execution from the left panel...")
