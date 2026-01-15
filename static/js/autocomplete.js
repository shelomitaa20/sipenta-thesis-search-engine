const input = document.getElementById("searchInput");
const suggestionBox = document.getElementById("suggestions");

if (input && suggestionBox) {
    input.addEventListener("input", async () => {
        const q = input.value.trim();
        if (q.length < 2) {
            suggestionBox.classList.add("hidden");
            suggestionBox.innerHTML = "";
            return;
        }

        try {
            const res = await fetch(`/autocomplete?q=${encodeURIComponent(q)}`);
            const data = await res.json();

            suggestionBox.innerHTML = "";

            if (data.length === 0) {
                suggestionBox.classList.add("hidden");
                return;
            }

            data.forEach(item => {
                const div = document.createElement("div");
                div.textContent = item;
                div.classList.add(
                    "px-6", "py-3", "cursor-pointer", 
                    "hover:bg-blue-50", "transition", 
                    "border-b", "border-gray-100", 
                    "last:border-b-0", "text-gray-800"
                );

                div.addEventListener("click", (e) => {
                    e.preventDefault();
                    e.stopPropagation();

                    const words = input.value.trim().split(/\s+/);
                    words.pop();
                    words.push(item);
                    input.value = words.join(" ") + " ";
                    suggestionBox.classList.add("hidden");
                    suggestionBox.innerHTML = "";
                    input.focus();
                });

                suggestionBox.appendChild(div);
            });

            suggestionBox.classList.remove("hidden");
        } catch (err) {
            console.error("Autocomplete error:", err);
            suggestionBox.classList.add("hidden");
        }
    });

    // Sembunyikan saat klik di luar
    document.addEventListener("click", () => {
        suggestionBox.classList.add("hidden");
    });

    // Jangan tutup saat klik di dalam suggestions atau input
    suggestionBox.addEventListener("click", (e) => {
        e.stopPropagation();
    });

    input.addEventListener("click", (e) => {
        e.stopPropagation();
        if (suggestionBox.children.length > 0) {
            suggestionBox.classList.remove("hidden");
        }
    });
}