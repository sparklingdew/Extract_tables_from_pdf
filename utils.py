import pandas as pd
import numpy as np
from pdfminer.high_level import extract_pages

#Read pdf and extract a list of its elements and corresponding page
def pdf_elements(file):
    '''
       Input
        file: pdf file
       Output
        elems: list of tuples (pdf element, page)          
    '''    
    elems=[]
    for page_layout in extract_pages(file):
        for element in page_layout:
            elems.append((element,page_layout.pageid))
    return elems

# Extract text and bounding box from each pdf element and create a DataFrame with the info
# If the element has something other than text, an empty string is assigned
def text_and_boxes(elems):
    '''
       Input
        elems: list of tuples (pdf element, page)  
       Output
        df: DataFrame with pdf element, text, page and bounding box coordinates          
    '''    
    b=[]
    for e, p in elems:    
        try:    
            row=[e,
                 e.get_text().strip(),
                 e.x0,
                 e.x1,
                 e.y0,
                 e.y1,
                 p]
            b.append(row)
        except:
            row=[e,
                 '',
                e.x0,
                e.x1,
                e.y0,
                e.y1,
                p]
            b.append(row)
    df = pd.DataFrame(b, columns = ['element','text', 'x0','x1','y0','y1','page'])        
    return df

# Define row number for each bounding box according to its position in the pdf page
def row_number(df):
    '''
       Input
        df: DataFrame with pdf element, text, page and bounding box coordinates                  
       Output
        df: input DataFrame with an extra column indicating the row for each pdf element
    '''        
    df=df.sort_values(by=['x0'],ascending=True)
    df=df.sort_values(by=['y0'],ascending=False,kind='stable')
    df=df.sort_values(by=['page'],ascending=True,kind='stable',ignore_index=True)
    df['row']=list(range(df.shape[0]))
    for i in range(df.shape[0]):
        for j in range(i+1,df.shape[0]):     
            overlap=df['element'][i].voverlap(df['element'][j])
            #is there vertical overlap between boxes and they are in the same page?
            if overlap>0 and df['page'].iloc[i]==df['page'].iloc[j]:
                df['row'].iloc[j]=df['row'].iloc[i]
    return df

# Define column number for each box according to its position in the pdf page
# To define the number of columns, all x0 values of the bounding boxes are divided into bins
def lambda_col_number(x,col_estimation,edges):
    for i,e in enumerate(edges):
        if e>=x:
            return i
            break

def col_number(df,col_estimation):
    '''
       Input
        df: DataFrame with pdf element, text, page and bounding box coordinates                  
        col_estimation: approximate number of columns in the pdf table.
                        It is better to overestimate this number. 
       Output
        df: input DataFrame with an extra column indicating the column for each pdf element
    '''    
    #list of x0 values
    x0_values=df['x0'].values
    #x0 range for each column
    hist, edges = np.histogram(x0_values, bins=col_estimation)
    df['col']=df['x0'].apply(lambda x: lambda_col_number(x,col_estimation,edges))
    return df

# Pdf table to DataFrame
def pdf_to_df(df,col_estimation=10):
    '''
       Input
        df: DataFrame with pdf element, text, row, column and pages                  
        col_estimation: approximate number of columns in the pdf table.
                        It is better to overestimate this number. Default=10
       Output
        df: DataFrame with pdf text arranged into a unique table
    '''    
    rows_count=df['row'].max()+1
    cols_count=col_estimation+1
    df_pdf_table=pd.DataFrame(index=range(rows_count),columns=range(cols_count))
    for i in range(df.shape[0]): 
        if df['text'][i]!='':
            r=df['row'][i]
            c=df['col'][i]
            df_pdf_table.iloc[r, c]=df['text'][i]
    # drop empty rows and columns
    df_pdf_table_h=df_pdf_table.dropna(axis=0,how='all')
    df_pdf_table_v=df_pdf_table_h.dropna(axis=1,how='all')
    return df_pdf_table_v
