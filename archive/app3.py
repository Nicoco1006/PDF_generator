from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from fpdf import FPDF
import openai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)

# Activer CORS pour toutes les routes
CORS(app, resources={r"/*": {"origins": "*"}})  # Permet toutes les origines

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

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        # Appel à OpenAI
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )

        generated_text = response['choices'][0]['text'].strip()

        # Générer le PDF
        pdf = PDF()
        pdf.add_text(generated_text)
        pdf_file_path = "output.pdf"
        pdf.output(pdf_file_path)

        # Envoyer le fichier en réponse
        return send_file(pdf_file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
