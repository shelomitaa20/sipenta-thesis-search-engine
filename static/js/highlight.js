function highlightKeywords(query) {
    if (!query) return;

    const keywords = query.toLowerCase().split(/\s+/).filter(k => k.length > 1);
    const elements = document.querySelectorAll(".judul");

    elements.forEach(el => {
        let text = el.textContent || el.innerText;

        keywords.forEach(k => {
            if (k.length > 1) {
                const regex = new RegExp(`(${escapeRegExp(k)})`, "gi");
                text = text.replace(regex, "<span class='highlight'>$1</span>");
            }
        });

        el.innerHTML = text;
    });
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}