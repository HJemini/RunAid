import streamlit as st
import pandas as pd
import os
import urllib.parse # URL 인코딩용
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. 설정 및 디자인
# ==========================================
st.set_page_config(page_title="RunAid", page_icon="🏃")

# 배경색 및 버튼 스타일
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F0F8FF;
    }
    /* 응급 박스 스타일 */
    .emergency-box {
        background-color: #FF4B4B;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .emergency-title {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .emergency-desc {
        font-size: 18px;
        margin-bottom: 20px;
    }
    .call-btn {
        background-color: white;
        color: #FF4B4B;
        padding: 15px 30px;
        text-decoration: none;
        font-size: 24px;
        font-weight: bold;
        border-radius: 50px;
        display: inline-block;
    }
    
    /* 지도 버튼 공통 스타일 */
    .map-btn {
        display: inline-block;
        padding: 8px 12px;
        border-radius: 8px;
        text-decoration: none;
        font-size: 13px;
        font-weight: bold;
        color: white !important;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: 0.3s;
        margin-right: 5px; /* 버튼 간 간격 */
        margin-bottom: 5px;
    }
    
    /* 네이버 지도 (초록색) */
    .naver-btn {
        background-color: #03C75A;
    }
    .naver-btn:hover {
        background-color: #029f48;
    }

    /* 구글 지도 (파란색) */
    .google-btn {
        background-color: #4285F4;
    }
    .google-btn:hover {
        background-color: #3367D6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. 다국어 텍스트 데이터
# ==========================================
LANG_TEXT = {
    "한국어": {
        "title": "RunAid",
        "loc_header": "1️⃣ 현재 위치 확인",
        "loc_info": "아래 버튼을 누르면 GPS 정보를 가져옵니다 (브라우저 권한 허용 필요).",
        "loc_success": "📍 위치 확인 완료!",
        "loc_warn": "위치 정보를 가져와야 병원을 추천할 수 있습니다.",
        "body_header": "2️⃣ 부상 정보 입력",
        "body_label": "아픈 부위를 선택하세요",
        "nrs_header": "3️⃣ 통증 정도 입력 (NRS)",
        "nrs_guide_cap": "💡 NRS: 숫자가 클수록 통증이 심함을 의미합니다.",
        "nrs_label": "통증 점수를 선택하세요 (0 ~ 10)",
        "btn_search": "병원 찾기 & 진단 시작",
        "err_loc": "먼저 상단의 버튼을 눌러 위치 정보를 가져와주세요!",
        "res_header": "🔄 분석 결과",
        "msg_mild": "경미한 통증입니다.",
        "msg_mild_tip": "관리 팁",
        "msg_mild_sub": "혹시 모를 상황을 위해 근처 병원을 안내합니다.",
        "msg_warning": "전문의 진료가 필요합니다.",
        "msg_warning_sub": "자가 처치보다는 병원 방문을 권장합니다.",
        "msg_emerg": "즉각적인 조치가 필요한 응급 상황입니다!",
        "msg_emerg_sub": "더 이상 움직이지 마세요. 즉시 응급실로 가야 합니다.",
        "call_119": "📞 119 전화걸기",
        "hosp_header": "🏥 가장 가까운 병원 / 한의원",
        "cat_ortho": "🦴 [정형외과]",
        "cat_orient": "🌿 [한의원]",
        "btn_naver": "네이버지도",
        "btn_google": "구글지도", # 한국어에서는 안쓰지만 형식상 유지
        "no_data": "근처 정보 없음"
    },
    "English": {
        "title": "RunAid",
        "loc_header": "1️⃣ Check Current Location",
        "loc_info": "Press the button below to get GPS info (Allow browser permission).",
        "loc_success": "📍 Location Found!",
        "loc_warn": "We need your location to recommend hospitals.",
        "body_header": "2️⃣ Injury Information",
        "body_label": "Select the injured area",
        "nrs_header": "3️⃣ Pain Level (NRS)",
        "nrs_guide_cap": "💡 NRS: Higher numbers mean worse pain.",
        "nrs_label": "Select Pain Score (0 ~ 10)",
        "btn_search": "Find Hospitals & Diagnose",
        "err_loc": "Please get location information first!",
        "res_header": "🔄 Analysis Result",
        "msg_mild": "Mild pain detected.",
        "msg_mild_tip": "Care Tip",
        "msg_mild_sub": "Showing nearby hospitals just in case.",
        "msg_warning": "Medical attention recommended.",
        "msg_warning_sub": "We recommend visiting a hospital rather than self-care.",
        "msg_emerg": "CRITICAL EMERGENCY!",
        "msg_emerg_sub": "Do NOT move. You need immediate emergency care.",
        "call_119": "📞 Call 119 Now",
        "hosp_header": "🏥 Nearest Hospitals",
        "cat_ortho": "🦴 [Orthopedics]",
        "cat_orient": "🌿 [Oriental Clinic]",
        "btn_naver": "Naver Map",
        "btn_google": "Google Maps",
        "no_data": "No nearby info"
    },
    "中文": {
        "title": "RunAid",
        "loc_header": "1️⃣ 确认当前位置",
        "loc_info": "点击下方按钮获取GPS信息（需允许浏览器权限）。",
        "loc_success": "📍 位置确认完毕！",
        "loc_warn": "需要获取位置信息才能推荐医院。",
        "body_header": "2️⃣ 输入受伤信息",
        "body_label": "请选择疼痛部位",
        "nrs_header": "3️⃣ 疼痛程度 (NRS)",
        "nrs_guide_cap": "💡 NRS: 数字越大，疼痛越严重。",
        "nrs_label": "请选择疼痛分数 (0 ~ 10)",
        "btn_search": "查找医院 & 开始诊断",
        "err_loc": "请先点击上方按钮获取位置信息！",
        "res_header": "🔄 分析结果",
        "msg_mild": "轻微疼痛。",
        "msg_mild_tip": "护理建议",
        "msg_mild_sub": "为了以防万一，为您介绍附近的医院。",
        "msg_warning": "需要专科医生诊疗。",
        "msg_warning_sub": "建议去医院就诊，而不是自行处理。",
        "msg_emerg": "需要立即采取措施的紧急情况！",
        "msg_emerg_sub": "请不要移动。必须立即去急诊室。",
        "call_119": "📞 拨打 119",
        "hosp_header": "🏥 最近的医院 / 韩医院",
        "cat_ortho": "🦴 [骨科]",
        "cat_orient": "🌿 [韩医院]",
        "btn_naver": "Naver地图",
        "btn_google": "谷歌地图",
        "no_data": "附近无信息"
    },
    "日本語": {
        "title": "RunAid",
        "loc_header": "1️⃣ 現在地の確認",
        "loc_info": "下のボタンを押してGPS情報を取得します（ブラウザの権限許可が必要）。",
        "loc_success": "📍 位置確認完了！",
        "loc_warn": "位置情報を取得しないと病院を推薦できません。",
        "body_header": "2️⃣ 怪我情報の入力",
        "body_label": "痛む部位を選択してください",
        "nrs_header": "3️⃣ 痛みの程度 (NRS)",
        "nrs_guide_cap": "💡 NRS: 数字が大きいほど痛みが強いことを意味します。",
        "nrs_label": "痛みのスコアを選択 (0 ~ 10)",
        "btn_search": "病院検索 & 診断開始",
        "err_loc": "先に上のボタンを押して位置情報を取得してください！",
        "res_header": "🔄 分析結果",
        "msg_mild": "軽度の痛みです。",
        "msg_mild_tip": "ケアのヒント",
        "msg_mild_sub": "万が一のために近くの病院を案内します。",
        "msg_warning": "専門医の診療が必要です。",
        "msg_warning_sub": "自己処置より病院の受診をお勧めします。",
        "msg_emerg": "早急な措置が必要な緊急事態です！",
        "msg_emerg_sub": "動かないでください。直ちに救急室へ行く必要があります。",
        "call_119": "📞 119番にかける",
        "hosp_header": "🏥 最寄りの病院 / 韓医院",
        "cat_ortho": "🦴 [整形外科]",
        "cat_orient": "🌿 [韓医院]",
        "btn_naver": "NAVER地図",
        "btn_google": "Googleマップ",
        "no_data": "近くの情報なし"
    }
}

INJURY_DATA = {
    "한국어": { "무릎": "러너스 니 의심. 무릎 바깥쪽 통증 시 IT밴드 스트레칭 필수. 내리막길 주행 금지.", "발목": "발목 염좌 의심. 즉시 R.I.C.E(휴식, 냉찜질, 압박, 거상) 요법 실시. 체중 부하 금지.", "족저근막": "족저근막염 의심. 발바닥 아치 부분을 골프공이나 캔으로 문질러 마사지하세요.", "종아리": "쥐(근육 경련) 또는 비복근 파열 의심. 발끝을 몸 쪽으로 당기는 스트레칭을 부드럽게 시행.", "허벅지/고관절": "햄스트링 부상 주의. 억지로 늘리지 말고 얼음찜질 후 압박 붕대 사용 권장.", "기타": "통증이 지속되면 즉시 러닝을 멈추고 전문가와 상담하세요." },
    "English": { "Knee": "Runner's Knee suspected. IT band stretching is essential. Avoid downhill running.", "Ankle": "Sprain suspected. Perform R.I.C.E (Rest, Ice, Compression, Elevation) immediately.", "Plantar Fascia": "Plantar fasciitis suspected. Massage the arch of your foot with a golf ball or can.", "Calf": "Cramp or muscle tear suspected. Gently stretch by pulling your toes toward your body.", "Thigh/Hip": "Hamstring injury warning. Do not stretch forcibly; use ice packs and compression bandages.", "Other": "If pain persists, stop running immediately and consult a specialist." },
    "中文": { "膝盖": "怀疑跑步膝。膝盖外侧疼痛时必须进行IT带拉伸。禁止下坡跑。", "脚踝": "怀疑脚踝扭伤。立即实施R.I.C.E（休息、冷敷、压迫、抬高）疗法。", "足底筋膜": "怀疑足底筋膜炎。用高尔夫球或罐子摩擦脚底足弓部位进行按摩。", "小腿": "怀疑抽筋或肌肉撕裂。轻轻将脚趾向身体方向拉伸。", "大腿/髋关节": "注意腘绳肌受伤。不要强行拉伸，建议冷敷后使用弹力绷带。", "其他": "如果疼痛持续，请立即停止跑步并咨询专家。" },
    "日本語": { "膝": "ランナー膝の疑い。膝の外側の痛みにはITバンドのストレッチが必須。下り坂の走行禁止。", "足首": "足首の捻挫の疑い。直ちにR.I.C.E（安静、冷却、圧迫、挙上）療法を実施。", "足底筋膜": "足底筋膜炎の疑い。足の裏のアーチ部分をゴルフボールや缶でこすってマッサージしてください。", "ふくらはぎ": "こむら返りまたは筋肉断裂の疑い。つま先を体の方に引くストレッチを優しく実施。", "太もも/股関節": "ハムストリングの怪我に注意。無理に伸ばさず、アイシング後に圧迫包帯の使用を推奨。", "その他": "痛みが続く場合は直ちにランニングを中止し、専門家に相談してください。" }
}

# ==========================================
# 3. 함수 정의
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(min(1, sqrt(a)))
    return R * c

@st.cache_data
def load_data():
    try:
        current_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_path, "jongno_run_hospitals.csv")
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return None

df = load_data()

# ==========================================
# 4. 웹 화면 구성 (UI)
# ==========================================

lang_code = st.radio(
    "Language / 言語 / 语言",
    ["한국어", "English", "中文", "日本語"],
    horizontal=True
)

txt = LANG_TEXT[lang_code]
guide_data = INJURY_DATA[lang_code]

st.title(txt["title"])
st.markdown("---")

if df is None:
    st.error("❌ Data file not found (jongno_run_hospitals.csv)")
    st.stop()

# (1) 위치 정보 받기
st.subheader(txt["loc_header"])
st.info(txt["loc_info"])

loc = get_geolocation()

user_lat = None
user_lon = None

if loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    st.success(f"{txt['loc_success']} (Lat: {user_lat:.4f}, Lon: {user_lon:.4f})")
else:
    st.warning(txt["loc_warn"])

# (2) 부상 부위 선택
st.subheader(txt["body_header"])
body_part = st.selectbox(txt["body_label"], list(guide_data.keys()))

# (3) 통증 점수 선택
st.subheader(txt["nrs_header"])
current_path = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(current_path, "image_0.png")

if os.path.exists(img_path):
    st.image(img_path, caption=txt["nrs_guide_cap"], use_column_width=True)
else:
    st.info("ℹ️ NRS: 0 ~ 10 Scale")

nrs_score = st.slider(txt["nrs_label"], 0, 10, 0)

# ==========================================
# 5. 결과 분석 및 출력
# ==========================================
if st.button(txt["btn_search"], type="primary"):
    if user_lat is None or user_lon is None:
        st.error(txt["err_loc"])
    else:
        st.markdown("---")
        st.header(txt["res_header"])
        
        guide_text = guide_data[body_part]
        
        if nrs_score >= 8:
            st.markdown(f"""
                <div class="emergency-box">
                    <div class="emergency-title">🆘 {txt['msg_emerg']}</div>
                    <div class="emergency-desc">{txt['msg_emerg_sub']}</div>
                    <a href="tel:119" class="call-btn">{txt['call_119']}</a>
                </div>
            """, unsafe_allow_html=True)
        else:
            if nrs_score < 4:
                st.success(f"✅ NRS {nrs_score}: {txt['msg_mild']}")
                st.info(f"💡 **[{body_part} {txt['msg_mild_tip']}]**\n\n{guide_text}")
                st.caption(txt['msg_mild_sub'])
            else:
                st.warning(f"🚨 NRS {nrs_score}: {txt['msg_warning']}")
                st.write(txt['msg_warning_sub'])

            st.markdown(f"### {txt['hosp_header']}")
            
            df['거리(km)'] = df.apply(
                lambda row: haversine(user_lat, user_lon, float(row['위도']), float(row['경도'])), axis=1
            )
            
            orthopedics = df[df['분류'] == '정형외과'].sort_values(by='거리(km)').head(2)
            oriental = df[df['분류'] == '한의원'].sort_values(by='거리(km)').head(2)

            col1, col2 = st.columns(2)
            
            # 병원 정보 출력 함수 (네이버 지도 + 구글 지도 분기 처리)
            def show_hospitals(container, data, category_name):
                with container:
                    st.markdown(f"#### {category_name}")
                    if data.empty:
                        st.write(txt['no_data'])
                    else:
                        for _, row in data.iterrows():
                            dist = int(row['거리(km)'] * 1000)
                            
                            # 네이버 지도 URL (이름 검색)
                            encoded_name = urllib.parse.quote(row['병원명'])
                            naver_url = f"https://map.naver.com/v5/search/{encoded_name}"
                            
                            # 구글 지도 URL (좌표 기반 검색 - 외국인에게 더 정확)
                            google_url = f"https://www.google.com/maps/search/?api=1&query={row['위도']},{row['경도']}"
                            
                            st.markdown(f"**{row['병원명']}** ({dist}m)")
                            st.text(f"📞 {row['전화번호']}")
                            
                            # 버튼 HTML 생성
                            btn_html = f"""
                                <a href="{naver_url}" target="_blank" class="map-btn naver-btn">
                                    {txt['btn_naver']}
                                </a>
                            """
                            
                            # 한국어가 아닐 경우에만 구글 버튼 추가
                            if lang_code != "한국어":
                                btn_html += f"""
                                    <a href="{google_url}" target="_blank" class="map-btn google-btn">
                                        {txt['btn_google']}
                                    </a>
                                """
                            
                            st.markdown(btn_html, unsafe_allow_html=True)
                            st.divider()

            show_hospitals(col1, orthopedics, txt['cat_ortho'])
            show_hospitals(col2, oriental, txt['cat_orient'])
