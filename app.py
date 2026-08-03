import streamlit as st

# The simpler student-friendly function using strings ("" and +=)
def caesar_shift3(message):
    plaintext = "abcdefghijklmnopqrstuvwxyz"
    ciphertext = "DEFGHIJKLMNOPQRSTUVWXYZABC"
    
    # 1. Start with a completely empty piece of text
    encrypted_message = ""
    
    for char in message:
        if char in plaintext:
            number = plaintext.index(char)
            # 2. Glue the secret letter directly onto the end
            encrypted_message += ciphertext[number]
        else:
            # 3. Glue spaces or punctuation onto the end
            encrypted_message += char
            
    return encrypted_message

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
