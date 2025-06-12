import os
import json
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

with open('model/alternatives.json', 'r', encoding='utf-8') as f:
    alternatives_data = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Dummy nutritional data
        nutrition_data = {
            'Calories': ('230 kcal', '11%'),
            'Sugar': ('20g', '40%'),
            'Fat': ('12g', '18%'),
            'Sodium': ('480mg', '20%')
        }
        warnings = [
            "⚠️ High sugar content detected.",
            "⚠️ Sodium exceeds 20% daily intake."
        ]

        alternatives = []
        for alt in alternatives_data:
            alt_copy = alt.copy()
            alt_copy['image'] = url_for('static', filename=alt['image'])
            alternatives.append(alt_copy)

        ingredients = ("Whole grain wheat, sugar, salt, malt flavoring, vitamins "
                       "(niacin, B6, B2, B1, folic acid, B12), iron.")
        dietitian_note = ("This product is okay occasionally, but not suitable for daily use due to "
                         "high sugar and sodium content. Consider switching to wholegrain cereals or oatmeal for better long-term health.")

        return render_template('result.html',
                               image_url=url_for('static', filename='uploads/' + filename),
                               nutrition=nutrition_data,
                               warnings=warnings,
                               alternatives=alternatives,
                               ingredients=ingredients,
                               dietitian_note=dietitian_note)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
