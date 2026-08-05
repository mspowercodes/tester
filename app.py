import ast
import streamlit as st

st.set_page_config(layout="wide")
st.title("🔐 Build Your Own Secret Cipher!")
st.caption("An instantly loading, cloud-safe sandbox for testing student encryption functions.")

# Initialize persistent session states
if "code_verified" not in st.session_state:
    st.session_state.code_verified = False
if "saved_code" not in st.session_state:
    st.session_state.saved_code = ""

# --- STEP 1: THE CODE EDITOR ---
st.header("1. Write Your Python Cipher")
st.markdown(
    "Define a function named `encrypt` that takes a text `message` string "
    "and **returns** the scrambled result. Use the example below as a guide:"
)

default_code = (
    'def encrypt(message):\n'
    '    output = ""\n'
    '    for letter in message:\n'
    '        # Shift the character up by 1 position\n'
    '        output += chr(ord(letter) + 1)\n'
    '    return output'
)

current_code = st.text_area(
    "💻 Python Editor:", 
    value=st.session_state.saved_code if st.session_state.saved_code else default_code, 
    height=200
)

def run_safe_cipher(code_string, test_message):
    """Parses and executes the student function safely using isolated AST trees."""
    try:
        # Step A: Parse the string code into a safe Abstract Syntax Tree
        parsed_tree = ast.parse(code_string, filename="student_cipher.py")
        
        # Step B: Scan tree to ensure they aren't importing dangerous system modules
        for node in ast.walk(parsed_tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return None, "Importing external modules is disabled for safety!"

        # Step C: Compile the verified tree structural logic
        compiled_code = compile(parsed_tree, filename="student_cipher.py", mode="exec")
        
        # Step D: Execute strictly within an isolated variables sandbox 
        # (Completely blocks access to 'os', file writing, or parent script memory)
        isolated_scope = {
            "chr": chr, "ord": ord, "len": len, "range": range, "str": str, "int": int
        }
        exec(compiled_code, {"__builtins__": isolated_scope}, isolated_scope)
        
        # Step E: Make sure they actually created the 'encrypt' function
        if "encrypt" not in isolated_scope or not callable(isolated_scope["encrypt"]):
            return None, "You must define a function named 'encrypt(message)'."
            
        # Run their function cleanly and capture the standard return value
        encrypted_result = isolated_scope["encrypt"](test_message)
        return str(encrypted_result), None

    except SyntaxError as syntax_err:
        return None, f"Syntax Error on line {syntax_err.lineno}: {syntax_err.msg}"
    except Exception as run_err:
        return None, f"Runtime Error: {run_err}"

if st.button("Check My Code Syntax 🛠️"):
    # Run an instant structural verification test
    output, error = run_safe_cipher(current_code, "test")
    
    if error:
        st.error("❌ Uh oh! There is an issue with your function script:")
        st.error(error)
        st.session_state.code_verified = False
    else:
        st.success("✅ Awesome! Your function compiled successfully. Look below to type your message!")
        st.session_state.code_verified = True
        st.session_state.saved_code = current_code

# --- STEP 2: THE CONDITIONAL ENCRYPTION BOX ---
if st.session_state.code_verified:
    st.write("---")
    st.header("2. Run Your Custom Cipher Machine")
    kids_message = st.text_input("🔑 Enter a secret message to encrypt:", value="Hello World")
    
    if st.button("🔒 Run Encryption"):
        output, error = run_safe_cipher(st.session_state.saved_code, kids_message)
        
        if output is not None:
            st.subheader("🎉 Your Encrypted Secret Message:")
            st.info(output)
            
        if error:
            st.error("⚠️ The encryption broken trying to scramble this message:")
            st.error(error)
