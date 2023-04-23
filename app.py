from flask import Flask,render_template,request
import requests

import pickle
import numpy as np
app = Flask(__name__)

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)



@app.route('/')
def index():
    # Define the API endpoint and search parameters
    url = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': 'subject:fiction',
        'orderBy': 'newest',
        'maxResults': 10,
    }

    # Send the request to the API and parse the response
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the book information
    books = []
    for item in data['items']:
        # Extract the book title
        title = item['volumeInfo']['title']

        # Extract the book author(s)
        authors = item['volumeInfo']['authors']
        if authors:
            author = authors[0]
        else:
            author = 'Unknown'

        # Extract the published date
        published_date = item['volumeInfo'].get('publishedDate', 'Unknown')

        # Extract the book description
        description = item['volumeInfo'].get('description', 'No description available.')

        # Extract the book image link
        image_link = item['volumeInfo'].get('imageLinks', {}).get('thumbnail', 'https://via.placeholder.com/150x200.png?text=No+Image')

        # Add the book information to the list of books
        books.append({
            'title': title,
            'author': author,
            'published_date': published_date,
            'description': description,
            'image_link': image_link
        })

    # Render the index.html template with the list of books
    return render_template('index.html', books=books)



@app.route('/home')
def home():
    return render_template('./home.html')

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html',data=data)

@app.route('/bestseller')
def bestseller():
    categories = ['Fiction', 'Nonfiction', 'Mystery', 'Romance', 'Science Fiction']
    category_books = {}
    for category in categories:
        url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{category}'
        response = requests.get(url)
        books = response.json().get('items', [])
        books_list = []
        for book in books:
            book_info = {}
            volume_info = book.get('volumeInfo', {})
            book_info['title'] = volume_info.get('title', '')
            book_info['authors'] = ', '.join(volume_info.get('authors', []))
            book_info['published_date'] = volume_info.get('publishedDate', '')
            book_info['description'] = volume_info.get('description', '')
            book_info['buy_link'] = volume_info.get('infoLink', '')
            book_info['image_link'] = volume_info.get('imageLinks', {}).get('thumbnail', '')
            books_list.append(book_info)
        category_books[category] = books_list
    return render_template('bestseller.html', categories=categories, category_books=category_books)

# @app.route("/bestsellers")
# def index():
#     url = "https://www.googleapis.com/books/v1/volumes"
#     params = {
#         "q": "subject:bestsellers",
#         "orderBy": "newest"
#     }
#     response = requests.get(url, params=params)
#     data = response.json()
#     books = []
#     for item in data["items"]:
#         book = {}
#         book["title"] = item["volumeInfo"].get("title", "No title available")
#         book["author"] = ", ".join(item["volumeInfo"].get("authors", ["No author available"]))
#         book["published_date"] = item["volumeInfo"].get("publishedDate", "No published date available")
#         book["description"] = item["volumeInfo"].get("description", "No description available")
#         book["image_url"] = item["volumeInfo"]["imageLinks"].get("thumbnail") if "imageLinks" in item["volumeInfo"] else None
#         books.append(book)
#     return render_template("bestseller.html", books=books)

@app.route('/bestselrrr')
def bestselrrr():
    return render_template('bestselrrr.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )


if __name__ == '__main__':
    app.run(debug=True)
