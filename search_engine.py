import re
import math
from collections import Counter
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# =========================
# STEMMER
# =========================

factory = StemmerFactory()
stemmer = factory.create_stemmer()

# =========================
# QUERY PREPROCESSING
# =========================

def preprocess_query(query):
    """
    Pipeline:
    1) case folding
    2) normalisasi angka -> <NUM>
    3) hapus simbol
    4) tokenisasi
    5) stemming Sastrawi
    """
    if query is None:
        return []

    # case folding
    query = query.lower()

    # normalisasi angka
    query = re.sub(r"\d+(\.\d+)?", " <NUM> ", query)

    # ganti tanda hubung
    query = query.replace("-", " ")

    # lindungi token <NUM>
    query = query.replace("<num>", "NUMTOKEN")
    query = re.sub(r"[^a-z0-9\s]", " ", query)
    query = query.replace("NUMTOKEN", "<NUM>")

    query = re.sub(r"\s+", " ", query).strip()

    # tokenisasi
    tokens = query.split()

    # stemming
    stemmed = []
    for t in tokens:
        if t == "<NUM>":
            stemmed.append(t)
        else:
            stemmed.append(stemmer.stem(t))

    return stemmed

# =========================
# BOOLEAN & PHRASE QUERY
# =========================

def and_query(terms, inverted_index):
    posting_lists = []

    for term in terms:
        if term in inverted_index:
            posting_lists.append(set(inverted_index[term].keys()))
        else:
            return set()

    return set.intersection(*posting_lists)


def or_query(terms, inverted_index):
    result = set()
    for term in terms:
        if term in inverted_index:
            result.update(inverted_index[term].keys())
    return result


def phrase_query(phrase_terms, inverted_index):
    """
    Mengecek apakah term muncul berurutan dalam dokumen yang sama
    """
    if any(t not in inverted_index for t in phrase_terms):
        return set()

    candidate_docs = set(inverted_index[phrase_terms[0]].keys())
    for term in phrase_terms[1:]:
        candidate_docs &= set(inverted_index[term].keys())

    result = set()
    for docid in candidate_docs:
        positions = inverted_index[phrase_terms[0]][docid]["positions"]

        for pos in positions:
            match = True
            for i, term in enumerate(phrase_terms[1:], start=1):
                if (pos + i) not in inverted_index[term][docid]["positions"]:
                    match = False
                    break
            if match:
                result.add(docid)
                break

    return result

# =========================
# TOLERANT RETRIEVAL
# =========================

def edit_distance(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]

    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # delete
                dp[i][j - 1] + 1,      # insert
                dp[i - 1][j - 1] + cost
            )

    return dp[-1][-1]

def tolerant_retrieval(query_term, trigram_index, dictionary_terms, max_dist=3):
    padded = f"${query_term}$"
    trigrams = [padded[i:i+3] for i in range(len(padded) - 2)]

    candidates = set()
    for tri in trigrams:
        candidates.update(trigram_index.get(tri, []))

    best_terms = []
    for cand in candidates:
        dist = edit_distance(query_term, cand)
        if dist <= max_dist:
            best_terms.append((cand, dist))

    best_terms.sort(key=lambda x: x[1])
    return [t[0] for t in best_terms[:5]]

def suggest_query(query, trigram_index, dictionary_terms, max_dist=2):
    tokens = preprocess_query(query)
    suggestions = []

    for t in tokens:
        if t in dictionary_terms:
            suggestions.append(t)
        else:
            candidates = tolerant_retrieval(
                t, trigram_index, dictionary_terms, max_dist
            )
            if candidates:
                suggestions.append(candidates[0])  # terbaik
            else:
                suggestions.append(t)

    suggested_query = " ".join(suggestions)

    # hanya kembalikan jika beda
    if suggested_query != " ".join(tokens):
        return suggested_query

    return None

# =========================
# SEARCH
# =========================

def search(query, inverted_index, trigram_index, mode="AND"):
    tokens = preprocess_query(query)

    # 1. Phrase query
    if len(tokens) > 1:
        phrase_docs = phrase_query(tokens, inverted_index)
        if phrase_docs:
            return phrase_docs

    # 2. Boolean search
    if mode == "AND":
        docs = and_query(tokens, inverted_index)
    else:
        docs = or_query(tokens, inverted_index)

    # 3. Tolerant retrieval jika kosong
    if not docs:
        expanded_terms = []
        for t in tokens:
            expanded_terms.extend(
                tolerant_retrieval(t, trigram_index, inverted_index.keys())
            )
        docs = or_query(expanded_terms, inverted_index)

    return docs

# =========================
# RANKING (TF-IDF + COSINE)
# =========================

def compute_idf(inverted_index, N):
    """
    IDF = log10(N / df)
    """
    idf = {}
    for term, postings in inverted_index.items():
        df = len(postings)
        idf[term] = math.log10(N / df) if df > 0 else 0.0
    return idf


def compute_query_vector(query_tokens, idf):
    tf = Counter(query_tokens)
    query_vector = {}

    for term, freq in tf.items():
        if term in idf:
            query_vector[term] = freq * idf[term]

    return query_vector


def compute_doc_vector(docid, inverted_index, idf):
    vector = {}

    for term, postings in inverted_index.items():
        if docid in postings:
            tf = postings[docid]["tf"]
            vector[term] = tf * idf[term]

    return vector


def cosine_similarity(vec1, vec2):
    dot = 0.0
    for term in vec1:
        if term in vec2:
            dot += vec1[term] * vec2[term]

    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot / (norm1 * norm2)


def rank_documents(query, candidate_docs, inverted_index, idf):
    query_tokens = preprocess_query(query)
    query_vector = compute_query_vector(query_tokens, idf)

    scores = []
    for docid in candidate_docs:
        doc_vector = compute_doc_vector(docid, inverted_index, idf)
        score = cosine_similarity(query_vector, doc_vector)

        if score > 0:
            scores.append((docid, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

# =========================
# PIPELINE UTAMA 
# =========================

def search_and_rank(query, inverted_index, trigram_index, N, mode="AND"):
    # =========================
    # 1. PREPROCESS QUERY
    # =========================
    query_tokens = preprocess_query(query)
    if not query_tokens:
        return [], None

    dictionary_terms = set(inverted_index.keys())

    # =========================
    # 2. CEK MISSPELLING (SEBELUM SEARCH)
    # =========================
    has_misspelled = any(t not in dictionary_terms for t in query_tokens)

    suggestion = None
    if has_misspelled:
        suggestion = suggest_query(
            query,
            trigram_index,
            dictionary_terms
        )

    # =========================
    # 3. SEARCH (BOOLEAN / PHRASE / TOLERANT)
    # =========================
    candidate_docs = search(query, inverted_index, trigram_index, mode)

    if not candidate_docs:
        return [], suggestion

    # =========================
    # 4. SINGLE TERM QUERY → TF
    # =========================
    if len(query_tokens) == 1:
        term = query_tokens[0]
        results = []

        if term in inverted_index:
            for docid, info in inverted_index[term].items():
                results.append((docid, info["tf"]))

        results.sort(key=lambda x: x[1], reverse=True)
        return results, suggestion

    # =========================
    # 5. MULTI TERM → TF-IDF + COSINE
    # =========================
    idf = compute_idf(inverted_index, N)
    ranked_docs = rank_documents(query, candidate_docs, inverted_index, idf)

    # =========================
    # 6. FALLBACK JIKA COSINE = 0
    # =========================
    if not ranked_docs:
        return [(docid, 0.0) for docid in candidate_docs], suggestion

    return ranked_docs, suggestion