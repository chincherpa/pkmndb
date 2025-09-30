import streamlit as st

# Custom CSS 
st.markdown(
    '''
    <style>
    .streamlit-expanderHeader {
        background-color: blue;
        color: black; # Adjust this for expander header color
    }
    .streamlit-expanderContent {
        background-color: red;
        color: black; # Expander content color
    }
    </style>
    ''',
    unsafe_allow_html=True
)

with st.expander("Expand blue red"):
    st.write("Content inside the expander")