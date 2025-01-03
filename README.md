
# **SJSU CS Assistant**

## **About the Project**
The **SJSU CS Assistant** is a Retrieval-Augmented Generation (RAG) application built using **LangChain**, **OpenAI**, and **Pinecone**. This application helps students search for information about instructors at **San Jose State University (SJSU)**.

It combines document embeddings, retrieval mechanisms, and conversational AI capabilities to provide accurate and context-aware answers to student queries about instructors, course details, and more.

![Screenshot (1308)](https://github.com/user-attachments/assets/7af00c60-ec15-4d6c-aacb-7089c4bfe80d)

---

## **Key Features**
- ✅ **Natural Language Interaction:** Ask questions about SJSU instructors.  
- ✅ **Pinecone Vector Database:** Stores and queries instructor data efficiently.  
- ✅ **Conversational Context Awareness:** Maintains chat history for better follow-up interactions.  

---

## **Tech Stack**
- **Python**
- **LangChain**
- **OpenAI GPT Models**
- **Pinecone**
- **Streamlit**

---

## **Dependencies**
To run this project, install the following dependencies:

```bash
pip install langchain
pip install langchain-openai
pip install langchain-pinecone
pip install langchain-community
pip install langchain-core
pip install openai
pip install pinecone-client
pip install python-dotenv
pip install streamlit
```

---

## **Environment Variables**
Create a `.env` file in the root directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=sjsu-index
```

Replace `your_openai_api_key` and `your_pinecone_api_key` with your actual API keys.


---

## **Example Query**
- **"Can you give me a list of 5 professors with high ratings?"**  
- **"What is the teaching style of Professor [name]?"**
