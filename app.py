import streamlit as st
import pandas as pd
import io

# 1. 페이지 기본 설정
st.set_page_config(page_title="상품 자동 매칭 카탈로그", page_icon="👗", layout="wide")

# --- Custom Premium CSS ---
st.markdown("""
<style>
/* 카드 호버 이펙트 및 전체적인 폰트 향상 */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

html, body, [class*="css"]  {
    font-family: 'Pretendard', sans-serif;
}

/* 카드 컨테이너(경계선 래퍼) 디자인 개선 */
[data-testid="stVerticalBlockBorderWrapper"] {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border-radius: 15px;
    background-color: #ffffff;
    border: 1px solid #eaeaea;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.08);
}

/* 다크모드 대응 */
@media (prefers-color-scheme: dark) {
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e1e1e;
        border: 1px solid #333333;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("👗 상품 자동 매칭 카탈로그")
st.write("안내: 포스기에서 다운받은 **엑셀 파일**과 **제품 사진**들을 올려주세요. ✨")

# 2. 파일 업로드 UI (컴맹 작업자용)
col1, col2 = st.columns(2)
with col1:
    excel_file = st.file_uploader("1. 엑셀/CSV 파일 업로드", type=['csv', 'xlsx', 'xls'])
with col2:
    # accept_multiple_files=True 로 수백 장 동시 업로드 지원
    image_files = st.file_uploader("2. 상품 사진 전체 업로드", type=['jpg', 'jpeg', 'png', 'webp'], accept_multiple_files=True)

# 3. 매칭 및 카드형 UI 렌더링 로직
if excel_file and image_files:
    st.divider()
    
    # 엑셀/CSV 데이터 읽기
    try:
        if excel_file.name.endswith('.csv'):
            try:
                df = pd.read_csv(excel_file, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(excel_file, encoding='euc-kr')
        elif excel_file.name.endswith('.xls'):
            df = pd.read_excel(excel_file, engine='xlrd')
        else:
            df = pd.read_excel(excel_file, engine='openpyxl')
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        st.stop()

    # 데이터에 '품번' 컬럼이 찾기 (앞뒤 공백 무시 등 유연한 스캔)
    df.columns = df.columns.str.strip()
    if '품번' not in df.columns:
        st.error("엑셀 파일에 '품번' 열(컬럼)이 없습니다. 포스기 엑셀 양식을 확인해주세요.")
        st.stop()

    # 카드형 레이아웃 세팅 (PC 기준 3~4열. Streamlit은 모바일 접속 시 자동으로 1열로 스태킹됩니다.)
    cols = st.columns([1, 1, 1]) 
    
    for index, row in df.iterrows():
        # 데이터 전처리: '5005.0' 같은 형태를 '5005'로 정리
        item_code = str(row['품번']).replace('.0', '').strip()
        if not item_code or item_code == 'nan':
            continue
            
        # 이미지 매칭: 사진 파일명에 '품번'이 포함되어 있는지 확인
        matched_image = None
        for img in image_files:
            if item_code in img.name:
                matched_image = img
                break
                
        # 매칭된 카드 정보 출력
        with cols[index % 3]:
            with st.container(border=True):
                if matched_image:
                    st.image(matched_image, use_container_width=True)
                else:
                    # 매칭되는 사진이 없을 경우 빈 박스 또는 안내
                    target_height = 200 # 임의 높이
                    st.info(f"📍 사진을 찾을 수 없습니다\n\n(파일명에 '{item_code}' 포함 필요)")
                
                # 텍스트 정보 출력 (상품명 및 정보가 없는 경우 방어코드 추가)
                goods_name = row.get('상품명', '상품명 없음')
                if pd.isna(goods_name): goods_name = '상품명 없음'
                st.subheader(f"{goods_name}")
                st.caption(f"**품번:** `{item_code}`")
                
                color = row.get('색상', '')
                if pd.notna(color) and str(color).strip():
                    st.write(f"**색상:** {color}")
                
                price = row.get('도매가', None)
                if pd.notna(price):
                    try:
                        price_int = int(float(price))
                        st.write(f"**도매가:** {price_int:,}원")
                    except ValueError:
                        st.write(f"**도매가:** {price}")