const words = document.querySelectorAll('.word');
words.forEach((word, index) => {
    word.style.animationDelay = `${index * 0.5}s`;
});