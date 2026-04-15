import sys
import os

def fix_eggnog_format(input_file, output_file):
    print(f"[-] 正在读取文件: {input_file}")
    
    fixed_count = 0
    header_processed = False
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f_in, \
             open(output_file, 'w', encoding='utf-8') as f_out:
            
            for line_idx, line in enumerate(f_in):
                original_line = line
                stripped_line = line.strip()
                
                # 跳过空行
                if not stripped_line:
                    continue

                # 核心逻辑：检测这是不是表头行
                # EggNOG 的表头通常包含 'query', 'seed_ortholog', 'evalue', 'score' 等关键词
                is_header_line = False
                if ('query' in stripped_line.lower() and 'evalue' in stripped_line.lower()) or \
                   ('Query_ID' in stripped_line and 'Evalue' in stripped_line):
                    is_header_line = True

                if is_header_line:
                    # 如果找到了表头行
                    if not stripped_line.startswith('#'):
                        # 情况A：表头没有 # 号（这是导致报错的元凶）
                        # 修复：加上 # 号，让 TBtools 把它当成注释跳过
                        new_line = '#' + stripped_line + '\n'
                        f_out.write(new_line)
                        print(f"[-] [修复] 第 {line_idx+1} 行看起来像表头但缺少'#'，已自动添加。")
                        header_processed = True
                    else:
                        # 情况B：表头已有 # 号，直接写入
                        f_out.write(original_line)
                        header_processed = True
                else:
                    # 处理数据行
                    if stripped_line.startswith('#'):
                        # 普通注释行，保留
                        f_out.write(original_line)
                    else:
                        # 纯数据行，保留
                        # 这里的逻辑是原样输出，保证数据完整性
                        f_out.write(original_line)
                        
        print(f"[-] 文件处理完毕！")
        print(f"[-] 输出文件: {output_file}")
        print(f"[-] 现在您可以将 {output_file} 投入 TBtools 的 EggNOG-mapper Helper 中运行了。")

    except Exception as e:
        print(f"[!] 处理出错: {e}")

if __name__ == "__main__":
    # 使用方法： python fix_for_helper.py 输入文件 输出文件
    
    if len(sys.argv) < 2:
        print("请提供输入文件名！")
        print("用法: python fix_for_helper.py UV_eggnog_output.emapper.annotations fixed_output.txt")
    else:
        input_filename = sys.argv[1]
        # 如果没指定输出名，自动加个前缀
        if len(sys.argv) >= 3:
            output_filename = sys.argv[2]
        else:
            output_filename = "Fixed_" + input_filename
            
        if not os.path.exists(input_filename):
            print(f"[!] 找不到文件: {input_filename}")
        else:
            fix_eggnog_format(input_filename, output_filename)