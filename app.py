import streamlit as st

st.set_page_config(layout="wide")
st.title("🔐 Build Your Own Secret Cipher!")
st.caption("A completely safe, fast-loading cipher studio for students.")

# Initialize persistent session states
if "code_verified" not in st.session_state:
    st.session_state.code_verified = False
if "shift_amount" not in st.session_state:
    st.session_state.shift_amount = 1

# --- STEP 1: THE CONFIGURATION ENGINE ---
st.header("1. Program Your Cipher Machine")
st.markdown("Set how many positions your machine will shift letters down the alphabet to hide the message!")

# Use native widgets to completely avoid code compilation issues
shift_value = st.number_input(
    "🔢 Enter your Cipher Shift Key (e.g., 1 to shift A to B):", 
    min_value=1, 
    max_value=25, 
    value=st.session_state.shift_amount
)

# Visual code display block to keep the "coding/scripting" feel for kids
st.markdown("**Your Program Logic:**")
simulated_script = f"""
def encrypt(secret_message):
    encrypted = ""
    for letter in secret_message:
        # Shift the character position by {shift_value}
        encrypted += chr(ord(letter) + {shift_value})
    return encrypted
"""
st.code(simulated_script, language="python")

if st.button("Save & Verify Code 🛠️", type="primary"):
    st.session_state.shift_amount = shift_value
    st.session_state.code_verified = True
    st.success("✅ System updated! Your custom cipher logic has been loaded into the machine.")

# --- STEP 2: THE CONDITIONAL ENCRYPTION BOX ---
if st.session_state.code_verified:
    st.write("---")
    st.header("2. Run Your Custom Cipher Machine")
    kids_message = st.text_input("🔑 Enter a secret message to encrypt:", value="Hello World")
    
    if st.button("🔒 Run Encryption"):
        # Pure native Python logic - runs perfectly with zero risk of hanging
        output_text = ""
        for letter in kids_message:
            output_text += chr(ord(letter) + st.session_state.shift_amount)
            
        st.subheader("🎉 Your Encrypted Secret Message:")
        st.info(output_text)
