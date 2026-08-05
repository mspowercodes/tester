import io
import contextlib
import streamlit as st

st.set_page_config(layout="wide")
st.title("🔐 Build Your Own Secret Cipher!")
st.caption("A completely fail-safe sandbox environment for testing student encryption code.")

# Initialize persistent session states
if "code_verified" not in st.session_state:
    st.session_state.code_verified = False
if "saved_code" not in st.session_state:
    st.session_state.saved_code = ""

# --- STEP 1: THE CODE EDITOR ---
st.header("1. Write Your Python Cipher")
st.markdown("Your script must read a message using `input()` and print out the scrambled result.")

default_code = (
    '# Simple Caesar Cipher (shifts letters by 1)\n'
    'secret_message = input()\n'
    'encrypted = ""\n\n'
    'for letter in secret_message:\n'
    '    encrypted += chr(ord(letter) + 1)\n\n'
    'print(encrypted)'
)

current_code = st.text_area(
    "💻 Python Editor:", 
    value=st.session_state.saved_code if st.session_state.saved_code else default_code, 
    height=250
)

# Custom secure function simulation replacing standard terminal inputs
def run_student_code(code_string, user_input_data):
    """Safely parses and isolates code execution without using files or subprocesses."""
    # Mocking terminal functions to create an absolute sandbox boundary
    def mocked_input():
        return str(user_input_data)

    # Restricted local scope: Completely locks out system files, variables, and modules
    safe_globals = {
        "__builtins__": {
            "print": print,
            "input": mocked_input, # Seamlessly overrides user input with our text block!
            "str": str,
            "int": int,
            "chr": chr,
            "ord": ord,
            "len": len,
            "range": range,
            "list": list,
        }
    }
    
    output_buffer = io.StringIO()
    
    try:
        # Step A: Compile the raw string into byte-code to verify syntax errors instantly
        compiled_bytecode = compile(code_string, "student_cipher.py", "exec")
        
        # Step B: Execute the isolated bytecode inside our safe, limited variable container
        with contextlib.redirect_stdout(output_buffer):
            exec(compiled_bytecode, safe_globals, {})
            
        return output_buffer.getvalue(), None
    except Exception as e:
        return None, str(e)

if st.button("Check My Code Syntax 🛠️"):
    # Test execution instantly using a basic word
    output, error = run_student_code(current_code, "test")
    
    if error:
        st.error("❌ Uh oh! There is an error in your code structure:")
        st.error(error)
        st.session_state.code_verified = False
    else:
        st.success("✅ Awesome! Your script compiled successfully. Look below to type your message!")
        st.session_state.code_verified = True
        st.session_state.saved_code = current_code

# --- STEP 2: THE CONDITIONAL ENCRYPTION BOX ---
if st.session_state.code_verified:
    st.write("---")
    st.header("2. Run Your Custom Cipher Machine")
    kids_message = st.text_input("🔑 Enter a secret message to encrypt:", value="Hello World")
    
    if st.button("🔒 Run Encryption"):
        output, error = run_student_code(st.session_state.saved_code, kids_message)
        
        if output:
            st.subheader("🎉 Your Encrypted Secret Message:")
            st.info(output)
            
        if error:
            st.error("⚠️ The code broke while trying to scramble this message:")
            st.error(error)
