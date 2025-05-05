// Main JavaScript file for general site functionality

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application
    initApp();
});

function initApp() {
    // Fetch site statistics
    fetchStats();
    
    // Initialize smooth scrolling for navigation links
    initSmoothScroll();
    
    // Add event listeners for navigation
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            // Get the target section from the href attribute
            const targetId = link.getAttribute('href');
            
            // Only handle links to sections on the same page
            if (targetId.startsWith('#')) {
                e.preventDefault();
                
                // Find the target element
                const targetSection = document.querySelector(targetId);
                if (targetSection) {
                    // Scroll to the target section
                    targetSection.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
    
    // Initialize trending section
    initTrendingSection();
    
    // Initialize artists section
    initArtistsSection();
    
    // Add scroll animation for elements
    initScrollAnimations();
    
    // Initialize contact form
    initContactForm();
}

function fetchStats() {
    // Check if stats elements exist before making the API call
    const statLyrics = document.getElementById('stat-lyrics');
    const statArtists = document.getElementById('stat-artists');
    const statViews = document.getElementById('stat-views');
    
    // Skip API call if none of the elements exist
    if (!statLyrics && !statArtists && !statViews) {
        return;
    }
    
    // Fetch site statistics and update the UI
    fetch('/api/stats')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update statistics display if elements exist
            if (statLyrics) {
                statLyrics.textContent = data.lyrics_count || 0;
            }
            if (statArtists) {
                statArtists.textContent = data.artists_count || 0;
            }
            if (statViews) {
                statViews.textContent = formatNumber(data.views_count || 0);
            }
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
        });
}

function formatNumber(num) {
    // Format large numbers with commas
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function initSmoothScroll() {
    // Add smooth scrolling behavior to all internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function initTrendingSection() {
    // Check if trending container exists before making the API call
    const trendingContainer = document.querySelector('.trending-container');
    const sliderContainer = document.querySelector('.trending-slider');
    
    if (!trendingContainer || !sliderContainer) {
        return;
    }
    
    // Fetch trending songs
    fetch('/api/trending?limit=10')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(songs => {
            if (songs.length === 0) {
                trendingContainer.innerHTML = 
                    '<p class="text-center">No trending songs available yet.</p>';
                return;
            }
            
            // Create the trending slider
            sliderContainer.innerHTML = '';
            
            songs.forEach(song => {
                const card = createLyricsCard(song);
                sliderContainer.appendChild(card);
            });
            
            // Initialize slider functionality
            initSlider();
        })
        .catch(error => {
            console.error('Error fetching trending songs:', error);
            trendingContainer.innerHTML = 
                '<p class="text-center">Error loading trending songs. Please try again later.</p>';
        });
}

function initSlider() {
    // Simple slider functionality for trending songs
    const slider = document.querySelector('.trending-slider');
    const cards = slider.querySelectorAll('.lyrics-card');
    const prevBtn = document.querySelector('.slider-prev');
    const nextBtn = document.querySelector('.slider-next');
    
    if (cards.length === 0) return;
    
    const cardWidth = cards[0].offsetWidth + parseInt(getComputedStyle(cards[0]).marginRight);
    let currentPosition = 0;
    const maxPosition = cards.length - Math.floor(slider.offsetWidth / cardWidth);
    
    // Add event listeners to slider controls
    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentPosition > 0) {
                currentPosition--;
                updateSliderPosition();
            }
        });
        
        nextBtn.addEventListener('click', () => {
            if (currentPosition < maxPosition) {
                currentPosition++;
                updateSliderPosition();
            }
        });
    }
    
    function updateSliderPosition() {
        slider.style.transform = `translateX(-${currentPosition * cardWidth}px)`;
    }
}

function createLyricsCard(song) {
    // Create a lyrics card element
    const card = document.createElement('div');
    card.className = 'lyrics-card glass';
    card.dataset.id = song.id;
    
    // Split emotions and take only the first 3
    const emotions = song.emotions ? song.emotions.split(',').slice(0, 3) : [];
    const emotionsHtml = emotions.map(emotion => 
        `<span class="emotion-tag ${emotion.toLowerCase()}">${emotion}</span>`
    ).join('');
    
    card.innerHTML = `
        <h3>${song.title}</h3>
        <div class="lyrics-card-artist">${song.artist}</div>
        <div class="lyrics-card-emotions">
            ${emotionsHtml}
        </div>
    `;
    
    // Add click event to show lyrics modal
    card.addEventListener('click', () => {
        showLyricsModal(song.id);
    });
    
    return card;
}

function showLyricsModal(lyricsId) {
    // Show the lyrics modal with the specified lyrics
    fetch(`/api/lyrics/${lyricsId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const modal = document.getElementById('lyrics-modal');
            const modalTitle = document.getElementById('modal-title');
            const modalArtist = document.getElementById('modal-artist');
            const modalContent = document.getElementById('modal-content');
            const similarSongsList = document.getElementById('similar-songs-list');
            
            // Update modal content
            modalTitle.textContent = data.metadata.title;
            modalArtist.textContent = data.metadata.artist;
            modalContent.textContent = data.content || 'Lyrics not available';
            
            // Update similar songs
            similarSongsList.innerHTML = '';
            if (data.similar && data.similar.length > 0) {
                data.similar.forEach(similar => {
                    const similarCard = document.createElement('div');
                    similarCard.className = 'similar-song-card glass';
                    similarCard.dataset.id = similar.id;
                    
                    similarCard.innerHTML = `
                        <h4>${similar.title}</h4>
                        <div class="lyrics-card-artist">${similar.artist}</div>
                    `;
                    
                    similarCard.addEventListener('click', () => {
                        // Close current modal and open new one
                        closeModal();
                        setTimeout(() => {
                            showLyricsModal(similar.id);
                        }, 300);
                    });
                    
                    similarSongsList.appendChild(similarCard);
                });
                
                document.getElementById('similar-songs-section').style.display = 'block';
            } else {
                document.getElementById('similar-songs-section').style.display = 'none';
            }
            
            // Show the modal
            modal.classList.add('open');
            document.body.style.overflow = 'hidden';
        })
        .catch(error => {
            console.error('Error fetching lyrics:', error);
            showNotification('Error loading lyrics. Please try again.', 'error');
        });
}

function closeModal() {
    const modal = document.getElementById('lyrics-modal');
    modal.classList.remove('open');
    document.body.style.overflow = 'auto';
}

function initArtistsSection() {
    // Check if artists grid exists before making the API call
    const artistsGrid = document.querySelector('.artists-grid');
    
    if (!artistsGrid) {
        return;
    }
    
    // Fetch artists data
    fetch('/api/artists')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(artists => {
            if (!artists || artists.length === 0) {
                artistsGrid.innerHTML = 
                    '<p class="text-center">No artists available yet.</p>';
                return;
            }
            
            // Create the artists grid
            artistsGrid.innerHTML = '';
            
            artists.forEach(artist => {
                const card = document.createElement('div');
                card.className = 'artist-card glass';
                
                // If image_url is not available, use a default placeholder
                const imageUrl = artist.image_url || 'https://via.placeholder.com/150?text=Artist';
                
                card.innerHTML = `
                    <img src="${imageUrl}" alt="${artist.name}" class="artist-image">
                    <div class="artist-info">
                        <h3 class="artist-name">${artist.name || 'Unknown Artist'}</h3>
                        <p class="artist-bio">${artist.bio || 'No bio available'}</p>
                    </div>
                `;
                
                artistsGrid.appendChild(card);
            });
        })
        .catch(error => {
            console.error('Error fetching artists:', error);
            artistsGrid.innerHTML = 
                '<p class="text-center">Error loading artists. Please try again later.</p>';
        });
}

function initScrollAnimations() {
    // Add scroll animations to elements
    const animateOnScroll = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, {
        threshold: 0.1
    });
    
    animateOnScroll.forEach(element => {
        observer.observe(element);
    });
}

function initContactForm() {
    // Initialize contact form submission
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Get form data
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const message = document.getElementById('message').value.trim();
            
            // Validate form data
            if (!name || !email || !message) {
                showNotification('Please fill out all fields.', 'error');
                return;
            }
            
            if (!isValidEmail(email)) {
                showNotification('Please enter a valid email address.', 'error');
                return;
            }
            
            // Submit form data
            submitContactForm(name, email, message);
        });
    }
}

function isValidEmail(email) {
    // Simple email validation
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function submitContactForm(name, email, message) {
    // Submit contact form data to the server
    const submitBtn = document.getElementById('submit-btn');
    
    // Disable submit button and show loading state
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';
    }
    
    // Send form data to the server
    fetch('/api/contact', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name,
            email,
            message
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Reset form
        document.getElementById('contact-form').reset();
        
        // Show success message
        showNotification('Your message has been sent successfully!', 'success');
    })
    .catch(error => {
        console.error('Error submitting contact form:', error);
        showNotification('Error sending message. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Send Message';
        }
    });
}

function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add notification to the DOM
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Hide and remove notification after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        
        // Remove from DOM after animation completes
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}
