// --- Seasonal Color Analysis Data ---
const SEASONAL_DATA = {
    "Spring": {
        "description": "Warm, clear, and light tones. Spring types glow in fresh, bright hues like peach, coral, and golden yellows.",
        "colors": ["#FFDAB9", "#FFE4B5", "#FA8072", "#FFFACD", "#F0E68C", "#F5DEB3", "#FAD6A5", "#FFC0CB", "#E6E200", "#FFD700", "#E9967A", "#FFA07A", "#F08080", "#FFB347", "#FFDAB9", "#D8BFD8", "#FFF8DC", "#FFEBCD", "#FF69B4", "#FF7F50"],
        "avoid_colors": ["#000000", "#808080", "#2F4F4F", "#5F9EA0", "#8A2BE2", "#4B0082", "#191970", "#708090", "#1C1C1C", "#A9A9A9"],
        "makeup": { "lip": ["coral", "peach", "warm pink"], "eyes": ["gold", "champagne", "soft brown"], "blush": ["apricot", "peach"] },
        "fabrics": ["cotton", "linen", "light silk", "chiffon"],
        "tone_contrast": "Low to medium",
        "looks": { "name": "Fresh Spring Collection", "images": ["/static/images/Spring_1.png", "/static/images/Spring_2.png", "/static/images/Spring_3.png", "/static/images/Spring_4.png"] },
        "grooming_tips": ["Use light, fresh scents.", "Keep hair natural and airy.", "Avoid heavy dark hairstyles.", "Minimal beard styling works best.", "Opt for subtle, fresh accessories.", "Light nail care and natural polish."]
    },
    "Summer": {
        "description": "Soft, cool, and muted tones. Summers shine in pastels, rose, and misty blues.",
        "colors": ["#ADD8E6", "#FFB6C1", "#E6E6FA", "#B0C4DE", "#D8BFD8", "#AFEEEE", "#87CEFA", "#BA55D3", "#DB7093", "#BFEFFF", "#F0F8FF", "#C1CDCD", "#D3D3D3", "#DDA0DD", "#F4A7B9", "#C6E2FF", "#B0E0E6", "#E0FFFF", "#F5F5F5", "#EED5D2"],
        "avoid_colors": ["#FFA500", "#FF0000", "#FFD700", "#A52A2A", "#8B0000", "#FF8C00", "#FF4500", "#DAA520", "#B22222", "#CD5C5C"],
        "makeup": { "lip": ["soft rose", "mauve", "raspberry"], "eyes": ["cool taupe", "lavender", "gray"], "blush": ["soft pink", "rose"] },
        "fabrics": ["cotton voile", "crepe", "cashmere", "brushed cotton"],
        "tone_contrast": "Low contrast",
        "looks": { "name": "Cool Summer Collection", "images": ["/static/images/Summer_1.png", "/static/images/Summer_2.png", "/static/images/Summer_3.png", "/static/images/Summer_4.png"] },
        "grooming_tips": ["Soft, pastel-friendly hairstyles.", "Use cool-toned colognes.", "Keep facial hair light and neat.", "Minimalist watches and accessories.", "Light moisturizers for summer skin.", "Pastel ties or pocket squares for style."]
    },
    "Autumn": {
        "description": "Rich, warm, and earthy tones. Autumns glow in rust, olive, mustard, and terracotta.",
        "colors": ["#D2691E", "#CD853F", "#808000", "#BDB76B", "#A0522D", "#8B4513", "#DAA520", "#BC8F8F", "#D2B48C", "#DEB887", "#C68642", "#FF8C00", "#F4A460", "#FFD700", "#E9967A", "#8B0000", "#A52A2A", "#C04000", "#C19A6B", "#9B7653"],
        "avoid_colors": ["#00CED1", "#00FFFF", "#E0FFFF", "#1E90FF", "#B0E0E6", "#87CEFA", "#4682B4", "#7B68EE", "#4169E1", "#0000FF"],
        "makeup": { "lip": ["brick red", "terracotta", "warm berry"], "eyes": ["bronze", "olive", "warm brown"], "blush": ["burnt apricot", "rust"] },
        "fabrics": ["wool", "suede", "tweed", "denim", "corduroy"],
        "tone_contrast": "Medium to high",
        "looks": { "name": "Earthy Autumn Collection", "images": ["/static/images/Aut_1.png", "/static/images/Aut_2.png", "/static/images/Aut_3.png", "/static/images/Aut_4.png"] },
        "grooming_tips": ["Warm hair highlights or tones.", "Beard oils for earthy look.", "Use rich fragrances.", "Structured hairstyles preferred.", "Layered clothing enhances the earthy palette.", "Dark nail polish optional for fashion-forward."]
    },
    "Winter": {
        "description": "Cool, bold, and dramatic tones. Winters dazzle in black, icy shades, and jewel tones.",
        "colors": ["#4682B4", "#8A2BE2", "#DC143C", "#00008B", "#2F4F4F", "#800000", "#000080", "#8B008B", "#483D8B", "#6A5ACD", "#5F9EA0", "#00CED1", "#6495ED", "#B0C4DE", "#1E90FF", "#708090", "#C0C0C0", "#778899", "#4169E1", "#191970"],
        "avoid_colors": ["#FFDAB9", "#FFE4B5", "#FAFAD2", "#F5DEB3", "#FFFACD", "#FAD6A5", "#FFDEAD", "#FFF8DC", "#FFFFE0", "#FDF5E6"],
        "makeup": { "lip": ["deep red", "fuchsia", "plum"], "eyes": ["charcoal", "silver", "cool black"], "blush": ["berry", "cool pink"] },
        "fabrics": ["satin", "silk", "velvet", "leather", "structured cotton"],
        "tone_contrast": "High contrast",
        "looks": { "name": "Dramatic Winter Collection", "images": ["/static/images/Winter_1.png", "/static/images/Winter_2.png", "/static/images/Winter_3.png", "/static/images/Winter_4.png"] },
        "grooming_tips": ["Bold hairstyles, sharp cuts.", "Use striking colognes.", "Well-groomed beard styles.", "Structured and tailored outfits.", "Leather gloves or belts for accessories.", "Moisturize skin in cold weather."]
    }
};

// Fixed questions for the chatbot to recognize
const FIXED_QUESTIONS = [
    "How is skin color used in color analysis?",
    "What are the best colors for a Spring tone?",
    "What makeup works for a Summer tone?",
    "Which fabrics suit the Autumn palette?",
    "What should a Winter tone avoid?",
    "Show me looks for the Dramatic Winter Collection.",
    "how is skin color calculated",
    "what is lab",
    "how is contrast measured",
    "how to find my undertone",
    "what is the 12 season system",
    "what is color draping",
    "best jewelry for cool tone"
];


// --- Helper Functions ---

/**
 * Appends a message to the chat window.
 * @param {string} sender - 'user' or 'bot'.
 * @param {string} text - The message text.
 * @param {string} [imagesHtml=''] - HTML string for image previews.
 */
function appendMessage(sender, text, imagesHtml = '') {
    const chat = document.getElementById("chatMessages");
    const msg = document.createElement("div");
    msg.className = "message " + sender;
    msg.innerHTML = `<p>${text}</p>${imagesHtml}`;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
}

/**
 * Creates and appends the initial bot message with suggestions.
 */
function showInitialMessage() {
    const welcome = "Hello! I'm StyleMate, your personal AI fashion assistant. I can help you with seasonal color analysis and style tips. Try one of the questions below!";
    
    // HTML structure for suggestions
    let suggestionsHtml = `
        <div class="suggestions">
            <h3>Quick Questions:</h3>
            <div class="suggestion-list">
    `;
    
    FIXED_QUESTIONS.slice(0, 15).forEach(q => { // Show first 5 questions as buttons
        suggestionsHtml += `<button class="suggest-btn" onclick="useSuggestion('${q.replace(/'/g, "\\'")}')">${q}</button>`;
    });

    suggestionsHtml += `
            </div>
        </div>
    `;

    // Append the welcome message and suggestions to the chat
    appendMessage("bot", welcome + suggestionsHtml);
}

/**
 * Handles the Enter key press in the input field.
 * @param {Event} event - The keyboard event.
 */
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// --- Main Chat Logic ---

function toggleChat() {
    const chatPopup = document.getElementById("chatPopup");
    const isVisible = chatPopup.style.display === "flex";
    
    chatPopup.style.display = isVisible ? "none" : "flex";
    chatPopup.style.flexDirection = "column";

    // Show initial message and suggestions only when opening the chat
    if (!isVisible) {
        const chatMessages = document.getElementById("chatMessages");
        // Clear previous messages if re-opening (optional, but good for fresh start)
        chatMessages.innerHTML = ''; 
        showInitialMessage();
    }
}

function useSuggestion(text) {
    document.getElementById("userInput").value = text;
    sendMessage(); 
}

function sendMessage() {
    const input = document.getElementById("userInput");
    const userMessage = input.value.trim();
    if (userMessage === "") return;

    appendMessage("user", userMessage);
    input.value = "";

    // Simulate thinking time
    setTimeout(() => {
        const botReply = getBotResponse(userMessage);
        appendMessage("bot", botReply.text, botReply.images);
    }, 500);
}

/**
 * Determines the bot's response based on the user's message.
 * @param {string} message - The user's input message.
 * @returns {{text: string, images: string}} - The bot's response text and image HTML.
 */
function getBotResponse(message) {
    const lowerMessage = message.toLowerCase();
    let responseText = "I'm sorry, I currently only have information on seasonal color analysis. Please try asking one of the suggested questions.";
    let imagesHtml = "";

    // Find a matching season (case-insensitive) for the dynamic search at the end
    const seasonMatch = Object.keys(SEASONAL_DATA).find(
        s => lowerMessage.includes(s.toLowerCase())
    );

    // --- Combined & Prioritized Fixed Question Handling ---

    // 1. Technical / Advanced Questions (Highest Priority)
    if (lowerMessage.includes("skin color calculated")) {
        responseText = "We sample **RGB** values from the selected skin region, then convert them to **CIELAB** (L*a*b*) using OpenCV. LAB is used because it models human color perception better than RGB. ";

// [Image of CIELAB color space diagram]
// ";
    } else if (lowerMessage.includes("what is lab")) {
        responseText = "**LAB** is a perceptual color space: **L** = lightness/value (0=black, 100=white), **a** = green-red axis, **b** = blue-yellow axis. We use LAB for color accuracy and precise palette matching.";
    } else if (lowerMessage.includes("palette generated")) {
        responseText = "The palette is generated from your LAB values, mapped to seasonal categories (Spring, Summer, Autumn, Winter). Then, curated colors and harmonious LAB shifts are applied to create your custom swatch set.";
    } else if (lowerMessage.includes("predict season")) {
        responseText = "Season prediction compares the **LAB values** of your skin, hair, and eye color against known seasonal undertone patterns (e.g., Cool/Warm, Light/Dark, Clear/Muted).";
    } else if (lowerMessage.includes("how is contrast measured")) {
        responseText = "Contrast is measured by the **Value Contrast** (difference in the L* value, or lightness) between your hair, skin, and eyes. High contrast (like Winter) means large differences. ";
    } else if (lowerMessage.includes("what is tone in color analysis")) {
        responseText = "**Tone** in color analysis refers to the **purity** of a color, often described as its **Chroma** or **Intensity**. Pure (clear) colors have high chroma, while muted (soft) colors have low chroma (as if gray was added).";
    } else if (lowerMessage.includes("12 season system")) {
        responseText = "The **12-Tone System** refines the 4 seasons by adding **sub-seasons** (e.g., Light Spring, Soft Autumn, Bright Winter). It provides a much more precise palette by focusing on your dominant color characteristic.";
    } else if (lowerMessage.includes("tonal system")) {
        responseText = "The **Tonal System** (or 6 Tones) ignores the seasons and classifies you based on your **dominant characteristic**—**Deep, Light, Warm, Cool, Clear, or Soft**. This works for those who don't fit neatly into a single season.";
    } else if (lowerMessage.includes("color draping")) {
        responseText = "**Color Draping** is the traditional consultation method where colored fabric swatches are held under a person's face to visually determine which colors make the skin look clearer and healthier.";
    } else if (lowerMessage.includes("how to find my undertone")) {
        responseText = "You can manually check your veins: **Blue/Purple** veins suggest **Cool** undertones, **Green** suggests **Warm** undertones, and a mix suggests **Neutral**. StyleMate's analysis is a more precise, digital method. ";
    } else if (lowerMessage.includes("best jewelry for cool tone") || lowerMessage.includes("silver")) {
        responseText = "**Cool** tones generally look best in **silver**, **platinum**, or **white gold**, as these cool metals harmonize with the pink or blue undertones in the skin.";
    } else if (lowerMessage.includes("best jewelry for warm tone") || lowerMessage.includes("gold")) {
        responseText = "**Warm** tones generally look best in **yellow gold** or **copper**, as the warm metal complements the golden or peachy undertones in the skin.";
    } else if (lowerMessage.includes("complementary colors")) {
        responseText = "**Complementary colors** are opposites on the color wheel (e.g., Red and Green). Wearing them together creates the **highest visual contrast** and makes both colors look more vibrant.";

    } else if (lowerMessage.includes("accuracy")) {
        responseText = "Accuracy depends heavily on **lighting** (natural light is best) and proper color swatch selection on the screen. **Consistency** across multiple readings improves reliability.";
    }
    
    // 2. Original General Seasonal Questions (Second Priority)
    else if (lowerMessage.includes("best colors for a spring tone")) {
        const data = SEASONAL_DATA.Spring;
        responseText = `For a **Spring** tone, the best colors are **${data.description.split('. ')[0]}**. Recommended colors include: ${data.colors.slice(0, 5).map(c => `<span style="color: ${c}; font-weight: bold;">${c}</span>`).join(', ')} and many others.`;
    } else if (lowerMessage.includes("makeup works for a summer tone")) {
        const data = SEASONAL_DATA.Summer.makeup;
        responseText = `A **Summer** tone should opt for soft, cool, and muted makeup. Try **Lip**: ${data.lip.join(', ')}. **Eyes**: ${data.eyes.join(', ')}. **Blush**: ${data.blush.join(', ')}.`;
    } else if (lowerMessage.includes("fabrics suit the autumn palette")) {
        const data = SEASONAL_DATA.Autumn;
        responseText = `The **Autumn** palette is complemented by rich, earthy textures. Suitable fabrics include: **${data.fabrics.join(', ')}**. These materials match the medium to high tone contrast of the season.`;
    } else if (lowerMessage.includes("what should a winter tone avoid")) {
        const data = SEASONAL_DATA.Winter;
        const avoidExample = data.avoid_colors.slice(0, 3).join(', ');
        responseText = `A **Winter** tone should avoid soft, light, and overly warm colors like ${avoidExample}. Stick to **cool, bold, and dramatic tones** for the best effect.`;
    } else if (lowerMessage.includes("show me looks for the dramatic winter collection")) {
        const data = SEASONAL_DATA.Winter;
        responseText = `Here are some looks from the **${data.looks.name}** to inspire your style:`;
        imagesHtml = `<div class="bot-images">${data.looks.images.map(src => `<img src="${src}" alt="Winter Collection Look">`).join('')}</div>`;
    } else if (lowerMessage.includes("skin color used in color analysis")) {
         responseText = "Skin tone is a primary factor in **Seasonal Color Analysis**, which determines if a person has a **Warm** (Spring, Autumn) or **Cool** (Summer, Winter) **undertone**. This undertone guides the selection of colors that complement and illuminate the skin, making you 'glow.' The final seasonal palette also considers factors like hair and eye color.";
    }

    // 3. Dynamic Season Data Search (Lowest Priority - runs only if no specific match above)
    else if (seasonMatch) {
        const season = seasonMatch;
        const data = SEASONAL_DATA[season];
        
        let detail = "";
        if (lowerMessage.includes("colors") || lowerMessage.includes("palette")) {
             detail = `Your recommended colors are: ${data.colors.slice(0, 7).map(c => `<span style="color: ${c}; font-weight: bold;">${c}</span>`).join(', ')}...`;
        } else if (lowerMessage.includes("makeup")) {
            detail = `Recommended makeup: **Lip**: ${data.makeup.lip.join(', ')}. **Eyes**: ${data.makeup.eyes.join(', ')}. **Blush**: ${data.makeup.blush.join(', ')}.`;
        } else if (lowerMessage.includes("grooming") || lowerMessage.includes("tips")) {
            detail = `Grooming tips: ${data.grooming_tips.join(' / ')}`;
        } else {
             // Default season description
             detail = `${data.description} Your tone contrast is **${data.tone_contrast}**.`;
        }

        responseText = `**${season} Tone Analysis:** ${detail}`;
    }

    return { text: responseText, images: imagesHtml };
}
// Ensure the initial message shows up when the chat popup is opened for the first time
document.addEventListener('DOMContentLoaded', () => {
    // This is handled inside toggleChat now, but keeping this listener is a good practice.
});