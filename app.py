import streamlit as st

def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)

# --- STREAMLIT INTERFACE ---
st.title("The Cryptoclub - Chapter 1")
st.write("This app encrypts lowercase text using a shift of 3.")

# Captures what the student types into the box
user_text = st.text_input("Enter lowercase plaintext:", value="hello world")

# Runs the simpler string function
result = caesar_shift3(user_text)

# Displays the final secret message
st.write("**Ciphertext:**")
st.code(result)
