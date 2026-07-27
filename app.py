import streamlit as st
import pandas as pd
import io
from allocator import allocate_classes

st.set_page_config(page_title="초등학교 반배정 앱", page_icon="🏫", layout="wide")

# CSS for Jjangu tone
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        color: #ff4b4b;
        font-weight: 900;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-title {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 초등학교 자동 반배정 시스템 🏫</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">호호이! 액션가면보다 빠르게 반배정을 해볼까?</div>', unsafe_allow_html=True)

# Step 1: File Upload
st.header("1단계: 학생 명단 엑셀 파일 업로드 📂")
st.write("학생 명단이 들어있는 엑셀 파일을 올려줘! (형식: 학번, 이름, 성별, 이전반, 분리대상, 동반대상)")

uploaded_file = st.file_uploader("엑셀 파일 선택", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success("짜잔! 파일 업로드 성공! 떡잎마을 방범대 출동 준비 완료!")
        st.write("미리보기:")
        st.dataframe(df.head())
        
        # Step 2: Settings
        st.header("2단계: 반배정 설정 ⚙️")
        col1, col2 = st.columns(2)
        
        with col1:
            num_classes = st.number_input("올해는 몇 반까지 있어?", min_value=1, max_value=20, value=5, step=1)
            
        # Step 3: Run Algorithm
        st.header("3단계: 자동 반배정 실행 🚀")
        if st.button("반배정 시작!"):
            with st.spinner("흰둥아 물어와! 빙글빙글 돌아가는 중..."):
                result_df = allocate_classes(df, num_classes)
                
            st.success("완성! 반배정이 끝났어! 🎉")
            
            # Show summary
            st.subheader("📊 반배정 요약 (성비)")
            summary = result_df.groupby(['배정반', '성별']).size().unstack(fill_value=0)
            summary['총인원'] = summary.sum(axis=1)
            st.dataframe(summary)
            
            st.subheader("📋 전체 배정 결과")
            st.dataframe(result_df)
            
            # Step 4: Download
            st.header("4단계: 결과 다운로드 💾")
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                result_df.to_excel(writer, index=False, sheet_name='반배정결과')
                summary.to_excel(writer, sheet_name='통계요약')
            
            processed_data = output.getvalue()
            
            st.download_button(
                label="엑셀로 다운로드 받기 📥",
                data=processed_data,
                file_name="class_placement_result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    except Exception as e:
        st.error(f"으악! 에러가 났어! 확인해봐: {e}")
else:
    st.info("파일을 업로드하면 다음 단계가 나타날 거야!")
