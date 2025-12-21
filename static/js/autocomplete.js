const input = document.getElementById("searchInput");
const suggestionBox = document.getElementById("suggestions");

input.addEventListener("keyup", async () => {
    const q = input.value;
    if (q.length < 2) {
        suggestionBox.innerHTML = "";
        return;
    }

    const res = await fetch(`/autocomplete?q=${encodeURIComponent(q)}`);
    const data = await res.json();

    suggestionBox.innerHTML = "";

    data.forEach(item => {
        const div = document.createElement("div");
        div.textContent = item;

        div.onclick = () => {
            const words = input.value.trim().split(" ");
            words.pop();          // hapus kata terakhir
            words.push(item);     // ganti dengan suggestion
            input.value = words.join(" ");
            suggestionBox.innerHTML = "";
        };

        suggestionBox.appendChild(div);
    });
});

// klik di luar → suggestion hilang
document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-wrapper")) {
        suggestionBox.innerHTML = "";
    }
});