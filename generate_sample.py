import pandas as pd
import random

def generate_sample_data(num_students=120):
    """
    Generate sample student data for the class placement app.
    """
    first_names = ['민수', '서연', '지호', '지은', '도윤', '하은', '시우', '지아', '지훈', '수아', 
                   '건우', '서진', '현우', '하윤', '우진', '서아', '민준', '유진', '선우', '다은']
    last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', 
                  '한', '오', '서', '신', '권', '황', '안', '송', '전', '홍']
    
    data = []
    for i in range(1, num_students + 1):
        name = random.choice(last_names) + random.choice(first_names)
        gender = random.choice(['남', '여'])
        score = random.randint(40, 100)
        prev_class = random.choice([1, 2, 3, 4, 5])
        
        # Special categories (sparse)
        special_ed = 'O' if random.random() < 0.02 else '' # 특수학급학생
        underachiever = 'O' if random.random() < 0.05 else '' # 학습부진학생
        guidance = 'O' if random.random() < 0.03 else '' # 생활지도필요학생
        
        # Separation/Together (Very sparse)
        # We will manually add some after generating
        
        data.append({
            '학번': str(20250000 + i),
            '이름': name,
            '성별': gender,
            '성적': score,
            '이전반': prev_class,
            '특수학급학생': special_ed,
            '학습부진학생': underachiever,
            '생활지도필요학생': guidance,
            '분리대상': '',
            '동반대상': ''
        })
        
    df = pd.DataFrame(data)
    
    # Let's add some manual separation/together rules
    # 20250001 and 20250002 should be separated
    df.loc[0, '분리대상'] = df.loc[1, '학번']
    df.loc[1, '분리대상'] = df.loc[0, '학번']
    
    # 20250003 and 20250004 should be together
    df.loc[2, '동반대상'] = df.loc[3, '학번']
    df.loc[3, '동반대상'] = df.loc[2, '학번']
    
    df.to_excel('sample_students.xlsx', index=False)
    print("sample_students.xlsx generated successfully!")

if __name__ == '__main__':
    generate_sample_data()
