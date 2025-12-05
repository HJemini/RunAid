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
        border-left: 5px solid #0078FF; /* 기본 파란색 (동적으로 변경됨) */
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
        margin-bottom: 10px;
    }
    
    /* 응급 박스 스타일 (NRS 8점 이상일 때 표시) */
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
# 2. 다국어 텍스트 및 데이터 (NRS 단계별 action 분리)
# ==========================================
LANG_TEXT = {
    "한국어": {
        "title": "RunAid", "loc_header": "1️⃣ 현재 위치 확인", "loc_info": "아래 버튼을 누르면 GPS 정보를 가져옵니다.", "loc_success": "📍 위치 확인 완료!", "loc_warn": "위치 정보를 가져와야 병원을 추천할 수 있습니다.", "body_header": "2️⃣ 부상 정보 입력", "body_label": "아픈 부위를 선택하세요", "nrs_header": "3️⃣ 통증 정도 입력 (NRS)", "nrs_guide_cap": "💡 NRS: 숫자가 클수록 통증이 심함을 의미합니다.", "nrs_label": "통증 점수를 선택하세요 (0 ~ 10)", "btn_search": "병원 찾기 & 진단 시작", "err_loc": "먼저 상단의 버튼을 눌러 위치 정보를 가져와주세요!", "res_header": "🔄 분석 결과", "msg_mild": "경미한 통증입니다.", "msg_warning": "전문의 진료가 필요합니다.", "msg_emerg": "즉각적인 조치가 필요한 응급 상황입니다!", "msg_emerg_sub": "더 이상 움직이지 마세요. 즉시 응급실로 가야 합니다.", "call_119": "📞 119 전화걸기", "hosp_header": "🏥 가장 가까운 병원 / 한의원", "cat_ortho": "🦴 [정형외과]", "cat_orient": "🌿 [한의원]", "btn_naver": "네이버지도 경로 안내", "no_data": "근처 정보 없음",
        "guide_self": "💊 자가 처치법 (Self-care)", "guide_emerg": "🩹 응급처치 (First Aid)", "guide_sub_warning": "※ 자가 처치보다는 병원 방문을 권장합니다.", "guide_sub_mild": "※ 본 정보는 가이드라인이며 의사의 진단을 대체할 수 없습니다.",
        "source_label": "출처"
    },
    "English": {
        "title": "RunAid", "loc_header": "1️⃣ Check Location", "loc_info": "Press button for GPS.", "loc_success": "📍 Location Found!", "loc_warn": "Need location.", "body_header": "2️⃣ Injury Info", "body_label": "Select area", "nrs_header": "3️⃣ Pain Level (NRS)", "nrs_guide_cap": "Higher = Worse pain.", "nrs_label": "Pain Score (0-10)", "btn_search": "Diagnose", "err_loc": "Get location first!", "res_header": "🔄 Analysis Result", "msg_mild": "Mild pain.", "msg_warning": "See a doctor.", "msg_emerg": "CRITICAL EMERGENCY!", "msg_emerg_sub": "Do NOT move. Call 119.", "call_119": "📞 Call 119", "hosp_header": "🏥 Nearest Hospitals", "cat_ortho": "🦴 [Orthopedics]", "cat_orient": "🌿 [Oriental Clinic]", "btn_naver": "Directions", "no_data": "No info",
        "guide_self": "💊 Self-care Method", "guide_emerg": "🩹 First Aid / Emergency Care", "guide_sub_warning": "※ Hospital visit recommended.", "guide_sub_mild": "※ Not a medical diagnosis.",
        "source_label": "Source"
    },
    "中文": {
        "title": "RunAid", "loc_header": "1️⃣ 确认位置", "loc_info": "点击按钮获取GPS。", "loc_success": "📍 位置确认！", "loc_warn": "需要位置信息。", "body_header": "2️⃣ 受伤信息", "body_label": "选择部位", "nrs_header": "3️⃣ 疼痛程度 (NRS)", "nrs_guide_cap": "数字越大越痛。", "nrs_label": "选择分数 (0-10)", "btn_search": "开始诊断", "err_loc": "请先获取位置！", "res_header": "🔄 分析结果", "msg_mild": "轻微疼痛。", "msg_warning": "需要就医。", "msg_emerg": "紧急情况！", "msg_emerg_sub": "不要移动，立即拨打119。", "call_119": "📞 拨打 119", "hosp_header": "🏥 最近医院", "cat_ortho": "🦴 [骨科]", "cat_orient": "🌿 [韩医院]", "btn_naver": "路线", "no_data": "无信息",
        "guide_self": "💊 自我护理", "guide_emerg": "🩹 应急处理", "guide_sub_warning": "※ 建议去医院。", "guide_sub_mild": "※ 不能替代医生诊断。",
        "source_label": "来源"
    },
    "日本語": {
        "title": "RunAid", "loc_header": "1️⃣ 現在地の確認", "loc_info": "ボタンを押してGPS取得。", "loc_success": "📍 位置確認完了！", "loc_warn": "位置情報が必要です。", "body_header": "2️⃣ 怪我情報", "body_label": "部位を選択", "nrs_header": "3️⃣ 痛みの程度 (NRS)", "nrs_guide_cap": "数字が大きいほど痛い。", "nrs_label": "スコア選択 (0-10)", "btn_search": "診断開始", "err_loc": "位置情報を取得してください！", "res_header": "🔄 分析結果", "msg_mild": "軽度の痛み。", "msg_warning": "専門医の診療が必要です。", "msg_emerg": "緊急事態です！", "msg_emerg_sub": "動かず119番してください。", "call_119": "📞 119番", "hosp_header": "🏥 最寄りの病院", "cat_ortho": "🦴 [整形外科]", "cat_orient": "🌿 [韓医院]", "btn_naver": "ルート案内", "no_data": "情報なし",
        "guide_self": "💊 セルフケア法", "guide_emerg": "🩹 応急処置", "guide_sub_warning": "※ 病院へ行くことを推奨。", "guide_sub_mild": "※ 診断の代わりにはなりません。",
        "source_label": "出典"
    }
}

# [데이터 구조] action -> mild / mod / emerg 3단계로 분리
INJURY_DATA = {
    "한국어": {
        "무릎": {
            "diagnosis": "장경인대 증후군(ITBS) 또는 무릎 연골 손상",
            "action_mild": "1. 러닝 속도를 줄이고 걷기로 전환하세요.\n2. 운동 후 폼롤러로 허벅지 바깥쪽을 마사지하세요.",
            "action_mod": "1. **즉시 러닝을 중단**하십시오.\n2. 무릎 바깥쪽에 얼음찜질(15분)을 하세요.\n3. 통증이 가라앉을 때까지 며칠간 휴식하세요.",
            "action_emerg": "1. **절대 걷거나 무릎을 구부리지 마십시오.**\n2. 골절이나 인대 파열 가능성이 있습니다. 즉시 응급 이송이 필요합니다.",
            "source": "서울아산병원 질환백과"
        },
        "발목": {
            "diagnosis": "발목 염좌 (Ankle Sprain)",
            "action_mild": "1. 발목을 천천히 돌리며 가동 범위를 확인하세요.\n2. 울퉁불퉁한 지면을 피해서 걷거나 천천히 뛰세요.",
            "action_mod": "1. **R.I.C.E 요법** 필수 (휴식, 냉찜질, 압박, 거상).\n2. 체중을 싣지 말고 즉시 귀가하여 안정을 취하세요.",
            "action_emerg": "1. 신발을 벗기지 말고(압박 유지) 그대로 두세요.\n2. 발목이 붓는 속도가 빠르다면 골절일 수 있습니다. 움직이지 말고 119를 부르세요.",
            "source": "MSD 매뉴얼"
        },
        "족저근막": {
            "diagnosis": "족저근막염 (Plantar Fasciitis)",
            "action_mild": "1. 발바닥 아치 부분에 골프공이나 캔을 굴려 마사지하세요.\n2. 아킬레스건 스트레칭을 가볍게 시행하세요.",
            "action_mod": "1. 러닝을 멈추고 쿠션이 좋은 신발로 갈아 신으세요.\n2. 귀가 후 차가운 물병으로 발바닥을 문지르세요.",
            "action_emerg": "1. 발을 디딜 수 없을 정도라면 족저근막 파열일 수 있습니다.\n2. 발을 땅에 닿지 않게 하고 병원으로 이동하세요.",
            "source": "서울대병원 의학정보"
        },
        "종아리": {
            "diagnosis": "비복근 파열 또는 근육 경련(쥐)",
            "action_mild": "1. 수분을 섭취하세요.\n2. 발끝을 몸 쪽으로 당겨 종아리를 부드럽게 늘려주세요.",
            "action_mod": "1. 뚝 소리가 났다면 스트레칭을 멈추세요(파열 위험).\n2. 즉시 얼음찜질을 하고 다리를 심장보다 높게 올리세요.",
            "action_emerg": "1. 근육 파열이나 아킬레스건 손상이 의심됩니다.\n2. **절대 스트레칭 금지**. 다리를 고정하고 즉시 응급실로 가야 합니다.",
            "source": "MSD 매뉴얼"
        },
        "허벅지/고관절": {
            "diagnosis": "햄스트링 긴장 또는 파열",
            "action_mild": "1. 보폭을 줄이고 속도를 낮추세요.\n2. 무리한 스트레칭보다는 가벼운 걷기로 쿨다운하세요.",
            "action_mod": "1. **스트레칭 절대 금지** (찢어진 부위가 넓어질 수 있습니다).\n2. 허벅지 뒤쪽에 냉찜질을 하고 압박 붕대를 감으세요.",
            "action_emerg": "1. 걷기가 불가능하다면 골반 박리 골절이나 완전 파열일 수 있습니다.\n2. 부축을 받아 이동하거나 119를 부르세요.",
            "source": "자생한방병원 건강칼럼"
        },
        "기타": {
            "diagnosis": "상세 불명의 통증",
            "action_mild": "잠시 멈춰서 휴식을 취하고 상태를 지켜보세요.",
            "action_mod": "통증이 지속되므로 즉시 운동을 종료하세요.",
            "action_emerg": "의식을 잃거나 호흡이 곤란하면 즉시 119에 신고하세요.",
            "source": "스포츠안전재단"
        }
    },
    "English": {
        "Knee": { "diagnosis": "Runner's Knee", "action_mild": "Reduce speed, stretch glutes.", "action_mod": "Stop running. Ice immediately.", "action_emerg": "Do not move. Call ambulance.", "source": "Mayo Clinic" },
        "Ankle": { "diagnosis": "Ankle Sprain", "action_mild": "Slow down, watch your step.", "action_mod": "Stop. R.I.C.E therapy.", "action_emerg": "Possible fracture. Do not walk.", "source": "Red Cross" },
        "Plantar Fascia": { "diagnosis": "Plantar Fasciitis", "action_mild": "Massage arch with ball.", "action_mod": "Stop running. Ice massage.", "action_emerg": "Severe pain. Do not weight bear.", "source": "AAOS" },
        "Calf": { "diagnosis": "Calf Strain/Cramp", "action_mild": "Hydrate and gentle stretch.", "action_mod": "Stop. Ice and Compress.", "action_emerg": "Suspected rupture. Do NOT stretch.", "source": "WebMD" },
        "Thigh/Hip": { "diagnosis": "Hamstring Injury", "action_mild": "Shorten stride.", "action_mod": "Stop. No stretching. Ice.", "action_emerg": "Cannot walk. Seek emergency care.", "source": "FIFA 11+" },
        "Other": { "diagnosis": "Unknown Pain", "action_mild": "Rest briefly.", "action_mod": "Stop activity.", "action_emerg": "Call 119 immediately.", "source": "General Safety" }
    },
    "中文": {
        "膝盖": {"diagnosis": "跑步膝", "action_mild": "减速，拉伸。", "action_mod": "停止跑步，冷敷。", "action_emerg": "不要移动，呼叫救护车。", "source": "百度健康"},
        "脚踝": {"diagnosis": "扭伤", "action_mild": "减慢速度。", "action_mod": "停止，RICE疗法。", "action_emerg": "可能骨折，禁止行走。", "source": "Red Cross"},
        "足底筋膜": {"diagnosis": "筋膜炎", "action_mild": "按摩足底。", "action_mod": "停止，冰敷按摩。", "action_emerg": "剧痛，禁止负重。", "source": "AAOS"},
        "小腿": {"diagnosis": "抽筋", "action_mild": "补水，轻微拉伸。", "action_mod": "停止，冰敷。", "action_emerg": "疑似断裂，禁止拉伸。", "source": "WebMD"},
        "大腿/髋关节": {"diagnosis": "腘绳肌", "action_mild": "减小步幅。", "action_mod": "停止，禁止拉伸，冷敷。", "action_emerg": "无法行走，急诊。", "source": "FIFA"},
        "其他": {"diagnosis": "其他疼痛", "action_mild": "休息。", "action_mod": "停止运动。", "action_emerg": "立即拨打119。", "source": "RunAid"}
    },
    "日本語": {
        "膝": {"diagnosis": "ランナー膝", "action_mild": "減速し、ストレッチ。", "action_mod": "中止し、アイシング。", "action_emerg": "動かさず、救急車を呼ぶ。", "source": "MSDマニュアル"},
        "足首": {"diagnosis": "捻挫", "action_mild": "ペースを落とす。", "action_mod": "中止。RICE処置。", "action_emerg": "骨折の疑い。歩行禁止。", "source": "赤十字"},
        "足底筋膜": {"diagnosis": "筋膜炎", "action_mild": "足裏マッサージ。", "action_mod": "中止。氷マッサージ。", "action_emerg": "激痛。体重をかけない。", "source": "AAOS"},
        "ふくらはぎ": {"diagnosis": "こむら返り", "action_mild": "水分補給、軽いストレッチ。", "action_mod": "中止。アイシング。", "action_emerg": "断裂の疑い。ストレッチ禁止。", "source": "MSD"},
        "太もも/股関節": {"diagnosis": "ハムストリング", "action_mild": "歩幅を狭める。", "action_mod": "中止。ストレッチ禁止。", "action_emerg": "歩行不可。救急搬送。", "source": "FIFA"},
        "その他": {"diagnosis": "その他", "action_mild": "休憩。", "action_mod": "運動中止。", "action_emerg": "直ちに119番。", "source": "RunAid"}
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
# 5. 결과 분석 및 출력
# ==========================================
if st.button(txt["btn_search"], type="primary"):
    if user_lat is None or user_lon is None:
        st.error(txt["err_loc"])
    else:
        st.markdown("---")
        st.header(txt["res_header"])
        
        selected_info = guide_data[body_part]

        # 변수 초기화
        card_title_prefix = ""
        sub_desc = ""
        border_color = "#0078FF"
        final_action_text = ""

        # ------------------------------------------------
        # [핵심 로직] NRS 점수에 따라 처치법과 UI 변경
        # ------------------------------------------------
        if nrs_score >= 8:
            # 1. 응급 (NRS 8~10) -> 붉은 박스 표시 & 응급처치 텍스트
            st.markdown(f"""
                <div class="emergency-box">
                    <div class="emergency-title">🆘 {txt['msg_emerg']}</div>
                    <div class="emergency-desc">{txt['msg_emerg_sub']}</div>
                    <a href="tel:119" class="call-btn">{txt['call_119']}</a>
                </div>
            """, unsafe_allow_html=True)
            
            card_title_prefix = txt['guide_emerg']
            sub_desc = txt['msg_emerg_sub']
            border_color = "#FF4B4B"
            final_action_text = selected_info['action_emerg']

        elif nrs_score >= 4:
            # 2. 중등도 (NRS 4~7) -> 경고 & 중등도 처치 텍스트
            st.warning(f"🚨 NRS {nrs_score}: {txt['msg_warning']}")
            
            card_title_prefix = txt['guide_emerg']
            sub_desc = txt['guide_sub_warning']
            border_color = "#ff9800"
            final_action_text = selected_info['action_mod']

        else:
            # 3. 경미 (NRS 0~3) -> 자가 처치 텍스트
            st.success(f"✅ NRS {nrs_score}: {txt['msg_mild']}")
            
            card_title_prefix = txt['guide_self']
            sub_desc = txt['guide_sub_mild']
            border_color = "#0078FF"
            final_action_text = selected_info['action_mild']

        # ------------------------------------------------
        # [정보 카드] 처치법 + 단순화된 출처 표시
        # ------------------------------------------------
        st.markdown(f"""
        <div class="med-card" style="border-left-color: {border_color};">
            <div class="med-title">🩺 {card_title_prefix} : {selected_info['diagnosis']}</div>
            <div class="med-content">
                <div style="color: #666; font-size: 0.9em; margin-bottom: 10px;">{sub_desc}</div>
                {final_action_text.replace(chr(10), '<br>')}
                <br><br>
                <span style="color: #999; font-size: 0.85em;">
                    ℹ️ {txt['source_label']}: {selected_info['source']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ------------------------------------------------
        # [병원 추천] 응급 상황(8점 이상)이 아닐 때만 표시
        # ------------------------------------------------
        if nrs_score < 8:
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
