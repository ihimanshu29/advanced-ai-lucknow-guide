
import os
import pandas as pd
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from ragas.run_config import RunConfig  # <-- Import RunConfig
from datasets import Dataset
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Configure Pandas for better terminal output
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 40)

def run_evaluation():
    """
    Runs a full evaluation of the RAG pipeline using Groq and Hugging Face.
    """
    print("--- Initializing RAG Evaluation Suite (Groq Edition) ---")

    # 1. Load knowledge base
    print("1. Loading knowledge base...")
    try:
        food_loader = TextLoader("./knowledge_base/lucknow_food.txt", encoding="utf-8")
        history_loader = TextLoader("./knowledge_base/lucknow_history.txt", encoding="utf-8")
        documents = food_loader.load() + history_loader.load()
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure the 'knowledge_base' folder and its files exist in the backend directory.")
        return

    # 2. Create vector store with Hugging Face embeddings
    print("2. Creating vector store...")
    print("   Using Hugging Face Endpoint Embeddings API (BAAI/bge-small-en-v1.5) to avoid OOM.")
    embedding_model = HuggingFaceEndpointEmbeddings(
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        model="BAAI/bge-small-en-v1.5"
    )
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model
    )
    retriever = vectorstore.as_retriever()

    # 3. Initialize LLM from Groq
    print("3. Initializing Groq LLM...")
    # This LLM is used by the QA chain to generate the initial answers
    qa_llm = ChatGroq(
        model_name="meta-llama/llama-4-maverick-17b-128e-instruct", 
        temperature=0, 
        max_retries=3
    )

    # 4. Create QA Chain for testing
    qa_chain = RetrievalQA.from_chain_type(llm=qa_llm, chain_type="stuff", retriever=retriever)

    # 5. Define Evaluation Dataset
    print("4. Defining evaluation dataset...")
    eval_questions = [
        "What is the historical significance of the Bara Imambara?",
        "Describe the famous Galouti Kebab.",
        "Who was Asaf-ud-Daula?",
        "What makes the Tunday Kababi so special according to the text?",
        "How is Lucknowi Biryani different from other types?",
    ]
    ground_truths = [
        "The Bara Imambara is a significant historical monument built in 1784 by Asaf-ud-Daula, known for its large central hall built without beams and a food-for-work program.",
        "The Galouti Kebab is a melt-in-the-mouth kebab made from finely minced meat and over 100 spices, created for a toothless Nawab.",
        "Asaf-ud-Daula was the fourth Nawab of Awadh who commissioned projects like the Bara Imambara to provide employment during a famine.",
        "According to the text, Tunday Kababi is special because of its secret family recipe using over 160 spices.",
        "Lucknowi Biryani is different because it is less spicy and more subtle and fragrant. The meat and rice are cooked separately before being layered and slow-cooked in the 'dum style'."
    ]


    # --- RUNNING EVALUATION ---
    print("\n--- Generating Answers for Evaluation ---")
    answers = []
    contexts = []
    for question in eval_questions:
        print(f"   Processing question: '{question}'")
        try:
            response = qa_chain.invoke(question)
            answers.append(response["result"])
            retrieved_docs = retriever.invoke(question)
            contexts.append([doc.page_content for doc in retrieved_docs])
        except Exception as e:
            print(f"   Error processing question: {question}. Error: {e}")
            answers.append("Error")
            contexts.append([])

    # 6. Create Dataset using the stable 'from_dict' method
    print("\n--- Creating Ragas Dataset ---")
    dataset_dict = {
        "question": eval_questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    dataset = Dataset.from_dict(dataset_dict)

    # 7. Configure the Ragas LLM Judge (to fix Timeouts)
    print("\n--- Starting Ragas Evaluation ---")
    # This is the "judge" LLM. We give it a longer timeout to prevent failures.
    ragas_llm = ChatGroq(
        model_name="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=0,
        max_retries=3,
        timeout=120  # <-- Increase timeout to 120 seconds
    )
    
    # --- FIX: Removed .evolve() from metrics ---
    metrics = [
        faithfulness,
        context_precision,
        context_recall
    ]
    
    # --- FIX: Added run_config to force serial execution (max_workers=1) ---
    config = RunConfig(max_workers=1)

    result = evaluate(
        dataset=dataset, 
        metrics=metrics, 
        llm=ragas_llm,  # <-- FIX: Pass LLM judge here
        embeddings=embedding_model,  # <-- FIX: Pass embeddings here
        run_config=config,  # <-- FIX: Pass config here
        raise_exceptions=False # Don't stop the whole eval if one row fails
    )

    print("\n--- Evaluation Complete ---")
    df = result.to_pandas()
    
    # Save results to files for easy viewing
    html_report_path = "evaluation_report.html"
    md_report_path = "evaluation_report.md"
    
    try:
        df.to_html(html_report_path, index=False, border=1, classes='table table-striped table-hover')
        print(f"\n✅ Successfully saved detailed report to: {html_report_path}")
    except Exception as e:
        print(f"Could not save HTML report: {e}")

    try:
        df.to_markdown(md_report_path, index=False)
        print(f"✅ Successfully saved Markdown report to: {md_report_path}")
    except Exception as e:
        print(f"Could not save Markdown report: {e}")

    print("\n--- RAG Performance Metrics (Terminal Preview) ---")
    print(df.to_string())


if __name__ == "__main__":
    run_evaluation()
