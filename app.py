import os
import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# -----------------------------
# 환경변수(.env) 로드
# -----------------------------
load_dotenv()

def get_key(name: str) -> str:
    """환경변수 또는 st.secrets에서 API 키를 가져옵니다."""
    val = os.environ.get(name, "")
    if not val:
        try:
            val = st.secrets.get(name, "")
        except Exception:
            val = ""
    return (val or "").strip()

OPENWEATHER_API_KEY = get_key("OPENWEATHER_API_KEY")
EXCHANGERATE_API_KEY = get_key("EXCHANGERATE_API_KEY")
KAKAO_REST_API_KEY = get_key("KAKAO_REST_API_KEY")
KAKAO_JS_API_KEY = get_key("KAKAO_JS_API_KEY")

st.set_page_config(page_title="여행 도우미", page_icon="✈️", layout="wide")


# -----------------------------
# API 함수들
# -----------------------------
@st.cache_data(ttl=600, show_spinner=False)
def kakao_search_place(query: str):
    """카카오 로컬 API로 장소(키워드) 검색"""
    if not KAKAO_REST_API_KEY:
        return None, "KAKAO_REST_API_KEY가 설정되지 않았습니다."
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": query, "size": 10}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        res.raise_for_status()
        return res.json().get("documents", []), None
    except requests.exceptions.RequestException as e:
        return None, f"카카오 검색 오류: {e}"


@st.cache_data(ttl=600, show_spinner=False)
def get_weather(lat: float, lon: float):
    """OpenWeather API로 현재 날씨 조회"""
    if not OPENWEATHER_API_KEY:
        return None, "OPENWEATHER_API_KEY가 설정되지 않았습니다."
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "kr",
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        return res.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"날씨 조회 오류: {e}"


@st.cache_data(ttl=3600, show_spinner=False)
def get_exchange_rate(base: str, target: str):
    """ExchangeRate-API로 환율 조회 (base -> target)"""
    if not EXCHANGERATE_API_KEY:
        return None, "EXCHANGERATE_API_KEY가 설정되지 않았습니다."
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{base}/{target}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data.get("result") != "success":
            return None, f"환율 조회 실패: {data.get('error-type', '알 수 없는 오류')}"
        return data, None
    except requests.exceptions.RequestException as e:
        return None, f"환율 조회 오류: {e}"


def render_kakao_map(lat: float, lon: float, place_name: str = ""):
    """카카오 지도 JS SDK로 지도 렌더링"""
    if not KAKAO_JS_API_KEY:
        st.warning("KAKAO_JS_API_KEY가 설정되지 않아 지도를 표시할 수 없습니다.")
        return

    # 주의: autoload=false + kakao.maps.load() 조합은 Streamlit의 srcdoc iframe 환경에서
    # 카카오 SDK가 https를 제대로 감지하지 못해 내부적으로 http:// 리소스를 요청하다가
    # Mixed Content 에러로 차단되는 문제가 있습니다.
    # 따라서 autoload(기본값, 동기 로드) 방식을 사용해 이 문제를 피합니다.
    html_code = f"""
    <div id="map" style="width:100%;height:420px;border-radius:12px;background:#f4f4f5;
         display:flex;align-items:center;justify-content:center;color:#888;font-size:13px;">
         지도를 불러오는 중...
    </div>
    <script src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_API_KEY}"></script>
    <script>
        var mapTries = 0;

        function showMapError(msg) {{
            document.getElementById('map').innerHTML =
                '<div style="padding:16px;color:#c00;font-size:13px;line-height:1.6;">' + msg + '</div>';
        }}

        function tryInitMap() {{
            mapTries++;
            var ready = (typeof kakao !== 'undefined')
                && kakao.maps
                && typeof kakao.maps.LatLng === 'function';

            if (ready) {{
                try {{
                    var container = document.getElementById('map');
                    container.innerHTML = '';
                    var options = {{
                        center: new kakao.maps.LatLng({lat}, {lon}),
                        level: 4
                    }};
                    var map = new kakao.maps.Map(container, options);

                    var marker = new kakao.maps.Marker({{
                        position: new kakao.maps.LatLng({lat}, {lon})
                    }});
                    marker.setMap(map);

                    var infowindow = new kakao.maps.InfoWindow({{
                        content: '<div style="padding:6px 10px;font-size:13px;">{place_name}</div>'
                    }});
                    infowindow.open(map, marker);
                }} catch (e) {{
                    showMapError(
                        '지도 초기화 오류: ' + e.message +
                        '<br><br>카카오 개발자 콘솔 &gt; 내 애플리케이션 &gt; 플랫폼 &gt; Web 에 ' +
                        '현재 배포 주소가 https:// 포함, 끝에 슬래시 없이 정확히 등록되어 있는지 확인해주세요.'
                    );
                }}
            }} else if (mapTries < 25) {{
                setTimeout(tryInitMap, 200);
            }} else {{
                showMapError(
                    '지도를 불러오지 못했습니다 (SDK 준비 시간 초과).' +
                    '<br><br>가능한 원인:' +
                    '<br>1) JavaScript 키 값이 올바르지 않음' +
                    '<br>2) 카카오 개발자 콘솔 &gt; 플랫폼 &gt; Web 도메인 미등록/불일치'
                );
            }}
        }}

        tryInitMap();
    </script>
    """
    components.html(html_code, height=440)


# -----------------------------
# 세션 상태 초기화
# -----------------------------
if "selected_place" not in st.session_state:
    st.session_state.selected_place = None


# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.title("✈️ 여행 도우미")
    st.caption("카카오 지도 · 실시간 날씨 · 환율 계산")
    st.divider()

    missing_keys = [
        name for name, val in [
            ("OPENWEATHER_API_KEY", OPENWEATHER_API_KEY),
            ("EXCHANGERATE_API_KEY", EXCHANGERATE_API_KEY),
            ("KAKAO_REST_API_KEY", KAKAO_REST_API_KEY),
            ("KAKAO_JS_API_KEY", KAKAO_JS_API_KEY),
        ] if not val
    ]
    if missing_keys:
        st.warning("다음 API 키가 설정되지 않았습니다:\n\n" + "\n".join(f"- {k}" for k in missing_keys))
        st.caption(".env 파일을 확인해주세요.")
    else:
        st.success("모든 API 키가 정상적으로 로드되었습니다.")


# -----------------------------
# 메인 화면
# -----------------------------
st.title("🌏 여행지 검색 & 정보")

search_query = st.text_input("가고 싶은 여행지, 장소, 맛집 등을 검색해보세요", placeholder="예: 부산 해운대, 제주 카페")

if search_query:
    places, err = kakao_search_place(search_query)
    if err:
        st.error(err)
    elif not places:
        st.info("검색 결과가 없습니다. 다른 키워드로 검색해보세요.")
    else:
        options = [f"{p['place_name']} ({p['road_address_name'] or p['address_name']})" for p in places]
        idx = st.selectbox("검색 결과에서 장소를 선택하세요", range(len(options)), format_func=lambda i: options[i])
        st.session_state.selected_place = places[idx]

st.divider()

if st.session_state.selected_place:
    place = st.session_state.selected_place
    lat = float(place["y"])
    lon = float(place["x"])
    name = place["place_name"]
    address = place.get("road_address_name") or place.get("address_name")

    tab_map, tab_weather, tab_currency = st.tabs(["🗺️ 지도", "🌤️ 날씨", "💱 환율 계산기"])

    with tab_map:
        st.subheader(f"📍 {name}")
        st.caption(address)
        render_kakao_map(lat, lon, place_name=name)
        if place.get("place_url"):
            st.link_button("카카오맵에서 자세히 보기", place["place_url"])

    with tab_weather:
        st.subheader(f"🌤️ {name}의 현재 날씨")
        weather, werr = get_weather(lat, lon)
        if werr:
            st.error(werr)
        elif weather:
            col1, col2, col3, col4 = st.columns(4)
            temp = weather["main"]["temp"]
            feels = weather["main"]["feels_like"]
            humidity = weather["main"]["humidity"]
            description = weather["weather"][0]["description"]
            icon_code = weather["weather"][0]["icon"]

            col1.metric("기온", f"{temp:.1f}°C")
            col2.metric("체감 온도", f"{feels:.1f}°C")
            col3.metric("습도", f"{humidity}%")
            col4.metric("바람", f"{weather['wind']['speed']} m/s")

            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            c1, c2 = st.columns([1, 4])
            with c1:
                st.image(icon_url, width=80)
            with c2:
                st.write(f"**날씨 상태:** {description}")

    with tab_currency:
        st.subheader("💱 환율 계산기")
        currency_list = ["KRW", "USD", "EUR", "JPY", "CNY", "GBP", "AUD", "CAD", "THB", "VND", "SGD"]

        c1, c2, c3 = st.columns([2, 2, 3])
        with c1:
            base_currency = st.selectbox("기준 통화", currency_list, index=0)
        with c2:
            target_currency = st.selectbox("변환 통화", currency_list, index=1)
        with c3:
            amount = st.number_input("금액", min_value=0.0, value=10000.0, step=1000.0)

        if base_currency == target_currency:
            st.info("기준 통화와 변환 통화가 같습니다.")
        else:
            rate_data, rerr = get_exchange_rate(base_currency, target_currency)
            if rerr:
                st.error(rerr)
            elif rate_data:
                rate = rate_data["conversion_rate"]
                converted = amount * rate
                st.metric(
                    label=f"{amount:,.0f} {base_currency} → {target_currency}",
                    value=f"{converted:,.2f} {target_currency}",
                )
                st.caption(f"1 {base_currency} = {rate:.4f} {target_currency} (실시간 환율 기준)")
else:
    st.info("👆 위 검색창에 여행지를 입력하면 지도, 날씨, 환율 정보를 한눈에 볼 수 있어요.")
