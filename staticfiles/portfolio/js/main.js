(function () {
    const html = document.documentElement;
    const body = document.body;
    const themeSelect = document.getElementById("theme-select");
    const darkToggle = document.getElementById("dark-mode-toggle");
    const yearSpan = document.getElementById("year");
    const iranTimeSpan = document.getElementById("iran-time");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatLog = document.getElementById("chat-log");

    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    const savedTheme = localStorage.getItem("theme") || "ocean";
    const savedDark = localStorage.getItem("dark") === "true";

    html.setAttribute("data-theme", savedTheme);
    if (themeSelect) themeSelect.value = savedTheme;

    if (savedDark) {
        body.classList.add("dark");
        if (darkToggle) darkToggle.checked = true;
    }

    if (themeSelect) {
        themeSelect.addEventListener("change", (e) => {
            const theme = e.target.value;
            html.setAttribute("data-theme", theme);
            localStorage.setItem("theme", theme);
        });
    }

    if (darkToggle) {
        darkToggle.addEventListener("change", (e) => {
            if (e.target.checked) {
                body.classList.add("dark");
                localStorage.setItem("dark", "true");
            } else {
                body.classList.remove("dark");
                localStorage.setItem("dark", "false");
            }
        });
    }

    function updateIranTime() {
        if (!iranTimeSpan) return;
        const now = new Date();
        const options = {
            timeZone: "Asia/Tehran",
            hour12: false,
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        };
        iranTimeSpan.textContent = now.toLocaleString("fa-IR", options);
    }
    setInterval(updateIranTime, 1000);
    updateIranTime();

    // Gemini chatbot frontend – expects a separate Flask backend at /gemini/api/chat or similar
    function appendMessage(text, who) {
        if (!chatLog) return;
        const div = document.createElement("div");
        div.className = who === "user" ? "msg-user" : "msg-bot";
        div.textContent = text;
        chatLog.appendChild(div);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    if (chatForm && chatInput && chatLog) {
        chatForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const msg = chatInput.value.trim();
            if (!msg) return;
            appendMessage(msg, "user");
            chatInput.value = "";

            fetch("http://127.0.0.1:5000/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: msg })
            })


            .then(r => r.json())
            .then(data => {
                appendMessage(data.reply || "[no reply]", "bot");
            })
            .catch(() => {
                appendMessage("خطا در ارتباط با بک‌اند Gemini.", "bot");
            });
        });
    }
})();
