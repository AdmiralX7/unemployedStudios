// Audio Manager Class for handling all game audio
class AudioManager {
    constructor() {
        this.audioElements = {};
        this.loadAudio();
        this.initializeVolumes();
    }
    
    // Load and manage audio resources
    loadAudio() {
        // UI sounds
        this.audioElements = {
            click: this.createAudioElement('assets/audio/button_click_sound.mp3'),
            hover: this.createAudioElement('assets/audio/menu_transition_sound.mp3'),
            
            // Game sounds
            jump: this.createAudioElement('assets/audio/jump_sound.mp3'),
            collect: this.createAudioElement('assets/audio/collect_item_sound.mp3'),
            enemyDefeat: this.createAudioElement('assets/audio/enemy_defeat_sound.mp3'),
            
            // Music
            universityMusic: this.createAudioElement('assets/audio/university_music.mp3'),
            internshipMusic: this.createAudioElement('assets/audio/internship_music.mp3'),
            
            // Ambient
            universityAmbient: this.createAudioElement('assets/audio/university_ambient.mp3')
        };
    }
    
    initializeVolumes() {
        // Set appropriate volumes for different types of audio
        const volumes = {
            click: 0.6,
            hover: 0.4,
            jump: 0.5,
            collect: 0.6,
            enemyDefeat: 0.7,
            universityMusic: 0.4,
            internshipMusic: 0.4,
            universityAmbient: 0.2
        };
        
        for (const [key, volume] of Object.entries(volumes)) {
            if (this.audioElements[key]) {
                this.audioElements[key].volume = volume;
            }
        }
    }
    
    // Helper function to create audio elements
    createAudioElement(src) {
        const audio = new Audio(src);
        audio.preload = 'auto';
        return audio;
    }
    
    // Play a sound by key
    playSound(key) {
        if (this.audioElements[key]) {
            const audio = this.audioElements[key].cloneNode(); // clone to allow overlapping
            audio.volume = this.audioElements[key].volume;
            audio.play().catch(e => console.error('Play failed:', e));
        } else {
            console.warn(`Sound ${key} not found.`);
        }
    }
    
    // Play background music
    playMusic(key, loop = true) {
        if (this.audioElements[key]) {
            const music = this.audioElements[key];
            music.loop = loop;
            music.play().catch(e => console.error('Music playback failed:', e));
        }
    }
    
    // Stop specific music
    stopMusic(key) {
        if (this.audioElements[key]) {
            const music = this.audioElements[key];
            music.pause();
            music.currentTime = 0;
        }
    }
    
    // Stop all music
    stopAllMusic() {
        ['universityMusic', 'internshipMusic', 'universityAmbient'].forEach(key => {
            this.stopMusic(key);
        });
    }
}

// Export the AudioManager class
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioManager;
} else {
    window.AudioManager = AudioManager;
} 