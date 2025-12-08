 // Dummy history data (replace with real data from backend)
 const history = [
    { sender: "user", text: "Hello" },
    { sender: "bot", text: "Hi, how can I help you?" },
    { sender: "user", text: "Tell me about your services." },
    { sender: "bot", text: "We offer AI-based solutions and support." },
  ];

  function loadHistory() {
    let historyDiv = document.getElementById("chatHistory");
    history.forEach(msg => {
      let div = document.createElement("div");
      div.className = "message " + msg.sender;
      div.innerText = msg.text;
      historyDiv.appendChild(div);
    });
  }

  loadHistory();

  