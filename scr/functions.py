import glob
import os
import pandas as pd


def filename(filepath):
    f_path = filepath
    full_name = os.path.basename(f_path)
    f_name = os.path.splitext(full_name)
    return(f_name[0])

def read_data_csv(csv_path):
    # current_directory = os.path.dirname(os.path.realpath(__file__))

    # # Go one folder up from the current directory
    # parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))

    # # Construct the absolute path to the CSV files directory
    # csv_directory = os.path.join(parent_directory, csv_path)

    # # Use glob to find all CSV files in the directory
    # csv_files = glob.glob(os.path.join(csv_directory, '*.csv'))

    # Define the path to the folder containing the CSV files
    # folder_path = csv_path

    # # Use glob to find all CSV files in the folder
    # csv_files = glob.glob(folder_path + "/*.csv")

# # initialize with an empty data fram
#     df=pd.DataFrame()

#     for file in csv_files:
#         dfs = pd.read_csv(file, sep=",", encoding='latin-1')
#         dfs['PARAM']= filename(file)
#         df = pd.concat([df,dfs],ignore_index=True, sort=False)
    # Initialize an empty list to store DataFrames
    dfs_list = []
     # Loop over files in the specified directory
    for file in os.listdir(csv_path):
        if file.endswith(".csv"):  # Check if the file is a CSV file
            file_path = os.path.join(csv_path, file)
            # Read the CSV file into a DataFrame and add a 'PARAM' column
            df = pd.read_csv(file_path, sep=",", encoding='latin-1')
            df['PARAM'] = os.path.splitext(file)[0]  # Get filename without extension
            dfs_list.append(df)

    # Concatenate all DataFrames in the list
    df = pd.concat(dfs_list, ignore_index=True, sort=False)
    # Reindex dataframe, order of columns
    df = df.reindex(columns=["PARAM","REGION","REGION2","TECHNOLOGY", "FUEL", "TIMESLICE", "EMISSION", "DAILYTIMEBRACKET","SEASON", "DAYTYPE","STORAGE","MODE_OF_OPERATION", "UDC", "YEAR","VALUE"])
    return df        

# reduce decimal places for the SpecifiedDemandProfile    
def SpeDemProf(dataframe, decimal_places):
    sdp_pivot = pd.pivot_table(dataframe, values='VALUE', index=['PARAM', 'REGION', 'YEAR', 'FUEL'],
                            columns=['TIMESLICE']).reset_index(level= ['REGION','YEAR', 'FUEL', 'PARAM'])
    sdp_pivot = sdp_pivot.round(decimals=decimal_places)
    #data frame shape
    rows = sdp_pivot.shape[1]
    dif = 1 - sdp_pivot.iloc[:,4:rows-1].sum(axis=1)
    #dif
    # penultimun columns
    sdp_pivot.iloc[:,rows-1] = dif
    #melt and reindex
    sdp = sdp_pivot.melt(id_vars=['PARAM', 'REGION', 'FUEL', 'YEAR'])
    sdp = sdp.reindex(columns=['PARAM', 'REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'value'])
    sdp.rename(columns = {'value': 'VALUE'}, inplace=True)
    return(sdp)



    
    
    