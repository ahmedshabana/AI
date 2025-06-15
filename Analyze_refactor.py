# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import warnings
# Disable only DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Disable all warnings
warnings.filterwarnings("ignore")
import Levenshtein
import pandas as pd
def levenshtein_distance(str1, str2):
    """
    Calculate the Levenshtein distance between two strings.

    Parameters:
    str1 (str): The first string.
    str2 (str): The second string.

    Returns:
    int: The Levenshtein distance between the two strings.
    """
    return Levenshtein.distance(str1, str2)
def updateEmployeeCode(dfMetric):
    dfEmployeeCode=pd.read_csv('report model\\EmployeeCode.csv')
    dfMetric=dfMetric.rename(columns={'userName':'Name','TimeInHours':'CompletedWork'})
    dfMetric.head()
    dfMetric['Employee ID']=""
    dfMetric['Name TFS']=""
    for i,row in dfMetric.iterrows():
        index=-1
        distance=1000000
        for j ,row2 in dfEmployeeCode.iterrows():
            
            distance1=levenshtein_distance(row['Name'], row2['Name'])
            if distance1<distance:
                    distance=distance1
                    index=j
        #print (row['Name'],dfTFS.iloc[index]['Name'])
        dfMetric.at[i,'Employee ID']=dfEmployeeCode.iloc[index]['Employee ID']
        dfMetric.at[i,'Name TFS']=dfEmployeeCode.iloc[index]['Name']   
    dfMetric=dfMetric.drop(columns={'Name'})
    dfMetric=dfMetric.rename(columns={'Name TFS':'Name'})
    return dfMetric


def UpdateEpicName(df,dfsource):
    for index, row in df.iterrows():
        dfresult=dfsource[dfsource['Budget Code']==row['Budget Code']]
        if len(dfresult)!=0:
            df.at[index,'Epic Name']=dfresult.iloc[0]['Product']
        else:
            print (row['Budget Code'] ,row['Epic Name'])
    return df
def update_budget_codes(df_codes, df_data, code_col='Budget Code'):
    """
    Updates budget codes in df_data based on a mapping provided in df_codes.

    Parameters:
        df_codes (pd.DataFrame): DataFrame containing 'old_budget_code' and 'new_budget_code' columns.
        df_data (pd.DataFrame): DataFrame where budget codes should be updated.
        code_col (str): Column name in df_data that contains budget codes.

    Returns:
        pd.DataFrame: A new DataFrame with updated budget codes.
    """

    # Create a dictionary mapping old codes to new codes
    code_map = df_codes.set_index('Budget Code')['New Budget code'].to_dict()

    # Debug print (optional): Check the mapping
    print("Budget code mapping:", code_map)

    # Replace the budget codes in df_data using the map
    df_data_updated = df_data.copy()
    df_data_updated[code_col] = df_data_updated[code_col].replace(code_map)

    return df_data_updated

def UpdateTeam(df,dfsource):
    for index, row in df.iterrows():
        dfresult=dfsource[dfsource['Employee ID']==row['Employee ID']]
        if len(dfresult):
            df.at[index,'Team']=dfresult.iloc[0]['Team']
    return df

def UpdatePortfolio(df,dfsource):
    
    print (print(df.dtypes))
    print (print(dfsource.dtypes))
    
    df['Portfolio']=""
    for index, row in df.iterrows():
        dfresultP=dfsource[dfsource['Budget Code']==row['Budget Code']]
        if len(dfresultP):
            if row['Employee ID']=='311032':
                print (dfresultP.iloc[0]['Portfolio'])
            df.iloc[index,6]=dfresultP.iloc[0]['Portfolio']
        else:
            print ("No row",row['Budget Code'],row['Employee ID'])
    return df

#Select emtpy Budget code
def ProcessData(df):
    dfTFSEmpty=df[df['Budget Code'].isna()]
    dfTFSEmpty["TotalHours"]=0
    dfTFSEmpty["Percentage"]=0

    #Calculate the percentage 

    # Group by EmployeeID and Project, then sum the hours
    grouped = df.groupby(['Budget Code','Epic Name','Employee ID','Name'])['CompletedWork'].sum().reset_index()

    # Calculate the total hours worked by each employee
    total_hours = grouped.groupby('Employee ID')['CompletedWork'].sum().reset_index()
    total_hours = total_hours.rename(columns={'CompletedWork': 'TotalHours'})

    # Merge the total hours with the grouped data
    merged = pd.merge(grouped, total_hours, on='Employee ID')

    # Calculate the percentage of time invested in each project
    merged['Percentage'] = (merged['CompletedWork'] / merged['TotalHours']) * 100

    print (merged.count())
    merged.head()

    for i, row in  dfTFSEmpty.iterrows():
        employeedata= merged[merged['Employee ID']==row['Employee ID']]
        max_completed_work_idx = employeedata.groupby('Employee ID')['CompletedWork'].idxmax()
        df_max_completed_work = employeedata.loc[max_completed_work_idx]
        if len(df_max_completed_work)>0:
            #print (df_max_completed_work.iloc[0]['Budget Code'])
            dfTFSEmpty.at[i,'Budget Code']=df_max_completed_work.iloc[0]['Budget Code']
            dfTFSEmpty.at[i,'Epic Name']=df_max_completed_work.iloc[0]['Epic Name']
        #else:
            #print (row['Employee ID'])

    final_result = pd.concat([dfTFSEmpty, merged])
    final_result.reset_index(drop=True, inplace=True)
    return final_result
def main(month="May"):
    Month = month
    # load support data
    dfOldResult=pd.read_csv('backup\\oldresult.csv')
    dfPorductCode=pd.read_csv('D:\\Medad Projects\\PI planning\\Budget Code\\Portfolio Budget Code_V3.csv')
    dfBackup=pd.read_csv('backup\\tsfresult.csv')
    dfNewCode=pd.read_excel('D:\\Medad Projects\\PI planning\\Budget Code\\NewBudgetCode.xlsx')
    
    
    import os
    
    def create_folder(path):
        """
        Creates a folder at the specified path.
    
        Parameters:
            path (str): The path where the folder will be created.
    
        Returns:
            bool: True if the folder was created successfully, False if it already exists.
        """
        try:
            os.makedirs(path, exist_ok=False)
            print(f"Folder created successfully: {path}")
            return True
        except FileExistsError:
            print(f"Folder already exists: {path}")
            return False
        except OSError as e:
            print(f"Error creating folder '{path}': {e}")
            raise
    
    
    # %%
    create_folder("Result\\"+Month)
    
    dfTFS=pd.read_excel("Data\\"+Month+"\\Medad TFS.xlsx")
    print (dfTFS.count())
    dfTFS=ProcessData(dfTFS)
    print (dfTFS.head())
    
    # update the budget code from old data 
    
    for index, row in dfTFS.iterrows():
        if pd.isna(row['Budget Code'] ):
           
            result=dfBackup[dfBackup['Employee ID']==row['Employee ID']]
            if len(result):
                print ( result.iloc[0]['Budget Code']  )
                dfTFS.at[index, 'Budget Code']   =  result.iloc[0]['Budget Code']  
                dfTFS.at[index, 'Epic Name']   =  result.iloc[0]['Epic Name']  
                print (index)
            else:
                print (row['Employee ID'])
    dfTFS.to_csv("Result\\"+Month+"\\tsfresult.csv")
    
    # %%
    
    # timeDoctor
    dftimeDoctor=pd.read_excel("Data\\"+Month+"\\timeDoctor.xlsx")
    dftimeDoctor=dftimeDoctor.rename(columns={'userName':'Name','TimeInHour':'CompletedWork'})
    # update un budget code 
    print (dftimeDoctor.head())
    
    dftimeDoctor=ProcessData(dftimeDoctor)
    for index, row in dftimeDoctor.iterrows():
        if pd.isna(row['Budget Code'] ):
            result=dfBackup[dfBackup['Employee ID']==row['Employee ID']]
            if len(result):
                #print ( result.iloc[0]['Budget Code']  )
                dftimeDoctor.at[index, 'Budget Code']   =  result.iloc[0]['Budget Code']  
                dftimeDoctor.at[index, 'Epic Name']   =  result.iloc[0]['Epic Name']  
                #print (index)
            else:
                print ("Not found",row['Employee ID'] )
    dftimeDoctor.to_csv("Result\\"+Month+"\\timeDoctorresult.csv")
    
    # %%
    
    #filter the data
    dfTFS=dfTFS[['Employee ID','Name','CompletedWork','Budget Code','Epic Name','TotalHours','Percentage']]
    dftimeDoctor=dftimeDoctor[['Employee ID','Name','CompletedWork','Budget Code','Epic Name','TotalHours','Percentage']]
    
    # %%
    # update budget code 
    dfTFS=UpdateEpicName(dfTFS,dfPorductCode)
    dftimeDoctor=UpdateEpicName(dftimeDoctor,dfPorductCode)
    dfOldResult=UpdateEpicName(dfOldResult,dfPorductCode)
    dfTFS.to_csv("Result\\"+Month+"\\tsfresult.csv")
    dftimeDoctor.to_csv("Result\\"+Month+"\\timeDoctorresult.csv")
    
    # %%
    
    dfEmployeeCode=pd.read_csv("report model\\EmployeeCode.csv")
    dfCapacity=pd.read_excel("Data\\"+Month+"\\Capacity.xlsx")
    
    dfCapacity['Budget Code']=""
    dfCapacity['Epic Name']=""
    dfCapacity['CompletedWork']=0
    dfCapacity['TotalHours']=0
    dfCapacity['Percentage']=0
    #dfCapacity=dfCapacity.drop(columns={'Role'})
    dfCapacity=dfCapacity.rename(columns={'EmployeeID':'Employee ID'})
    print (dfCapacity.head())
    for i ,row in dfCapacity.iterrows():
       
        try :
            reminingPart= round ((1-row['TLI%'])*row[2],2)
            dfresult=dftimeDoctor[dftimeDoctor['Employee ID']==row['Employee ID']]
            if len(dfresult)==0:
                 dfresult=dfTFS[dfTFS['Employee ID']==row['Employee ID']]
                 if len(dfresult)==0:
                    dfresult=dfOldResult[dfOldResult['Employee ID']==row['Employee ID']]
    
            print ("Employee ID:",row['Employee ID'],len(dfresult))
    
            dfresult['CompletedWork'] = pd.to_numeric(dfresult['CompletedWork'], errors='coerce')
            max_completed_work_idx = dfresult.groupby('Employee ID')['CompletedWork'].idxmax()
            df_max_completed_work = dfresult.loc[max_completed_work_idx]
            if len(df_max_completed_work)>0:
                #print (df_max_completed_work.iloc[0]['Budget Code'])
    
    
                dfCapacity.at[i,'Budget Code']=df_max_completed_work.iloc[0]['Budget Code']
                dfCapacity.at[i,'Epic Name']=df_max_completed_work.iloc[0]['Epic Name']
         
                
                dfCapacity.at[i,'Percentage']=round ((1-row['TLI%']),2)
                dfCapacity.at[i,'TLI%']=round ((row['TLI%']),2)
                #dfCapacity.at[i,'Productivity over Availability']=round (row['Productivity over Availability'],2)
    
    
                dfCapacity.at[i,'CompletedWork']=reminingPart
                dfCapacity.at[i,'TotalHours']=reminingPart
                dfCapacity.at[i,'Percentage']=round ((1-row['TLI%']),2)
                
            else:
               print (reminingPart,row['Name'])
               dfCapacity.at[i,'CompletedWork']=reminingPart
               dfCapacity.at[i,'TotalHours']=reminingPart
               dfCapacity.at[i,'Percentage']=round ((1-row['TLI%']),2)
        except Exception:
             print (Exception)
    
    for i ,row in dfCapacity.iterrows():            
    
                if row['TLI%']>=1:
                         
                         reminingPart= round ((1-row['TLI%'])*row[2],2)
                         print (reminingPart)
                         if row['Name']=="Diaa Shalabi":
                             print ("prod:",row['TLI%'])
                             print ("remining time",reminingPart)
                         filtered_result=dfTFS[dfTFS['Employee ID']==row['Employee ID']]
                         if not filtered_result.empty:
                            print (row['Employee ID'])
                            index_of_max = filtered_result['CompletedWork'].idxmax()
                            print (index_of_max)
                            print ("Completed hours:",dfTFS.loc[index_of_max, 'CompletedWork'])
                            # Update the completedWork value at this index
                            timecount =dfTFS.iloc[index_of_max]['CompletedWork'] +reminingPart
                            print (timecount)
                            if timecount <0:
                                 dfTFS.loc[index_of_max, 'CompletedWork'] = 0
                                 reminingPart=timecount
                                 while timecount<0:
                                    reminingPart=timecount
                                    print ("within loop",reminingPart)
                                    filtered_result=dfTFS[dfTFS['Employee ID']==row['Employee ID']]
                                    index_of_max = filtered_result['CompletedWork'].idxmax()
                                    print ("Index:",index_of_max)
                                    if dfTFS.iloc[index_of_max]['CompletedWork'] ==0:
                                         print ("End")
                                         break
                                    timecount =dfTFS.iloc[index_of_max]['CompletedWork'] +reminingPart
                                    print (reminingPart)
                                    if timecount<0:
                                        dfTFS.loc[index_of_max, 'CompletedWork'] = 0
                                    else:
                                        dfTFS.loc[index_of_max, 'CompletedWork'] = dfTFS.loc[index_of_max, 'CompletedWork'] +reminingPart
    
    
                            else:
                                dfTFS.loc[index_of_max, 'CompletedWork'] = dfTFS.loc[index_of_max, 'CompletedWork'] +reminingPart
                
                
    dfCapacity=UpdateTeam(dfCapacity,dfEmployeeCode)
    dfCapacityfinal=dfCapacity[dfCapacity['CompletedWork']>0]
    
    dfCapacityfinal=dfCapacityfinal[['Employee ID','Name','Budget Code','Epic Name','CompletedWork','TotalHours','Percentage']]
    
    dfCapacity.to_csv('Result\\'+Month+'\\CapacityResults.csv')
    dfCapacityfinal["ReportType"]="Remaining Capacity" 
    dfTFS["ReportType"] ="TFS"
    
    dftimeDoctor["ReportType"] ="TimeDoctor"
    dfTFS['CompletedWork']=dfTFS['CompletedWork'].round(2)
    dffinalResult= pd.concat([dftimeDoctor, dfTFS,dfCapacityfinal])
    dffinalResult=dffinalResult[dffinalResult['CompletedWork']>0]
    dffinalResult.reset_index(drop=True, inplace=True)
    dfCapacityfinal=dfCapacityfinal.drop(columns={'ReportType'})
    dfTFS=dfTFS.drop(columns={'ReportType'})
    dffinalResult.to_csv("finalResult.csv")
    dffinalResult=dffinalResult.drop(columns={'TotalHours','Percentage'})
    
    dffinalResult['Budget Code'] = dffinalResult['Budget Code'].replace('', '0').fillna('0')
    # Convert column type from object (string) to integer
    dffinalResult['Budget Code'] = dffinalResult['Budget Code'].astype(int)
    
    dffinalResult=UpdatePortfolio(dffinalResult,dfPorductCode)
    dffinalResult=update_budget_codes(dfNewCode,dffinalResult)
    dffinalResult.to_csv('Result\\'+Month+'\\Total Completed.csv')
    name='Result\\'+Month+'\\'+Month+'-Report.xlsx'
    dfCapacity=dfCapacity.rename(columns={'TotalHours':'Variance','Percentage':'Variance %'})
    dfCapacity=dfCapacity.drop(columns={'CompletedWork'})
    dfCapacityfinal=update_budget_codes(dfNewCode,dfCapacityfinal)
    dfTFS=update_budget_codes(dfNewCode,dfTFS)
    with pd.ExcelWriter(name, engine='openpyxl') as writer:
        dffinalResult.to_excel(writer, sheet_name='Total Completed-'+Month, index=False)
        dfCapacity.to_excel(writer, sheet_name=Month+' Capacity', index=False)
        dfCapacityfinal.to_excel(writer, sheet_name='filtered '+Month+' Capacity', index=False)
        dfTFS.to_excel(writer, sheet_name='TFS time', index=False)
        dftimeDoctor.to_excel(writer, sheet_name='Time Doctor time', index=False)
    

if __name__ == "__main__":
    main()
