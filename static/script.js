async function checkNews() {

    const newsText = document.getElementById("newsText").value.trim();
    const language = document.getElementById("language").value;

    const loading = document.getElementById("loading");
    const result = document.getElementById("result");

    result.innerHTML = "";

    if (!newsText) {
        result.innerHTML = "⚠️ Please enter some news text.";
        return;
    }

    loading.style.display = "block";

    try {

        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                news: newsText,
                language: language
            })
        });

        const data = await response.json();

        loading.style.display = "none";

        if (!response.ok) {
            result.innerHTML = "❌ " + data.error;
            return;
        }

        const fakeWords = data.fake_words
            .map(word => `<span class="word">${word}</span>`)
            .join("");

        const realWords = data.real_words
            .map(word => `<span class="word">${word}</span>`)
            .join("");

        result.innerHTML = `
            <div class="prediction">

                <div class="prediction-result">
                    ${data.result}
                </div>

                <div class="confidence">
                    Confidence: ${data.confidence}%
                </div>

                <div class="explanation">

                    <h3>🔍 Why did AI predict this?</h3>

                    <p>
                        Language: ${language}
                    </p>

                    <p>
                        Words that influenced the prediction:
                    </p>

                    <div class="important-words">

                        <strong>⚠️ Fake-related words:</strong>

                        <div class="word-list">
                            ${fakeWords || "None detected"}
                        </div>

                        <br>

                        <strong>✅ Real-related words:</strong>

                        <div class="word-list">
                            ${realWords || "None detected"}
                        </div>

                    </div>

                </div>

            </div>
        `;

    } catch (error) {

        loading.style.display = "none";

        result.innerHTML =
            "❌ Unable to connect to the AI server.";

        console.error(error);
    }
}