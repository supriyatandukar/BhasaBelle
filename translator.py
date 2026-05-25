from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def parse_translate_response(response_text):
    lines = response_text.strip().split('\n')
    translation = ""
    romaji = ""
    breakdown_text = ""
    current_section = None
    
    for line in lines:
        if "TRANSLATION:" in line:
            current_section = "translation"
        elif "PHONETIC" in line or "ROMANIZATION" in line:
            current_section = "romaji"
        elif "WORD-BY-WORD" in line or "BREAKDOWN" in line:
            current_section = "breakdown"
        elif line.strip() and current_section:
            if current_section == "translation":
                translation += line + "\n"
            elif current_section == "romaji":
                romaji += line + "\n"
            elif current_section == "breakdown":
                breakdown_text += line + "\n"
    
    breakdown = []
    if breakdown_text:
        items = breakdown_text.strip().split('\n')
        for item in items:
            if " - " in item and item.strip():
                parts = item.split(' - ')
                if len(parts) >= 3:
                    breakdown.append({
                        "english": parts[0].strip(),
                        "target": parts[1].strip(),
                        "romaji": parts[1].strip(),
                        "meaning": parts[2].strip()
                    })
    
    return {
        "translation": translation.strip(),
        "romaji": romaji.strip(),
        "breakdown": breakdown if breakdown else []
    }

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    language = data.get('language')
    
    if not text or not language:
        return jsonify({"error": "Missing text or language"}), 400
    
    prompt = f"""Translate the following text into {language}.

Provide the output in this exact format, no deviations:

TRANSLATION:
[Full translation in {language}]

PHONETIC GUIDE (Romanization):
[Phonetic/romanized version]

WORD-BY-WORD BREAKDOWN:
[one line per word, exactly like this format:]
word1 - {language}_word1 (romanization1) - meaning1/ context1
word2 - {language}_word2 (romanization2) - meaning2/ context2


Text to translate:
{text}"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        
        print("Raw response from Gemini API:")
        print(response.text)
        print("End of raw response")
        parsed = parse_translate_response(response.text)
        print("Parsed response:")
        print(parsed)
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data.get('text')
    
    if not text:
        return jsonify({"error": "Missing text"}), 400
    
    prompt = f"""Summarize the following text in 2-3 sentences. Be concise and clear.

{text}"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return jsonify({"summary": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sentiment', methods=['POST'])
def sentiment():
    data = request.json
    text = data.get('text')
    
    if not text:
        return jsonify({"error": "Missing text"}), 400
    
    prompt = f"""Analyze the sentiment of this text and respond in this exact format:

Sentiment: [Positive/Negative/Neutral]
Confidence: [High/Medium/Low]
Explanation: [Brief explanation]

Text:
{text}"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        
        sentiment_value = "Neutral"
        if "Positive" in response.text:
            sentiment_value = "Positive"
        elif "Negative" in response.text:
            sentiment_value = "Negative"
        
        return jsonify({
            "sentiment": sentiment_value,
            "analysis": response.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)