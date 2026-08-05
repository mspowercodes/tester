import streamlit as st
import sys
import io
import traceback

st.set_page_config(
    page_title="Dynamic Code Sandbox",
    page_icon="🐍",
    layout="wide"
)

# Inject custom CSS to make the standard text area look like an IDE box
st.markdown("""
<style>
    div[data-baseweb="textarea"] {
        background-color: #1e1e1e !important;
        border: 1px solid #444 !important;
        border-radius: 4px !important;
    }
    textarea {
        color: #ffffff !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🐍 Code Sandbox & Dynamic Message Creator")

# Default starter code template
default_code = """# Write your script here
print("Initialization completed.")
"""

# Maintain persistent states across interactions
if "user_code" not in st.session_state:
    st.session_state.user_code = default_code
if "code_has_run" not in st.session_state:
    st.session_state.code_has_run = False

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Integrated Code Box")
    
    # Custom styled code box
    code_input = st.text_area(
        label="Editor Window",
        value=st.session_state.user_code,
        height=300,
        label_visibility="collapsed"
    )
    
    # Toggle execution state on click
    if st.button("🚀 Run & Compile Code", type="primary"):
        st.session_state.user_code = code_input
        st.session_state.code_has_run = True

with col_right:
    st.subheader("🧪 Live Output Testing")
    
    if st.session_state.code_has_run:
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Execute user script directly
            exec(st.session_state.user_code, current_env)
            
            sys.stdout = old_stdout
            printed_output = output_buffer.getvalue()
            
            st.success("🎉 Code executed successfully!")
            
            if printed_output.strip():
                st.write("**Console Output (stdout):**")
                st.code(printed_output, language="plaintext")
            
            st.write("---")
            st.subheader("📥 Generated Message Input Box")
            
            # FIXED: Form wrapper prevents the app from wiping data when typing messages
            with st.form(key="message_submission_form"):
                user_message = st.text_input("Type your message here:")
                submit_message = st.form_submit_button("Submit Message")
                
                if submit_message and user_message:
                    st.info(f"**Submitted message:** {user_message}")
                    
        except Exception as e:
            sys.stdout = old_stdout
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")
    else:
        st.caption("Awaiting successful code submission from the left panel...")
