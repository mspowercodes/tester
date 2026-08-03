import streamlit as st

# Your exact function untouched
def cryptoclub_ch01(message):
    plaintext = "abcdefghijklmnopqrstuvwxyz"
    ciphertext = "DEFGHIJKLMNOPQRSTUVWXYZABC"
    
    encrypted_message = []
    
    for char in message:
        if char in plaintext:
            number = plaintext.index(char)
            encrypted_message.append(ciphertext[number])
        else:
            encrypted_message.append(char)
            
    return "".join(encrypted_message)

# --- STREAMLIT INTERFACE ---
st.title("The Cryptoclub - Chapter 1")

# This creates the text box on the screen and captures whatever the user types into 'user_text'
user_text = st.text_input("Enter lowercase plaintext:", value="hello world")

# This takes the text from the box, runs your function, and saves it to 'result'
result = cryptoclub_ch01(user_text)

# This displays the result on the webpage
st.write("**Ciphertext:**")
st.code(result)
