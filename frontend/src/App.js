import React, { useState } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:8005';

function App() {
  const [text, setText] = useState('');
  const [audioUrl, setAudioUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 음성 복제 관련 상태
  const [voiceFile, setVoiceFile] = useState(null);
  const [language, setLanguage] = useState('en');
  const [mode, setMode] = useState('basic'); // 'basic' 또는 'clone'
  const [clonedAudioUrl, setClonedAudioUrl] = useState(null);

  const handleSynthesize = async () => {
    if (!text) {
      alert('음성으로 변환할 텍스트를 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setAudioUrl(null);

    try {
      const response = await fetch(`${API_BASE_URL}/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const audioBlob = await response.blob();
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

    } catch (e) {
      console.error("API 요청 중 오류 발생:", e);
      setError('음성 생성에 실패했습니다. API 서버가 실행 중인지 확인해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceClone = async () => {
    if (!text) {
      alert('음성으로 변환할 텍스트를 입력해주세요.');
      return;
    }

    if (!voiceFile) {
      alert('복제할 음성 파일을 선택해주세요.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setClonedAudioUrl(null);

    try {
      const formData = new FormData();
      formData.append('text', text);
      formData.append('language', language);
      formData.append('voice_file', voiceFile);

      const response = await fetch(`${API_BASE_URL}/clone-voice`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const audioBlob = await response.blob();
      const url = URL.createObjectURL(audioBlob);
      setClonedAudioUrl(url);

    } catch (e) {
      console.error("음성 복제 중 오류 발생:", e);
      setError('음성 복제에 실패했습니다. 음성 파일과 텍스트를 확인해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // 오디오 파일 확인
      if (file.type.startsWith('audio/')) {
        setVoiceFile(file);
      } else {
        alert('오디오 파일만 업로드 가능합니다.');
        e.target.value = '';
      }
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎤 Voice Cloning TTS</h1>
        <p>텍스트를 음성으로 변환하거나 자신의 목소리를 복제해보세요!</p>
        
        {/* 모드 선택 */}
        <div className="mode-selector">
          <button 
            className={mode === 'basic' ? 'active' : ''}
            onClick={() => setMode('basic')}
          >
            기본 TTS
          </button>
          <button 
            className={mode === 'clone' ? 'active' : ''}
            onClick={() => setMode('clone')}
          >
            음성 복제
          </button>
        </div>

        {/* 텍스트 입력 */}
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="여기에 텍스트를 입력하세요..."
          rows="5"
          disabled={isLoading}
        />

        {/* 음성 복제 모드일 때만 표시 */}
        {mode === 'clone' && (
          <div className="voice-clone-controls">
            <div className="file-upload">
              <label htmlFor="voice-file">음성 파일 업로드:</label>
              <input
                id="voice-file"
                type="file"
                accept="audio/*"
                onChange={handleFileChange}
                disabled={isLoading}
              />
              {voiceFile && <p>선택된 파일: {voiceFile.name}</p>}
            </div>

            <div className="language-select">
              <label htmlFor="language">언어 선택:</label>
              <select
                id="language"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                disabled={isLoading}
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="it">Italian</option>
                <option value="pt">Portuguese</option>
                <option value="pl">Polish</option>
                <option value="tr">Turkish</option>
                <option value="ru">Russian</option>
                <option value="nl">Dutch</option>
                <option value="cs">Czech</option>
                <option value="ar">Arabic</option>
                <option value="zh-cn">Chinese</option>
                <option value="hu">Hungarian</option>
                <option value="ko">Korean</option>
                <option value="ja">Japanese</option>
                <option value="hi">Hindi</option>
              </select>
            </div>
          </div>
        )}

        {/* 실행 버튼 */}
        {mode === 'basic' ? (
          <button onClick={handleSynthesize} disabled={isLoading}>
            {isLoading ? '음성 생성 중...' : '음성 생성하기'}
          </button>
        ) : (
          <button onClick={handleVoiceClone} disabled={isLoading}>
            {isLoading ? '음성 복제 중...' : '내 목소리로 생성하기'}
          </button>
        )}

        {/* 에러 메시지 */}
        {error && <p className="error-message">{error}</p>}

        {/* 기본 TTS 결과 */}
        {audioUrl && mode === 'basic' && (
          <div className="audio-player-container">
            <h3>생성된 음성 (기본):</h3>
            <audio controls src={audioUrl} />
            <a href={audioUrl} download="synthesized_audio.wav">
              다운로드
            </a>
          </div>
        )}

        {/* 음성 복제 결과 */}
        {clonedAudioUrl && mode === 'clone' && (
          <div className="audio-player-container">
            <h3>복제된 음성:</h3>
            <audio controls src={clonedAudioUrl} />
            <a href={clonedAudioUrl} download="cloned_voice.wav">
              다운로드
            </a>
          </div>
        )}

        {/* 사용법 안내 */}
        <div className="instructions">
          <h3>사용법:</h3>
          <ul>
            <li><strong>기본 TTS:</strong> 텍스트를 입력하고 '음성 생성하기' 버튼을 클릭</li>
            <li><strong>음성 복제:</strong> 
              <ol>
                <li>복제하고 싶은 음성 파일 업로드 (5-10초 권장)</li>
                <li>언어 선택</li>
                <li>텍스트 입력</li>
                <li>'내 목소리로 생성하기' 버튼 클릭</li>
              </ol>
            </li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;