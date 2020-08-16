#

import pandas as pd

def createColumnDescriptionHTML(cal_df, path_to_desc_csv, output_html_path):
    #load descriptions from csv
    col_desc_df = pd.read_csv(path_to_desc_csv)

    #load latest calendar table columns and datatypes
    cal_col_df = pd.DataFrame(
        columns=['col_name'],
        data=cal_df.dtypes.index.tolist()
        )
    cal_col_df['col_dtype'] = cal_df.dtypes.tolist()

    cal_col_df.columns = ['col_name','col_dtype']
    #cal_col_df.rename(columns={'

    #merge the descriptions into the latest column list
    cal_merged_df = cal_col_df.merge(col_desc_df, how='left', on='col_name')

    df_html = cal_merged_df.to_html()

    html_file = open(output_html_path, 'w')
    n = html_file.write(df_html)
    html_file.close()

    return cal_merged_df
