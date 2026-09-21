async function checkNews() {

    const newsText = document.getElementById("newsText").value.trim();
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");

    // Clear previous result
    result.innerHTML = "";

    // Check empty input
    if (!newsText) {
        result.innerHTML = "⚠️ Please enter some news text.";
        return;
    }

    // Show loading
    loading.style.display = "block";

    try {

        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                news: newsText
            })
        });

        const data = await response.json();

        loading.style.display = "none";

        if (!response.ok) {
            result.innerHTML = "❌ " + data.error;
            return;
        }

        // Display prediction
        result.innerHTML = `
            <div class="prediction">
                <div class="prediction-result">
                    ${data.result}
                </div>

                <div class="confidence">
                    Confidence: ${data.confidence}%
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