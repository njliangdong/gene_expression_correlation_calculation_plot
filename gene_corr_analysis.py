import pandas as pd
import argparse
from scipy.stats import pearsonr, spearmanr, kendalltau

def compute_corr(v1, v2, method):
    if method == 'pearson':
        return pearsonr(v1, v2)[0]
    elif method == 'spearman':
        return spearmanr(v1, v2)[0]
    elif method == 'kendall':
        return kendalltau(v1, v2)[0]
    else:
        raise ValueError(f"Unknown method: {method}")

def main():
    parser = argparse.ArgumentParser(description="计算基因表达相关系数 (支持 pearson/spearman/kendall)")
    parser.add_argument('-i', '--input', required=True,
                        help="输入表达矩阵 (Tab 分隔, 第一列是基因ID)")
    parser.add_argument('-o', '--output', required=True,
                        help="输出三列格式相关性表 (Tab 分隔)")
    parser.add_argument('-m', '--method', choices=['pearson','spearman','kendall'],
                        default='pearson', help="相关性计算方法")

    args = parser.parse_args()

    # 读取表达矩阵
    expr_df = pd.read_csv(args.input, sep='\t', index_col=0)

    # 把数据强制转成 float
    try:
        expr_df = expr_df.astype(float)
    except Exception as e:
        # 如果有无法转换的列，会自动尝试转换
        expr_df = expr_df.apply(pd.to_numeric, errors='coerce')

    # 去掉完全是 NaN 或无法转成数值的基因
    expr_df = expr_df.dropna(how='all')

    genes = expr_df.index.tolist()
    n = len(genes)

    with open(args.output, 'w') as fout:
        fout.write("Query_Gene\tTarget_Gene\tCorrelation\n")
        for i in range(n):
            for j in range(i+1, n):
                g1 = genes[i]
                g2 = genes[j]

                v1 = expr_df.loc[g1].values
                v2 = expr_df.loc[g2].values

                corr = compute_corr(v1, v2, args.method)
                fout.write(f"{g1}\t{g2}\t{corr:.4f}\n")

    print(f"完成 {args.method} 相关系数计算, 输出到 {args.output}")

if __name__ == "__main__":
    main()