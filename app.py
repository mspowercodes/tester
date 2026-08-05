import streamlit as st
import sys
import io
import traceback
import inspect
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(
    page_title="Line Number Sandbox",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Interactive Python Function Sandbox")
st.markdown("Define your encryption function below. Line numbers are generated securely via an image column on the left.")

# Default template code
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)
"""

# Establish global track state to remember what the user types
if "code_text" not in st.session_state:
    st.session_state.code_text = default_code
if "exec_env" not in st.session_state:
    st.session_state.exec_env = {}
if "detected_functions" not in st.session_state:
    st.session_state.detected_functions = []

# Function to generate a clean image of numbers 1 through 15 dynamically
@st.cache_data
def generate_line_numbers_image():
    # Create a small, narrow canvas (width 40px, height 385px to match text_area)
    img = Image.new("RGBA", (40, 385), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw numbers 1 to 15 separated by a clean 25.5px vertical jump
    y_start = 5
    line_height = 25.4
    
    for i in range(1, 16):
        # Draw a clear gray number text string
        draw.text((15, int(y_start + (i - 1) * line_height)), f"{i}", fill=(136, 136, 136, 255))
        
    # Draw a distinct vertical separator border line along the right edge
    draw.line([(38, 0), (38, 385)], fill=(68, 68, 68, 255), width=2)
    return img

# Main split for the interface (Left panel vs Right panel)
col_left_panel, col_right_panel = st.columns(2)

with col_left_panel:
    st.subheader("Input Python Script")
    
    # Split the left panel into a tiny image margin (1) and a wide typing area (15)
    col_numbers, col_textarea = st.columns([1, 15])
    
    with col_numbers:
        # Generate and display our custom-drawn vertical number image
        line_num_img = generate_line_numbers_image()
        st.image(line_num_img, use_container_width=False)
        
    with col_textarea:
        with st.form(key="code_form"):
            user_code = st.text_area(
                label="Your Python Script:",
                value=st.session_state.code_text,
                height=385,  # Matches the exact height of our generated image canvas
                label_visibility="collapsed"  # Hides label to line up row 1 with number 1
            )
            submit_button = st.form_submit_button(label="🚀 Activate My Function")

with col_right_panel:
    st.subheader("Live Output Testing")
    
    if submit_button:
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
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")

    # --- LIVE INTERACTION ZONE ---
    if st.session_state.detected_functions:
        target_func_name = st.session_state.detected_functions
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
        st.caption("Awaiting successful function build from the left panel...")
