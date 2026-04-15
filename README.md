# gene_expression_correlation_calculation_plot

python gene_corr_analysis.py \
  -i 1.txt \
  -o gene_correlation.txt \
  -m pearson
  
python draw_gene_net.py \
  -i gene_correlation.txt \
  -o focus_network.pdf \
  -g Uv8b_02153,Uv8b_03621 \
  -c 0.8 \
  --edge_label_color gray \
  --power 6 \
  --line_scale 25 \
  --edge_font_size 18
  
python fix_eggnog_helper.py UV_eggnog_output.emapper.annotations fixed_annotations.txt
python draw_kegg_bar_plot.py --input TBtools.KEGG.enrichment.result.xls.final.xls --output my_kegg_plot.png --top 20  
