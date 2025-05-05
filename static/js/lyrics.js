document.addEventListener('DOMContentLoaded', function() {
    // Select result items if they exist
    const resultItems = document.querySelectorAll('.result-item');
    
    // Modal elements
    const modal = document.querySelector('.modal');
    const modalTitle = document.querySelector('.modal-title');
    const modalArtist = document.querySelector('.modal-artist');
    const lyricsContent = document.querySelector('.lyrics-content');
    
    // If we're on the search page with results
    if (resultItems.length > 0 && modal) {
        resultItems.forEach(item => {
            item.addEventListener('click', function() {
                const filename = this.getAttribute('data-filename');
                const title = this.querySelector('h3').textContent;
                const artist = this.querySelector('.result-meta').textContent.split('|')[0].trim();
                
                // Show loading state
                modalTitle.textContent = title;
                modalArtist.textContent = artist;
                lyricsContent.textContent = 'Loading lyrics...';
                modal.style.display = 'block';
                
                // Fetch lyrics content
                fetch(`/lyrics/${filename}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to load lyrics');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.lyrics) {
                            lyricsContent.textContent = data.lyrics;
                        } else {
                            lyricsContent.textContent = 'No lyrics found.';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching lyrics:', error);
                        lyricsContent.textContent = 'Error loading lyrics. Please try again.';
                    });
            });
        });
    }
    
    // If we're on a page with suggestion cards
    const suggestionCards = document.querySelectorAll('.suggestion-card');
    if (suggestionCards.length > 0 && modal) {
        suggestionCards.forEach(card => {
            card.addEventListener('click', function() {
                const filename = this.getAttribute('data-filename');
                const title = this.querySelector('h3').textContent;
                const artist = this.querySelector('.card-meta').textContent.split('|')[0].trim();
                
                // Show loading state
                modalTitle.textContent = title;
                modalArtist.textContent = artist;
                lyricsContent.textContent = 'Loading lyrics...';
                modal.style.display = 'block';
                
                // Fetch lyrics content
                fetch(`/lyrics/${filename}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to load lyrics');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.lyrics) {
                            lyricsContent.textContent = data.lyrics;
                        } else {
                            lyricsContent.textContent = 'No lyrics found.';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching lyrics:', error);
                        lyricsContent.textContent = 'Error loading lyrics. Please try again.';
                    });
            });
        });
    }
    
    // Handle trending song clicks
    const trendingCards = document.querySelectorAll('.trending-card');
    if (trendingCards.length > 0 && modal) {
        trendingCards.forEach(card => {
            card.addEventListener('click', function() {
                const filename = this.getAttribute('data-filename');
                const title = this.querySelector('h3').textContent;
                const artist = this.querySelector('p').textContent;
                
                // Show loading state
                modalTitle.textContent = title;
                modalArtist.textContent = artist;
                lyricsContent.textContent = 'Loading lyrics...';
                modal.style.display = 'block';
                
                // Fetch lyrics content
                fetch(`/lyrics/${filename}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to load lyrics');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.lyrics) {
                            lyricsContent.textContent = data.lyrics;
                        } else {
                            lyricsContent.textContent = 'No lyrics found.';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching lyrics:', error);
                        lyricsContent.textContent = 'Error loading lyrics. Please try again.';
                    });
            });
        });
    }
    
    // Handle artist song list clicks
    const songLinks = document.querySelectorAll('.songs-list a');
    if (songLinks.length > 0 && modal) {
        songLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const filename = this.getAttribute('data-filename');
                const title = this.textContent;
                const artist = this.closest('.artist-card').querySelector('.artist-name').textContent;
                
                // Show loading state
                modalTitle.textContent = title;
                modalArtist.textContent = artist;
                lyricsContent.textContent = 'Loading lyrics...';
                modal.style.display = 'block';
                
                // Fetch lyrics content
                fetch(`/lyrics/${filename}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to load lyrics');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.lyrics) {
                            lyricsContent.textContent = data.lyrics;
                        } else {
                            lyricsContent.textContent = 'No lyrics found.';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching lyrics:', error);
                        lyricsContent.textContent = 'Error loading lyrics. Please try again.';
                    });
            });
        });
    }
});
