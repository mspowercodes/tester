import streamlit as st

# 1. These are your defined variables
alphabet_plain = 'abcdefghijklmnopqrstuvwxyz'
alphabet_cipher = 'DEFGHIJKLMNOPQRSTUVWXYZABC'

def caesar_cipher_simple(message):
    text_cipher = ""
    
    for char in message.lower():
        # FIXED: Changed 'alphabet' to 'alphabet_plain'
        if char in alphabet_plain:
            # FIXED: Changed 'alphabet' to 'alphabet_plain'
            position_plain = alphabet_plain.find(char)
            # FIXED: Changed 'alphabet_encrypt[position]' to 'alphabet_cipher[position_plain]'
            text_cipher += alphabet_cipher[position_plain]
        else:
            text_cipher += char
            
    return text_cipher

# Streamlit Interface
st.title("Simple Caesar Cipher")

user_message = st.text_input("Enter text to encrypt:", value="hello")

if user_message:
    secret_result = caesar_cipher_simple(user_message)
    st.success(f"Encrypted text: **{secret_result}**")
