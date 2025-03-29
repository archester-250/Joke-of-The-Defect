import csv
import os

def process_comments():
    # 初始化计数器
    counter = 1
    # 获取当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    comments_dir = os.path.join(base_dir, 'comments')
    output_file = os.path.join(base_dir, 'Joke-of-The-Defect.md')
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as md_file:
        # 写入标题
        md_file.write('# 鸡煲笑话大全\n\n')
        
        # 遍历comments目录下所有csv文件
        for filename in os.listdir(comments_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(comments_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as csv_file:
                        reader = csv.DictReader(csv_file)
                        for row in reader:
                            # 处理换行符并写入Markdown
                            content = row['content'].replace('\n', ' ').strip()
                            if content:
                                md_file.write(f'{counter}. {content}\n')
                                counter += 1
                except Exception as e:
                    print(f'处理文件 {filename} 时出错: {e}')

if __name__ == '__main__':
    process_comments()
    print('处理完成，结果已保存至 Joke-of-The-Defect.md')