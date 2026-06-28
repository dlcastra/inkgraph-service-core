# INKGRAPH SERVICE CORE

### Short project description:
Automated editorial review engine. Highlights spelling issues, suggests emphasis, and annotates .docx documents via AI.

### Tech Stack: 
1. Python (3.12), 
2. FastAPI, 
3. LangChain/LandGraph, 
4. OpenAI API, 
5. Pydantic, 
6. python-docx, 
7. Docker

### Linter:
1. black (raw length: 120)
```shell
black . -l 120
```

## Motivation

Writing large documents, books, technical documentation, or reports often requires more than grammar checking. This project aims to provide AI-assisted document review that understands the document as a whole.

## Features

- Grammar and spelling review
- Style suggestions
- Chapter and section consistency checks
- Logical coherence analysis
- Context-aware comments
- RAG-powered knowledge retrieval
- Support for local and cloud LLMs
- Extensible agent workflow built with LangGraph

## How It Works

1. The document is split into logical chunks.
2. The AI agent analyzes each chunk.
3. When necessary, the agent retrieves external knowledge using RAG.
4. The agent produces comments and improvement suggestions.
5. The original document remains unchanged until the user accepts the suggestions.
