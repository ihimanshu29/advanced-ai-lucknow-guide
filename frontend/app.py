# import streamlit as st
# import requests

# # --- CONFIGURATION ---
# st.set_page_config(page_title="Advanced AI Lucknow Tour Guide", page_icon="🗺️", layout="wide")

# # This is the URL of your FastAPI backend.
# # When running locally, it will be http://localhost:8000
# BACKEND_URL = "http://127.0.0.1:8000/query"

# # --- UI SETUP ---
# st.title("🗺️ Advanced AI Lucknow Tour Guide")
# st.caption("⚡ Powered by a FastAPI backend, Groq, and RAG")

# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# # Display chat history
# for message in st.session_state.chat_history:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Handle user input   
# if prompt := st.chat_input("Plan my trip to Lucknow..."):
#     # Display user message
#     st.session_state.chat_history.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Call the backend API
#     with st.chat_message("assistant"):
#         with st.spinner("The AI planner is thinking..."):
#             try:
#                 # The request body must match the Pydantic model in the backend
#                 payload = {"query": prompt}
#                 response = requests.post(BACKEND_URL, json=payload)
#                 response.raise_for_status() # Raise an exception for bad status codes
                
#                 # Extract the response from the JSON
#                 backend_response = response.json().get("response", "No response from backend.")
#                 st.markdown(backend_response)
#                 st.session_state.chat_history.append({"role": "assistant", "content": backend_response})

#             except requests.exceptions.RequestException as e:
#                 error_message = f"Could not connect to the backend. Please ensure the FastAPI server is running. Error: {e}"
#                 st.error(error_message)
#                 st.session_state.chat_history.append({"role": "assistant", "content": error_message})
import streamlit as st
import requests
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Advanced AI Lucknow Tour Guide", page_icon="🗺️", layout="wide")

# Read the backend URL from the environment variable set by Docker Compose
# Provide a default (http://127.0.0.1:8000/query) for running locally if the variable isn't set.
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/query")
# BACKEND_URL = "http://127.0.0.1:8000/query"
# --- UI SETUP ---
st.title("🗺️ Advanced AI Lucknow Tour Guide")
st.caption("⚡ Powered by a FastAPI backend, Groq, and RAG")

# Initialize chat history in session state if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history from session state
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input from the chat interface
if prompt := st.chat_input("Plan my trip to Lucknow..."):
    # Add user message to chat history and display it
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the backend API and display the response
    with st.chat_message("assistant"):
        with st.spinner("The AI planner is thinking..."):
            try:
                # Prepare the data payload for the backend API
                payload = {"query": prompt}

                # Send the request to the backend using the configured URL
                response = requests.post(BACKEND_URL, json=payload)
                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

                # Extract the actual response text from the JSON
                backend_response_data = response.json()
                backend_response = backend_response_data.get("response", "No response text received from backend.")

                # Display the backend's response
                st.markdown(backend_response)

                # Add assistant's response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": backend_response})

            except requests.exceptions.RequestException as e:
                # Handle connection errors or bad responses from the backend
                error_message = (f"Could not connect to or get a valid response from the backend. "
                                 f"Please ensure the FastAPI server is running and accessible at {BACKEND_URL}. "
                                 f"Error: {e}")
                st.error(error_message)
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})
            except Exception as e:
                # Handle unexpected errors during the request/response processing
                error_message = f"An unexpected error occurred: {e}"
                st.error(error_message)
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})

