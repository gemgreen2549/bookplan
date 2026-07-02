# =========================================================
# 🐶 멍멍이의 한달 챌린지 (Streamlit 버전)
# - 책읽기 체크판 / 영어단어 체크판 메뉴 분리
# - 누가(누적) 기록 표시
# - 기록은 challenge_data.json 파일에 저장
# 실행: streamlit run app.py
# =========================================================
import streamlit as st
import json, os, calendar
from datetime import date

DATA_FILE = "challenge_data.json"

# ---------------------- 데이터 저장/불러오기 ----------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def month_key(y, m):
    return f"{y}-{m:02d}"

def get_month(data, y, m):
    k = month_key(y, m)
    if k not in data:
        data[k] = {"reading": {}, "vocab": {}}
    return data[k]

def reading_done(r):
    return bool(r and r.get("done") and r.get("title", "").strip())

def vocab_done(v):
    return bool(v and all(v.get("paws", [False] * 5)))

# ---------------------- 페이지 기본 설정 ----------------------
st.set_page_config(page_title="🐶 멍멍이의 한달 챌린지", page_icon="🐾", layout="centered")

# ---------------------- 귀여운 스타일 (CSS) ----------------------
st.markdown("""
<style>
  .stApp { background-color: #FFF8E7; }
  h1, h2, h3 { color: #3A2E2A !important; }
  .doghouse {
    background: #fff; border: 3px solid #3A2E2A; border-radius: 16px;
    padding: 18px; text-align: center; box-shadow: 6px 6px 0 rgba(58,46,42,.15);
    margin-bottom: 10px;
  }
  .roofbar { height: 14px; background: #E85A4F; border: 3px solid #3A2E2A;
    border-radius: 10px 10px 0 0; margin: -18px -18px 12px -18px; }
  .statbox {
    background: #fff; border: 3px solid #3A2E2A; border-radius: 14px;
    padding: 10px 4px; text-align: center; box-shadow: 4px 4px 0 rgba(58,46,42,.12);
  }
  .statbox .num { font-size: 28px; font-weight: 800; color: #E85A4F; }
  .statbox .lbl { font-size: 12px; color: #8a7b6d; }
  .calcell {
    display: inline-block; width: 40px; height: 40px; margin: 3px;
    border: 2px solid #E8DCC3; border-radius: 10px; background: #fff;
    text-align: center; line-height: 36px; font-size: 15px; color: #8a7b6d;
  }
  .calcell.done { background: #FFD166; border-color: #C98F2B; font-size: 18px; }
  .calcell.today { border-color: #7EC8E3; border-width: 3px; line-height: 34px; }
  div.stButton > button {
    background: #E85A4F; color: white; border: 2px solid #3A2E2A;
    border-radius: 10px; font-weight: 700;
  }
</style>
""", unsafe_allow_html=True)

# ---------------------- 데이터 준비 ----------------------
if "data" not in st.session_state:
    st.session_state.data = load_data()
data = st.session_state.data
today = date.today()

# ---------------------- 사이드바 메뉴 ----------------------
st.sidebar.markdown("## 🐶 메뉴")
menu = st.sidebar.radio("체크판을 골라주세요!", ["📚 책읽기 체크판", "✏️ 영어단어 체크판"])
st.sidebar.markdown("---")
year = st.sidebar.number_input("연도", 2024, 2100, today.year)
month = st.sidebar.number_input("월", 1, 12, today.month)
st.sidebar.caption("🐾 기록은 자동으로 저장돼요!")

m = get_month(data, year, month)
num_days = calendar.monthrange(year, month)[1]

# ---------------------- 헤더 ----------------------
st.markdown("""
<div class="doghouse">
  <div class="roofbar"></div>
  <h1>🐶 멍멍이의 한달 챌린지 🦴</h1>
  <p style="color:#8a7b6d; margin:0;">매일 조금씩, 꾸준히! 다 하면 발도장 쾅!</p>
</div>
""", unsafe_allow_html=True)

# ---------------------- 누가(누적) 기록 계산 ----------------------
total_days, total_books, total_words = set(), 0, 0
for mk, mv in data.items():
    for d, r in mv.get("reading", {}).items():
        if reading_done(r):
            total_books += 1
            total_days.add(f"{mk}-{d}")
    for d, v in mv.get("vocab", {}).items():
        if vocab_done(v):
            total_words += v.get("count", 0)
            total_days.add(f"{mk}-{d}")

# 이번달 연속 기록(둘 중 하나라도 완료한 날 기준)
streak = best = 0
for d in range(1, num_days + 1):
    ok = reading_done(m["reading"].get(str(d))) or vocab_done(m["vocab"].get(str(d)))
    streak = streak + 1 if ok else 0
    best = max(best, streak)

c1, c2, c3, c4 = st.columns(4)
for col, num, lbl in [(c1, len(total_days), "총 참여일"), (c2, total_books, "읽은 책(일수)"),
                      (c3, total_words, "암기한 단어"), (c4, best, "이번달 연속기록")]:
    col.markdown(f'<div class="statbox"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>',
                 unsafe_allow_html=True)

st.markdown(f"### 🗓️ {year}년 {month}월")

# ---------------------- 오늘 기록 입력 ----------------------
default_day = today.day if (today.year == year and today.month == month) else 1
day = st.selectbox("기록할 날짜를 골라주세요 🐾", list(range(1, num_days + 1)), index=default_day - 1)
dkey = str(day)

if menu == "📚 책읽기 체크판":
    st.subheader(f"📚 {month}월 {day}일의 책읽기")
    r = m["reading"].get(dkey, {"title": "", "amount": "", "done": False})
    title = st.text_input("📖 책 제목", r["title"], placeholder="오늘 읽은 책 제목")
    amount = st.text_input("📄 읽은 양", r["amount"], placeholder="예: 30쪽 / 한 권 다!")
    done = st.checkbox("오늘의 책읽기 완료! ✅", r["done"])
    if st.button("🐾 발도장 찍기 (저장)"):
        m["reading"][dkey] = {"title": title, "amount": amount, "done": done}
        save_data(data)
        if reading_done(m["reading"][dkey]):
            st.balloons()
            st.success(f"멍멍! 🐶 {day}일 책읽기 완료! 발도장 쾅!")
        else:
            st.info("저장했어요! 완료 체크와 책 제목까지 채우면 발도장이 찍혀요 🐾")
    done_check = reading_done  # 달력용
    records = m["reading"]

else:
    st.subheader(f"✏️ {month}월 {day}일의 영어단어 (하루 20개 × 5번 쓰기)")
    v = m["vocab"].get(dkey, {"pages": "", "count": 20, "paws": [False] * 5})
    pages = st.text_input("📑 쓴 단어의 쪽수", v["pages"], placeholder="예: 12~13쪽")
    count = st.number_input("🔤 단어 개수", 0, 200, v["count"])
    st.write("✍️ **5번 쓰기 체크** (한 번 쓸 때마다 하나씩!)")
    pcols = st.columns(5)
    paws = [pcols[i].checkbox(f"{i+1}번째 🐾", v["paws"][i], key=f"paw{year}{month}{day}{i}")
            for i in range(5)]
    if st.button("🐾 발도장 찍기 (저장)"):
        m["vocab"][dkey] = {"pages": pages, "count": int(count), "paws": paws}
        save_data(data)
        if vocab_done(m["vocab"][dkey]):
            st.balloons()
            st.success(f"멍멍! 🐶 {day}일 단어 5번 쓰기 완료! {count}개 암기 성공!")
        else:
            st.info("저장했어요! 5번 모두 체크하면 발도장이 찍혀요 🐾")
    done_check = vocab_done
    records = m["vocab"]

# ---------------------- 이번달 발도장 달력 ----------------------
st.markdown("### 🐾 이번달 발도장 달력")
cells = ""
for d in range(1, num_days + 1):
    done = done_check(records.get(str(d)))
    is_today = (today.year == year and today.month == month and today.day == d)
    cls = "calcell" + (" done" if done else "") + (" today" if is_today else "")
    cells += f'<span class="{cls}">{"🐾" if done else d}</span>'
st.markdown(f'<div style="text-align:center">{cells}</div>', unsafe_allow_html=True)

# 이번달 요약
m_books = sum(1 for r in m["reading"].values() if reading_done(r))
m_words = sum(v.get("count", 0) for v in m["vocab"].values() if vocab_done(v))
st.caption(f"이번달: 책 {m_books}일 완료 · 단어 {m_words}개 암기 🎉")
