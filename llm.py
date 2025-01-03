from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
from pinecone import Pinecone
from config import answer_examples
import os 

load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def get_retriever():
    # text_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=2000,
    #     chunk_overlap=100
    # )
    # file_path = os.path.abspath('./total.txt')
    # print(file_path)
    # loader = TextLoader(file_path,encoding='utf-8')
    # file_path = os.path.abspath('./data.csv')
    # loader = CSVLoader(file_path)
    # documents = loader.load()
    
    # text_list = text_splitter.split_documents(documents)
    
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'sjsu-index'
    
    try:
        database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)
        # database.add_documents(text_list)
    except Exception as e:
        print(f"Error: {e}")
        # database = PineconeVectorStore.from_documents(text_list, embedding, index_name=index_name)    


    # query = 'Who is the best instructor?'
    # retrieved_docs = database.similarity_search(query)
    retriever = database.as_retriever(search_kwargs={'k': 4})
    return retriever

def get_history_retriever():
    llm = get_llm()
    retriever = get_retriever()
    
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever


def get_llm(model='gpt-4o'):
    llm = ChatOpenAI(model=model)
    return llm

# A chain that modifies the question based on a dictionary
def get_dictionary():
    dictionary = [
        "people or person -> Instructor",
        "teaching staff -> Professor",
        "academic advisor -> Advisor",
        "someone with significant research contributions -> Researcher",
        "someone teaching introductory courses -> Lecturer",
        "office hours provider -> Instructor",
        "faculty member -> Staff"
    ]
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(f"""
        Review the user's question and refer to our dictionary to adjust the question if necessary.
        If you determine that no adjustment is needed, return the question as is.
        Dictionary: {dictionary}
        
        Question: {{question}}
    """)

    dictionary = prompt | llm | StrOutputParser()
    
    return dictionary

# A RAG that retrieves information based on a question and generates an answer
def get_rag():
    llm = get_llm()
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{answer}"),
        ]
    )
    # Using few-shot examples for improved responses
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=answer_examples,
    )
    system_prompt = (
        "You are an expert on the SJSU Computer Science department and its instructors"
        "Please answer questions related to SJSU CS instructors based on the provided context"
        "If you do not know the answer, simply state that you do not know"
        "When providing an answer, start with According to the SJSU rate my professor,"
        "Keep your response brief, ideally 2-3 sentences"
        "\n\n"
        "{context}"
    )
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            few_shot_prompt,
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    history_aware_retriever = get_history_retriever()
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    conversational_rag = RunnableWithMessageHistory(
        rag,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ).pick('answer')
    
    return conversational_rag


def get_response(user_message):
    dictionary = get_dictionary()
    rag = get_rag()
    result = {"input": dictionary} | rag

    response = result.stream(
        {
            "question": user_message
        },
        config={
            "configurable": {"session_id": "abc123"}
        },
    )

    return response