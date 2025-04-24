import streamlit as st
from pymongo import MongoClient
from PIL import Image
import google.generativeai as genai
from key import gemini_api_key
from pymongo.errors import ServerSelectionTimeoutError


# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/',ServerSelectionTimeoutMs=5000)  # Change this to your MongoDB URI
db = client['project']
collection = db['users']

# Function to register a new user
def register_user(username, password):
    user_data = {'username': username, 'password': password}  # Store plain password (not secure)
    collection.insert_one(user_data)

# Function to check if the user exists and password matches
def validate_user(username, password):
    user = collection.find_one({'username': username})
    return user and user['password'] == password

# Streamlit app
st.title("Image Analysis")

# Initialize session state if not already done
if 'username' not in st.session_state:
    st.session_state['username'] = None

# If user is logged in, show main application; otherwise show login/register options
if st.session_state['username']:
    st.sidebar.write(f"Logged in as: {st.session_state['username']}")

    # Image uploader
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Open the image file
        img = Image.open(uploaded_file)
                # Display the image
        st.image(img, caption='Uploaded Image', use_column_width=True)
        if img:
            try:
                genai.configure(api_key=gemini_api_key)

                model = genai.GenerativeModel('gemini-1.5-flash')
                response=model.generate_content(["analyze the picture and give me the details in brief",img],stream=False)
                for responses in response:
                    st.write(responses.text)
            except Exception as error:
                st.write("there seems to be a problem please do not leave the page!")
        else:
            st.write("please upload the file")
    
    # Logout option
    if st.sidebar.button("Logout"):
        st.session_state['username'] = None
        st.success("You have logged out.")
        st.rerun()
else:
    menu = st.sidebar.selectbox("Choose Register/Login", ["Register","Login" ])

    if menu == "Register":
        st.subheader("Create an Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if st.button("Register"):
            if username and password:
                if collection.find_one({'username': username}):
                    st.error("Username already exists!")
                else:
                    register_user(username, password)
                    st.success("You have successfully registered!")
            else:
                st.error("Please fill out all fields.")

    elif menu == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        # Check for successful login
        login_button = st.button("Login")

        if login_button:
            if validate_user(username, password):
                st.session_state['username'] = username  # Store username in session state
                st.success("Login successful!")
                st.rerun()  # Rerun the script to update the UI
            else:
                st.error("Invalid username or password.")




