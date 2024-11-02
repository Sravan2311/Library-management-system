from bson import ObjectId
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/library"
mongo = PyMongo(app)

# File upload configuration
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/home')
def index():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/book_list')
def book_list_page():
    if 'username' in session:
        return render_template('book_list.html')
    return redirect(url_for('login'))

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_input = request.form['message']
        response = get_chatbot_response(user_input)
        return jsonify({'response': response})

    return render_template('chatbot.html')

def get_chatbot_response(user_input):
    # Simple responses based on user input
    user_input = user_input.lower()
    if "hello" in user_input or "hi" in user_input:
        return "Hello! How can I assist you today?"
    elif "books" in user_input:
        return "You can view and add books in the book list page."
    elif "help" in user_input:
        return "You can ask me about the available features or the book list."
    elif "nice" in user_input:
        return "Glad to hear that! What's on your mind today?"
    elif "i want to read a book" in user_input:
        return "Great choice! What type of book are you interested in? Fiction, non-fiction, mystery, fantasy, self-help, or something else?"
    else:
        return "I'm sorry, I don't understand. Can you please rephrase?"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({'username': username, 'password': hashed_password})
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    pdf = request.files['pdf']
    if pdf:
        filename = secure_filename(pdf.filename)
        pdf.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        mongo.db.books.insert_one({'title': title, 'pdf': filename})
        return jsonify({'message': 'Book added successfully!'})
    return jsonify({'message': 'Failed to add book.'})

@app.route('/get_books', methods=['GET'])
def get_books():
    books = mongo.db.books.find()
    return jsonify([{
        '_id': str(book['_id']),
        'title': book['title'],
        'pdf': book.get('pdf', None)  # Use .get to avoid KeyError if 'pdf' is missing
    } for book in books])

@app.route('/delete_book/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    # Convert book_id to ObjectId before querying
    mongo.db.books.delete_one({'_id': ObjectId(book_id)})  # Correct usage of ObjectId
    return jsonify({'message': 'Book deleted successfully!'})
@app.route('/delete_all_books', methods=['DELETE'])
def delete_all_books():
    mongo.db.books.delete_many({})  # Deletes all documents in the books collection
    return jsonify({'message': 'All books deleted successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
