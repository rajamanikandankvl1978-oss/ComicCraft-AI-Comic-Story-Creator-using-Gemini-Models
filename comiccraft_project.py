# ============================================================
# ComicCraft - AI Comic Story Creator using Gemini Models
# SINGLE-FILE PROJECT BUNDLE
# ============================================================
# This file contains the complete project. Save it as:
# comiccraft_project.py
#
# Run:
#   python comiccraft_project.py
#
# Then open:
#   http://127.0.0.1:5000
#
# Install:
#   pip install flask python-dotenv google-generativeai
#
# Create .env in the same folder:
#   GEMINI_API_KEY=YOUR_GEMINI_API_KEY
#
# ============================================================

import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

# Gemini SDK
try:
    import google.generativeai as genai
except ImportError:
    genai = None

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY", "")
if genai and API_KEY:
    genai.configure(api_key=API_KEY)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# ============================================================
# GEMINI SERVICE
# ============================================================

def generate_with_gemini(prompt):
    if not API_KEY:
        return {
            "error": "GEMINI_API_KEY is missing. Create a .env file and add your Gemini API key."
        }

    if not genai:
        return {
            "error": "google-generativeai is not installed. Run: pip install google-generativeai"
        }

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = getattr(response, "text", "") or ""

        if not text.strip():
            return {"error": "Gemini returned an empty response."}

        return {"text": text.strip()}

    except Exception as exc:
        return {"error": f"Gemini API error: {exc}"}


def create_story_prompt(data):
    idea = data.get("idea", "").strip()
    genre = data.get("genre", "Adventure")
    style = data.get("style", "Modern Comic")
    tone = data.get("tone", "Exciting")
    scenes = data.get("scenes", 6)
    characters = data.get("characters", "").strip()

    return f"""
You are ComicCraft, an expert comic-book writer.

Create a complete comic story from the user's idea.

USER IDEA:
{idea}

GENRE:
{genre}

COMIC STYLE:
{style}

TONE:
{tone}

NUMBER OF SCENES:
{scenes}

USER CHARACTERS:
{characters if characters else "Create suitable characters yourself."}

Return the answer using exactly this structure:

TITLE:
<short creative title>

LOGLINE:
<one sentence>

CHARACTERS:
1. Name - role - personality - appearance
2. Name - role - personality - appearance

SCENES:
SCENE 1:
Description:
<visual description>

Caption:
<narration>

Dialogue:
Character: "dialogue"

Image Prompt:
<detailed visual prompt for the comic panel>

Repeat for every scene.

ENDING:
<short satisfying ending>

Keep the story original, coherent, family-friendly, and visually descriptive.
"""

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


@app.route("/create")
def create():
    return render_template_string(HTML_PAGE)


@app.route("/generate-story", methods=["POST"])
def generate_story():
    data = request.get_json(silent=True) or {}

    if not data.get("idea", "").strip():
        return jsonify({"error": "Please enter a story idea."}), 400

    result = generate_with_gemini(create_story_prompt(data))

    if "error" in result:
        return jsonify(result), 500

    return jsonify({
        "success": True,
        "story": result["text"]
    })


@app.route("/generate-character", methods=["POST"])
def generate_character():
    data = request.get_json(silent=True) or {}
    description = data.get("description", "").strip()

    if not description:
        return jsonify({"error": "Enter a character description."}), 400

    prompt = f"""
Create a detailed comic-book character based on:

{description}

Return:
Name:
Role:
Age:
Personality:
Appearance:
Clothing:
Abilities:
Strength:
Weakness:
Character Arc:
Comic Visual Prompt:
"""

    result = generate_with_gemini(prompt)

    if "error" in result:
        return jsonify(result), 500

    return jsonify({"success": True, "character": result["text"]})


@app.route("/generate-scene", methods=["POST"])
def generate_scene():
    data = request.get_json(silent=True) or {}
    description = data.get("description", "").strip()

    if not description:
        return jsonify({"error": "Enter a scene description."}), 400

    prompt = f"""
Create one detailed comic panel from this scene:

{description}

Return:
Scene Description:
Caption:
Characters:
Dialogue:
Action:
Camera Angle:
Lighting:
Comic Image Prompt:
"""

    result = generate_with_gemini(prompt)

    if "error" in result:
        return jsonify(result), 500

    return jsonify({"success": True, "scene": result["text"]})


@app.route("/regenerate", methods=["POST"])
def regenerate():
    data = request.get_json(silent=True) or {}
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"error": "Nothing to regenerate."}), 400

    prompt = f"""
Rewrite and improve the following comic content.
Keep the same core meaning but make it more exciting,
visual, natural, and suitable for a comic.

CONTENT:
{content}
"""

    result = generate_with_gemini(prompt)

    if "error" in result:
        return jsonify(result), 500

    return jsonify({"success": True, "content": result["text"]})


# ============================================================
# FRONTEND
# ============================================================

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ComicCraft - AI Comic Story Creator</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background:
        radial-gradient(circle at top left, #3b1b69 0, transparent 35%),
        radial-gradient(circle at bottom right, #142b63 0, transparent 35%),
        #080b18;
    color: #fff;
    min-height: 100vh;
}

.container {
    width: min(1100px, 94%);
    margin: auto;
}

header {
    text-align: center;
    padding: 45px 15px 25px;
}

.logo {
    font-size: 48px;
    font-weight: 900;
    letter-spacing: 1px;
}

.logo span {
    color: #ffcc33;
}

.subtitle {
    color: #c8c9d7;
    font-size: 18px;
    margin-top: 8px;
}

.card {
    background: rgba(20, 24, 48, 0.92);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 22px;
    padding: 28px;
    margin-bottom: 24px;
    box-shadow: 0 18px 50px rgba(0,0,0,.3);
}

h2 {
    margin-top: 0;
}

label {
    display: block;
    margin: 15px 0 7px;
    font-weight: bold;
}

textarea, input, select {
    width: 100%;
    border: 1px solid #41486b;
    background: #0d1124;
    color: white;
    padding: 13px;
    border-radius: 12px;
    outline: none;
    font-size: 15px;
}

textarea:focus, input:focus, select:focus {
    border-color: #ffcc33;
}

textarea {
    min-height: 125px;
    resize: vertical;
}

.grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
}

button {
    border: 0;
    border-radius: 12px;
    padding: 13px 20px;
    margin-top: 18px;
    cursor: pointer;
    font-weight: 800;
    font-size: 15px;
    background: #ffcc33;
    color: #171717;
}

button:hover {
    transform: translateY(-1px);
    opacity: .92;
}

.secondary {
    background: #303752;
    color: white;
}

.result {
    white-space: pre-wrap;
    line-height: 1.7;
    background: #0a0d1b;
    border-radius: 15px;
    padding: 22px;
    border: 1px solid #303752;
    min-height: 150px;
}

.loading {
    display: none;
    color: #ffcc33;
    margin-top: 15px;
    font-weight: bold;
}

.error {
    color: #ff7c7c;
    margin-top: 15px;
    white-space: pre-wrap;
}

.success {
    color: #75e6a5;
    margin-top: 15px;
}

footer {
    text-align: center;
    padding: 25px;
    color: #9699aa;
}

@media(max-width: 700px) {
    .grid {
        grid-template-columns: 1fr;
    }

    .logo {
        font-size: 36px;
    }

    .card {
        padding: 20px;
    }
}
</style>
</head>

<body>

<div class="container">

<header>
    <div class="logo">🎨 <span>ComicCraft</span></div>
    <div class="subtitle">
        AI Comic Story Creator powered by Gemini
    </div>
</header>

<section class="card">
    <h2>🚀 Create Your Comic</h2>

    <label>Story Idea</label>
    <textarea id="idea"
        placeholder="Example: A college student discovers a mysterious robot hidden beneath his campus..."></textarea>

    <div class="grid">

        <div>
            <label>Genre</label>
            <select id="genre">
                <option>Adventure</option>
                <option>Fantasy</option>
                <option>Science Fiction</option>
                <option>Superhero</option>
                <option>Mystery</option>
                <option>Comedy</option>
                <option>Horror</option>
                <option>Romance</option>
            </select>
        </div>

        <div>
            <label>Comic Style</label>
            <select id="style">
                <option>Modern Comic</option>
                <option>Superhero Comic</option>
                <option>Manga</option>
                <option>Cartoon</option>
                <option>Fantasy Comic</option>
                <option>Cyberpunk Comic</option>
            </select>
        </div>

        <div>
            <label>Tone</label>
            <select id="tone">
                <option>Exciting</option>
                <option>Funny</option>
                <option>Dramatic</option>
                <option>Mysterious</option>
                <option>Emotional</option>
                <option>Dark</option>
            </select>
        </div>

        <div>
            <label>Number of Scenes</label>
            <select id="scenes">
                <option value="4">4</option>
                <option value="6" selected>6</option>
                <option value="8">8</option>
                <option value="10">10</option>
            </select>
        </div>

    </div>

    <label>Characters (optional)</label>
    <input id="characters"
        placeholder="Example: Arjun - student, Robo-X - friendly robot">

    <button onclick="generateStory()">✨ Generate Comic</button>

    <div id="loading" class="loading">
        Gemini is creating your comic... Please wait.
    </div>

    <div id="error" class="error"></div>
</section>


<section class="card">
    <h2>📖 Generated Comic</h2>

    <div id="story" class="result">
        Your generated comic will appear here.
    </div>

    <button class="secondary" onclick="regenerateStory()">
        🔄 Regenerate
    </button>

    <button class="secondary" onclick="downloadStory()">
        💾 Download Story
    </button>
</section>


<section class="card">
    <h2>🧑‍🎨 Character Generator</h2>

    <textarea id="characterDescription"
        placeholder="Example: A brave teenage superhero who controls electricity..."></textarea>

    <button onclick="generateCharacter()">
        🧑‍🎨 Generate Character
    </button>

    <div id="characterResult" class="result" style="margin-top:15px;">
        Character details will appear here.
    </div>
</section>


<section class="card">
    <h2>🎬 Scene Generator</h2>

    <textarea id="sceneDescription"
        placeholder="Example: The hero enters an abandoned laboratory and sees a glowing robot..."></textarea>

    <button onclick="generateScene()">
        🎬 Generate Scene
    </button>

    <div id="sceneResult" class="result" style="margin-top:15px;">
        Scene details will appear here.
    </div>
</section>

<footer>
    ComicCraft © 2026 | AI Comic Story Creator
</footer>

</div>


<script>
let currentStory = "";

async function generateStory() {

    const idea = document.getElementById("idea").value.trim();

    if (!idea) {
        showError("Please enter a story idea.");
        return;
    }

    clearError();

    document.getElementById("loading").style.display = "block";
    document.getElementById("story").textContent =
        "Creating your comic story...";

    const payload = {
        idea: idea,
        genre: document.getElementById("genre").value,
        style: document.getElementById("style").value,
        tone: document.getElementById("tone").value,
        scenes: document.getElementById("scenes").value,
        characters: document.getElementById("characters").value
    };

    try {
        const response = await fetch("/generate-story", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Failed to generate story.");
        }

        currentStory = data.story;
        document.getElementById("story").textContent = currentStory;

    } catch (error) {
        showError(error.message);
        document.getElementById("story").textContent =
            "Story generation failed.";
    }

    document.getElementById("loading").style.display = "none";
}


async function regenerateStory() {

    if (!currentStory) {
        showError("Generate a comic first.");
        return;
    }

    clearError();

    try {
        const response = await fetch("/regenerate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                content: currentStory
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Regeneration failed.");
        }

        currentStory = data.content;
        document.getElementById("story").textContent = currentStory;

    } catch (error) {
        showError(error.message);
    }
}


async function generateCharacter() {

    const description =
        document.getElementById("characterDescription").value.trim();

    if (!description) {
        showError("Enter a character description.");
        return;
    }

    try {
        const response = await fetch("/generate-character", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                description: description
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Character generation failed.");
        }

        document.getElementById("characterResult").textContent =
            data.character;

    } catch (error) {
        showError(error.message);
    }
}


async function generateScene() {

    const description =
        document.getElementById("sceneDescription").value.trim();

    if (!description) {
        showError("Enter a scene description.");
        return;
    }

    try {
        const response = await fetch("/generate-scene", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                description: description
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Scene generation failed.");
        }

        document.getElementById("sceneResult").textContent =
            data.scene;

    } catch (error) {
        showError(error.message);
    }
}


function downloadStory() {

    if (!currentStory) {
        showError("Generate a comic first.");
        return;
    }

    const blob = new Blob(
        [currentStory],
        {type: "text/plain;charset=utf-8"}
    );

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "comiccraft_story.txt";
    a.click();

    URL.revokeObjectURL(url);
}


function showError(message) {
    document.getElementById("error").textContent = message;
}


function clearError() {
    document.getElementById("error").textContent = "";
}
</script>

</body>
</html>
"""


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" ComicCraft - AI Comic Story Creator")
    print("=" * 60)
    print("Server: http://127.0.0.1:5000")
    print("Gemini Model:", MODEL_NAME)
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
