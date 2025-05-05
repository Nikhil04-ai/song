import os
import logging
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import nltk
from file_watcher import start_watching_lyrics
from lyrics_analyzer import get_lyrics, search_lyrics, get_emotion_based_suggestions, get_trending_songs, get_artists

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# We've moved NLTK data downloading to lyrics_analyzer.py
# NLTK data will be downloaded there and fallback implementations will be used if needed

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
 

from flask import Flask
from extensions import db
from models import Contact, Lyrics, Artist

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lyrics.db'
db.init_app(app)


# Configure the database
# Use PostgreSQL if DATABASE_URL is available, otherwise fallback to SQLite for local development
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    # For local development in VS Code, use SQLite
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_url = 'sqlite:///' + os.path.join(base_dir, 'lyrics.db')
    logging.info(f"Using SQLite database at {db_url}")
else:
    logging.info("Using PostgreSQL database")

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Lyrics folder
app.config["LYRICS_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lyrics")
os.makedirs(app.config["LYRICS_FOLDER"], exist_ok=True)



with app.app_context():
    # Import models
    from models import Contact, Lyrics, Artist
    
    # Create tables
    db.create_all()
    
    # Start the file watcher
    start_watching_lyrics(app.config["LYRICS_FOLDER"], app)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    suggestions = []
    
    if query:
        results = search_lyrics(query, app.config["LYRICS_FOLDER"])
        if results:
            suggestions = get_emotion_based_suggestions(results[0]['content'], app.config["LYRICS_FOLDER"])
    
    return render_template('search.html', query=query, results=results, suggestions=suggestions)

@app.route('/lyrics/<filename>')
def lyrics(filename):
    content = get_lyrics(filename, app.config["LYRICS_FOLDER"])
    if content:
        return jsonify({"lyrics": content})
    return jsonify({"error": "Lyrics not found"}), 404

@app.route('/trending')
def trending():
    trending_songs = get_trending_songs(10)
    return render_template('trending.html', trending_songs=trending_songs)

@app.route('/artists')
def artists():
    from models import Artist
    all_artists = Artist.query.all()
    return render_template('artists.html', artists=[artist.to_dict() for artist in all_artists])

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message = None
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message_content = request.form.get('message')
        
        if name and email and message_content:
            new_contact = Contact(name=name, email=email, message=message_content)
            db.session.add(new_contact)
            db.session.commit()
            message = "Your message has been sent successfully!"
        else:
            message = "Please fill all required fields."
    
    return render_template('contact.html', message=message)

# API Routes
@app.route('/api/trending')
def api_trending():
    """Get trending songs"""
    limit = request.args.get('limit', 10, type=int)
    trending = get_trending_songs(limit)
    return jsonify(trending)

@app.route('/api/recent')
def api_recent():
    """Get recently added songs"""
    limit = request.args.get('limit', 10, type=int)
    recent = get_recent_songs(limit)
    return jsonify(recent)

@app.route('/api/search', methods=['GET'])
def api_search():
    """Search for lyrics"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = search_lyrics(query, app.config["LYRICS_FOLDER"])
    return jsonify(results)

@app.route('/api/lyrics/<int:lyrics_id>')
def api_get_lyrics(lyrics_id):
    """Get lyrics details and content"""
    try:
        lyrics = Lyrics.query.get_or_404(lyrics_id)
        lyrics_content = get_lyrics_content(lyrics.filename)
        
        # Increment view count
        increment_view_count(lyrics_id)
        
        # Get similar songs
        similar = find_similar_songs(lyrics.emotions.split(',')[0] if lyrics.emotions else 'neutral', exclude_id=lyrics_id)
        
        return jsonify({
            'metadata': lyrics.to_dict(),
            'content': lyrics_content,
            'similar': similar
        })
    except Exception as e:
        logging.error(f"Error getting lyrics: {str(e)}")
        return jsonify({'error': 'Failed to retrieve lyrics'}), 500

@app.route('/api/artists')
def api_artists():
    """Get all artists"""
    try:
        artists = Artist.query.all()
        return jsonify([artist.to_dict() for artist in artists])
    except Exception as e:
        logging.error(f"Error getting artists: {str(e)}")
        return jsonify({'error': 'Failed to retrieve artists'}), 500

@app.route('/api/suggestions', methods=['POST'])
def api_suggestions():
    lyrics = request.json.get('lyrics', '')
    suggestions = get_emotion_based_suggestions(lyrics, app.config["LYRICS_FOLDER"])
    return jsonify(suggestions)

@app.route('/api/contact', methods=['POST'])
def api_contact():
    """Handle contact form submissions"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create and save contact entry
        contact = Contact(
            name=data['name'],
            email=data['email'],
            message=data['message']
        )
        
        db.session.add(contact)
        db.session.commit()
        
        logging.info(f"New contact form submission from {data['name']} ({data['email']})")
        return jsonify({'success': True})
    
    except Exception as e:
        logging.error(f"Error processing contact form: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to process contact form'}), 500

@app.route('/api/submit_contact', methods=['POST'])
def submit_contact():
    return api_contact()

@app.route('/api/stats')
def api_stats():
    """Get site statistics"""
    try:
        lyrics_count = Lyrics.query.count()
        artists_count = Artist.query.count()
        views_count = db.session.query(db.func.sum(Lyrics.views)).scalar() or 0
        
        return jsonify({
            'lyrics_count': lyrics_count,
            'artists_count': artists_count,
            'views_count': int(views_count)
        })
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve stats'}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logging.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
