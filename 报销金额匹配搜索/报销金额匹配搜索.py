import re
from itertools import combinations

def parse_input_numbers(input_str):
    """解析用户输入的数字字符串，支持多种分隔符"""
    # 移除方括号、花括号等常见符号
    cleaned = re.sub(r'[\[\]\{\}\(\)]', '', input_str)
    # 分割数字（支持逗号、空格、分号等分隔符）
    parts = re.split(r'[,\s;]+', cleaned.strip())
    numbers = []
    for part in parts:
        if part:  # 忽略空字符串
            try:
                numbers.append(float(part))
            except ValueError:
                raise ValueError(f"无法解析数字: '{part}'")
    return numbers

def find_all_subsets_with_target(numbers, target):
    """查找所有和等于目标值的子集"""
    # 转换为整数（乘以100）以避免浮点精度问题
    scaled_numbers = [round(x * 100) for x in numbers]
    scaled_target = round(target * 100)
    
    n = len(scaled_numbers)
    valid_subsets = []
    
    # 枚举所有可能的子集（从1到2^n - 1）
    for mask in range(1, 1 << n):
        total = 0
        subset = []
        for i in range(n):
            if mask & (1 << i):
                total += scaled_numbers[i]
                subset.append(numbers[i])
        
        if total == scaled_target:
            valid_subsets.append(subset)
    
    return valid_subsets

def main():
    print("=== 子集和问题求解器 ===")
    print("支持查找给定数字列表中所有和等于目标值的子集")
    print()
    
    # 获取目标值
    while True:
        try:
            target_input = input("请输入目标值: ").strip()
            target = float(target_input)
            break
        except ValueError:
            print("❌ 请输入有效的数字！")
    
    # 获取数据列表
    print("\n请输入数字列表（支持以下格式）:")
    print("- 用逗号分隔: 1.5, 2.3, 3.7")
    print("- 用空格分隔: 1.5 2.3 3.7")
    print("- 混合分隔符: [1.5, 2.3; 3.7 4.1]")
    print("- 直接粘贴列表: [1496, 10.8, 32, 62.43, ...]")
    
    while True:
        try:
            numbers_input = input("\n请输入数字列表: ").strip()
            if not numbers_input:
                print("❌ 输入不能为空！")
                continue
            numbers = parse_input_numbers(numbers_input)
            if not numbers:
                print("❌ 未找到有效数字！")
                continue
            break
        except ValueError as e:
            print(f"❌ {e}")
    
    print(f"\n📊 数据摘要:")
    print(f"目标值: {target}")
    print(f"数字个数: {len(numbers)}")
    print(f"数字列表: {numbers}")
    
    # 检查是否可行（简单优化）
    total_sum = sum(numbers)
    if total_sum < target:
        print(f"\n❌ 所有数字的总和 ({total_sum}) 小于目标值 ({target})，无解！")
        return
    
    if len(numbers) > 25:
        print(f"\n⚠️  注意: 数字个数较多 ({len(numbers)})，计算可能需要较长时间...")
        confirm = input("是否继续？(y/N): ").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print("已取消计算。")
            return
    
    print(f"\n🔍 正在搜索所有可能的子集... (共 {2**len(numbers):,} 种组合)")
    
    # 查找所有解
    try:
        solutions = find_all_subsets_with_target(numbers, target)
    except KeyboardInterrupt:
        print("\n\n⚠️  计算被用户中断！")
        return
    
    # 输出结果
    if solutions:
        print(f"\n✅ 找到 {len(solutions)} 个解：")
        print("=" * 60)
        for i, subset in enumerate(solutions, 1):
            actual_sum = sum(subset)
            print(f"\n解 #{i}:")
            print(f"子集: {subset}")
            print(f"和: {actual_sum}")
            if abs(actual_sum - target) > 1e-10:
                print("⚠️  注意：和与目标值存在微小差异（浮点精度问题）")
        print("=" * 60)
    else:
        print(f"\n❌ 未找到任何子集的和等于 {target}")

if __name__ == "__main__":
    main()