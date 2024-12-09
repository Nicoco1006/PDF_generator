from flask import Flask, request, send_file, jsonify, send_from_directory
from fpdf import FPDF
import openai
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Initialisation de l'application Flask
app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app, resources={r"/*": {"origins": "*"}})

# Charger les variables d'environnement
#load_dotenv()

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Classe pour créer un PDF
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_font('Arial', size=12)

    def add_text(self, text):
        self.multi_cell(0, 10, text)

# Route pour afficher l'interface utilisateur (frontend)
@app.route('/')
def home():
    print("Serving index.html")
    return send_from_directory(app.static_folder, 'index.html')

# Route pour générer un PDF
@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Missing "prompt" in the request'}), 400

    prompt = data['prompt']

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        generated_text = response['choices'][0]['message']['content'].strip()

        pdf = PDF()
        pdf.add_text(generated_text)
        pdf_path = "output.pdf"
        pdf.output(pdf_path)

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
