import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from lyrics_analyzer import parse_lyrics_file

class LyricsFileHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app
        
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            logging.info(f"New lyrics file detected: {event.src_path}")
            self._update_lyrics_database(event.src_path)
            
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            logging.info(f"Lyrics file modified: {event.src_path}")
            self._update_lyrics_database(event.src_path)
            
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            logging.info(f"Lyrics file deleted: {event.src_path}")
            self._remove_from_database(event.src_path)
            
    def _update_lyrics_database(self, filepath):
        from models import Lyrics
        from app import db
        
        with self.app.app_context():
            try:
                lyrics_data = parse_lyrics_file(filepath)
                if lyrics_data:
                    filename = os.path.basename(filepath)
                    
                    # Check if this lyrics file already exists in the database
                    existing_lyric = Lyrics.query.filter_by(filename=filename).first()
                    
                    if existing_lyric:
                        # Update existing record
                        existing_lyric.title = lyrics_data['title']
                        existing_lyric.artist = lyrics_data['artist']
                        existing_lyric.content = lyrics_data['content']
                        existing_lyric.sentiment_score = lyrics_data['sentiment_score']
                        # Set a default emotion
                        if not existing_lyric.emotions:
                            emotion = 'happy' if lyrics_data['sentiment_score'] > 0 else 'sad'
                            existing_lyric.emotions = emotion
                    else:
                        # Determine a simple emotion based on sentiment score
                        emotion = 'happy' if lyrics_data['sentiment_score'] > 0 else 'sad'
                        
                        # Create new record
                        new_lyric = Lyrics(
                            filename=filename,
                            title=lyrics_data['title'],
                            artist=lyrics_data['artist'],
                            content=lyrics_data['content'],
                            sentiment_score=lyrics_data['sentiment_score'],
                            emotions=emotion,
                            views=0
                        )
                        db.session.add(new_lyric)
                    
                    db.session.commit()
                    logging.info(f"Successfully updated database for {filename}")
            except Exception as e:
                logging.error(f"Error updating lyrics database for {filepath}: {str(e)}")
                db.session.rollback()
    
    def _remove_from_database(self, filepath):
        from models import Lyrics
        from app import db
        
        with self.app.app_context():
            try:
                filename = os.path.basename(filepath)
                Lyrics.query.filter_by(filename=filename).delete()
                db.session.commit()
                logging.info(f"Successfully removed {filename} from database")
            except Exception as e:
                logging.error(f"Error removing lyrics from database for {filepath}: {str(e)}")
                db.session.rollback()

def index_existing_lyrics(lyrics_folder, app):
    """Index all existing lyrics files in the folder."""
    logging.info(f"Indexing existing lyrics in {lyrics_folder}")
    
    handler = LyricsFileHandler(app)
    
    for filename in os.listdir(lyrics_folder):
        if filename.endswith('.txt'):
            filepath = os.path.join(lyrics_folder, filename)
            handler._update_lyrics_database(filepath)

def start_watching_lyrics(lyrics_folder, app):
    """Start watching the lyrics folder for changes."""
    # First, index existing lyrics
    index_existing_lyrics(lyrics_folder, app)
    
    # Then, set up the observer
    event_handler = LyricsFileHandler(app)
    observer = Observer()
    observer.schedule(event_handler, lyrics_folder, recursive=False)
    
    # Start the observer in a separate thread
    observer_thread = threading.Thread(target=observer.start, daemon=True)
    observer_thread.start()
    
    logging.info(f"Started watching lyrics folder: {lyrics_folder}")
