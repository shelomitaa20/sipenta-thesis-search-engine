function highlightKeywords(query) {
    if (!query) return;

    const keywords = query.toLowerCase().split(" ");
    const elements = document.querySelectorAll(".judul");

    elements.forEach(el => {
        let text = el.innerHTML;

        keywords.forEach(k => {
            if (k.length > 1) {
                const regex = new RegExp(`(${k})`, "gi");
                text = text.replace(regex, "<mark>$1</mark>");
            }
        });

        el.innerHTML = text;
    });
}