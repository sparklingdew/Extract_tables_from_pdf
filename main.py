
import utils

file='Price table.pdf' # https://www.docdroid.net/58eQDoN/price-table-pdf
col_estimation=10

# Extract tables from pdf and turn then it into a DataFrame
# Text outside tables is also present in the DataFrame. It generally appears in the first column 
def extract_table_from_pdf(file,col_estimation):
    '''
       Input
        file: pdf file with tables                  
        col_estimation: approximate number of columns in the pdf table.
                        It is better to overestimate this number. Default=10
       Output
        df: DataFrame with pdf text arranged into a unique table
    '''     
    elems=utils.pdf_elements(file)
    df=utils.text_and_boxes(elems)
    df=utils.row_number(df)
    df=utils.col_number(df,col_estimation)
    df=utils.pdf_to_df(df,col_estimation)
    return df


df_from_pdf=extract_table_from_pdf(file,col_estimation)

