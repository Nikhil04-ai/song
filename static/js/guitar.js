// Guitar string sound functionality

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the audio context
    let audioContext;
    
    // Initialize the guitar strings
    initGuitar();
    
    function initGuitar() {
        const guitarStrings = document.querySelectorAll('.guitar-string');
        
        if (guitarStrings.length === 0) return;
        
        // Create audio context on first user interaction
        const initAudio = () => {
            // Create audio context if it doesn't exist yet
            if (!audioContext) {
                try {
                    window.AudioContext = window.AudioContext || window.webkitAudioContext;
                    audioContext = new AudioContext();
                } catch (e) {
                    console.error('Web Audio API is not supported in this browser.');
                    return;
                }
            }
            
            // Remove the initialization event listeners once audio context is created
            document.removeEventListener('click', initAudio);
            document.removeEventListener('keydown', initAudio);
            document.removeEventListener('touchstart', initAudio);
        };
        
        // Wait for user interaction to create audio context (browser requirement)
        document.addEventListener('click', initAudio);
        document.addEventListener('keydown', initAudio);
        document.addEventListener('touchstart', initAudio);
        
        // Add click events to guitar strings
        guitarStrings.forEach(string => {
            string.addEventListener('click', () => playNote(string));
            string.addEventListener('touchstart', (e) => {
                e.preventDefault();
                playNote(string);
            });
        });
    }
    
    function playNote(stringElement) {
        // Don't do anything if audio context isn't initialized
        if (!audioContext) return;
        
        // Get frequency from data attribute
        const frequency = parseFloat(stringElement.dataset.frequency);
        
        // Add active class for animation
        stringElement.classList.add('active');
        setTimeout(() => {
            stringElement.classList.remove('active');
        }, 500);
        
        // Create oscillator
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        // Connect oscillator to gain and gain to audio output
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Set oscillator type and frequency
        oscillator.type = 'sine';
        oscillator.frequency.value = frequency;
        
        // Set gain value to 0.5 (volume)
        gainNode.gain.setValueAtTime(0.5, audioContext.currentTime);
        
        // Schedule the note to start now and stop in 1 second
        oscillator.start();
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 1);
        oscillator.stop(audioContext.currentTime + 1);
    }
    
    // Keyboard controls for guitar strings (1-7 keys)
    document.addEventListener('keydown', (e) => {
        // Check if audio context has been initialized
        if (!audioContext) return;
        
        const keyToString = {
            '1': 0, // Sa
            '2': 1, // Re
            '3': 2, // Ga
            '4': 3, // Ma
            '5': 4, // Pa
            '6': 5, // Dha
            '7': 6  // Ni
        };
        
        if (keyToString.hasOwnProperty(e.key)) {
            const stringIndex = keyToString[e.key];
            const guitarStrings = document.querySelectorAll('.guitar-string');
            
            if (guitarStrings.length > stringIndex) {
                playNote(guitarStrings[stringIndex]);
            }
        }
    });
});