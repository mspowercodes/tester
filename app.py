import streamlit as st

def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)

# --- STREAMLIT INTERFACE ---
st.title("Cryptocoding in Python Lesson 1")
st.write("This app encrypts lowercase text using a +3 Caesar cipher.")

# Captures what the student types into the box
user_text = st.text_input("Message:", value="hello world")

# Runs the simpler string function
result = caesar_shift3(user_text)

# Displays the final secret message
st.write("Encrypted message:")
st.code(result)
