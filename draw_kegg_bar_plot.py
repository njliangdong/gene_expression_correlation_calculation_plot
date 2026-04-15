import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import numpy as np
import matplotlib as mpl

# 设置全局字体，尽量模拟学术期刊风格
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['font.sans-serif'] = ['Arial', 'Liberation Sans', 'DejaVu Sans', 'sans-serif']

def plot_kegg_bubble(input_file, output_file, top_n=20):
    # 1. 读取数据 (处理 TBtools 的制表符格式)
    try:
        df = pd.read_csv(input_file, sep='\t')
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    # 2. 映射实际表头
    # 根据你提供的反馈：
    # Term Name -> 路径名称
    # GeneHitsInSelectedSet -> Count (气泡大小)
    # enrichFactor -> X轴
    # p-value -> 颜色 (显著性)
    
    try:
        plot_df = pd.DataFrame({
            'Term': df['Term Name'],
            'Count': df['GeneHitsInSelectedSet'],
            'RichFactor': df['enrichFactor'],
            'PValue': df['p-value']
        })
    except KeyError as e:
        print(f"表格列名不匹配，请检查。报错列名: {e}")
        print(f"当前文件列名为: {df.columns.tolist()}")
        return

    # 3. 数据预处理
    # 计算 -log10(P-value)
    plot_df['neg_log10_p'] = -np.log10(plot_df['PValue'].replace(0, 1e-10))
    
    # 取前 N 个最显著的通路并反转排序（让最显著的在上方）
    plot_df = plot_df.sort_values('PValue').head(top_n).iloc[::-1]

    # 4. 绘图
    # 增加绘图比例，确保文字不拥挤
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.set_style("ticks")
    
    # 核心气泡图
    # s: 气泡大小倍数，可根据需要调整 (例如 Count * 15)
    scatter = ax.scatter(
        x=plot_df['RichFactor'],
        y=plot_df['Term'],
        s=plot_df['Count'] * 15, 
        c=plot_df['neg_log10_p'],
        cmap='Spectral_r', 
        alpha=0.8,
        edgecolors='black',
        linewidth=0.6,
        zorder=3
    )

    # 5. 美化细节
    ax.set_xlabel('Enrichment Factor', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('KEGG Pathway', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('KEGG Pathway Enrichment Analysis', fontsize=14, fontweight='bold', pad=15)
    
    # 添加辅助网格线线
    ax.grid(axis='both', linestyle='--', linewidth=0.5, alpha=0.7, zorder=0)
    
    # 颜色条 (显著性)
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.7)
    cbar.set_label('-log10(P-value)', fontsize=10, rotation=270, labelpad=15)

    # 气泡大小图例 (基因数量)
    # 自动生成 4 个代表性的点大小
    handles, labels = scatter.legend_elements(prop="sizes", alpha=0.5, num=4, 
                                            func=lambda s: s/15, color='gray')
    ax.legend(handles, labels, loc="upper right", title="Gene Count", 
              bbox_to_anchor=(1.35, 1), frameon=False, labelspacing=1.2)

    # 6. 保存为 PDF 矢量图
    # 如果输出文件名没写 .pdf，自动补全
    if not output_file.lower().endswith('.pdf'):
        output_file = output_file.rsplit('.', 1)[0] + '.pdf'
        
    plt.tight_layout()
    plt.savefig(output_file, format='pdf', bbox_inches='tight')
    print(f"✅ 绘图成功！矢量文件已保存至: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot KEGG Bubble PDF from TBtools result.')
    parser.add_argument('--input', type=str, required=True, help='输入 xls 文件')
    parser.add_argument('--output', type=str, default='KEGG_Enrichment_Plot.pdf', help='输出文件名')
    parser.add_argument('--top', type=int, default=20, help='展示通路条数')
    
    args = parser.parse_args()
    plot_kegg_bubble(args.input, args.output, args.top)