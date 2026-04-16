async function postData(url = "", data = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    return response.json(); // Will return { answer: "..." }
}

document.getElementById("sendButton").addEventListener("click", async () => {
    const inputField = document.getElementById("questionInput");
    const question = inputField.value.trim();
    inputField.value = "";

    if (!question) return;

    // Show right2 and hide right1
    document.querySelector(".right2").style.display = "block";
    document.querySelector(".right1").style.display = "none";

    document.getElementById("question1").innerText = question;
    document.getElementById("question2").innerText = question;

    try {
        const data = await postData("/api", { question });

        // FIX: Check if data.answer exists
        if (data.answer) {
            document.getElementById("solution").innerText = data.answer;
        } else {
            document.getElementById("solution").innerText = "No answer found.";
            console.error("No answer received:", data);
        }
    } catch (err) {
        console.error("Fetch error:", err);
        document.getElementById("solution").innerText = "Error occurred!";
    }
});