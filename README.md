# ✈️ 여행 도우미 (Streamlit)

카카오 지도/장소 검색 + 실시간 날씨(OpenWeather) + 환율 계산(ExchangeRate-API)을 한 화면에서 볼 수 있는 여행 앱입니다.

## 1. 폴더 준비
바탕화면(Desktop)에 `project3` 폴더를 만들고, 이 폴더 안의 파일들(`app.py`, `requirements.txt`, `.env.example`)을 그대로 넣어주세요.

```
Desktop/
└── project3/
    ├── app.py
    ├── requirements.txt
    └── .env.example
```

## 2. 파이썬 패키지 설치
터미널(또는 명령 프롬프트)에서 `project3` 폴더로 이동한 뒤 아래 명령을 실행하세요.

```bash
cd Desktop/project3
pip install -r requirements.txt
```

(선택) 가상환경을 쓰고 싶다면:
```bash
python -m venv venv
source venv/bin/activate   # Windows는 venv\Scripts\activate
pip install -r requirements.txt
```

## 3. API 키 설정
`.env.example` 파일을 복사해서 `.env` 라는 이름으로 저장한 뒤, 실제 발급받은 키를 입력하세요.

```bash
cp .env.example .env
```

`.env` 파일 내용 예시:
```
OPENWEATHER_API_KEY=실제_openweather_키
EXCHANGERATE_API_KEY=실제_exchangerate_키
KAKAO_REST_API_KEY=실제_카카오_REST_키
KAKAO_JS_API_KEY=실제_카카오_JavaScript_키
```

### 키 발급 받는 곳
- **OpenWeather**: https://openweathermap.org/api → 회원가입 후 API Keys 메뉴
- **ExchangeRate-API**: https://www.exchangerate-api.com/ → 무료 플랜 가입 후 키 발급
- **Kakao REST API Key / JavaScript Key**:
  1. https://developers.kakao.com 접속 후 로그인
  2. "내 애플리케이션" → 애플리케이션 추가
  3. "앱 키" 메뉴에서 REST API 키, JavaScript 키 확인
  4. "플랫폼" 설정에서 **Web 플랫폼**을 등록하고, 사이트 도메인에 `http://localhost:8501` 을 추가해야 지도가 정상적으로 뜹니다.

## 4. 앱 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 이 자동으로 열립니다.

## 5. 주요 기능
- 🔍 **장소 검색**: 카카오 로컬 API로 여행지/맛집/명소 키워드 검색
- 🗺️ **지도**: 카카오맵 JS SDK로 검색한 장소를 지도에 마커 표시
- 🌤️ **날씨**: 선택한 장소의 실시간 날씨(기온, 체감온도, 습도, 바람)
- 💱 **환율 계산기**: 원하는 통화 쌍으로 실시간 환율 변환

## 문제 해결
- 사이드바에 "API 키가 설정되지 않았습니다" 경고가 뜨면 `.env` 파일의 키 이름과 값이 올바른지 확인하세요.
- 지도가 뜨지 않으면 카카오 개발자 콘솔의 "플랫폼 > Web" 도메인에 `http://localhost:8501`이 등록되어 있는지 확인하세요.
- `.env` 파일은 절대 공개 저장소(GitHub 등)에 올리지 마세요.
