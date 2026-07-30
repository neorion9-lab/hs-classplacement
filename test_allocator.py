import pandas as pd
from allocator import allocate_classes

df = pd.read_excel('sample_students.xlsx')
result = allocate_classes(df, 5)

print("Class placement successful.")
print(result.groupby(['배정반', '성별']).size().unstack(fill_value=0))

# Check separation
sep_students = df[df['분리대상'].notna() & (df['분리대상'] != '')]
print("\nSeparation constraints check:")
for _, row in sep_students.iterrows():
    student_id = str(row['학번']).split('.')[0]
    targets = [str(t).strip().split('.')[0] for t in str(row['분리대상']).split(',')]
    
    match = result[result['학번'] == student_id]
    if match.empty: continue
    student_class = match['배정반'].iloc[0]
    
    target_classes = []
    for t in targets:
        target_class_series = result[result['학번'] == t]['배정반']
        if not target_class_series.empty:
            target_classes.append(target_class_series.iloc[0])
    
    print(f"Student {student_id} is in class {student_class}. Targets {targets} are in {target_classes}")
    if student_class in target_classes:
        print("ERROR! Separation constraint violated.")

# Check together
tog_students = df[df['동반대상'].notna() & (df['동반대상'] != '')]
print("\nTogether constraints check:")
for _, row in tog_students.iterrows():
    student_id = str(row['학번']).split('.')[0]
    targets = [str(t).strip().split('.')[0] for t in str(row['동반대상']).split(',')]
    
    match = result[result['학번'] == student_id]
    if match.empty: continue
    student_class = match['배정반'].iloc[0]
    
    target_classes = []
    for t in targets:
        target_class_series = result[result['학번'] == t]['배정반']
        if not target_class_series.empty:
            target_classes.append(target_class_series.iloc[0])
    
    print(f"Student {student_id} is in class {student_class}. Targets {targets} are in {target_classes}")
    print(f"Student {student_id} is in class {student_class}. Targets {targets} are in {target_classes}")
    if any(tc != student_class for tc in target_classes):
        print("ERROR! Together constraint violated.")

# Check special categories distribution
print("\nSpecial Categories Distribution:")
print("Underachievers (학습부진학생):")
under_dist = result[result['학습부진학생'] == 'O'].groupby('배정반').size()
print(under_dist)

print("\nGuidance Needed (생활지도필요학생):")
guidance_dist = result[result['생활지도필요학생'] == 'O'].groupby('배정반').size()
print(guidance_dist)
