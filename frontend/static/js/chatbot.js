
  function toggleChat() {
    var chatPopup = document.getElementById("chatPopup");
    chatPopup.style.display = chatPopup.style.display === "flex" ? "none" : "flex";
    chatPopup.style.flexDirection = "column";
  }

  function sendMessage() {
    var input = document.getElementById("userInput");
    var message = input.value.trim();
    if (message === "") return;

    appendMessage("user", message);
    input.value = "";

    // Fake bot reply (replace this with API call)
    setTimeout(() => {
      appendMessage("bot", "This is a sample reply.");
    }, 500);
  }

  function appendMessage(sender, text) {
    var chat = document.getElementById("chatMessages");
    var msg = document.createElement("div");
    msg.className = "message " + sender;
    msg.innerText = text;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
  }

  // function goToHistory() {
  //   window.location.href = "history.html";
  // }