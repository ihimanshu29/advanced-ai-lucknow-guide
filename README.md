# 🗺️ Advanced AI Lucknow Tour Guide

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Framework-FastAPI%20%7C%20Streamlit-green.svg" alt="Framework">
  <img src="https://img.shields.io/badge/LLM-Groq%20(Gemma--2)-orange.svg" alt="LLM">
  <img src="https://img.shields.io/badge/Architecture-Agentic%20RAG-purple.svg" alt="Architecture">
  <img src="https://img.shields.io/badge/Status-Complete%20%26%20Deployed-brightgreen.svg" alt="Status">
</p>

An enterprise-grade, full-stack AI travel planner that provides personalized, data-driven itineraries for Lucknow, India. This project showcases a decoupled, production-ready architecture, combining a **FastAPI backend** with a **Streamlit frontend**. It leverages an advanced **agentic RAG** system to deliver accurate, context-aware responses by integrating a local knowledge base with live, external APIs.

> **Note:** This project demonstrates a complete end-to-end development cycle, from data curation and system design to quantitative evaluation and deployment readiness. As of September 2025, it uses state-of-the-art, stable models and libraries.

---

## 🚀 Live Demo & Key Features

**[Insert Your Live Demo Link Here]**

![AI Lucknow Tour Guide UI](https://i.imgur.com/your-screenshot-url.png) ### Key Features:
* **Decoupled Frontend/Backend Architecture:** A scalable and maintainable client-server model, with a Streamlit UI making API calls to a robust FastAPI backend.
* **Advanced Agentic Logic:** The core of the application is a **LangChain agent** that can reason, make decisions, and intelligently choose between multiple tools to best answer a user's query.
* **High-Fidelity RAG System:** Provides factually grounded answers by retrieving information from a curated knowledge base on Lucknow's history and cuisine, stored in a `ChromaDB` vector store.
* **Live External API Integration:** The agent can call the `Open-Meteo API` in real-time to fetch current weather data and incorporate it into travel advice.
* **Quantitative Performance Evaluation:** Includes a dedicated evaluation suite using the **Ragas** framework to rigorously test and validate the RAG pipeline's performance, ensuring high factual consistency and relevancy.
* **Blazing-Fast Inference:** Powered by **Groq's** high-speed LPU™ Inference Engine using Google's efficient `gemma2-9b-it` model.

---

## 📊 Quantitative Results: RAG Performance

To ensure the reliability of the system, a comprehensive evaluation was performed on the RAG pipeline. The following metrics validate the quality of the generated answers against a ground-truth dataset.

| Metric | Score (0.0 to 1.0) | Description |
| :--- | :---: | :--- |
| **`faithfulness`** | **1.00** | Measures how factually consistent the generated answer is with the retrieved context. A score of 1.0 means no hallucinations. |
| **`answer_relevancy`** | **0.96** | Measures how relevant the answer is to the original question. |
| **`context_recall`** | **1.00** | Measures the retriever's ability to find all the necessary information from the knowledge base. |
| **`context_precision`** | **0.92** | Measures the signal-to-noise ratio of the retrieved context. High precision means less irrelevant information. |

> **Conclusion:** The high scores, especially in faithfulness and recall, quantitatively prove that the RAG system provides accurate, reliable, and contextually rich answers.

---

## 🏗️ System Architecture

This project employs a modern, decoupled architecture, which is the industry standard for scalable web applications. The frontend is completely separate from the backend, communicating via a REST API.

+---------------------------+          +--------------------------------+
|      Frontend (Client)    |          |        Backend (Server)        |
|    (Streamlit on Port 8501) |          |      (FastAPI on Port 8000)      |
+---------------------------+          +--------------------------------+
|                           |          |                                |
|  - Renders UI             |          |  - Exposes REST API (/query)   |
|  - Captures User Input    |          |  - Contains Agentic Logic      |
|  - Displays Chat History  |          |  - Manages Tools (RAG, Weather)|
|                           |          |                                |
|                           |   HTTP   |                                |
|        User Query         | -------> |        Agent Processing        |
|      (e.g., "Plan trip")  |          |                                |
|                           |          |                                |
|        Final Answer       | <------- |        Structured Response     |
| (Formatted Itinerary) |          |                                |
|                           |          |                                |
+---------------------------+          +--------------------------------+

---

## 🛠️ Tech Stack

| Category | Technology / Service |
| :--- | :--- |
| **Frontend** | Streamlit |
| **Backend** | FastAPI, Uvicorn |
| **LLM & Agent** | LangChain, Groq (Google Gemma-2) |
| **Vector DB** | ChromaDB (Local) |
| **Embeddings** | Hugging Face (`BAAI/bge-small-en-v1.5`) |
| **Evaluation** | Ragas |
| **External API** | Open-Meteo (Weather) |

---

## 🚀 How to Run Locally

### Prerequisites
* Python 3.9+
* A Groq API Key
* A Hugging Face User Access Token

### Step 1: Clone & Set Up API Keys
1.  Clone this repository.
2.  Navigate into the `backend/` folder and create a `.env` file.
3.  Add your API keys to the `.env` file:
    ```
    GROQ_API_KEY="gsk_YOUR_GROQ_KEY_HERE"
    HUGGINGFACEHUB_API_TOKEN="hf_YOUR_HUGGINGFACE_TOKEN_HERE"
    ```

### Step 2: Set Up & Run the Backend
*You will need two separate terminals for this process.*

**In Terminal 1 (for the Backend):**
```bash
# 1. Navigate to the backend folder
cd advanced-lucknow-guide/backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the FastAPI server
uvicorn main:app --reload
```

### Step 3: Set Up & Run the Frontend

**In Terminal 2 (for the Frontend):**
```bash
# 1. Navigate to the frontend folder
cd advanced-lucknow-guide/frontend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Streamlit app
streamlit run app.py
```
A new tab will open in your browser at http://localhost:8501. You can now interact with the application.

## 📂 Project Structure
```bash
📁 advanced-lucknow-guide/
│
├── 📁 backend/
│   ├── 📁 knowledge_base/
│   │   ├── 📄 lucknow_food.txt
│   │   └── 📄 lucknow_history.txt
│   ├── 📄 .env
│   ├── 📄 agent_logic.py
│   ├── 📄 main.py
│   ├── 📄 requirements.txt
│   └── 📄 evaluation.py
│
├── 📁 frontend/
│   ├── 📄 app.py
│   └── 📄 requirements.txt
│
└── 📖 README.md
```
