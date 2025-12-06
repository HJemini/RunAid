st.markdown(
    """
    <style>
    /* [전역 폰트 및 렌더링 설정 개선] */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
        text-rendering: optimizeLegibility; /* 텍스트 렌더링 최적화 */
        -webkit-font-smoothing: antialiased; /* 맥/iOS에서 폰트 부드럽게 */
        -moz-osx-font-smoothing: grayscale;
    }

    .stApp {
        background-color: #F0F8FF;
    }
    
    /* [의료 정보 카드 스타일] */
    .med-card {
        background-color: #ffffff;
        border-left: 5px solid #0078FF;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .med-title {
        font-size: 20px;
        font-weight: 700; /* bold 대신 숫자로 지정하여 선명도 확보 */
        color: #111111; /* #333 -> #111 (더 진하게) */
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        letter-spacing: -0.5px; /* 자간을 살짝 좁혀 가독성 향상 */
    }
    .med-content {
        font-size: 16px;
        line-height: 1.6;
        color: #222222; /* #444 -> #222 (더 진하게) */
        margin-bottom: 10px;
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
        text-shadow: 0 1px 2px rgba(0,0,0,0.1); /* 흰 글씨에 그림자 추가로 선명도 향상 */
    }
    .emergency-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .emergency-desc {
        font-size: 18px;
        margin-bottom: 20px;
        font-weight: 500;
    }
    .call-btn {
        background-color: white;
        color: #FF4B4B;
        padding: 15px 30px;
        text-decoration: none;
        font-size: 24px;
        font-weight: 700;
        border-radius: 50px;
        display: inline-block;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* 네이버 지도 버튼 */
    .map-btn {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 8px;
        text-decoration: none;
        font-size: 14px;
        font-weight: 700;
        color: white !important;
        background-color: #03C75A;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: 0.3s;
        -webkit-font-smoothing: antialiased;
    }
    .map-btn:hover {
        background-color: #029f48;
    }
    </style>
    """,
    unsafe_allow_html=True
)
