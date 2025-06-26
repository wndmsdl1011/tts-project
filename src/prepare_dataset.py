import os

# --- 설정 ---
# KSS 데이터셋이 위치한 기본 경로
DATA_DIR = "C:/Users/wndmsdl/tts_project/data/"

# KSS 원본 대본 파일
TRANSCRIPT_FILE = os.path.join(DATA_DIR, "transcript.v.1.4.txt")

# Coqui TTS 학습에 사용할 출력 파일
OUTPUT_METADATA_FILE = os.path.join(DATA_DIR, "metadata.csv")


def run():
    """
    KSS 데이터셋의 transcript.v.1.4.txt 파일을 읽어
    Coqui TTS 학습에 필요한 metadata.csv 파일을 생성합니다.
    """
    print(f"원본 대본 파일 읽기 시작: {TRANSCRIPT_FILE}")

    try:
        with open(TRANSCRIPT_FILE, 'r', encoding='utf-8') as f_in, \
             open(OUTPUT_METADATA_FILE, 'w', encoding='utf-8') as f_out:
            
            for line in f_in:
                # 라인 형식: '2/2002/2002-3185-01-01-F-01-C.wav|그는 괜찮은 선수가 아니야.|...'
                parts = line.strip().split('|')
                
                if len(parts) < 2:
                    continue
                
                # wav 파일 경로에서 파일명만 추출
                wav_filename = os.path.basename(parts[0])
                text = parts[1]
                
                # Coqui TTS 형식으로 변환: 'wavs/파일명.wav|텍스트'
                new_line = f"wavs/{wav_filename}|{text}"
                f_out.write(new_line + '\n')

        print(f"성공적으로 metadata.csv 파일을 생성했습니다: {OUTPUT_METADATA_FILE}")
        print(f"이제 'python src/train_tts.py' 명령어로 학습을 시작할 수 있습니다.")

    except FileNotFoundError:
        print(f"[오류] 원본 대본 파일을 찾을 수 없습니다: {TRANSCRIPT_FILE}")
        print("KSS 데이터셋 다운로드 후 파일을 data 폴더로 올바르게 옮겼는지 확인해주세요.")
    except Exception as e:
        print(f"[오류] 파일 처리 중 문제가 발생했습니다: {e}")

if __name__ == '__main__':
    run()
