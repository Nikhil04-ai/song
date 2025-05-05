import os
import re
import nltk
import logging
import random

# Initialize NLTK components - download required data first
print("Downloading NLTK data in lyrics_analyzer.py...")
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

# Only import NLTK modules after downloading the data
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    
    sentiment_analyzer = SentimentIntensityAnalyzer()
    stop_words = set(stopwords.words('english'))
    print("NLTK components initialized successfully.")
except Exception as e:
    print(f"Error initializing NLTK components: {str(e)}")
    logging.error(f"Error initializing NLTK components: {str(e)}")
    
    # Fallback sentiment analyzer if VADER is not available
    class SimpleSentimentAnalyzer:
        def polarity_scores(self, text):
            # Very simple sentiment analysis - just count positive and negative words
            positive_words = ['good', 'great', 'happy', 'love', 'joy', 'wonderful', 'peace']
            negative_words = ['bad', 'sad', 'hate', 'pain', 'terrible', 'awful', 'angry']
            
            text_lower = text.lower()
            words = re.findall(r'\b\w+\b', text_lower)
            
            pos_count = sum(1 for word in words if word in positive_words)
            neg_count = sum(1 for word in words if word in negative_words)
            
            total = len(words) if words else 1
            compound = (pos_count - neg_count) / total
            
            return {'compound': compound}
    
    sentiment_analyzer = SimpleSentimentAnalyzer()
    
    # Fallback stopwords if NLTK stopwords not available
    stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
                      'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 
                      'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 
                      'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
                      'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 
                      'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 
                      'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 
                      'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
                      'with', 'about', 'against', 'between', 'into', 'through', 'during', 
                      'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 
                      'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'])
    
    # Simplified word tokenizer
    def simple_word_tokenize(text):
        return re.findall(r'\b\w+\b', text.lower())
    
    word_tokenize = simple_word_tokenize
    print("Using fallback sentiment analyzer and tokenizer.")

def parse_lyrics_file(filepath):
    """Parse a lyrics file and extract metadata and content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Extract metadata (assuming first few lines might contain title and artist)
        lines = content.split('\n')
        title = "Unknown Title"
        artist = "Unknown Artist"
        
        # Try to parse title and artist from the filename or content
        filename = os.path.basename(filepath)
        filename_parts = os.path.splitext(filename)[0].split(' - ')
        
        if len(filename_parts) >= 2:
            artist = filename_parts[0].strip()
            title = filename_parts[1].strip()
        elif len(lines) > 0 and ':' in lines[0]:
            # Try to extract from first line if it has a colon
            parts = lines[0].split(':', 1)
            if parts[0].lower().strip() in ['title', 'song']:
                title = parts[1].strip()
                content = '\n'.join(lines[1:])
            
        # If second line contains artist info
        if len(lines) > 1 and ':' in lines[1]:
            parts = lines[1].split(':', 1)
            if parts[0].lower().strip() in ['artist', 'by']:
                artist = parts[1].strip()
                if len(lines) > 2:
                    content = '\n'.join(lines[2:])
        
        # Calculate sentiment
        sentiment_score = get_sentiment_score(content)
        
        return {
            'filename': filename,
            'title': title,
            'artist': artist,
            'content': content,
            'sentiment_score': sentiment_score
        }
    except Exception as e:
        logging.error(f"Error parsing lyrics file {filepath}: {str(e)}")
        return None

def get_lyrics(filename, lyrics_folder):
    """Get lyrics content from a file."""
    filepath = os.path.join(lyrics_folder, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    return None

def search_lyrics(query, lyrics_folder):
    """Search lyrics files for the given query."""
    results = []
    
    try:
        if not query or not os.path.exists(lyrics_folder):
            logging.warning(f"Invalid search parameters: query='{query}', lyrics_folder='{lyrics_folder}'")
            return results
        
        query = query.lower()
        
        for filename in os.listdir(lyrics_folder):
            if filename.endswith('.txt'):
                try:
                    filepath = os.path.join(lyrics_folder, filename)
                    lyrics_data = parse_lyrics_file(filepath)
                    
                    if lyrics_data:
                        # Check if query appears in title, artist, or lyrics content
                        if (query in lyrics_data['title'].lower() or 
                            query in lyrics_data['artist'].lower() or 
                            query in lyrics_data['content'].lower()):
                            results.append(lyrics_data)
                except Exception as e:
                    logging.error(f"Error processing file {filename} during search: {str(e)}")
    except Exception as e:
        logging.error(f"Error during lyrics search: {str(e)}")
    
    return results

def get_sentiment_score(text):
    """Calculate sentiment score for the given text."""
    sentiment = sentiment_analyzer.polarity_scores(text)
    return sentiment['compound']

def get_keywords(text, num_keywords=10):
    """Extract important keywords from text."""
    tokens = word_tokenize(text.lower())
    filtered_tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
    
    # Get frequency distribution
    freq_dist = nltk.FreqDist(filtered_tokens)
    return [word for word, _ in freq_dist.most_common(num_keywords)]

def get_emotion_based_suggestions(lyrics_content, lyrics_folder, max_suggestions=5):
    """Get song suggestions based on emotional similarity."""
    suggestions = []
    
    try:
        if not lyrics_content or not os.path.exists(lyrics_folder):
            logging.warning(f"Invalid parameters for emotion suggestions: content length={len(lyrics_content) if lyrics_content else 0}, folder={lyrics_folder}")
            return suggestions
        
        # Get sentiment score for the input lyrics
        input_sentiment = get_sentiment_score(lyrics_content)
        input_keywords = set(get_keywords(lyrics_content))
        logging.debug(f"Input sentiment: {input_sentiment}, keywords: {input_keywords}")
        
        for filename in os.listdir(lyrics_folder):
            if filename.endswith('.txt'):
                try:
                    filepath = os.path.join(lyrics_folder, filename)
                    lyrics_data = parse_lyrics_file(filepath)
                    
                    if lyrics_data and lyrics_data['content'] != lyrics_content:
                        # Calculate sentiment difference
                        sentiment_diff = abs(lyrics_data['sentiment_score'] - input_sentiment)
                        
                        # Calculate keyword overlap
                        suggestion_keywords = set(get_keywords(lyrics_data['content']))
                        keyword_overlap = len(input_keywords.intersection(suggestion_keywords))
                        
                        # Score is a combination of sentiment similarity and keyword overlap
                        score = (1 - sentiment_diff) + (keyword_overlap / 10)
                        
                        suggestions.append({
                            'filename': lyrics_data['filename'],
                            'title': lyrics_data['title'],
                            'artist': lyrics_data['artist'],
                            'score': score,
                            'sentiment_score': lyrics_data['sentiment_score']
                        })
                except Exception as e:
                    logging.error(f"Error processing file {filename} for suggestions: {str(e)}")
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:max_suggestions]
    except Exception as e:
        logging.error(f"Error generating emotion-based suggestions: {str(e)}")
        return suggestions

def get_lyrics_content(filename):
    """Get the content of a lyrics file given its filename."""
    from app import app
    
    lyrics_folder = app.config["LYRICS_FOLDER"]
    filepath = os.path.join(lyrics_folder, filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    return None

def increment_view_count(lyrics_id):
    """Increment the view count for a lyrics entry."""
    from app import db
    from models import Lyrics
    
    try:
        lyrics = Lyrics.query.get(lyrics_id)
        if lyrics:
            lyrics.views = (lyrics.views or 0) + 1
            db.session.commit()
            return True
    except Exception as e:
        logging.error(f"Error incrementing view count: {str(e)}")
        db.session.rollback()
    return False

def find_similar_songs(emotion, exclude_id=None, limit=5):
    """Find songs with similar emotions."""
    from models import Lyrics
    
    try:
        query = Lyrics.query.filter(Lyrics.emotions.like(f'%{emotion}%'))
        if exclude_id:
            query = query.filter(Lyrics.id != exclude_id)
        
        similar_songs = query.order_by(Lyrics.views.desc()).limit(limit).all()
        return [song.to_dict() for song in similar_songs]
    except Exception as e:
        logging.error(f"Error finding similar songs: {str(e)}")
        return []

def get_trending_songs(count=10):
    """Get a list of trending songs based on view count."""
    from models import Lyrics
    
    try:
        trending_songs = Lyrics.query.order_by(Lyrics.views.desc()).limit(count).all()
        return [song.to_dict() for song in trending_songs]
    except Exception as e:
        logging.error(f"Error getting trending songs: {str(e)}")
        return []
        
def get_recent_songs(count=10):
    """Get a list of recently added songs."""
    from models import Lyrics
    
    try:
        recent_songs = Lyrics.query.order_by(Lyrics.last_updated.desc()).limit(count).all()
        return [song.to_dict() for song in recent_songs]
    except Exception as e:
        logging.error(f"Error getting recent songs: {str(e)}")
        return []

def get_artists(lyrics_folder):
    """Get a list of all artists with their songs."""
    artists = {}
    
    for filename in os.listdir(lyrics_folder):
        if filename.endswith('.txt'):
            filepath = os.path.join(lyrics_folder, filename)
            lyrics_data = parse_lyrics_file(filepath)
            
            if lyrics_data:
                artist = lyrics_data['artist']
                if artist not in artists:
                    artists[artist] = []
                
                artists[artist].append({
                    'filename': lyrics_data['filename'],
                    'title': lyrics_data['title']
                })
    
    # Convert to list of artist objects
    result = []
    for artist_name, songs in artists.items():
        result.append({
            'name': artist_name,
            'songs': songs,
            'song_count': len(songs)
        })
    
    # Sort by number of songs (most songs first)
    result.sort(key=lambda x: x['song_count'], reverse=True)
    return result
