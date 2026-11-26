const promptInput = document.getElementById("promptInput");
const sendBtn = document.getElementById("sendBtn");
const conversation = document.getElementById("conversation");
const welcomeSection = document.getElementById("welcomeSection");
const quickPrompts = document.getElementById("quickPrompts");
const pageTitle = document.getElementById("pageTitle");


// Send message to Flask and receive AI response
async function sendMessage() {

    // Get user input
    const message = promptInput.value.trim();

    // Check empty input
    if (message === "") {
        alert("Please enter a message first.");
        return;
    }

    // Hide welcome screen
    welcomeSection.style.display = "none";
    quickPrompts.style.display = "none";

    // Update page title
    pageTitle.textContent = "Chat";

    // Display user message
    addMessage(message, "user");

    // Clear input
    promptInput.value = "";

    // Prevent duplicate requests while waiting
    sendBtn.disabled = true;

    // Show loading indicator
    let loadingRow = addMessage(
        "Ollama is thinking",
        "assistant loading"
    );

    try {

        // Send user prompt to Flask
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        // Receive and validate Flask response
        const rawText = await response.text();
        let data;

        try {
            data = JSON.parse(rawText);
        } catch {
            throw new Error(
                `Expected JSON from /api/chat (status ${response.status}), but received HTML/text instead.`
            );
        }

        // Check HTTP errors
        if (!response.ok) {
            throw new Error(
                data.error || "Failed to generate AI response."
            );
        }

        // Check AI response
        if (!data.reply || typeof data.reply !== "string") {
            throw new Error(
                "No AI response was received from Flask."
            );
        }

        // Remove loading indicator
        loadingRow.remove();
        loadingRow = null;

        // Display actual Ollama-generated response
        addMessage(data.reply, "assistant");

    } catch (error) {

        // Remove loading indicator
        if (loadingRow) {
            loadingRow.remove();
        }

        // Display error message
        addMessage(
            "Unable to get AI response: " + error.message,
            "assistant"
        );

        console.error("Chat error:", error);

    } finally {

        // Enable send button again
        sendBtn.disabled = false;

        // Return focus to input
        promptInput.focus();

    }
}


// Send button click
sendBtn.addEventListener("click", sendMessage);


// Enter to send, Shift + Enter for new line
promptInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }

});


// Add message to conversation
function addMessage(text, sender) {

    const messageRow = document.createElement("div");
    messageRow.className = "message " + sender;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";

    avatar.innerHTML = sender === "user"
        ? '<i class="bi bi-person"></i>'
        : '<i class="bi bi-stars"></i>';

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    // Use textContent to safely display user text
    bubble.textContent = text;

    if (sender === "user") {
        messageRow.appendChild(bubble);
        messageRow.appendChild(avatar);
    } else {
        messageRow.appendChild(avatar);
        messageRow.appendChild(bubble);
    }

    conversation.appendChild(messageRow);

    // Scroll to latest message
    messageRow.scrollIntoView({
        behavior: "smooth",
        block: "end"
    });

    // Return message row for loading indicator
    return messageRow;
}


// Quick prompt buttons
document.querySelectorAll(".quick-prompt").forEach(function (button) {

    button.addEventListener("click", function () {

        promptInput.value = button.dataset.prompt;

        promptInput.focus();
    });

});


// New chat button
document.getElementById("newChatBtn").addEventListener("click", function () {

    conversation.innerHTML = "";

    welcomeSection.style.display = "block";
    quickPrompts.style.display = "block";

    promptInput.value = "";

    pageTitle.textContent = "New chat";

    promptInput.focus();

});


// Attach file button
document.getElementById("attachBtn").addEventListener("click", function () {

    document.getElementById("fileInput").click();

});


// Show selected filename
document.getElementById("fileInput").addEventListener("change", function () {

    if (this.files.length > 0) {

        promptInput.value +=
            "\nSelected file: " + this.files[0].name;

    }

});


// Voice message demo
document.getElementById("voiceBtn").addEventListener("click", function () {

    alert("Voice message functionality will be added later.");

});


// Prompt library demo
document.getElementById("promptLibraryBtn").addEventListener("click", function () {

    alert("Your prompt library will be added later.");

});


// Load chat history from Flask / SQLite when clicking History
document.getElementById("historyBtn").addEventListener("click", async function (event) {
    event.preventDefault();

    // Update active sidebar link & title
    document.querySelectorAll(".sidebar-link").forEach(function (link) {
        link.classList.remove("active");
    });
    this.classList.add("active");
    pageTitle.textContent = "History";

    // Hide welcome and quick prompts, clear current view
    welcomeSection.style.display = "none";
    quickPrompts.style.display = "none";
    conversation.innerHTML = "";

    try {
        const response = await fetch("/api/history");
        const rawText = await response.text();
        let data;

        try {
            data = JSON.parse(rawText);
        } catch {
            throw new Error(
                `Expected JSON from /api/history (status ${response.status}), but received HTML/text instead.`
            );
        }

        if (!response.ok) {
            throw new Error(data.error || "Failed to load chat history.");
        }

        const records = Array.isArray(data.history) ? data.history.slice().reverse() : [];

        if (records.length === 0) {
            addMessage("No saved conversations found yet.", "assistant");
            return;
        }

        records.forEach(function (item) {
            addMessage(item.user_message, "user");
            addMessage(item.ai_response, "assistant");
        });
    } catch (error) {
        addMessage("Unable to load history: " + error.message, "assistant");
        console.error("History error:", error);
    }
});