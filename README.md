# Stock Summary and Financial Metrics with Local LLM

This project utilizes LangChain to generate summaries of stock transcripts using a local Language Model (LLM). The project stores summarized data in ChromaDB for easy access and uses MongoDB to manage financial metrics associated with the stocks.

## Features
- **LangChain Integration**: Summarizes stock transcripts using a local LLM.
- **ChromaDB**: Stores and indexes stock summaries for efficient retrieval.
- **MongoDB**: Stores financial metrics such as revenue, earnings, etc.


## Current results - BERTScorer

|           |   lexrank |      raw |
|:----------|----------:|---------:|
| Precision |  0.385635 | 0.421326 |
| Recall    |  0.503401 | 0.511537 |
| F1        |  0.436718 | 0.462069 |