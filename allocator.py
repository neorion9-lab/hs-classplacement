import pandas as pd
import random

def allocate_classes(df, num_classes):
    """
    df: pandas DataFrame containing student data.
    num_classes: integer, number of classes to form.
    Returns: a new DataFrame with a '배정반' column.
    """
    df = df.copy()
    
    # Initialize classes
    classes = {i: [] for i in range(1, num_classes + 1)}
    
    # Track class counts
    class_counts = {i: {'남': 0, '여': 0, 'total': 0, '학습부진학생': 0, '생활지도필요학생': 0} for i in range(1, num_classes + 1)}
    
    # Convert dataframe to list of dicts for easier manipulation
    students = df.to_dict('records')
    # Ensure all student IDs are strings
    for s in students:
        s['학번'] = str(s['학번']).split('.')[0]
    
    # Dictionary to keep track of placed students to avoid duplicates
    placed = set()
    
    def add_to_class(student, c_idx):
        if student['학번'] in placed:
            return
        classes[c_idx].append(student)
        class_counts[c_idx][student['성별']] += 1
        class_counts[c_idx]['total'] += 1
        if str(student.get('학습부진학생', '')).strip() == 'O':
            class_counts[c_idx]['학습부진학생'] += 1
        if str(student.get('생활지도필요학생', '')).strip() == 'O':
            class_counts[c_idx]['생활지도필요학생'] += 1
        placed.add(student['학번'])
        
    def get_best_class_for_student(student, exclude_classes=None):
        if exclude_classes is None:
            exclude_classes = []
        
        valid_classes = [c for c in range(1, num_classes + 1) if c not in exclude_classes]
        if not valid_classes:
            return random.choice(range(1, num_classes + 1))
            
        is_underachiever = str(student.get('학습부진학생', '')).strip() == 'O'
        is_guidance = str(student.get('생활지도필요학생', '')).strip() == 'O'
        
        def class_score(c):
            score = []
            if is_underachiever:
                score.append(class_counts[c]['학습부진학생'])
            if is_guidance:
                score.append(class_counts[c]['생활지도필요학생'])
            score.append(class_counts[c][student['성별']])
            return tuple(score)
            
        best_c = min(valid_classes, key=class_score)
        return best_c

    def get_given_name(full_name):
        full_name = str(full_name).strip()
        if len(full_name) <= 2:
            return full_name[1:] if len(full_name) == 2 else full_name
        elif len(full_name) == 4:
            two_char_family_names = ["남궁", "황보", "제갈", "사공", "선우", "서문", "독고", "동방", "어구"]
            if full_name[:2] in two_char_family_names:
                return full_name[2:]
        return full_name[1:]

    # 0. Process Same Given Names (동명이인 분리)
    given_name_groups = {}
    for s in students:
        gn = get_given_name(s['이름'])
        if gn not in given_name_groups:
            given_name_groups[gn] = []
        given_name_groups[gn].append(s['학번'])
        
    for s in students:
        gn = get_given_name(s['이름'])
        same_name_ids = [tid for tid in given_name_groups[gn] if tid != s['학번']]
        if same_name_ids:
            current_sep = s.get('분리대상')
            if pd.notna(current_sep) and str(current_sep).strip() != '' and str(current_sep) != 'nan':
                existing = [x.strip().split('.')[0] for x in str(current_sep).split(',')]
            else:
                existing = []
            
            combined = list(set(existing + same_name_ids))
            s['분리대상'] = ','.join(combined)

    # 1. Process "Together" constraints
    # Group students who need to be together
    for s in students:
        if pd.notna(s.get('동반대상')) and str(s.get('동반대상')).strip() != '':
            if s['학번'] not in placed:
                # Excel might load IDs as floats e.g., '20250002.0'
                target_ids = [str(tid).strip().split('.')[0] for tid in str(s['동반대상']).split(',')]
                group = [s]
                for other_s in students:
                    if other_s['학번'] in target_ids and other_s['학번'] not in placed:
                        group.append(other_s)
                
                # Pick a class for this group
                # For simplicity, pick the class with lowest total
                best_c = min(range(1, num_classes + 1), key=lambda c: class_counts[c]['total'])
                for member in group:
                    add_to_class(member, best_c)

    # 2. Process "Separation" constraints
    for s in students:
        if pd.notna(s.get('분리대상')) and str(s.get('분리대상')).strip() != '':
            if s['학번'] not in placed:
                # Excel might load IDs as floats e.g., '20250002.0'
                target_ids = [str(tid).strip().split('.')[0] for tid in str(s['분리대상']).split(',')]
                
                # Check where target students are already placed
                excluded_classes = set()
                target_students = []
                for other_s in students:
                    if other_s['학번'] in target_ids:
                        target_students.append(other_s)
                        # Find if other_s is placed
                        for c_idx, c_list in classes.items():
                            if any(x['학번'] == other_s['학번'] for x in c_list):
                                excluded_classes.add(c_idx)
                                break
                                
                best_c = get_best_class_for_student(s, exclude_classes=list(excluded_classes))
                add_to_class(s, best_c)
                
                # If target students are not placed yet, place them in different classes
                for ts in target_students:
                    if ts['학번'] not in placed:
                        excluded = excluded_classes.copy()
                        excluded.add(best_c) # Don't put where we just put 's'
                        ts_best_c = get_best_class_for_student(ts, exclude_classes=list(excluded))
                        add_to_class(ts, ts_best_c)
                        excluded_classes.add(ts_best_c)

    # 3. Process the rest (distribute evenly by special categories, then gender)
    remaining = [s for s in students if s['학번'] not in placed]
    
    # 3-1. Place students with special needs first
    special_needs = [s for s in remaining if str(s.get('학습부진학생', '')).strip() == 'O' or str(s.get('생활지도필요학생', '')).strip() == 'O']
    random.shuffle(special_needs)
    for s in special_needs:
        best_c = get_best_class_for_student(s)
        add_to_class(s, best_c)
        
    # 3-2. Place the rest
    regular = [s for s in students if s['학번'] not in placed]
    random.shuffle(regular)
    
    for s in regular:
        best_c = get_best_class_for_student(s)
        add_to_class(s, best_c)
        
    # Reconstruct DataFrame with '배정반'
    result_data = []
    for c_idx, s_list in classes.items():
        for s in s_list:
            s_copy = dict(s)
            s_copy['배정반'] = c_idx
            result_data.append(s_copy)
            
    result_df = pd.DataFrame(result_data)
    # Sort by class and then by name
    result_df = result_df.sort_values(by=['배정반', '이름']).reset_index(drop=True)
    return result_df
