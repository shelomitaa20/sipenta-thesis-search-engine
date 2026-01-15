# SIPENTA – Thesis Search Engine
**An Academic Information Retrieval System for Undergraduate Theses**

SIPENTA (*Sistem Pencarian Tugas Akhir*) is an **academic search engine** designed to assist users in retrieving undergraduate thesis documents efficiently based on titles, topics, or keywords.

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

---

## 🖼️ User Interface Preview

### 🔎 Search Page
Displays the main search interface where users can enter queries, apply filters, and view ranked thesis search results.

![Search Page](screenshots/search_page.png)



### ✏️ Query Suggestion (Did You Mean?)
Shows query correction suggestions when a misspelled query is detected using tolerant retrieval.

![Query Suggestion](screenshots/query_suggestion.png)



### 📄 Thesis Detail Page
Presents detailed information of a selected thesis document, including title, abstract, keywords, metadata, and PDF access.

![Detail Page](screenshots/detail_page.png)
