import torch
import uvicorn
from fastapi import FastAPI, Response, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from TTS.api import TTS
import io
import os
import tempfile
from typing import Optional
import warnings

# 🆓 무료 음성 복제 라이브러리들
try:
    import speechbrain as sb
    SPEECHBRAIN_AVAILABLE = True
    print("✅ SpeechBrain 로딩 성공 - 무료 음성 복제 사용 가능!")
except ImportError:
    SPEECHBRAIN_AVAILABLE = False
    print("❌ SpeechBrain 사용 불가")

# 🔧 PyTorch 및 Transformers 호환성 문제 해결
def apply_compatibility_patches():
    """PyTorch 2.x와 Transformers 호환성 문제 해결"""
    try:
        # 1. PyTorch weights_only 문제 해결
        import torch
        original_load = torch.load
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        torch.load = patched_load
        print("✅ PyTorch weights_only 패치 적용")
        
        # 2. Transformers GenerationMixin 문제 해결
        try:
            from transformers import PreTrainedModel, GenerationMixin
            if not hasattr(PreTrainedModel, 'generate'):
                # generate 메서드를 직접 추가
                def dummy_generate(self, *args, **kwargs):
                    raise NotImplementedError("Generate method not available")
                PreTrainedModel.generate = dummy_generate
                print("✅ Transformers GenerationMixin 패치 적용")
        except Exception as e:
            print(f"⚠️ Transformers 패치 실패: {e}")
        
        # 3. TTS 관련 전역 설정
        try:
            from TTS.tts.configs.xtts_config import XttsConfig
            torch.serialization.add_safe_globals([XttsConfig])
            print("✅ TTS 안전 글로벌 설정 추가")
        except Exception as e:
            print(f"⚠️ TTS 글로벌 설정 실패: {e}")
            
        # 4. 경고 무시
        warnings.filterwarnings("ignore", category=FutureWarning)
        warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
        print("✅ 경고 메시지 필터링 적용")
        
        return True
    except Exception as e:
        print(f"❌ 호환성 패치 실패: {e}")
        return False

# 호환성 패치 적용
compatibility_success = apply_compatibility_patches()

# --- 설정 ---
# 다중 모델 지원을 위한 모델 리스트 (우선순위 순)
MODEL_OPTIONS = [
    {
        "name": "tts_models/multilingual/multi-dataset/xtts_v2",
        "type": "xtts",
        "description": "XTTS v2 (음성 복제 지원)",
        "voice_cloning": True
    },
    {
        "name": "tts_models/en/ljspeech/tacotron2-DDC",
        "type": "basic",
        "description": "Tacotron2 (기본 TTS)",
        "voice_cloning": False
    },
    {
        "name": "tts_models/en/ljspeech/speedy-speech",
        "type": "basic",
        "description": "Speedy Speech (빠른 TTS)",
        "voice_cloning": False
    }
]

# --- FastAPI 앱 초기화 ---
app = FastAPI(
    title="Voice Cloning TTS API",
    description="A TTS API with voice cloning capabilities using Coqui TTS models.",
    version="3.0.0"
)

# --- CORS 미들웨어 추가 ---
origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://192.168.56.1:3000",
    "http://192.168.56.1:3001",
    "*"  # 개발 환경에서 모든 origin 허용
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- TTS 모델 로드 ---
tts_model = None
model_type = "none"
MODEL_NAME = None

def load_model_with_fallback():
    """여러 모델을 순차적으로 시도하여 로드"""
    global tts_model, model_type, MODEL_NAME
    
    for model_option in MODEL_OPTIONS:
        try:
            print(f"\n🔄 모델 로딩 시도: {model_option['name']}")
            print(f"   설명: {model_option['description']}")
            
            # GPU 사용 가능 여부 확인
            use_gpu = torch.cuda.is_available()
            print(f"   GPU 사용: {use_gpu}")
            
            # 모델 로딩 시도
            tts_model = TTS(
                model_option['name'], 
                progress_bar=True, 
                gpu=use_gpu
            )
            
            model_type = model_option['type']
            MODEL_NAME = model_option['name']
            
            print(f"✅ 모델 로딩 성공!")
            print(f"   모델 타입: {model_type}")
            print(f"   음성 복제 지원: {model_option['voice_cloning']}")
            return True
            
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            print(f"   에러 타입: {type(e).__name__}")
            continue
    
    print("❌ 모든 모델 로딩 실패")
    return False

# 모델 로딩 실행
model_loaded = load_model_with_fallback()

if not model_loaded:
    print("⚠️ 서버가 TTS 모델 없이 시작됩니다.")
    print("   /model-info 엔드포인트에서 상태를 확인할 수 있습니다.")

# --- 요청 Body 모델 정의 ---
class TTSRequest(BaseModel):
    text: str

class VoiceCloneRequest(BaseModel):
    text: str
    language: str = "en"

# --- API 엔드포인트 정의 ---
@app.post("/synthesize")
def synthesize_speech(request: TTSRequest):
    """
    기본 TTS: 입력된 텍스트를 기본 음성으로 변환
    """
    if not tts_model:
        return Response(content="TTS model is not loaded.", status_code=500)

    try:
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_path = tmp_file.name
        
        # 기본 음성으로 TTS 실행
        tts_model.tts_to_file(text=request.text, file_path=tmp_path)
        
        with open(tmp_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        os.unlink(tmp_path)
        
        return Response(content=audio_data, media_type="audio/wav")

    except Exception as e:
        return Response(content=f"Error during synthesis: {e}", status_code=500)

@app.post("/clone-voice")
async def clone_voice(
    text: str = Form(...),
    language: str = Form("en"),
    voice_file: UploadFile = File(...)
):
    """
    음성 복제: 업로드된 음성을 참조하여 음성 합성
    """
    voice_tmp_path = None
    output_tmp_path = None

    try:
        if not tts_model:
            return Response(content="TTS model is not loaded.", status_code=500)
        
        # 업로드된 음성 파일을 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as voice_tmp:
            voice_content = await voice_file.read()
            voice_tmp.write(voice_content)
            voice_tmp_path = voice_tmp.name

        # 출력 음성 파일을 위한 임시 파일
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as output_tmp:
            output_tmp_path = output_tmp.name

        print(f"\n🎤 음성 복제 시작")
        print(f"   파일: {voice_file.filename}")
        print(f"   텍스트: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"   언어: {language}")
        print(f"   모델 타입: {model_type}")
        
        # XTTS v2 지원 언어
        supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh-cn', 'hu', 'ko', 'ja', 'hi']
        
        # 언어 코드 정규화
        language_map = {
            "ko": "ko", "kr": "ko",  # 한국어
            "en": "en",  # 영어
            "es": "es",  # 스페인어
            "fr": "fr",  # 프랑스어
            "de": "de",  # 독일어
            "it": "it",  # 이탈리아어
            "pt": "pt",  # 포르투갈어
            "zh": "zh-cn", "zh-cn": "zh-cn",  # 중국어
            "ja": "ja",  # 일본어
        }
        
        xtts_language = language_map.get(language, language)
        if xtts_language not in supported_languages:
            xtts_language = "en"  # 기본값
        
        print(f"   정규화된 언어: {xtts_language}")
        
        # 🎯 모델 타입별 처리
        success = False
        
        if model_type == "xtts":
            # XTTS v2 음성 복제 시도
            success = await try_xtts_cloning(text, voice_tmp_path, xtts_language, output_tmp_path)
        
        if not success:
            # 기본 TTS로 대체 (음성 복제 없음)
            success = await try_basic_tts(text, output_tmp_path)
        
        if not success:
            raise Exception("모든 TTS 방법이 실패했습니다.")
        
        # 생성된 음성 파일 읽기
        with open(output_tmp_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        print(f"✅ 음성 생성 완료: {len(audio_data)} bytes")
        
        return Response(content=audio_data, media_type="audio/wav")

    except Exception as e:
        print(f"❌ 음성 복제 에러: {e}")
        return Response(content=f"Error during voice cloning: {e}", status_code=500)
    
    finally:
        # 임시 파일들 정리
        cleanup_temp_files(voice_tmp_path, output_tmp_path)

async def try_xtts_cloning(text: str, voice_path: str, language: str, output_path: str) -> bool:
    """XTTS v2 음성 복제 시도"""
    try:
        print("🎯 XTTS v2 음성 복제 시도...")
        
        # 방법 1: 언어 매개변수와 함께
        try:
            tts_model.tts_to_file(
                text=text,
                speaker_wav=voice_path,
                language=language,
                file_path=output_path
            )
            print("✅ XTTS v2 음성 복제 성공 (언어 매개변수 포함)")
            return True
        except Exception as e:
            print(f"   언어 매개변수 포함 실패: {e}")
        
        # 방법 2: 언어 매개변수 없이
        try:
            tts_model.tts_to_file(
                text=text,
                speaker_wav=voice_path,
                file_path=output_path
            )
            print("✅ XTTS v2 음성 복제 성공 (언어 매개변수 없음)")
            return True
        except Exception as e:
            print(f"   언어 매개변수 없이도 실패: {e}")
        
        # 방법 3: 새로운 XTTS 인스턴스로 시도
        try:
            print("   새로운 XTTS 인스턴스 생성 시도...")
            new_tts = TTS(MODEL_NAME, progress_bar=False, gpu=torch.cuda.is_available())
            new_tts.tts_to_file(
                text=text,
                speaker_wav=voice_path,
                language=language,
                file_path=output_path
            )
            print("✅ 새로운 XTTS 인스턴스로 성공")
            return True
        except Exception as e:
            print(f"   새로운 인스턴스도 실패: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ XTTS 복제 전체 실패: {e}")
        return False

async def try_basic_tts(text: str, output_path: str) -> bool:
    """기본 TTS 시도 (음성 복제 없음)"""
    try:
        print("🔊 기본 TTS 시도 (음성 복제 없음)...")
        
        tts_model.tts_to_file(text=text, file_path=output_path)
        print("✅ 기본 TTS 성공")
        return True
        
    except Exception as e:
        print(f"❌ 기본 TTS 실패: {e}")
        return False

def cleanup_temp_files(*file_paths):
    """임시 파일들 정리"""
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except Exception as e:
                print(f"⚠️ 임시 파일 정리 실패 ({file_path}): {e}")

@app.get("/model-info")
def get_model_info():
    """현재 로드된 모델 정보 반환"""
    if tts_model:
        return {
            "status": "loaded",
            "model_name": MODEL_NAME,
            "model_type": model_type,
            "supports_voice_cloning": model_type == "xtts",
            "compatibility_patches": compatibility_success,
            "available_features": {
                "basic_tts": True,
                "voice_cloning": model_type == "xtts",
                "multi_language": model_type == "xtts"
            },
            "supported_languages": supported_languages if model_type == "xtts" else ["en"]
        }
    else:
        return {
            "status": "not_loaded",
            "model_name": None,
            "model_type": "none",
            "supports_voice_cloning": False,
            "compatibility_patches": compatibility_success,
            "available_features": {
                "basic_tts": False,
                "voice_cloning": False,
                "multi_language": False
            },
            "supported_languages": []
        }

@app.get("/")
def root():
    return {"message": "Voice Cloning TTS API", "version": "3.0.0"}

# --- 서버 실행 ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
