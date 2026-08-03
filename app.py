import streamlit as st

alphabet_plain = 'abcdefghijklmnopqrstuvwxyz'
alphabet_cipher = 'DEFGHIJKLMNOPQRSTUVWXYZABC'

def caesar_cipher_simple(message):
    text_cipher = ""
    
    for char in message.lower():
        if char in alphabet:
            position_plain = alphabet_plain.find(char)
            text_cipher += alphabet_encrypt[position]
        else:
            encrypted_message += char
            
    return encrypted_message

# Streamlit Interface
st.title("Simple Caesar Cipher")

user_message = st.text_input("Enter text to encrypt:", value="hello")

if user_message:
    secret_result = caesar_cipher_simple(user_message)
    st.success(f"Encrypted text: **{secret_result}**")
