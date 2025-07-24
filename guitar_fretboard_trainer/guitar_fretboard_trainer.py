import random

# 吉他标准调弦的空弦音（1-6弦）及其八度
STRING_NOTES = [
    (6, 'E', 2),  # 6弦空弦 E2
    (5, 'A', 2),  # 5弦空弦 A2
    (4, 'D', 3),  # 4弦空弦 D3
    (3, 'G', 3),  # 3弦空弦 G3
    (2, 'B', 3),  # 2弦空弦 B3
    (1, 'E', 4)   # 1弦空弦 E4
]

# 所有可能的音（使用升号表示）
ALL_NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NATURAL_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']  # 自然音（无升降号）

def get_note_with_octave(base_note, base_octave, fret):
    """
    计算指定弦上某品的完整音名（包含八度）
    :param base_note: 空弦音名
    :param base_octave: 空弦八度
    :param fret: 品号
    :return: (音名, 八度数)
    """
    base_index = ALL_NOTES.index(base_note)
    note_index = (base_index + fret) % len(ALL_NOTES)
    note = ALL_NOTES[note_index]
    
    # 计算八度变化（每12品升高一个八度）
    octave_change = fret // 12
    octave = base_octave + octave_change
    
    return note, octave

def is_natural_note(note_name):
    """检查是否是自然音（无升降号）"""
    return note_name in NATURAL_NOTES

def guitar_fretboard_trainer():
    print("吉他指板记忆训练器")
    
    # 用户设置
    include_high_frets = input("是否包含13-22品？(y/n): ").lower() == 'y'
    max_fret = 22 if include_high_frets else 12
    
    include_sharps_flats = input("是否包含升降音？(y/n): ").lower() != 'n'
    
    while True:
        # 尝试生成符合条件的音符
        valid_note_found = False
        attempts = 0
        
        while not valid_note_found and attempts < 100:  # 防止无限循环
            # 随机选择弦
            string_data = random.choice(STRING_NOTES)
            string_num, base_note, base_octave = string_data
            
            # 随机选择品（0到最大品）
            fret = random.randint(0, max_fret)
            
            # 获取完整音名（含八度）
            note, octave = get_note_with_octave(base_note, base_octave, fret)
            full_note = f"{note}{octave}"
            
            # 如果不包含升降音，检查是否是自然音
            if include_sharps_flats or is_natural_note(note):
                valid_note_found = True
            else:
                attempts += 1
        
        if not valid_note_found:
            print("无法生成符合条件的自然音，请尝试扩大品范围或包含升降音。")
            break
        
        # 显示问题和弦号
        user_input = input(f"\n音: {full_note}  弦: {string_num} \n")
        if user_input.lower() == 'q':
            break
        
        # 显示答案
        print(f"→ 品: {fret}   (弦{string_num}空弦音: {base_note}{base_octave})")
        
        # 继续提示
        user_input = input("\n按Enter继续练习，输入q退出...")
        if user_input.lower() == 'q':
            break
    
    print("\n练习结束！")

if __name__ == "__main__":
    guitar_fretboard_trainer()