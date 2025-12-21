from flask import Flask, render_template, request, jsonify
import math, json, pickle, re
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
# UTIL: EXTRACT KATA KUNCI
# =========================
def extract_kata_kunci(text):
    """
    Mengambil teks setelah 'Kata Kunci :' sampai akhir
    """
    if not text:
        return None

    match = re.search(r'kata\s*kunci\s*:\s*(.*)$', text, re.I | re.S)
    return match.group(1).strip() if match else None


def clean_abstrak(text):
    """
    Menghapus bagian 'Kata Kunci :' dari abstrak
    """
    if not text:
        return text

    return re.sub(
        r'kata\s*kunci\s*:.*$',
        '',
        text,
        flags=re.I | re.S
    ).strip()


# =========================
# ROUTE: SEARCH PAGE
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    query = request.form.get("query", "").strip()
    page = int(request.args.get("page", 1))

    # filter & sort
    filter_year = request.form.get("year") or request.args.get("year")
    sort_by = request.form.get("sort") or request.args.get("sort", "relevance")

    results = []
    total_results = 0
    suggestion = None

    if query:
        ranked, suggestion = search_and_rank(
            query, inverted_index, trigram_index, N
        )

        # filter tahun
        if filter_year and filter_year != "all":
            ranked = [
                (docid, score)
                for docid, score in ranked
                if str(metadata.get(docid, {}).get("tahun")) == filter_year
            ]

        # sorting
        if sort_by == "year":
            ranked.sort(
                key=lambda x: metadata.get(x[0], {}).get("tahun", 0),
                reverse=True
            )

        total_results = len(ranked)

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

    total_pages = math.ceil(total_results / RESULTS_PER_PAGE)

    years = sorted(
        {str(m["tahun"]) for m in metadata.values()},
        reverse=True
    )

    return render_template(
        "index.html",
        query=query,
        results=results,
        suggestion=suggestion,
        page=page,
        total_pages=total_pages,
        total_results=total_results,
        years=years,
        selected_year=filter_year or "all",
        sort_by=sort_by
    )


# =========================
# AUTOCOMPLETE
# =========================
AUTOCOMPLETE_TERMS = set()

for term in inverted_index.keys():
    if len(term) > 3:
        AUTOCOMPLETE_TERMS.add(term)

for m in metadata.values():
    for w in m["judul"].lower().split():
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
# ROUTE: DETAIL PAGE
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
        doc={
            **doc,
            "abstrak": abstrak_clean,
            "kata_kunci": kata_kunci
        },
        query=q
    )


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run()
