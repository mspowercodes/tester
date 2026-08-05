import streamlit as st

st.set_page_config(layout="wide")
st.title("🔐 Interactive Coding Cipher Machine")
st.caption("Write your custom function on the left, click run, and test messages on the right!")

# 1. Initialize persistent memory variables
if "code_compiled" not in st.session_state:
    st.session_state.code_compiled = False
if "student_code" not in st.session_state:
    st.session_state.student_code = ""

# 2. Build the side-by-side interface layout
col_left, col_right = st.columns(2)

with col_left:
    st.header("1. Write Your Cipher Code")
    st.markdown("Your code must define an **`encrypt(text)`** function that takes a word and **returns** the scrambled text.")
    
    default_starter_code = (
        'def encrypt(text):\n'
        '    secret = ""\n'
        '    for character in text:\n'
        '        # Shift the character position by 1\n'
        '        secret += chr(ord(character) + 1)\n'
        '    return secret'
    )
    
    # Text field where kids enter their code
    raw_code_input = st.text_area(
        "📝 Write Python Code:", 
        value=st.session_state.student_code if st.session_state.student_code else default_starter_code, 
        height=300
    )
    
    if st.button("🚀 Compile & Run Script", type="primary"):
        try:
            # Create a sandboxed boundary that blocks access to system files, modules, and servers
            safe_sandbox_scope = {
                "chr": chr, "ord": ord, "len": len, "range": range, "str": str, "int": int
            }
            # Execute the code strictly within our isolated variables container
            exec(raw_code_input, {"__builtins__": safe_sandbox_scope}, safe_sandbox_scope)
            
            # Verify if the student correctly created the target function name
            if "encrypt" not in safe_sandbox_scope or not callable(safe_sandbox_scope["encrypt"]):
                st.error("❌ Your code compiled, but you forgot to declare a function named `encrypt(text)`.")
                st.session_state.code_compiled = False
            else:
                st.success("✅ Script loaded perfectly! Look at the right panel to scramble your message.")
                st.session_state.student_code = raw_code_input
                st.session_state.code_compiled = True
                
        except SyntaxError as syntax_err:
            st.error(f"❌ Syntax Error on line {syntax_err.lineno}: {syntax_err.msg}")
            st.session_state.code_compiled = False
        except Exception as run_err:
            st.error(f"❌ Runtime Error: {run_err}")
            st.session_state.code_compiled = False

with col_right:
    st.header("2. Your Cipher Machine")
    
    # Conditional logic block: Shows the input box only after code is verified
    if st.session_state.code_compiled:
        st.markdown("### 📥 Test Your Script Input")
        message_to_scramble = st.text_input("🔑 Enter a secret phrase to pass to your code:", value="Hello World")
        
        if st.button("🔒 Encrypt Message"):
            try:
                # Re-run execution setup to parse current saved script structure
                safe_sandbox_scope = {
                    "chr": chr, "ord": ord, "len": len, "range": range, "str": str, "int": int
                }
                exec(st.session_state.student_code, {"__builtins__": safe_sandbox_scope}, safe_sandbox_scope)
                
                # Grab the student's function dynamically and pass the message box string to it
                scrambled_result = safe_sandbox_scope["encrypt"](message_to_scramble)
                
                st.subheader("🎉 Scrambled Output:")
                st.info(scrambled_result)
                
            except Exception as e:
                st.error(f"⚠️ The code broke running your function: {e}")
    else:
        # Placeholder warning block displayed before the script is loaded
        st.info("👋 Write your script on the left and click 'Compile & Run Script' to activate this terminal machine.")
