import streamlit as st
import pandas as pd
import os
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. 페이지 설정 및 디자인
# ==========================================
st.set_page_config(page_title="RunAid", page_icon="🏃")

# 배경색 변경 (연한 하늘색)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F0F8FF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. 데이터 로드 및 함수 정의
# ==========================================

# 하버사인 공식 (거리 계산)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(min(1, sqrt(a)))
    return R * c

# 데이터 불러오기
@st.cache_data
def load_data():
    try:
        current_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_path, "jongno_run_hospitals.csv")
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return None

df = load_data()

# 응급처치 가이드 데이터
INJURY_GUIDES = {
    "무릎(Knee)": "러너스 니 의심. 무릎 바깥쪽 통증 시 IT밴드 스트레칭 필수. 내리막길 주행 금지.",
    "발목(Ankle)": "발목 염좌 의심. 즉시 R.I.C.E(휴식, 냉찜질, 압박, 거상) 요법 실시. 체중 부하 금지.",
    "족저근막(Foot)": "족저근막염 의심. 발바닥 아치 부분을 골프공이나 캔으로 문질러 마사지하세요.",
    "종아리(Calf)": "쥐(근육 경련) 또는 비복근 파열 의심. 발끝을 몸 쪽으로 당기는 스트레칭을 부드럽게 시행.",
    "허벅지/고관절": "햄스트링 부상 주의. 억지로 늘리지 말고 얼음찜질 후 압박 붕대 사용 권장.",
    "기타": "통증이 지속되면 즉시 러닝을 멈추고 전문가와 상담하세요."
}

# ==========================================
# 3. 웹 화면 구성 (UI)
# ==========================================
st.title("RunAid")
st.markdown("---")

if df is None:
    st.error("❌ 데이터 파일(jongno_run_hospitals.csv)이 없습니다.")
    st.stop()

# (1) 위치 정보 받기
st.subheader("1️⃣ 현재 위치 확인")
st.info("아래 버튼을 누르면 GPS 정보를 가져옵니다 (브라우저 권한 허용 필요).")

loc = get_geolocation() # GPS 버튼

user_lat = None
user_lon = None

if loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    st.success(f"📍 위치 확인 완료! (위도: {user_lat:.4f}, 경도: {user_lon:.4f})")
else:
    st.warning("위치 정보를 가져와야 병원을 추천할 수 있습니다.")

# (2) 부상 부위 선택
st.subheader("2️⃣ 부상 정보 입력")
body_part = st.selectbox("아픈 부위를 선택하세요", list(INJURY_GUIDES.keys()))

# (3) 통증 점수 선택
nrs_score = st.slider("통증 정도 (0: 안 아픔 ~ 10: 극심함)", 0, 10, 0)

# ==========================================
# 4. 결과 분석 및 출력
# ==========================================
if st.button("병원 찾기 & 진단 시작", type="primary"):
    if user_lat is None or user_lon is None:
        st.error("먼저 상단의 버튼을 눌러 위치 정보를 가져와주세요!")
    else:
        st.markdown("---")
        st.header("🔄 분석 결과")
        
        guide_text = INJURY_GUIDES[body_part]
        
        # [Case A] 경미함
        if nrs_score < 4:
            st.success(f"✅ NRS {nrs_score}: 경미한 통증입니다.")
            st.info(f"💡 **[{body_part} 관리 팁]**\n\n{guide_text}")
            st.caption("혹시 모를 상황을 위해 근처 병원을 안내합니다.")
            
        # [Case B] 병원 방문 권장
        elif 4 <= nrs_score <= 7:
            st.warning(f"🚨 NRS {nrs_score}: 전문의 진료가 필요합니다.")
            st.write("자가 처치보다는 병원 방문을 권장합니다.")
            
        # [Case C] 응급
        else:
            st.error(f"🚑 NRS {nrs_score}: 즉각적인 조치가 필요한 응급 상황입니다!")
            st.write("🚫 **즉시 119를 부르거나 응급실로 이동하세요.**")

        # 병원 추천 로직
        if nrs_score <= 10:
            st.markdown("### 🏥 가장 가까운 병원 / 한의원")
            
            # 거리 계산
            df['거리(km)'] = df.apply(
                lambda row: haversine(user_lat, user_lon, float(row['위도']), float(row['경도'])), axis=1
            )
            
            orthopedics = df[df['분류'] == '병원'].sort_values(by='거리(km)').head(2)
            oriental = df[df['분류'] == '한의원'].sort_values(by='거리(km)').head(2)

            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🦴 [병원]")
                if orthopedics.empty:
                    st.write("근처 정보 없음")
                else:
                    for _, row in orthopedics.iterrows():
                        dist = int(row['거리(km)'] * 1000)
                        st.markdown(f"**{row['병원명']}** ({dist}m)")
                        st.text(f"📞 {row['전화번호']}")
                        st.markdown(f"[지도 보기]({row['지도URL']})")
                        st.divider()

            with col2:
                st.markdown("#### 🌿 [한의원]")
                if oriental.empty:
                    st.write("근처 정보 없음")
                else:
                    for _, row in oriental.iterrows():
                        dist = int(row['거리(km)'] * 1000)
                        st.markdown(f"**{row['병원명']}** ({dist}m)")
                        st.text(f"📞 {row['전화번호']}")
                        st.markdown(f"[지도 보기]({row['지도URL']})")
                        st.divider()