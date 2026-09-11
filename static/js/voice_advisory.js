/**
 * Pashu Suraksha - Multilingual Voice Synthesis & Farmer Advisory Engine
 * Uses Web Speech API for in-browser Text-to-Speech playback in Indian regional languages.
 */

class VoiceAdvisoryManager {
  constructor() {
    this.synth = window.speechSynthesis;
    this.currentUtterance = null;
    this.isPlaying = false;
    this.voices = [];
    this.initVoices();
  }

  initVoices() {
    if (!this.synth) return;
    this.voices = this.synth.getVoices();
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = () => {
        this.voices = this.synth.getVoices();
      };
    }
  }

  speak(text, langCode = 'hi-IN', onEndCallback = null) {
    if (!this.synth) {
      alert('Speech synthesis is not supported on this device/browser.');
      return;
    }

    this.stop(); // Stop any ongoing speech

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = 0.92; // slightly slower for rural comprehension
    utterance.pitch = 1.0;

    // Try finding matching voice
    const matchedVoice = this.voices.find(v => v.lang.startsWith(langCode.split('-')[0]));
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    utterance.onstart = () => {
      this.isPlaying = true;
      this.updateVoiceButtonState(true);
    };

    utterance.onend = () => {
      this.isPlaying = false;
      this.updateVoiceButtonState(false);
      if (onEndCallback) onEndCallback();
    };

    utterance.onerror = (e) => {
      console.warn('Speech synthesis notice:', e);
      this.isPlaying = false;
      this.updateVoiceButtonState(false);
    };

    this.currentUtterance = utterance;
    this.synth.speak(utterance);
  }

  stop() {
    if (this.synth) {
      this.synth.cancel();
      this.isPlaying = false;
      this.updateVoiceButtonState(false);
    }
  }

  updateVoiceButtonState(speaking) {
    const playBtn = document.getElementById('playAdvisoryAudioBtn');
    if (!playBtn) return;

    if (speaking) {
      playBtn.className = 'btn btn-danger';
      playBtn.innerHTML = `⏹ Stop Voice Broadcast`;
    } else {
      playBtn.className = 'btn btn-primary';
      playBtn.innerHTML = `🔊 Play Audio Advisory (आवाज़ सुनें)`;
    }
  }

  togglePlayback(text, langCode) {
    if (this.isPlaying) {
      this.stop();
    } else {
      this.speak(text, langCode);
    }
  }
}

window.VoiceManager = new VoiceAdvisoryManager();
