import os
from trainer import Trainer, TrainerArgs
from TTS.config.loader import load_config
from TTS.tts.datasets import load_tts_samples
from TTS.tts.models.glow_tts import GlowTTS
from TTS.tts.utils.text.tokenizer import TTSTokenizer
from TTS.utils.audio import AudioProcessor

# 1. 학습 설정 파일 불러오기
# config.json 파일의 절대 경로를 지정합니다.
config_path = "C:\Users\wndmsdl\tts_project\config.json"
C = load_config(config_path)

# 2. 오디오 처리기 초기화
# 오디오 데이터를 모델이 처리할 수 있는 형태로 변환합니다.
ap = AudioProcessor.init_from_config(C)

# 3. 토크나이저(Tokenizer) 초기화
# 텍스트를 모델이 이해할 수 있는 숫자 시퀀스(토큰)로 변환합니다.
tokenizer, C = TTSTokenizer.init_from_config(C)

# 4. 학습 데이터셋 불러오기
# metadata.csv 파일을 기반으로 학습 및 검증 데이터 샘플을 불러옵니다.
train_samples, eval_samples = load_tts_samples(
    C.datasets,
    eval_split=True,
    eval_split_max_size=C.eval_split_max_size,
    eval_split_size=C.eval_split_size,
)

# 5. 모델 초기화 (GlowTTS)
# 단일 화자 모델이므로 speaker_manager는 None으로 설정합니다.
model = GlowTTS(C, ap, tokenizer, speaker_manager=None)

# 6. 학습기(Trainer) 초기화
# 모델 학습을 관리하는 Trainer를 설정합니다.
# GPU 사용이 강력하게 권장됩니다.
trainer = Trainer(
    TrainerArgs(),
    C,
    output_path=C.output_path,
    model=model,
    train_samples=train_samples,
    eval_samples=eval_samples,
)

# 7. 모델 학습 시작
# fit() 함수를 호출하여 실제 학습을 시작합니다.
trainer.fit()

print("--- 학습이 완료되었습니다 ---")
print(f"모델은 다음 경로에 저장되었습니다: {C.output_path}")
