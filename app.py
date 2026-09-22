"""A tiny document-grounded FAQ chatbot built with LangChain and Streamlit."""

from io import BytesIO

import streamlit as st
from pypdf import PdfReader
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI


SYSTEM_PROMPT = """You are a friendly placement and FAQ assistant.
Answer the user's question using only the reference document below. If the
answer is not in the document, say that you do not have that information and
recommend contacting the relevant placement/organization team. Never make up
policies, dates, eligibility rules, or contact details.

REFERENCE DOCUMENT:
{reference_text}
"""


def extract_pdf_text(uploaded_file) -> str:
    """Return all readable text from a Streamlit uploaded PDF."""
    reader = PdfReader(BytesIO(uploaded_file.getvalue()))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def answer_question(api_key: str, reference_text: str, history, question: str) -> str:
    """Ask Gemini with the PDF text as the only knowledge base."""
    model = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        temperature=0,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )
    chain = prompt | model | StrOutputParser()
    return chain.invoke(
        {
            "reference_text": reference_text,
            "history": history[-6:],  # keep the conversation compact
            "question": question,
        }
    )


st.set_page_config(page_title="Placement FAQ Bot", page_icon="🎓")
st.title("🎓 Placement FAQ Bot")
st.caption("Ask questions grounded in your uploaded placement or FAQ PDF.")

with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("Google AI API key", type="password")
    pdf_file = st.file_uploader("Upload a reference PDF", type=["pdf"])
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)

question = st.chat_input("For example: What are the eligibility requirements?")
if question:
    if not api_key:
        st.warning("Enter your Google AI API key in the sidebar first.")
        st.stop()
    if not pdf_file:
        st.warning("Upload a PDF in the sidebar first.")
        st.stop()

    try:
        reference_text = extract_pdf_text(pdf_file)
        if not reference_text:
            st.error("I couldn't extract readable text from that PDF.")
            st.stop()

        user_message = HumanMessage(content=question)
        st.session_state.messages.append(user_message)
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Looking in the reference PDF..."):
                reply = answer_question(
                    api_key, reference_text, st.session_state.messages[:-1], question
                )
            st.markdown(reply)
        st.session_state.messages.append(AIMessage(content=reply))
    except Exception as error:
        st.error(f"Something went wrong: {error}")
