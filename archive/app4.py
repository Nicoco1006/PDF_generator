from flask import Flask, request, jsonify, send_file, render_template
from fpdf import FPDF
import openai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialisation de Flask
app = Flask(__name__, static_folder="static")

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Classe PDF personnalisée
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_font("Arial", size=12)

    def add_text(self, text):
        self.multi_cell(0, 10, text)

# Route pour servir l'interface utilisateur
@app.route('/')
def home():
    return app.send_static_file('index.html')

# Route pour générer le PDF
@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        # Récupération du prompt depuis la requête JSON
        data = request.get_json()
        prompt = data.get("prompt", "")

        if not prompt:
            return jsonify({"error": "Le prompt est vide."}), 400

        # Générer une réponse via OpenAI
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=500
        )

        # Extraire le texte généré
        text = response.choices[0].text.strip()

        # Créer le PDF
        pdf = PDF()
        pdf.add_text(text)
        output_path = "output.pdf"
        pdf.output(output_path)

        # Retourner le fichier PDF généré
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
