
import os

import pandas as pd
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from datasets import Dataset
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

def run_evaluation():
    """
    Runs a full evaluation of the RAG pipeline using Groq and Hugging Face.
    """
    print("--- Initializing RAG Evaluation Suite (Groq Edition) ---")

    # 1. Load knowledge base
    print("1. Loading knowledge base...")
    try:
        food_loader = TextLoader("./knowledge_base/lucknow_food.txt")
        history_loader = TextLoader("./knowledge_base/lucknow_history.txt")
        documents = food_loader.load() + history_loader.load()
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure knowledge base files are in the same directory.")
        return

    # 2. Create vector store with Hugging Face embeddings
    print("2. Creating vector store...")
    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model
    )
    retriever = vectorstore.as_retriever()

    # 3. Initialize LLM from Groq
    print("3. Initializing Groq LLM...")
    llm = ChatGroq(model_name="gemma2-9b-it", temperature=0, max_retries=3)

    # 4. Create QA Chain for testing
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

    # 5. Define Evaluation Dataset
    print("4. Defining evaluation dataset...")
    eval_questions = [
        "What is the historical significance of the Bara Imambara?",
        "Describe the famous Galouti Kebab.",
        "Who was Asaf-ud-Daula?",
        "What makes the Tunday Kababi so special according to the text?",
    ]
    ground_truths = [
         "The Bara Imambara is a significant historical monument built in 1784 by Asaf-ud-Daula, known for its large central hall built without beams.",
        "The Galouti Kebab is a melt-in-the-mouth kebab made from finely minced meat and over 100 spices, created for a toothless Nawab.",
        "Asaf-ud-Daula was the fourth Nawab of Awadh who commissioned projects like the Bara Imambara to provide employment during a famine.",
        "According to the text, Tunday Kababi is special because of its secret family recipe using over 160 spices."
    ]

    # --- RUNNING EVALUATION ---
    print("\n--- Generating Answers for Evaluation ---")
    answers = []
    contexts = []
    for question in eval_questions:
        response = qa_chain.invoke(question)
        answers.append(response["result"])
        retrieved_docs = retriever.invoke(question)
        contexts.append([doc.page_content for doc in retrieved_docs])

    response_dataset = Dataset.from_dict({
        "question": eval_questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })

    print("\n--- Starting Ragas Evaluation ---")
    metrics = [faithfulness, answer_relevancy, context_precision, context_recall]
    result = evaluate(dataset=response_dataset, metrics=metrics, llm=llm, embeddings=embedding_model)

    print("\n--- Evaluation Complete ---")
    df = result.to_pandas()

    try:
        df.to_html("evaluation_report.html", index=False, border=1, classes='table table-striped table-hover')
        print("\n✅ Successfully saved detailed report to 'evaluation_report.html'")
    except Exception as e:
        print(f"Could not save HTML report: {e}")

    # Save the results to a Markdown file for easy viewing on GitHub
    try:
        df.to_markdown("evaluation_report.md", index=False)
        print("✅ Successfully saved Markdown report to 'evaluation_report.md'")
    except Exception as e:
        print(f"Could not save Markdown report: {e}")

    # These settings ensure the table prints neatly in the terminal.
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 60) # Truncate long text columns
    pd.set_option('display.width', 1000)      # Use more horizontal space
    pd.set_option('display.colheader_justify', 'left')

    print("\n--- RAG Performance Metrics ---")
    print(df.to_string())

if __name__ == "__main__":
    run_evaluation()