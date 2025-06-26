
document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("imageCanvas");
    const ctx = canvas.getContext("2d");
    const image = new Image();
    const instructions = document.getElementById("instructions");

    const swatches = [
        { id: "hairPoint", label: "Hair", color: "red", x: 100, y: 100 },
        { id: "eyePoint", label: "Eye", color: "green", x: 150, y: 150 },
        { id: "skinPoint", label: "Skin", color: "blue", x: 200, y: 200 },
    ];

    const radius = 20;
    let draggingIndex = null;

    const uploadInput = document.getElementById("upload");
    const canvasCard = document.getElementById("canvas-card");

    uploadInput.addEventListener("change", function () {
        const file = uploadInput.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (e) {
            image.onload = function () {
                canvas.width = image.width;
                canvas.height = image.height;
                canvasCard.style.display = "block";
                draw();
            };
            image.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 0, 0);

        swatches.forEach((s, index) => {
            // Swatch circle
            ctx.beginPath();
            ctx.arc(s.x, s.y, radius, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
            ctx.fill();
            ctx.strokeStyle = s.color;
            ctx.lineWidth = 3;
            ctx.stroke();

            // Label
            ctx.fillStyle = s.color;
            ctx.font = "bold 13px Arial";
            ctx.fillText(s.label, s.x + radius + 4, s.y + 4);
        });
    }

    function isInsideSwatch(x, y, swatch) {
        const dx = x - swatch.x;
        const dy = y - swatch.y;
        return Math.sqrt(dx * dx + dy * dy) < radius;
    }

    canvas.addEventListener("mousedown", function (e) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        draggingIndex = swatches.findIndex(s => isInsideSwatch(x, y, s));
    });

    canvas.addEventListener("mousemove", function (e) {
        if (draggingIndex === null) return;

        const rect = canvas.getBoundingClientRect();
        swatches[draggingIndex].x = e.clientX - rect.left;
        swatches[draggingIndex].y = e.clientY - rect.top;

        draw();
    });

    canvas.addEventListener("mouseup", function () {
        if (draggingIndex !== null) {
            const s = swatches[draggingIndex];
            document.getElementById(s.id).value = `${Math.round(s.x)},${Math.round(s.y)}`;
        }
        draggingIndex = null;
    });

    canvas.addEventListener("mouseleave", () => draggingIndex = null);
});