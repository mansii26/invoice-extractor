import streamlit as st
import os
import pathlib
import textwrap
from PIL import Image  # Not strictly needed for PDF handling


import google.generativeai as genai


os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function to handle PDF upload and extraction
def handle_pdf_upload(uploaded_file):
    """
    Handles the upload of a PDF file and extracts its text content using PyPDF2.

    Args:
        uploaded_file (streamlit.UploadedFile): The uploaded PDF file.

    Returns:
        str: The extracted text content from the PDF (if successful), or an error message.
    """

    if uploaded_file is not None:
        try:
            from PyPDF2 import PdfReader  # Import PyPDF2 for text extraction (install if needed)
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text.strip()  # Remove leading/trailing whitespace
        except (ImportError, Exception) as e:
            return f"Error processing PDF: {str(e)}"
    else:
        return "No file uploaded"


def get_gemini_response(input_text, prompt):
    """
    Gets a response from the Gemini model using the provided text input and prompt.

    Args:
        input_text (str): The text input for the model (likely a combination of extracted text and user question).
        prompt (str): The prompt to guide the model's response.

    Returns:
        str: The generated response from the Gemini model.
    """

    model = genai.GenerativeModel('gemini-pro-vision')  # Assuming no vision component is needed
    tasks = [genai.query_task(text=input_text, prompt=prompt)]
    response = model.run(tasks)
    return response[0].text  # Assuming a single task is submitted


def analyze_motor_data(motor_data_text, question):
    """
    Analyzes the extracted motor data text and attempts to answer the user's question
    using the Gemini LLM model.

    Args:
        motor_data_text (str): The extracted text content from the motor datasheet.
        question (str): The user's question about the motor datasheet.

    Returns:
        str: The answer generated by the Gemini model based on the combined input.
    """

    # Combine the motor data text and user question (potentially with pre-processing)
    combined_text = f"{motor_data_text.lower()} || USER_QUERY: {question.lower()}"

    # Prompt for the Gemini model (tailor it as needed)
    prompt = """You are an expert in understanding motor datasheets. 
    The text above is a combination of extracted text from a datasheet 
    and a user's question about the motor. 
    Answer the user's question in a comprehensive and informative way, 
    focusing on key motor specifications like power, torque, speed, etc."""

    response = get_gemini_response(combined_text, prompt)
    return response


## Initialize Streamlit app
st.set_page_config(page_title="Motor Datasheet Analyzer")

st.header("Motor Datasheet Analyzer (using LLM)")

uploaded_file = st.file_uploader("Select your motor datasheet (PDF)", type="pdf")
motor_data_text = ""

if uploaded_file is not None:
    motor_data_text = handle_pdf_upload(uploaded_file)
    if motor_data_text.startswith("Error"):
        st.error(motor_data_text)
    else:
        st.success("Motor datasheet text extracted successfully!")

input_text = st.text_input("Ask your question about the motor datasheet:", key="input")
submit = st.button("Get Answer")

if submit:
    response = analyze_motor_data(motor_data_text, input_text)
    st.subheader("The Response is:")
    st.write(response)

def footer():
    """Creates a footer component with the text."""
    st.write('<p style="text-align: center; font-size: 12px;">Developed by RajYug Solutions Ltd.</p>', unsafe_allow_html=True)

# Your Streamlit app code...

# Call the footer function at the end
footer()
