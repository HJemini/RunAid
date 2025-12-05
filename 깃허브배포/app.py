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
        "loc_success": "📍
