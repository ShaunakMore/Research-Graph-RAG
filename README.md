# 🧠 ResearchGraph

> A full-stack Graph-RAG research assistant that combines Knowledge Graphs, Vector Search, and LLM reasoning to help researchers explore, compare, and understand scientific papers.
---
🌐 Live Demo: https://research-graph-rag.vercel.app
---

## 🚀 Overview

ResearchGraph goes beyond traditional Retrieval-Augmented Generation (RAG) systems by combining:

* 📚 Vector Search for semantic retrieval
* 🕸️ Knowledge Graphs for structured reasoning
* 🤖 LLMs for answer generation
* 🔍 Multi-paper comparison capabilities

Instead of only retrieving relevant text chunks, ResearchGraph builds a structured knowledge graph of research papers and uses both graph facts and semantic retrieval to generate grounded answers.

---

## ✨ Key Capabilities

### 📄 Upload and Analyze Research Papers

Upload scientific papers through the web interface and automatically:

* Extract text
* Generate embeddings
* Build a knowledge graph
* Store papers for future sessions

---

### 🧠 Hybrid Graph-RAG Retrieval

Combines:

* Semantic Vector Search (Pinecone)
* Knowledge Graph Retrieval (Neo4j)
* LLM Reasoning (Gemini / Gemma)

to provide more accurate and explainable answers.

---

### 🔍 Knowledge Graph Construction

Automatically extracts:

* Methods
* Datasets
* Metrics
* Claims
* Limitations

and stores relationships between them.

Example:

```text
(BERT Paper)
      │
      ▼
    (BERT)
      │
      ├── EVALUATED_ON ──► (SQuAD)
      ├── EVALUATED_ON ──► (MNLI)
      ├── MEASURED_BY ──► (F1 Score)
      ├── ACHIEVED ──► (State-of-the-Art Results)
      └── HAS_LIMITATION ──► (Large Compute Requirements)
```

---

### 📚 Multi-Paper Comparison

Compare multiple uploaded papers using natural language.

Examples:

```text
Compare BERT and CLIP.

What datasets are common between both papers?

What limitations are shared?

How do their evaluation metrics differ?
```

---

### 🔐 User Authentication

Powered by Clerk.

Features:

* Secure authentication
* User-specific sessions
* Persistent paper libraries
* Personalized research workspace

---

### 💾 Persistent Research Library

Uploaded papers are associated with user accounts.

Users can:

* Revisit previous papers
* Continue conversations
* Compare newly uploaded papers with existing ones

---

### 🌐 Modern Full-Stack Application

Frontend:

* React
* Vite
* Clerk Authentication

Backend:

* FastAPI
* Hugging Face Spaces

Infrastructure:

* Pinecone
* Neo4j
* Gemini / Gemma

---

### 📑 Grounded Responses

Answers are generated using:

* Graph Facts
* Retrieved Chunks
* LLM Reasoning

This reduces hallucinations and improves explainability.

---

## 🏗️ Architecture

```text
┌────────────────────────────┐
│     React Frontend         │
│        (Vercel)            │
└─────────────┬──────────────┘
              │
              ▼

┌────────────────────────────┐
│      FastAPI Backend       │
│   (Hugging Face Spaces)    │
└─────────────┬──────────────┘
              │

      ┌───────┼────────┐
      ▼                ▼

┌──────────────┐  ┌──────────────┐
│   Pinecone   │  │    Neo4j     │
│  Vector DB   │  │ Knowledge KG │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └───────┬─────────┘
               ▼

      ┌─────────────────┐
      │ Gemini / Gemma  │
      │ Answer Engine   │
      └─────────────────┘
```

---

## 🧬 Knowledge Graph Schema

```text
(Paper)-[:PROPOSES]->(Method)

(Method)-[:EVALUATED_ON]->(Dataset)

(Method)-[:MEASURED_BY]->(Metric)

(Method)-[:ACHIEVED]->(Claim)

(Method)-[:HAS_LIMITATION]->(Limitation)
```

This structure allows ResearchGraph to answer questions that traditional RAG systems struggle with.

---

## 🔄 Ingestion Pipeline

```text
PDF Upload
    │
    ▼

Text Extraction
    │
    ▼

Chunking
    │
    ├──► Embeddings
    │         │
    │         ▼
    │    Pinecone
    │
    ▼

Entity Extraction
    │
    ▼

Knowledge Graph Builder
    │
    ▼

Neo4j
```

---

## 💬 Example Queries

### Single-Paper Queries

```text
What methods are proposed in the BERT paper?

What datasets were used to evaluate CLIP?

What limitations are mentioned in the paper?

What metrics were used to evaluate the model?

Summarize the paper's main claims.
```

### Multi-Paper Queries

```text
Compare BERT and CLIP.

What datasets are common between the papers?

Which paper evaluates on more datasets?

What limitations are shared by both papers?

How do the evaluation metrics differ?
```

---

## 📂 Project Structure

```text
ResearchGraph/

├── frontend/
│   ├── src/
│   ├── public/
│   └── ...
│
├── backend/
│   ├── ingestion/
│   ├── graph/
│   ├── retrieval/
│   ├── prompts/
│   └── backend.py
│
├── uploaded_papers/
│
├── requirements.txt
│
└── README.md
```

---

## ⚙️ Tech Stack

### Frontend

* React
* Vite
* Clerk

### Backend

* FastAPI
* Python

### Vector Database

* Pinecone

### Knowledge Graph

* Neo4j

### LLMs

* Gemini
* Gemma
* Ollama

### Deployment

* Vercel
* Hugging Face Spaces

### PDF Processing

* PyPDF
* PyMuPDF

---

## 🔮 Future Work

### 🖼️ Figure Retrieval

Planned support for retrieving relevant figures directly from papers.

Pipeline:

```text
PDF
 ├── Extract Images
 ├── Extract Captions
 ├── Generate Embeddings
 └── Retrieve Relevant Figures
```

This will allow answers to include:

* Architecture diagrams
* Experimental plots
* Benchmark visualizations

alongside textual explanations.

---

### 📈 Advanced Research Graphs

* Citation Networks
* Method Lineage Tracking
* Temporal Research Evolution
* Confidence Scoring
* Cross-Paper Knowledge Discovery

---

## 🌟 Why Graph-RAG?

Traditional RAG answers:

> "Where is the information?"

Knowledge Graphs answer:

> "How is the information related?"

ResearchGraph combines both approaches to provide:

* Better reasoning
* More explainable answers
* Reduced hallucinations
* Structured research understanding

---

## 📜 License

MIT License

---

Built to explore how Graph-RAG can improve scientific literature understanding, comparison, and knowledge discovery.
