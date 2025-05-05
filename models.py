from datetime import datetime
from extensions import db
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.name}>'

class Lyrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    title = db.Column(db.String(255))
    artist = db.Column(db.String(255))
    content = db.Column(db.Text)
    sentiment_score = db.Column(db.Float)
    views = db.Column(db.Integer, default=0)
    emotions = db.Column(db.String(255), default='neutral')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Lyrics {self.title} by {self.artist}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'title': self.title,
            'artist': self.artist,
            'sentiment_score': self.sentiment_score,
            'views': self.views,
            'emotions': self.emotions.split(',') if self.emotions else [],
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    bio = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Artist {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'image_url': self.image_url,
            'songs': [lyric.to_dict() for lyric in Lyrics.query.filter_by(artist=self.name).all()]
        }
