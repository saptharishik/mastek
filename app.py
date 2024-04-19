from flask import Flask

# Create a Flask application instance
app = Flask(__name__)

# Define a route for the home page
@app.route('/')
def home():
    return 'Hello, World! This is the home page.'

# Define a route for another page
@app.route('/about')
def about():
    return 'This is the about page.'

# Run the Flask application
