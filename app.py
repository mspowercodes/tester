import streamlit as nn  # You can use 'import streamlit as st' 
import streamlit as st

# Your function works perfectly
def is_lowercase(char):
    if 'a' <= char <= 'z':
        return True
    else:
        return False

# Streamlit Title
st.title("Lowercase Checker")

# Let users type a character to test it live!
user_input = st.text_input("Type a single letter:", value="g", max_chars=1)

if user_input:
    result = is_lowercase(user_input)
    st.write(f"Is '{user_input}' lowercase? **{result}**")
