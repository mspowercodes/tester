import ast
import streamlit as st

st.set_page_config(layout="wide")
st.title("🔐 Interactive Coding Cipher Machine")
st.caption("Write your custom function on the left, click run, and test messages on the right!")

# 1. Initialize persistent memory variables
if "code_compiled" not in st.session_state:
    st.session_state.code_compiled = False
if "student_code" not in st.session_state:
    st.session_state.student_code = ""
if "detected_function_name" not in st.session_state:
    st.session_state.detected_function_name = ""

# 2. Build the side-by-side interface layout
col_left, col_right = st.columns(2)

with col_left:
    st.header("1. Write Your Cipher Code")
    st.markdown("Write a custom encryption function that takes a message string and **returns** the scrambled text. **Name your function whatever you want!**")
    
    # Starter template matches your exact custom function name and structure
    default_starter_code = (
        'def caesar_shift3(message):\n'
        '    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")\n'
        '    return message.translate(table)'
    )
    
    raw_code_input = st.text_area(
        "📝 Write Python Code:", 
        value=st.session_state.student_code if st.session_state.student_code else default_starter_code, 
        height=300
    )
    
    if st.button("🚀 Compile & Run Script", type="primary"):
        clean_code = raw_code_input.strip()
        
        try:
            # DYNAMIC STEP: Read the student's code block structure using Abstract Syntax Trees
            parsed_ast = ast.parse(clean_code)
            
            # Automatically find the first function defined in their script, no matter what it is called
            found_function_name = None
            for node in parsed_ast.body:
                if isinstance(node, ast.FunctionDef):
                    found_function_name = node.name
                    break
            
            if not found_function_name:
                st.error("❌ The app couldn't find a function. Make sure your script starts with `def your_function_name(message):`!")
                st.session_state.code_compiled = False
            else:
                # Set up the secure environment (includes 'str' for text translations like maketrans)
                safe_sandbox_scope = {
                    "chr": chr, "ord": ord, "len": len, "range": range, "str": str, "int": int
                }
                
                # Execute code inside the safe scope variables container
                exec(clean_code, {"__builtins__": safe_sandbox_scope}, safe_sandbox_scope)
                
                # Double-check that their custom function name exists in the memory map
                if found_function_name in safe_sandbox_scope and callable(safe_sandbox_scope[found_function_name]):
                    st.success(f"✅ Script loaded perfectly! Found your custom function: `{found_function_name}()`.")
                    st.session_state.student_code = clean_code
                    st.session_state.detected_function_name = found_function_name
                    st.session_state.code_compiled = True
                else:
                    st.error("❌ Something went wrong reading your function name.")
                    st.session_state.code_compiled = False
                
        except SyntaxError as syntax_err:
            st.error(f"❌ Syntax Error on line {syntax_err.lineno}: {syntax_err.msg}")
            st.session_state.code_compiled = False
        except Exception as run_err:
            st.error(f"❌ Runtime Error: {run_err}")
            st.session_state.code_compiled = False

with col_right:
    st.header("2. Your Cipher Machine")
    
    # Show the interactive panel once ANY custom function is compiled successfully
    if st.session_state.code_compiled:
        st.markdown(f"### 📥 Testing your custom function: `{st.session_state.detected_function_name}()`")
        message_to_scramble = st.text_input("🔑 Enter a secret phrase to pass to your code:", value="hello world")
        
        if st.button("🔒 Encrypt Message"):
            try:
                # Re-run execution setup to parse the saved script structure
                safe_sandbox_scope = {
                    "chr": chr, "ord": ord, "len": len, "range": range, "str": str, "int": int
                }
                exec(st.session_state.student_code, {"__builtins__": safe_sandbox_scope}, safe_sandbox_scope)
                
                # Dynamically retrieve and run whatever custom name they chose
                target_function = safe_sandbox_scope[st.session_state.detected_function_name]
                scrambled_result = target_function(message_to_scramble)
                
                st.subheader("🎉 Scrambled Output:")
                st.info(scrambled_result)
                
            except Exception as e:
                st.error(f"⚠️ The code broke running your function: {e}")
    else:
        st.info("👋 Write your script on the left and click 'Compile & Run Script' to activate this terminal machine.")
