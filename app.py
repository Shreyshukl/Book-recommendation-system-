import os
import requests
import pickle
import numpy as np
from flask import Flask, render_template, request  # Removed duplicate `requests` import

# Google Drive direct download link (Replace with actual file ID)
BOOKS_URL = "https://drive.google.com/uc?id=1-S9GgoW_jwyddSBRWi_-IMcIOAEpJ8J4"
BOOKS_FILE = "books.pkl"

# Check if the file exists, if not, download it
if not os.path.exists(BOOKS_FILE):
    print("Downloading books.pkl...")
    response = requests.get(BOOKS_URL, stream=True)
    if response.status_code == 200:
        with open(BOOKS_FILE, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print("Download complete!")
    else:
        print("Failed to download the file. Check the URL or permissions.")

# Load pickled files
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open(BOOKS_FILE, 'rb'))  # Use downloaded file
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    if user_input not in pt.index:
        return render_template('recommend.html', data=[], error="Book not found in dataset.")

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]] if 'Book-Title' in books.columns else books
        item = [
            temp_df.drop_duplicates('Book-Title')['Book-Title'].values[0] if not temp_df.empty else "N/A",
            temp_df.drop_duplicates('Book-Title')['Book-Author'].values[0] if not temp_df.empty else "N/A",
            temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values[0] if not temp_df.empty else "N/A"
        ]
        data.append(item)

    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
