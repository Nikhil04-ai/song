import os
import json
import logging
from flask import render_template, request, jsonify, send_from_directory
from app import app, db
from models import Lyrics, Artist, Contact
from lyrics_analyzer import (
    search_lyrics, get_lyrics_content, increment_view_count,
    find_similar_songs, get_trending_songs, get_recent_songs
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize sample artists data
def init_sample_artists():
    try:
        if Artist.query.count() == 0:
            sample_artists = [
                {
                    "name": "Adele",
                    "bio": "Adele Laurie Blue Adkins MBE is an English singer-songwriter known for her powerful vocals and emotional ballads.",
                    "image_url": "https://cdn.pixabay.com/photo/2016/01/10/22/08/microphone-1132528_960_720.jpg"
                },
                {
                    "name": "Ed Sheeran",
                    "bio": "Edward Christopher Sheeran MBE is an English singer-songwriter, musician, and record producer known for his diverse musical style.",
                    "image_url": "https://cdn.pixabay.com/photo/2016/11/19/13/57/guitar-1839387_960_720.jpg"
                },
                {
                    "name": "Taylor Swift",
                    "bio": "Taylor Alison Swift is an American singer-songwriter known for narrative songs about her personal life.",
                    "image_url": "https://cdn.pixabay.com/photo/2017/11/11/21/55/girl-2940655_960_720.jpg"
                },
                {
                    "name": "Drake",
                    "bio": "Aubrey Drake Graham is a Canadian rapper, singer, and actor known for blending singing and rapping.",
                    "image_url": "https://cdn.pixabay.com/photo/2017/11/02/20/31/guitars-2912447_960_720.jpg"
                },
                {
                    "name": "Billie Eilish",
                    "bio": "Billie Eilish Pirate Baird O'Connell is an American singer-songwriter known for her unique musical style.",
                    "image_url": "https://cdn.pixabay.com/photo/2019/05/26/12/30/microphone-4230001_960_720.jpg"
                }
            ]
            
            for artist_data in sample_artists:
                artist = Artist(**artist_data)
                db.session.add(artist)
            
            db.session.commit()
            logger.info("Sample artists initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing sample artists: {str(e)}")
        db.session.rollback()

# Initialize sample artists when the app starts
with app.app_context():
    init_sample_artists()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

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

@app.route('/api/search')
def api_search():
    """Search for lyrics"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = search_lyrics(query)
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
        similar = find_similar_songs(lyrics.emotions.split(',')[0], exclude_id=lyrics_id)
        
        return jsonify({
            'metadata': lyrics.to_dict(),
            'content': lyrics_content,
            'similar': similar
        })
    except Exception as e:
        logger.error(f"Error getting lyrics: {str(e)}")
        return jsonify({'error': 'Failed to retrieve lyrics'}), 500

@app.route('/api/artists')
def api_artists():
    """Get all artists"""
    try:
        artists = Artist.query.all()
        return jsonify([artist.to_dict() for artist in artists])
    except Exception as e:
        logger.error(f"Error getting artists: {str(e)}")
        return jsonify({'error': 'Failed to retrieve artists'}), 500

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
        
        logger.info(f"New contact form submission from {data['name']} ({data['email']})")
        return jsonify({'success': True})
    
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to process contact form'}), 500

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
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve stats'}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500
