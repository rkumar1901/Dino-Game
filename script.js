const dino = document.getElementById("dino");
const cactus = document.getElementById("cactus");
const scoreDisplay = document.getElementById("score");
let score = 0;

function jump() {
    if (!dino.classList.contains("jump")) {
        dino.classList.add("jump");
        setTimeout(() => dino.classList.remove("jump"), 300);
    }
}

document.addEventListener("keydown", (event) => {
    if (event.code === "Space" || event.code === "ArrowUp") {
        jump();
    }
});

let isAlive = setInterval(() => {
    let dinoBottom = parseInt(window.getComputedStyle(dino).getPropertyValue("bottom"));
    let cactusLeft = parseInt(window.getComputedStyle(cactus).getPropertyValue("left"));

    // Basic scoring
    if (cactusLeft < 0) {
        score++;
        scoreDisplay.innerText = "Score: " + Math.floor(score / 10);
    }

    // Collision detection
    if (cactusLeft > 50 && cactusLeft < 90 && dinoBottom <= 40) {
        alert("Game Over! Your Score: " + Math.floor(score / 10));
        score = 0;
    }
}, 10);
