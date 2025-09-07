class TTSWebApp {
    constructor() {
        this.currentAudio = null;
        this.isPlaying = false;
        this.audioContext = null;
        this.analyser = null;
        this.animationId = null;
        this.currentAudioFile = null;
        
        this.initializeElements();
        this.setupEventListeners();
        this.updateStatus('준비 중...', 'ready');
        this.checkServerStatus();
    }

    initializeElements() {
        // 입력 요소들
        this.textInput = document.getElementById('textInput');
        this.charCount = document.getElementById('charCount');
        
        // 설정 요소들
        this.emotionSelect = document.getElementById('emotionSelect');
        this.speedSlider = document.getElementById('speedSlider');
        this.speedValue = document.getElementById('speedValue');
        this.exaggerationSlider = document.getElementById('exaggerationSlider');
        this.exaggerationValue = document.getElementById('exaggerationValue');
        this.cfgSlider = document.getElementById('cfgSlider');
        this.cfgValue = document.getElementById('cfgValue');
        
        // 버튼들
        this.generateBtn = document.getElementById('generateBtn');
        this.playBtn = document.getElementById('playBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.clearBtn = document.getElementById('clearBtn');
        
        // 오디오 관련
        this.audioPlayBtn = document.getElementById('audioPlayBtn');
        this.audioStopBtn = document.getElementById('audioStopBtn');
        this.audioProgress = document.getElementById('audioProgress');
        this.currentTime = document.getElementById('currentTime');
        this.totalTime = document.getElementById('totalTime');
        this.audioCanvas = document.getElementById('audioCanvas');
        
        // 상태 표시
        this.status = document.getElementById('status');
        this.statusDot = document.getElementById('statusDot');
        this.progressOverlay = document.getElementById('progressOverlay');
        this.progressText = document.getElementById('progressText');
        this.progressFill = document.getElementById('progressFill');
        
        // 토스트
        this.toast = document.getElementById('toast');
    }

    setupEventListeners() {
        // 텍스트 입력 이벤트
        this.textInput.addEventListener('input', () => {
            this.updateCharCount();
            this.validateInput();
        });

        // 슬라이더 이벤트
        this.speedSlider.addEventListener('input', () => {
            this.speedValue.textContent = `${this.speedSlider.value}x`;
        });

        this.exaggerationSlider.addEventListener('input', () => {
            this.exaggerationValue.textContent = this.exaggerationSlider.value;
        });

        this.cfgSlider.addEventListener('input', () => {
            this.cfgValue.textContent = this.cfgSlider.value;
        });

        // 버튼 이벤트
        this.generateBtn.addEventListener('click', () => this.generateTTS());
        this.playBtn.addEventListener('click', () => this.playAudio());
        this.downloadBtn.addEventListener('click', () => this.downloadAudio());
        this.clearBtn.addEventListener('click', () => this.clearAll());

        // 오디오 컨트롤 이벤트
        this.audioPlayBtn.addEventListener('click', () => this.toggleAudioPlayback());
        this.audioStopBtn.addEventListener('click', () => this.stopAudio());
        this.audioProgress.addEventListener('input', () => this.seekAudio());

        // 초기화
        this.updateCharCount();
        this.validateInput();
    }

    async checkServerStatus() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            if (data.model_ready) {
                this.updateStatus('서버 준비 완료!', 'ready');
                this.generateBtn.disabled = false;
            } else if (data.model_loading) {
                this.updateStatus('모델 로딩 중...', 'generating');
                this.generateBtn.disabled = true;
                // 2초 후 다시 확인
                setTimeout(() => this.checkServerStatus(), 2000);
            } else {
                this.updateStatus('서버 오류', 'ready');
                this.generateBtn.disabled = true;
            }
        } catch (error) {
            console.error('서버 상태 확인 실패:', error);
            this.updateStatus('서버 연결 실패', 'ready');
            this.generateBtn.disabled = true;
        }
    }

    updateCharCount() {
        const count = this.textInput.value.length;
        this.charCount.textContent = count;
        
        if (count > 450) {
            this.charCount.style.color = '#ff6b6b';
        } else if (count > 400) {
            this.charCount.style.color = '#ffd43b';
        } else {
            this.charCount.style.color = '#666';
        }
    }

    validateInput() {
        const hasText = this.textInput.value.trim().length > 0;
        this.generateBtn.disabled = !hasText;
    }

    updateStatus(message, type = 'ready') {
        this.status.textContent = message;
        this.statusDot.className = `status-dot ${type}`;
    }

    showToast(message, type = 'success') {
        const toastContent = this.toast.querySelector('.toast-content');
        const toastIcon = toastContent.querySelector('.toast-icon');
        const toastMessage = toastContent.querySelector('.toast-message');
        
        // 아이콘 설정
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle'
        };
        
        toastIcon.className = `toast-icon ${icons[type] || icons.success}`;
        toastMessage.textContent = message;
        
        // 토스트 클래스 설정
        this.toast.className = `toast ${type}`;
        this.toast.classList.remove('hidden');
        this.toast.classList.add('show');
        
        // 3초 후 자동 숨김
        setTimeout(() => {
            this.toast.classList.remove('show');
            setTimeout(() => {
                this.toast.classList.add('hidden');
            }, 300);
        }, 3000);
    }

    showProgress(message) {
        this.progressText.textContent = message;
        this.progressOverlay.classList.remove('hidden');
    }

    hideProgress() {
        this.progressOverlay.classList.add('hidden');
    }

    updateProgress(percent) {
        this.progressFill.style.width = `${percent}%`;
    }

    async generateTTS() {
        const text = this.textInput.value.trim();
        if (!text) {
            this.showToast('텍스트를 입력해주세요!', 'warning');
            return;
        }

        this.showProgress('음성을 생성하는 중...');
        this.updateStatus('음성 생성 중...', 'generating');
        this.generateBtn.disabled = true;

        try {
            const data = {
                text: text,
                emotion: this.emotionSelect.value,
                speed: parseFloat(this.speedSlider.value),
                exaggeration: parseFloat(this.exaggerationSlider.value),
                cfgWeight: parseFloat(this.cfgSlider.value)
            };

            this.updateProgress(20);
            
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            this.updateProgress(80);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.currentAudioFile = result.audioFile;
                this.setupAudioPlayer(result.audioFile, result.userId);
                this.playBtn.disabled = false;
                this.downloadBtn.disabled = false;
                this.audioPlayBtn.disabled = false;
                
                this.updateProgress(100);
                this.showToast('음성 생성이 완료되었습니다!', 'success');
                this.updateStatus('음성 생성 완료!', 'ready');
            } else {
                throw new Error(result.error || '음성 생성에 실패했습니다.');
            }
        } catch (error) {
            console.error('TTS Generation Error:', error);
            this.showToast(`음성 생성 실패: ${error.message}`, 'error');
            this.updateStatus('음성 생성 실패', 'ready');
        } finally {
            this.hideProgress();
            this.generateBtn.disabled = false;
        }
    }

    setupAudioPlayer(audioFile, userId = null) {
        let audioUrl;
        if (userId) {
            audioUrl = `/api/audio/${userId}/${audioFile}`;
        } else {
            audioUrl = `/api/audio/${audioFile}`;
        }
        
        this.currentAudio = new Audio(audioUrl);
        
        this.currentAudio.addEventListener('loadedmetadata', () => {
            this.totalTime.textContent = this.formatTime(this.currentAudio.duration);
            this.audioProgress.max = this.currentAudio.duration;
        });

        this.currentAudio.addEventListener('timeupdate', () => {
            if (this.audioProgress.max > 0) {
                this.audioProgress.value = this.currentAudio.currentTime;
                this.currentTime.textContent = this.formatTime(this.currentAudio.currentTime);
            }
        });

        this.currentAudio.addEventListener('ended', () => {
            this.isPlaying = false;
            this.updatePlayButton();
            this.stopVisualization();
        });

        this.currentAudio.addEventListener('play', () => {
            this.isPlaying = true;
            this.updatePlayButton();
            this.startVisualization();
        });

        this.currentAudio.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updatePlayButton();
            this.stopVisualization();
        });
    }

    updatePlayButton() {
        const icon = this.audioPlayBtn.querySelector('i');
        if (this.isPlaying) {
            icon.className = 'fas fa-pause';
        } else {
            icon.className = 'fas fa-play';
        }
    }

    toggleAudioPlayback() {
        if (!this.currentAudio) return;

        if (this.isPlaying) {
            this.currentAudio.pause();
        } else {
            this.currentAudio.play();
        }
    }

    stopAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            this.audioProgress.value = 0;
            this.currentTime.textContent = '0:00';
        }
    }

    seekAudio() {
        if (this.currentAudio && this.audioProgress.max > 0) {
            this.currentAudio.currentTime = this.audioProgress.value;
        }
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    startVisualization() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            
            const source = this.audioContext.createMediaElementSource(this.currentAudio);
            source.connect(this.analyser);
            this.analyser.connect(this.audioContext.destination);
        }

        this.drawVisualization();
    }

    stopVisualization() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        
        // 캔버스 클리어
        const canvas = this.audioCanvas;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    drawVisualization() {
        if (!this.analyser) return;

        const canvas = this.audioCanvas;
        const ctx = canvas.getContext('2d');
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            this.animationId = requestAnimationFrame(draw);

            this.analyser.getByteFrequencyData(dataArray);

            ctx.fillStyle = '#f8f9fa';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const barWidth = (canvas.width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                barHeight = (dataArray[i] / 255) * canvas.height;

                const gradient = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - barHeight);
                gradient.addColorStop(0, '#667eea');
                gradient.addColorStop(1, '#764ba2');

                ctx.fillStyle = gradient;
                ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);

                x += barWidth + 1;
            }
        };

        draw();
    }

    downloadAudio() {
        if (!this.currentAudioFile) {
            this.showToast('다운로드할 오디오가 없습니다.', 'warning');
            return;
        }

        try {
            // 현재 오디오 URL을 사용하여 다운로드
            const link = document.createElement('a');
            link.href = this.currentAudio.src;
            link.download = this.currentAudioFile;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showToast('오디오 파일이 다운로드되었습니다!', 'success');
        } catch (error) {
            console.error('Download Error:', error);
            this.showToast('파일 다운로드에 실패했습니다.', 'error');
        }
    }

    clearAll() {
        this.textInput.value = '';
        this.updateCharCount();
        this.validateInput();
        
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
        
        this.playBtn.disabled = true;
        this.downloadBtn.disabled = true;
        this.audioPlayBtn.disabled = true;
        this.audioStopBtn.disabled = true;
        
        this.stopVisualization();
        this.audioProgress.value = 0;
        this.currentTime.textContent = '0:00';
        this.totalTime.textContent = '0:00';
        this.currentAudioFile = null;
        
        this.showToast('모든 내용이 초기화되었습니다.', 'success');
    }

    playAudio() {
        if (this.currentAudio) {
            this.toggleAudioPlayback();
        } else {
            this.showToast('재생할 오디오가 없습니다.', 'warning');
        }
    }
}

// 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    const app = new TTSWebApp();
    
    // 전역에서 접근 가능하도록 설정
    window.ttsApp = app;
});
