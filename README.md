# Placement FAQ Bot

A minimal Streamlit chatbot that uses LangChain and Gemini to answer questions
from an uploaded PDF. It does not store your API key and is instructed not to
invent information that is absent from the reference document.

## Run it

1. Create and activate a Python virtual environment (optional but recommended).
2. Install packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

4. Open the local URL, enter your Google AI (Gemini) API key, and upload
   `Resturaunt Q&A.pdf` (or your own placement FAQ PDF).

The supplied PDF contains restaurant information, so the bot will accurately
answer restaurant questions from it. To make it a real placement assistant,
upload a PDF containing your placement eligibility, application, interview,
and contact information.
