let selectedMap = null;

const maps = document.querySelectorAll(".map-item");
const okBtn = document.getElementById("okBtn");

maps.forEach(map => {
    map.addEventListener("click", () => {
        // reset semua
        maps.forEach(m => m.classList.remove("selected"));

        // tandai yang dipilih
        map.classList.add("selected");
        selectedMap = map.dataset.map;
    });
});

okBtn.addEventListener("click", () => {
    if (!selectedMap) {
        alert("Pilih map terlebih dahulu!");
        return;
    }

    localStorage.setItem("selectedMap", selectedMap);
    window.location.href = "game.html";
});

