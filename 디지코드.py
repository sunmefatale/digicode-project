import csv
import os  # 파일 존재 여부 확인용
from datetime import datetime  # 날짜 기록용
from collections import defaultdict, Counter  # 도감 정리 및 카운팅용
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
from wcwidth import wcswidth  # 이모지/한글 길이 정확하게 계산 pip install wcwidth 설치해야

# 진화 메시지 출력 함수
def print_evolution_message(evolved_name, action):
    if action in action_messages:
        message = f"{evolved_name} : {action_messages[action]}"
        msg_width = wcswidth(message)
        border = "═" * (msg_width + 4)

        
        print("╔" + border + "╗")
        print("║  " + message + "  ║")
        print("╚" + border + "╝")
        


# 한글 폰트 설정 (matplotlib용)
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')  # Windows 기본 한글 폰트
else:
    plt.rc('font', family='AppleGothic')  # Mac일 경우

# 마이너스 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False





# 진화 딕셔너리 (감정 + 행동 => 진화체 이름)
evolution_dict = {
    # 화남
    ("화남", "매운걸 먹었다"): "🔥 분노의 매콤몬",
    ("화남", "단걸 먹었다"): "🍫 화를 삭이는 초코몬",
    ("화남", "운동을 했다"): "💪 근육몬",
    ("화남", "무언갈 샀다"): "💸 충동의 쇼핑몬",
    ("화남", "해당되는게 없음"): "🌩️ 폭풍감정몬",

    # 슬픔
    ("슬픔", "매운걸 먹었다"): "🌶️ 눈물의 아린몬",
    ("슬픔", "단걸 먹었다"): "🍬 위로의 달콤몬",
    ("슬픔", "운동을 했다"): "🏃‍♂️ 피땀눈물몬",
    ("슬픔", "무언갈 샀다"): "🛍️ 펑펑몬",
    ("슬픔", "해당되는게 없음"): "🌧️ 외로운 고독몬",

    # 행복
    ("행복", "매운걸 먹었다"): "🌶러브 스파이시몬",
    ("행복", "단걸 먹었다"): "🍭 꿀달콤몬",
    ("행복", "운동을 했다"): "🏋️ 행복근육몬",
    ("행복", "무언갈 샀다"): "🛍️ 행복한 쇼핑몬",
    ("행복", "해당되는게 없음"): "☀️ 밝은 햇살몬",

    # 놀람
    ("놀람", "매운걸 먹었다"): "🌶️ 깜놀매운몬",
    ("놀람", "단걸 먹었다"): "🍪 깜짝쿠키몬",
    ("놀람", "운동을 했다"): "🤸 깜찍피트니스몬",
    ("놀람", "무언갈 샀다"): "📦 충동택배몬",
    ("놀람", "해당되는게 없음"): "❓ 미스터리몬",

    # 추가 행동들
    ("화남", "책을 읽었다"): "📚 화를 삭이는 북몬",
    ("화남", "게임을 했다"): "🎮 분노의 게이머몬",
    ("화남", "공부를 했다"): "🧠 분노집중몬",
    ("화남", "요리를 했다"): "🔪 이열치열몬",

    ("슬픔", "책을 읽었다"): "📖 위로의 독서몬",
    ("슬픔", "게임을 했다"): "🕹️ 마음달래기몬",
    ("슬픔", "공부를 했다"): "😔 슬픈공부몬",
    ("슬픔", "요리를 했다"): "🍲 힐링쿠킹몬",

    ("행복", "책을 읽었다"): "📘 지적인 해피몬",
    ("행복", "게임을 했다"): "🎉 즐겜몬",
    ("행복", "공부를 했다"): "📚 똑똑이몬",
    ("행복", "요리를 했다"): "🍳 사랑의 밥상몬",

    ("놀람", "책을 읽었다"): "😲 갑분독서몬",
    ("놀람", "게임을 했다"): "👾 깜짝게이밍몬",
    ("놀람", "공부를 했다"): "😵 깜놀공부몬",
    ("놀람", "요리를 했다"): "🍴 놀라운 요리몬",

    
    ("행복", "맛있는걸 먹었다"): "🍕🍟🍗🍜🍣먹보몬🍕🍟🍗🍜🍣",
    ("슬픔", "맛있는걸 먹었다"): "🍕🍟🍗🍜🍣먹보몬🍕🍟🍗🍜🍣",
    ("놀람", "맛있는걸 먹었다"): "🍕🍟🍗🍜🍣먹보몬🍕🍟🍗🍜🍣",
    ("화남", "맛있는걸 먹었다"): "🍕🍟🍗🍜🍣먹보몬🍕🍟🍗🍜🍣"
}

# 감정 키워드 매칭용 딕셔너리
mood_keywords = {
    "화": "화남",
    "짜": "화남",
    "분노": "화남",
    "좋": "행복",
    "행복": "행복",
    "기쁨": "행복",
    "슬": "슬픔",
    "우울": "슬픔",
    "놀람": "놀람",
    "깜짝": "놀람",
    "당황": "놀람"
}



# 감정 입력 매칭 키워드 함
def match_mood(user_input):
    for keyword, mood in mood_keywords.items():
        if keyword in user_input:
            return mood
    return None

# 행동 키워드 매칭용 딕셔너리
action_keywords = {
    "매운": "매운걸 먹었다",
    "불닭": "매운걸 먹었다",
    "매": "매운걸 먹었다",
    "닭발": "매운걸 먹었다",
    "엽떡": "매운걸 먹었다",

    "단": "단걸 먹었다",
    "사탕": "단걸 먹었다",
    "초콜릿": "단걸 먹었다",
    "과자": "단걸 먹었다",
    "디저트": "단걸 먹었다",
    "케이크": "단걸 먹었다",
    "아이스크림": "단걸 먹었다",

    "운동": "운동을 했다",
    "달리기": "운동을 했다",
    "조깅": "운동을 했다",
    "헬스": "운동을 했다",
    "스트레칭": "운동을 했다",
    "요가": "운동을 했다",
    "자전거": "운동을 했다",

    "샀": "무언갈 샀다",
    "구매": "무언갈 샀다",
    "쇼핑": "무언갈 샀다",
    "택배": "무언갈 샀다",
    "선물": "무언갈 샀다",
    "결제": "무언갈 샀다",

    "읽": "책을 읽었다",
    "게임": "게임을 했다",
    "공부": "공부를 했다",
    "요리": "요리를 했다",
    "맛" : "맛있는걸 먹었다"
}

# 행동별 대사 매핑 딕셔너리
action_messages = {
    "매운걸 먹었다": "불꽃이여, 내 안에서 폭발하라! 화염의 분노!! 🔥🔥",
    "단걸 먹었다": "달콤함의 힘으로 전장을 제압한다! 슈거 블래스트, !! 🍭⚡",
    "운동을 했다": "근육의 한계를 깨뜨려라! 파워 스트라이크, 진화!! 💪⚡",
    "무언갈 샀다": "에너지 폭발! 쇼핑의 신이여, 나를 각성시켜라! !! 💥🛒",
    "책을 읽었다": "지식의 빛으로 어둠을 베어라! 인텔리전스 포스 📚⚡",
    "게임을 했다": "승리의 함성, 전장을 뒤흔들어라! 게이머 스트라이크🎮🔥",
    "공부를 했다": "집중의 폭풍이 몰아친다! 브레인 파이어🧠🔥",
    "요리를 했다": "맛의 마법으로 세상을 바꾼다! 셰프 블레이즈!🍳🔥"
}


# 행동 매칭 함수
def match_action(user_input):
    for keyword, action in action_keywords.items():
        if keyword in user_input:
            return action
    return "해당되는게 없음"

# 진화 판별 함수 - 기록에 따라 진화체 출력
def evolve_by_count(mood, action, filename="감정로그.csv"):
    """
    기록된 감정, 행동 수를 세고 일정 조건 달성 시 진화체 출력
    """
    if not os.path.exists(filename):
        return "기록이 없어서 진화할 수 없어요."

    count = 0
    with open(filename, encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 3:
                continue
            _, m, a = row
            if m == mood and a == action:
                count += 1
    
    # 3번 이상 반복 시 진화
    if count >= 3:
        evolved = evolution_dict.get((mood, action), None)
        if evolved:
            return "#### " + evolved + " 진화!! ####"
        else:
            return "진화 조건은 맞았지만 진화체가 등록되어있지 않아요."
    else:
        return "✨ 무언가로 진화하려합니다....신비함 증가 +++✨"





# 도감 업데이트 함수
def update_dex(name, evolved_name, mood, action, filename="도감.csv"):
    """
    진화체 정보를 도감에 저장 (중복도 허용)
    """
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_entry = [name, evolved_name, mood, action, time_now]

    # 기존 도감 불러오기 (있으면)
    entries = []
    if os.path.exists(filename):
        with open(filename, encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 5:
                    entries.append(row)

    # 새 항목 추가
    entries.append(new_entry)

    # 다시 저장
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        for row in entries:
            writer.writerow(row)

    print(name + "(이)가 " + evolved_name + "(으)로 도감에 등록되었어요! 🧬")

# 도감 출력 함수
def view_dex(filename="도감.csv"):
    if not os.path.exists(filename):
        print("도감이 비어있습니다. 😢")
        return

    print("\n=== 도감 목록 ===")
    with open(filename, encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 5:
                print("❤️: " + row[0] +
                      ", 진화체: " + row[1] +
                      ", 감정: " + row[2] +
                      ", 행동: " + row[3] +
                      ", ⏰: " + row[4])
# 기록 초기화 함수
def reset_log(filename="감정로그.csv"):
    if os.path.exists(filename):
        os.remove(filename)
        print("감정 로그를 초기화했어요.")
    else:
        print("초기화할 감정 로그가 없어요.")



#감정별 분포 시각화 함수

def show_mood_distribution(filename="감정로그.csv"):
    if not os.path.exists(filename):
        print("감정 로그가 없습니다.")
        return
    
    df = pd.read_csv(filename, header=None, names=["이름", "감정", "행동"])
    mood_counts = df["감정"].value_counts()

    if mood_counts.empty:
        print("기록이 없습니다.")
        return
    
    print("\n[전체 감정 분포]")
    

    # 시각화
    plt.figure(figsize=(8, 5))
    mood_counts.plot(kind='bar', color='skyblue')
    plt.title("전체 감정 분포")
    plt.xlabel("감정")
    plt.ylabel("횟수")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()




#행동추천함수
def recommend_combined(mood, filename="감정로그.csv"):
    """
    감정에 따라 추천 행동을 보여주되,
    사용자가 이미 자주 한 행동은 제외하고 새로운 행동만 추천합니다. 
    """

    if not os.path.exists(filename):
        print("감정 로그가 없습니다. 😢")
        return

    # 감정별 추천 행동 사전
    recs = {
        "슬픔": ["달려보기", "친구와 대화하기", "좋아하는 음악 듣기"],
        "화남": ["심호흡하기", "잠깐 휴식하기", "운동하기"],
        "놀람": ["깊게 생각하기", "명상하기", "차분히 정리하기"],
        "행복": ["기록 남기기", "감사일기 쓰기", "좋아하는 활동 계속하기"]
    }

    if mood not in recs:
        print("추천할 감정 행동이 없습니다. 😥")
        return

    # 사용자가 이미 했던 행동 목록 가져오기
    done_actions = []
    with open(filename, encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 3:
                continue
            _, row_mood, action = row
            if row_mood == mood:
                done_actions.append(action)

    # 추천 행동 중 이미 한 것과 안 한 것 구분
    already_done = list(set(done_actions))
    not_done = [act for act in recs[mood] if act not in already_done]

    # 추천 출력
    

    if not_done:
        print("이런 행동을 해보는 건 어때요?? ✨ " + ", ".join(not_done))
    else:
        print("멋져요! 💖\n계속 그렇게 해보세요~ 💪")





     

# 메인 함수 - 메뉴 및 기능 통합
def main():
    print("=== 디지몬 감정 진화 프로그램 ===")
    digimon_name = input("디지몬 이름을 입력하세요: ").strip()

    while True:
        print("\n옵션을 선택하세요:")
        print("1. 감정 및 행동 기록하기")
        print("2. 기록 초기화하기")
        print("3. 종료하기")
        print("4. 도감 보기")
        print("5. 감정별 행동 통계 보기")
        

        choice = input("번호 입력: ").strip()

        if choice == "1":
            while True:
                user_mood_input = input("오늘 기분은 어때??: ").strip()
                mood = match_mood(user_mood_input)
                if mood is None:
                    print("감정을 인식하지 못했어요. 다시 입력해주세요.")
                    continue

                user_action_input = input("오늘 뭐했어??: ").strip()
                action = match_action(user_action_input)

                with open("감정로그.csv", "a", encoding="utf-8", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([digimon_name, mood, action])

                evolution_result = evolve_by_count(mood, action)
                print(digimon_name + "의 진화 결과: " + evolution_result)

                

                 # ✅ 진화 대사 컬러 박스 출력
                if "진화!!" in evolution_result:
                        evolved_name = evolution_result.replace("#### ", "").replace(" 진화!! ####", "")
    
    # 🔽 여기!!
                        print_evolution_message(evolved_name, action)

                        update_dex(digimon_name, evolved_name, mood, action)


                    

                        
                cont = input("계속 기록할까? (Y/N): ").strip().lower()
                if cont == "n":
                    break
                elif cont != "y":
                    print("잘못된 입력입니다. 'Y' 또는 'N'만 입력해주세요.")
                    continue

        elif choice == "2":
            reset_log()

        elif choice == "3":
            print("프로그램을 종료합니다.")
            break

        elif choice == "4":
            view_dex()

        elif choice == "5":
            show_mood_distribution()

            if os.path.exists("감정로그.csv"):
                df = pd.read_csv("감정로그.csv", header=None, names=["이름", "감정", "행동"])
                mood_counts = df["감정"].value_counts()

            if not mood_counts.empty:
                most_common_mood = mood_counts.idxmax()
                count = mood_counts.max()

                print("\n가장 자주 나타난 감정은 '" + most_common_mood + "'입니다. (" + str(count) + "번)")
                ans = input("'" + most_common_mood + "' 감정에 대한 추천을 받아볼까요? (Y/N): ").strip().lower()
             
                if ans == "y":
                    recommend_combined(most_common_mood)
                else:
                    print("추천을 건너뜁니다. 😊")
            else:
                print("감정 기록이 아직 없어요. 😅")
        else:
            print("감정 로그 파일이 존재하지 않아요. 🗂️")




if __name__ == "__main__":
    main()

