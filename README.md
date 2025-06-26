# 🎤 Korean TTS with Voice Cloning

한국어를 포함한 다국어 TTS(Text-to-Speech) 및 음성 복제 기능을 제공하는 웹 애플리케이션입니다.

## ✨ 주요 기능

- **다국어 TTS**: 한국어, 영어, 일본어, 중국어 등 17개 언어 지원
- **음성 복제**: 사용자의 음성을 학습하여 해당 음성으로 텍스트를 읽어주는 기능
- **웹 인터페이스**: React.js 기반의 사용자 친화적인 웹 UI
- **RESTful API**: FastAPI 기반의 백엔드 API

## 🚀 기술 스택

### 백엔드
- **Python 3.11+**
- **FastAPI**: 웹 API 프레임워크
- **Coqui TTS**: XTTS v2 모델을 활용한 음성 합성
- **SpeechBrain**: 무료 음성 처리 라이브러리
- **PyTorch**: 딥러닝 프레임워크

### 프론트엔드
- **React.js**: 사용자 인터페이스
- **JavaScript (ES6+)**: 모던 자바스크립트

## 📋 시스템 요구사항

- **Python**: 3.11 이상
- **Node.js**: 18.0 이상
- **메모리**: 최소 8GB RAM (GPU 권장)
- **디스크**: 최소 10GB 여유 공간

## 🛠️ 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/YOUR_USERNAME/korean-tts-voice-cloning.git
cd korean-tts-voice-cloning
```

### 2. Python 환경 설정

```bash
# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. Node.js 환경 설정

```bash
cd frontend
npm install
```

### 4. 서버 실행

#### 백엔드 (API 서버)
```bash
# 프로젝트 루트에서
python src/api.py
```
서버가 `http://localhost:8005`에서 실행됩니다.

#### 프론트엔드 (웹 UI)
```bash
cd frontend
npm start
```
웹 애플리케이션이 `http://localhost:3000`에서 실행됩니다.

## 📱 사용 방법

### 기본 TTS
1. 웹 브라우저에서 `http://localhost:3000` 접속
2. "기본 TTS" 모드 선택
3. 텍스트 입력 후 "음성 생성" 클릭

### 음성 복제
1. "음성 복제" 모드 선택
2. 복제할 음성 파일 업로드 (.wav, .mp3 지원)
3. 언어 선택 (한국어, 영어 등)
4. 텍스트 입력 후 "음성 복제" 클릭

## 🌏 지원 언어

- 🇰🇷 한국어 (ko)
- 🇺🇸 영어 (en)
- 🇯🇵 일본어 (ja)
- 🇨🇳 중국어 (zh-cn)
- 🇪🇸 스페인어 (es)
- 🇫🇷 프랑스어 (fr)
- 🇩🇪 독일어 (de)
- 🇮🇹 이탈리아어 (it)
- 🇵🇹 포르투갈어 (pt)
- 🇵🇱 폴란드어 (pl)
- 🇹🇷 터키어 (tr)
- 🇷🇺 러시아어 (ru)
- 🇳🇱 네덜란드어 (nl)
- 🇨🇿 체코어 (cs)
- 🇸🇦 아랍어 (ar)
- 🇭🇺 헝가리어 (hu)
- 🇮🇳 힌디어 (hi)

## 🔧 API 엔드포인트

### 기본 TTS
```
POST /synthesize
Content-Type: application/json

{
  "text": "안녕하세요, TTS 테스트입니다."
}
```

### 음성 복제
```
POST /clone-voice
Content-Type: multipart/form-data

text: "복제할 텍스트"
language: "ko"
voice_file: [음성 파일]
```

### 모델 정보
```
GET /model-info
```

### 헬스 체크
```
GET /health
```

## 🗂️ 프로젝트 구조

```
korean-tts-voice-cloning/
├── src/
│   ├── api.py              # FastAPI 백엔드 서버
│   ├── prepare_dataset.py  # 데이터셋 준비 스크립트
│   ├── synthesize.py       # TTS 합성 유틸리티
│   └── train_tts.py        # 모델 학습 스크립트
├── frontend/
│   ├── src/
│   │   ├── App.js          # React 메인 컴포넌트
│   │   ├── App.css         # 스타일시트
│   │   └── index.js        # React 엔트리 포인트
│   ├── public/
│   └── package.json        # Node.js 종속성
├── korean_sample1.wav      # 한국어 샘플 음성 1
├── korean_sample2.wav      # 한국어 샘플 음성 2
├── korean_sample3.wav      # 한국어 샘플 음성 3
├── requirements.txt        # Python 종속성
├── config.json            # 설정 파일
└── README.md              # 프로젝트 문서
```

## 🐛 문제 해결

### 일반적인 문제들

1. **모델 로딩 실패**
   - 인터넷 연결을 확인하세요 (첫 실행 시 모델 다운로드 필요)
   - 디스크 공간을 확인하세요 (모델은 약 2-3GB)

2. **포트 충돌**
   - 다른 애플리케이션이 포트를 사용 중인지 확인하세요
   - `src/api.py`에서 포트 번호를 변경할 수 있습니다

3. **음성 복제 실패**
   - 업로드한 음성 파일이 명확하고 노이즈가 적은지 확인하세요
   - 지원되는 오디오 형식(.wav, .mp3)을 사용하세요

### macOS 특별 고려사항

```bash
# macOS에서 필요할 수 있는 추가 설정
brew install portaudio
pip install pyaudio
```

### GPU 지원

CUDA가 설치된 시스템에서는 GPU 가속을 자동으로 사용합니다:
```bash
# CUDA 지원 PyTorch 설치 (선택사항)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 🤝 기여하기

1. 저장소를 포크하세요
2. 기능 브랜치를 생성하세요 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성하세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙏 감사의 말

- [Coqui TTS](https://github.com/coqui-ai/TTS) - 훌륭한 TTS 라이브러리
- [SpeechBrain](https://speechbrain.github.io/) - 무료 음성 처리 툴킷
- [FastAPI](https://fastapi.tiangolo.com/) - 빠르고 현대적인 웹 프레임워크
- [React](https://reactjs.org/) - 사용자 인터페이스 라이브러리

---

문제가 있거나 제안사항이 있으시면 이슈를 생성해 주세요! 🚀