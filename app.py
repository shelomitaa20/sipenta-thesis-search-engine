from flask import Flask, render_template, request, jsonify
import math
import json
import pickle
import re
from search_engine import search_and_rank

app = Flask(__name__)

# =========================
# LOAD DATA
# =========================
with open("data/inverted_index.json", "rb") as f:
    inverted_index = json.load(f)

with open("data/trigram_index.pkl", "rb") as f:
    trigram_index = pickle.load(f)

with open("data/metadata_clean.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

N = len(metadata)
RESULTS_PER_PAGE = 10


# =========================
# EXTRACT KATA KUNCI
# =========================
def extract_kata_kunci(text):
    if not text:
        return None
    match = re.search(r'kata\s*kunci\s*:\s*(.*)$', text, re.I | re.S)
    return match.group(1).strip() if match else None


def clean_abstrak(text):
    if not text:
        return text
    return re.sub(r'kata\s*kunci\s*:.*$', '', text, flags=re.I | re.S).strip()


# =========================
# ROUTE: SEARCH PAGE
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    # Ambil parameter
    query = request.form.get("query", "").strip() or request.args.get("query", "").strip()
    page = int(request.args.get("page", 1))
    filter_year = request.form.get("year") or request.args.get("year") or "all"
    sort_by = request.form.get("sort") or request.args.get("sort") or "relevance"

    results = []
    total_results = 0
    suggestion = None
    page_range = []

    if query:
        ranked, suggestion = search_and_rank(query, inverted_index, trigram_index, N)

        # Filter tahun
        if filter_year != "all":
            ranked = [
                (docid, score)
                for docid, score in ranked
                if str(metadata.get(docid, {}).get("tahun")) == filter_year
            ]

        # Sorting
        if sort_by == "year":
            ranked.sort(
                key=lambda x: metadata.get(x[0], {}).get("tahun", 0),
                reverse=True
            )

        total_results = len(ranked)

        # Pagination slicing
        start = (page - 1) * RESULTS_PER_PAGE
        end = start + RESULTS_PER_PAGE
        for docid, score in ranked[start:end]:
            info = metadata.get(docid, {})
            results.append({
                "docid": docid,
                "judul": info.get("judul", "-"),
                "nama": info.get("nama_mahasiswa", "-"),
                "tahun": info.get("tahun", "-"),
                "score": round(score, 4)
            })

    # Hitung total halaman
    total_pages = math.ceil(total_results / RESULTS_PER_PAGE)

    # Page range untuk tampilan pagination
    if total_pages > 1:
        start_page = max(1, page - 2)
        end_page = min(total_pages + 1, page + 3)
        page_range = list(range(start_page, end_page))

    # Daftar tahun
    years = sorted(
        {str(m["tahun"]) for m in metadata.values() if m.get("tahun")},
        reverse=True
    )

    # Recent theses untuk homepage
    recent_theses = []
    sorted_metadata = sorted(metadata.items(), key=lambda x: x[1].get("tahun", 0), reverse=True)
    for docid, info in sorted_metadata[:6]:
        recent_theses.append({
            "docid": docid,
            "judul": info.get("judul", "-"),
            "nama": info.get("nama_mahasiswa", "-"),
            "tahun": info.get("tahun", "-")
        })

    # Parameter saat ini untuk digunakan di link pagination
    current_params = {
        "query": query if query else None,
        "year": filter_year if filter_year != "all" else None,
        "sort": sort_by if sort_by != "relevance" else None
    }

    return render_template(
        "index.html",
        query=query,
        results=results,
        suggestion=suggestion,
        page=page,
        total_pages=total_pages,
        total_results=total_results,
        years=years,
        selected_year=filter_year,
        sort_by=sort_by,
        recent_theses=recent_theses,
        page_range=page_range,
        current_params=current_params
    )


# =========================
# AUTOCOMPLETE
# =========================
AUTOCOMPLETE_TERMS = set()
for term in inverted_index.keys():
    if len(term) > 3:
        AUTOCOMPLETE_TERMS.add(term)
for m in metadata.values():
    for w in m.get("judul", "").lower().split():
        if len(w) > 3:
            AUTOCOMPLETE_TERMS.add(w)


@app.route("/autocomplete")
def autocomplete():
    q = request.args.get("q", "").lower().strip()
    if not q:
        return jsonify([])
    last_word = q.split()[-1]
    suggestions = []
    for info in metadata.values():
        title = info.get("judul", "")
        if last_word in title.lower():
            suggestions.append(title)
    return jsonify(suggestions[:10])


# =========================
# DETAIL PAGE
# =========================
@app.route("/detail/<docid>")
def detail(docid):
    q = request.args.get("q", "")
    doc = metadata.get(docid)
    if not doc:
        return "Dokumen tidak ditemukan", 404

    abstrak_raw = doc.get("abstrak", "")
    kata_kunci = extract_kata_kunci(abstrak_raw)
    abstrak_clean = clean_abstrak(abstrak_raw)

    return render_template(
        "detail.html",
        doc={**doc, "abstrak": abstrak_clean, "kata_kunci": kata_kunci},
        query=q
    )


if __name__ == "__main__":
    app.run(debug=True)