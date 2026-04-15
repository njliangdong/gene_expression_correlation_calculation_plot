import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import argparse

def choose_layout(G):
    """根据节点数量和密度选择布局算法"""
    n = G.number_of_nodes()
    e = G.number_of_edges()
    if n <= 8:
        return nx.circular_layout(G)
    density = e / (n*(n-1)/2) if n > 1 else 0
    if density < 0.2:
        return nx.kamada_kawai_layout(G)
    return nx.spring_layout(G, k=1.8, seed=42)

def main():
    parser = argparse.ArgumentParser(description="绘制自定义网络图")
    
    # --- 输入输出参数 ---
    parser.add_argument('-i', '--input', required=True, help='相关系数文件 (Tab 分隔)')
    parser.add_argument('-o', '--output', required=True, help='输出图片名 (比如 result.pdf)')
    parser.add_argument('-g', '--genes', required=True, help='关注基因列表，用逗号分隔')
    parser.add_argument('-c', '--cutoff', type=float, default=0.7, help='绝对相关系数阈值 (默认 0.7)')
    
    # --- 节点参数 ---
    parser.add_argument('--node_size', type=int, default=1200, help='节点大小 (默认 1200)')
    parser.add_argument('--font_size', type=int, default=14, help='节点标签字体大小 (默认 14)')
    
    # --- 连线外观参数 (粗细对比) ---
    parser.add_argument('--line_scale', type=float, default=20.0, help='连线基础粗细缩放系数 (默认 20)')
    parser.add_argument('--power', type=float, default=4.0, help='连线粗细的指数对比度 (默认 4)')

    # --- 连线标签文字参数 (用户自定义部分) ---
    parser.add_argument('--edge_font_size', type=int, default=10, 
                        help='连线数值的字体大小 (默认 10)')
    parser.add_argument('--edge_label_color', type=str, default='black', 
                        help='连线数值的颜色 (默认 black, 可选 red, blue, gray 等)')
    parser.add_argument('--edge_weight', type=str, default='bold', choices=['normal', 'bold'],
                        help='连线数值是否加粗 (可选 normal 或 bold, 默认 bold)')

    args = parser.parse_args()

    # 1. 读取数据
    df = pd.read_csv(args.input, sep='\t')
    focus_list = [g.strip() for g in args.genes.split(',')]

    # 2. 过滤数据
    df = df[(df['Correlation'].abs() >= args.cutoff) &
            ((df['Query_Gene'].isin(focus_list)) |
             (df['Target_Gene'].isin(focus_list)))]

    if df.empty:
        print("没有符合条件的相关对，请检查阈值或基因名！")
        return

    # 3. 构建图
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['Query_Gene'], row['Target_Gene'], weight=row['Correlation'])

    pos = choose_layout(G)

    # 4. 样式计算
    # 节点颜色
    node_color_map = ['gold' if node in focus_list else 'gray' for node in G.nodes()]

    # 连线粗细 (指数缩放)
    edge_weights = [abs(G[u][v]['weight']) for u,v in G.edges()]
    edge_widths = [1 + (w ** args.power) * args.line_scale for w in edge_weights]

    # 连线颜色 (正红负绿)
    edge_colors = ['red' if G[u][v]['weight'] > 0 else 'lightgreen' for u, v in G.edges()]

    # 5. 绘图
    plt.figure(figsize=(12,12))

    # 画节点
    nx.draw_networkx_nodes(G, pos, node_size=args.node_size, node_color=node_color_map, edgecolors='black')

    # 画连线
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, alpha=0.8)

    # 画节点标签 (基因名)
    nx.draw_networkx_labels(G, pos, font_family="Arial", font_size=args.font_size, font_weight='bold', font_color='black')

    # 画连线标签 (相关系数数值)
    edge_labels = {(u, v): f"{G[u][v]['weight']:.2f}" for u, v in G.edges()}
    
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_family="Arial",
        font_color=args.edge_label_color, # 参数控制颜色
        font_size=args.edge_font_size,    # 参数控制大小
        font_weight=args.edge_weight      # 参数控制粗细 (normal/bold)
    )

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(args.output)
    # plt.show() 

if __name__ == "__main__":
    main()