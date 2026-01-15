# SIPENTA – Thesis Search Engine
**An Academic Information Retrieval System for Undergraduate Theses**

SIPENTA (*Sistem Pencarian Tugas Akhir*) is an **academic search engine** designed to assist users in retrieving undergraduate thesis documents efficiently based on titles, topics, or keywords. Due to privacy considerations, the original thesis data (metadata_clean.json, inverted_index.json, trigram_index_pkl) is not included in this repository.

---

## 🎯 System Objectives
The objectives of SIPENTA are to:
- Facilitate efficient searching of undergraduate thesis documents
- Handle query misspellings through tolerant retrieval
- Rank search results based on relevance
- Provide an interactive web-based interface for academic document exploration

---

## 🚀 Main Features

### 🔍 Document Search
- **Phrase Query Search**
- Query preprocessing including:
  - Case folding
  - Tokenization
  - Numeric normalization
  - Indonesian stemming using **Sastrawi Stemmer**

### ✏️ Tolerant Retrieval (Did You Mean?)
- Detection of misspelled query terms
- Query correction suggestions using:
  - **Trigram Index**
  - **Edit Distance (Levenshtein Distance)**

### 📊 Document Ranking
- **TF-IDF weighting scheme**
- **Cosine Similarity** for relevance scoring
- Ranked search results based on similarity scores

### 🧭 User Interface & Navigation
- Filtering by **publication year**
- Sorting by **relevance** or **most recent year**
- Autocomplete suggestions in the search bar
- Detailed document view including:
  - Title
  - Abstract
  - Keywords
  - Author information
  - Publication year
  - PDF access (if available)
  
---

## 🧠 Technologies Used
- Python
- Flask
- Sastrawi Stemmer
- HTML & Tailwind CSS
- JavaScript
