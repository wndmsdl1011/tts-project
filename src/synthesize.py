import torch
from TTS.api import TTS

# 1. 학습된 모델 경로 설정
# 가장 성능이 좋았던 모델(best_model.pth)의 경로를 지정합니다.
# 실제 경로로 수정해야 합니다。
model_path = "C:\Users\wndmsdl\tts_project\models\<YOUR_RUN_NAME>\best_model.pth"
config_path = "C:\Users\wndmsdl\tts_project\models\<YOUR_RUN_NAME>\config.json"

# 2. 음성 생성할 텍스트
text_to_synthesize = "안녕하세요, 이것은 코키 TTS로 생성된 한국어 음성입니다."

# 3. 출력 파일 경로
output_wav_path = "C:\Users\wndmsdl\tts_project\output.wav"

# 4. TTS 객체 초기화
# GPU 사용 가능 여부를 자동으로 감지합니다.
tts = TTS(model_path=model_path, config_path=config_path, progress_bar=True, gpu=torch.cuda.is_available())

# 5. 텍스트로부터 음성 생성 및 저장
tts.tts_to_file(text=text_to_synthesize, file_path=output_wav_path)

print(f"--- 음성 생성이 완료되었습니다 ---")
print(f"생성된 파일은 다음 경로에 저장되었습니다: {output_wav_path}")
