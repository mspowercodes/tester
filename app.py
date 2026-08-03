import streamlit as st

plaintext = 'abcdefghijklmnopqrstuvwxyz'
ciphertext = 'DEFGHIJKLMNOPQRSTUVWXYZABC'

def caesar_cipher_simple(message):
    encrypted_message = ""
    
    for char in message.lower():
        # FIXED: Changed 'plain' to 'plaintext'
        if char in plaintext:
            position_plain = plaintext.find(char)
            encrypted_message += ciphertext[position_plain]
        else:
            # FIXED: Changed 'text_cipher' to 'encrypted_message'
            encrypted_message += char
            
    # FIXED: Changed 'text_cipher' to 'encrypted_message'
    return encrypted_message

# Streamlit Interface
st.title("Simple Caesar Cipher")

user_message = st.text_input("Enter text to encrypt:", value="hello")

if user_message:
    secret_result = caesar_cipher_simple(user_message)
    st.success(f"Encrypted text: **{secret_result}**")
