import streamlit as st
import pandas as pd
import os
import urllib.parse
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. 설정 및 디자인
# ==========================================
st.set_page_config(page_title="RunAid", page_icon="🏃")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F0F8FF;
    }
    
    /* [의료 정보 카드 스타일] */
    .med-card {
        background-color: #ffffff;
        border-left: 5px solid #0078FF; /* 의료용 파란색 */
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .med-title {
        font-size: 20px;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    .med-content {
        font-size: 16px;
        line-height: 1.6;
        color: #444;
        margin-bottom: 15px;
    }
    
    /* [핵심] 클릭 가능한 출처 링크 버튼 스타일 */
    .med-source-link a {
        color: #0078FF;
        text-decoration: none;
        font-weight: bold;
        font-size: 13px;
        background-color: #f1f8ff;
        padding: 8px 12px;
        border-radius: 20px;
        border: 1px solid #cce5ff;
        display: inline-block;
        transition: all 0.2s;
    }
    .med-source-link a:hover {
        background-color: #0078FF;
        color: white;
        text-decoration: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    
    /* 네이버 지도 버튼 */
    .map-btn {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 8px;
        text-decoration: none;
        font-size: 14px;
        font-weight: bold;
        color: white !important;
        background-color: #03C75A;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    .map-btn:hover {
        background-color: #029f48;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. 다국어 텍스트 및 [전문 의학 데이터 + 링크]
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
        "msg_mild_tip": "RunAid 처치 가이드",
        "msg_mild_sub": "본 정보는 전문 가이드라인을 기반으로 하지만, 의사의 진단을 대체할 수 없습니다.",
        "msg_warning": "전문의 진료가 필요합니다.",
        "msg_warning_sub": "자가 처치보다는 병원 방문을 권장합니다.",
        "msg_emerg": "즉각적인 조치가 필요한 응급 상황입니다!",
        "msg_emerg_sub": "더 이상 움직이지 마세요. 즉시 응급실로 가야 합니다.",
        "call_119": "📞 119 전화걸기",
        "hosp_header": "🏥 가장 가까운 병원 / 한의원",
        "cat_ortho": "🦴 [정형외과]",
        "cat_orient": "🌿 [한의원]",
        "btn_naver": "네이버지도 경로 안내",
        "no_data": "근처 정보 없음"
    },
    "English": {
        "title": "RunAid", "loc_header": "1️⃣ Check Location", "loc_info": "Press button for GPS.", "loc_success": "📍 Location Found!", "loc_warn": "Need location.", "body_header": "2️⃣ Injury Info", "body_label": "Select area", "nrs_header": "3️⃣ Pain Level (NRS)", "nrs_guide_cap": "Higher = Worse pain.", "nrs_label": "Pain Score (0-10)", "btn_search": "Diagnose", "err_loc": "Get location first!", "res_header": "🔄 Analysis Result", "msg_mild": "Mild pain.", "msg_mild_tip": "Care Guide", "msg_mild_sub": "Based on guidelines. Not a diagnosis.", "msg_warning": "See a doctor.", "msg_warning_sub": "Visit hospital recommended.", "msg_emerg": "CRITICAL EMERGENCY!", "msg_emerg_sub": "Do NOT move. Call 119.", "call_119": "📞 Call 119", "hosp_header": "🏥 Nearest Hospitals", "cat_ortho": "🦴 [Orthopedics]", "cat_orient": "🌿 [Oriental Clinic]", "btn_naver": "Directions", "no_data": "No info"
    },
    "中文": {
        "title": "RunAid", "loc_header": "1️⃣ 确认位置", "loc_info": "点击按钮获取GPS。", "loc_success": "📍 位置确认！", "loc_warn": "需要位置信息。", "body_header": "2️⃣ 受伤信息", "body_label": "选择部位", "nrs_header": "3️⃣ 疼痛程度 (NRS)", "nrs_guide_cap": "数字越大越痛。", "nrs_label": "选择分数 (0-10)", "btn_search": "开始诊断", "err_loc": "请先获取位置！", "res_header": "🔄 分析结果", "msg_mild": "轻微疼痛。", "msg_mild_tip": "护理建议", "msg_mild_sub": "基于专业指南，不能替代医生诊断。", "msg_warning": "需要就医。", "msg_warning_sub": "建议去医院。", "msg_emerg": "紧急情况！", "msg_emerg_sub": "不要移动，立即拨打119。", "call_119": "📞 拨打 119", "hosp_header": "🏥 最近医院", "cat_ortho": "🦴 [骨科]", "cat_orient": "🌿 [韩医院]", "btn_naver": "路线", "no_data": "无信息"
    },
    "日本語": {
        "title": "RunAid", "loc_header": "1️⃣ 現在地の確認", "loc_info": "ボタンを押してGPS取得。", "loc_success": "📍 位置確認完了！", "loc_warn": "位置情報が必要です。", "body_header": "2️⃣ 怪我情報", "body_label": "部位を選択", "nrs_header": "3️⃣ 痛みの程度 (NRS)", "nrs_guide_cap": "数字が大きいほど痛い。", "nrs_label": "スコア選択 (0-10)", "btn_search": "診断開始", "err_loc": "位置情報を取得してください！", "res_header": "🔄 分析結果", "msg_mild": "軽度の痛み。", "msg_mild_tip": "ケアガイド", "msg_mild_sub": "専門ガイドラインに基づきますが、診断の代わりにはなりません。", "msg_warning": "専門医の診療が必要です。", "msg_warning_sub": "病院へ行くことを推奨。", "msg_emerg": "緊急事態です！", "msg_emerg_sub": "動かず119番してください。", "call_119": "📞 119番", "hosp_header": "🏥 最寄りの病院", "cat_ortho": "🦴 [整形外科]", "cat_orient": "🌿 [韓医院]", "btn_naver": "ルート案内", "no_data": "情報なし"
    }
}

INJURY_DATA = {
    "한국어": {
        "무릎": {
            "diagnosis": "장경인대 증후군(ITBS) 또는 슬개대퇴 통증",
            "action": "1. 즉시 러닝을 중단하십시오.\n2. 무릎 바깥쪽 아이싱(15분)을 실시하세요.\n3. 폼롤러를 이용해 허벅지 바깥쪽을 부드럽게 마사지하세요.",
            "source": "서울아산병원 질환백과: 장경인대 마찰 증후군",
            "link": "https://www.amc.seoul.kr/asan/healthinfo/disease/diseaseDetail.do?contentId=32556"
        },
        "발목": {
            "diagnosis": "발목 염좌 (Ankle Sprain) 의심",
            "action": "즉시 **R.I.C.E 요법**을 실시하세요:\n- **R**est (휴식)\n- **I**ce (냉찜질)\n- **C**ompression (압박)\n- **E**levation (심장보다 높게 거상)",
            "source": "MSD 매뉴얼: 발목 염좌 처치법",
            "link": "https://www.msdmanuals.com/ko-kr/홈/부상-및-중독/염좌-및-기타-연조직-손상/발목-염좌"
        },
        "족저근막": {
            "diagnosis": "족저근막염 (Plantar Fasciitis) 의심",
            "action": "1. 발바닥 아치 부분에 골프공이나 캔을 굴려 마사지하세요.\n2. 아침 기상 직후 발바닥 스트레칭이 가장 중요합니다.",
            "source": "서울대병원 의학정보: 족저근막염",
            "link": "http://www.snuh.org/health/nMedInfo/nView.do?category=DIS&medid=AA000156"
        },
        "종아리": {
            "diagnosis": "비복근 파열 또는 단순 근육 경련",
            "action": "1. **경련 시:** 발끝을 몸 쪽으로 당겨 종아리를 늘려주세요.\n2. **파열(뚝 소리) 시:** 스트레칭 금지. 즉시 냉찜질 후 병원 이동.",
            "source": "MSD 매뉴얼: 근육 경련(쥐)",
            "link": "https://www.msdmanuals.com/ko-kr/홈/뇌,-척수,-신경-장애/증상/근육-경련"
        },
        "허벅지/고관절": {
            "diagnosis": "햄스트링 긴장 또는 파열 의심",
            "action": "허벅지 뒤쪽 통증 시 억지로 늘리는 스트레칭은 **절대 금물**입니다. 얼음찜질 후 압박 붕대를 감고 안정을 취하세요.",
            "source": "자생한방병원 건강칼럼: 햄스트링 부상",
            "link": "https://health.jaseng.co.kr/healthInfo/healthInfoView.do?idx=86"
        },
        "기타": {
            "diagnosis": "상세 불명의 통증",
            "action": "통증이 지속되거나 붓기가 심해지면 즉시 활동을 멈추고 전문가와 상담하세요.",
            "source": "스포츠안전재단: 스포츠 안전 가이드",
            "link": "https://www.kssf.or.kr/"
        }
    },
    "English": {
        "Knee": { "diagnosis": "Runner's Knee", "action": "Ice & Rest.", "source": "Mayo Clinic", "link": "https://www.mayoclinic.org" },
        "Ankle": { "diagnosis": "Ankle Sprain", "action": "R.I.C.E Therapy.", "source": "Red Cross First Aid", "link": "https://www.redcross.org" },
        "Plantar Fascia": { "diagnosis": "Plantar Fasciitis", "action": "Massage arch.", "source": "AAOS Guidelines", "link": "https://orthoinfo.aaos.org" },
        "Calf": { "diagnosis": "Cramp", "action": "Gentle Stretch.", "source": "WebMD", "link": "https://www.webmd.com" },
        "Thigh/Hip": { "diagnosis": "Hamstring", "action": "No stretching.", "source": "FIFA 11+", "link": "https://www.fifamedicalnetwork.com/" },
        "Other": { "diagnosis": "Consult Doctor", "action": "Stop running.", "source": "General Safety", "link": "#" }
    },
    "中文": {
        "膝盖": {"diagnosis": "跑步膝", "action": "冷敷。", "source": "百度健康", "link": "https://health.baidu.com"},
        "脚踝": {"diagnosis": "扭伤", "action": "RICE", "source": "Red Cross", "link": "#"},
        "足底筋膜": {"diagnosis": "筋膜炎", "action": "按摩", "source": "AAOS", "link": "#"},
        "小腿": {"diagnosis": "抽筋", "action": "拉伸", "source": "WebMD", "link": "#"},
        "大腿/髋关节": {"diagnosis": "腘绳肌", "action": "禁止拉伸", "source": "FIFA", "link": "#"},
        "其他": {"diagnosis": "咨询", "action": "停止", "source": "RunAid", "link": "#"}
    },
    "日本語": {
        "膝": {"diagnosis": "ランナー膝", "action": "アイシング。", "source": "MSDマニュアル", "link": "https://www.msdmanuals.com/ja-jp"},
        "足首": {"diagnosis": "捻挫", "action": "RICE", "source": "赤十字", "link": "#"},
        "足底筋膜": {"diagnosis": "筋膜炎", "action": "マッサージ", "source": "AAOS", "link": "#"},
        "ふくらはぎ": {"diagnosis": "こむら返り", "action": "ストレッチ", "source": "MSD", "link": "#"},
        "太もも/股関節": {"diagnosis": "ハムストリング", "action": "安静", "source": "FIFA", "link": "#"},
        "その他": {"diagnosis": "相談", "action": "中止", "source": "RunAid", "link": "#"}
    }
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
# 5. 결과 분석 및 출력 (HTML 링크 버튼 적용)
# ==========================================
if st.button(txt["btn_search"], type="primary"):
    if user_lat is None or user_lon is None:
        st.error(txt["err_loc"])
    else:
        st.markdown("---")
        st.header(txt["res_header"])
        
        # 선택된 부위의 상세 데이터 가져오기 (진단명, 조치, 출처, 링크)
        selected_info = guide_data[body_part]
        
        # 1. 응급 상황 (NRS 8 이상) -> 병원 추천 로직 제외, 119만 표시
        if nrs_score >= 8:
            st.markdown(f"""
                <div class="emergency-box">
                    <div class="emergency-title">🆘 {txt['msg_emerg']}</div>
                    <div class="emergency-desc">{txt['msg_emerg_sub']}</div>
                    <a href="tel:119" class="call-btn">{txt['call_119']}</a>
                </div>
            """, unsafe_allow_html=True)
            
        # 2. 비응급 상황 (자가 처치 정보 + 병원 추천 제공)
        else:
            if nrs_score < 4:
                st.success(f"✅ NRS {nrs_score}: {txt['msg_mild']}")
                
                # 경미한 통증 카드 (출처 버튼 포함)
                st.markdown(f"""
                <div class="med-card">
                    <div class="med-title">🩺 {selected_info['diagnosis']}</div>
                    <div class="med-content">{selected_info['action'].replace(chr(10), '<br>')}</div>
                    
                    <div class="med-source-link">
                        <a href="{selected_info['link']}" target="_blank">
                            📖 {selected_info['source']} 보러가기 🔗
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.caption(txt['msg_mild_sub'])
                
            else:
                st.warning(f"🚨 NRS {nrs_score}: {txt['msg_warning']}")
                
                # 중등도 통증 카드 (주의 문구 + 출처 버튼 포함)
                st.markdown(f"""
                <div class="med-card" style="border-left-color: #ff9800;">
                    <div class="med-title">🩺 {selected_info['diagnosis']}</div>
                    <div class="med-content">
                        <b>{txt['msg_warning_sub']}</b><br><br>
                        {selected_info['action'].replace(chr(10), '<br>')}
                    </div>
                    
                    <div class="med-source-link">
                        <a href="{selected_info['link']}" target="_blank">
                            📖 {selected_info['source']} 보러가기 🔗
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # [수정됨] 병원 추천 로직을 else 블록 내부로 이동 (응급 시 실행 안 됨)
            st.markdown(f"### {txt['hosp_header']}")
            
            df['거리(km)'] = df.apply(
                lambda row: haversine(user_lat, user_lon, float(row['위도']), float(row['경도'])), axis=1
            )
            
            orthopedics = df[df['분류'] == '정형외과'].sort_values(by='거리(km)').head(2)
            oriental = df[df['분류'] == '한의원'].sort_values(by='거리(km)').head(2)

            col1, col2 = st.columns(2)
            
            def show_hospitals(container, data, category_name):
                with container:
                    st.markdown(f"#### {category_name}")
                    if data.empty:
                        st.write(txt['no_data'])
                    else:
                        for _, row in data.iterrows():
                            dist = int(row['거리(km)'] * 1000)
                            encoded_name = urllib.parse.quote(row['병원명'])
                            naver_url = f"https://map.naver.com/v5/search/{encoded_name}"
                            
                            st.markdown(f"**{row['병원명']}** ({dist}m)")
                            st.text(f"📞 {row['전화번호']}")
                            
                            st.markdown(f"""
                                <a href="{naver_url}" target="_blank" class="map-btn">
                                    {txt['btn_naver']}
                                </a>
                            """, unsafe_allow_html=True)
                            st.divider()

            show_hospitals(col1, orthopedics, txt['cat_ortho'])
            show_hospitals(col2, oriental, txt['cat_orient'])
