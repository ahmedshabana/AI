# Utility module for data analysis
import os
import pandas as pd
import Levenshtein

class StringUtils:
    @staticmethod
    def levenshtein_distance(str1: str, str2: str) -> int:
        """Calculate the Levenshtein distance between two strings."""
        return Levenshtein.distance(str1, str2)

class DataProcessor:
    def __init__(self, product_codes: pd.DataFrame):
        self.product_codes = product_codes

    def update_epic_name(self, df: pd.DataFrame) -> pd.DataFrame:
        for index, row in df.iterrows():
            dfresult = self.product_codes[self.product_codes['Budget Code'] == row['Budget Code']]
            if len(dfresult) != 0:
                df.at[index, 'Epic Name'] = dfresult.iloc[0]['Product']
            else:
                print(row['Budget Code'], row['Epic Name'])
        return df

    @staticmethod
    def update_budget_codes(df_codes: pd.DataFrame, df_data: pd.DataFrame, code_col: str = 'Budget Code') -> pd.DataFrame:
        code_map = df_codes.set_index('Budget Code')['New Budget code'].to_dict()
        print("Budget code mapping:", code_map)
        df_data_updated = df_data.copy()
        df_data_updated[code_col] = df_data_updated[code_col].replace(code_map)
        return df_data_updated

    @staticmethod
    def update_team(df: pd.DataFrame, dfsource: pd.DataFrame) -> pd.DataFrame:
        for index, row in df.iterrows():
            dfresult = dfsource[dfsource['Employee ID'] == row['Employee ID']]
            if len(dfresult):
                df.at[index, 'Team'] = dfresult.iloc[0]['Team']
        return df

    def update_portfolio(self, df: pd.DataFrame) -> pd.DataFrame:
        df['Portfolio'] = ""
        for index, row in df.iterrows():
            dfresultP = self.product_codes[self.product_codes['Budget Code'] == row['Budget Code']]
            if len(dfresultP):
                if row['Employee ID'] == '311032':
                    print(dfresultP.iloc[0]['Portfolio'])
                df.iloc[index, 6] = dfresultP.iloc[0]['Portfolio']
            else:
                print("No row", row['Budget Code'], row['Employee ID'])
        return df

    @staticmethod
    def process_data(df: pd.DataFrame) -> pd.DataFrame:
        dfTFSEmpty = df[df['Budget Code'].isna()]
        dfTFSEmpty["TotalHours"] = 0
        dfTFSEmpty["Percentage"] = 0

        grouped = df.groupby(['Budget Code', 'Epic Name', 'Employee ID', 'Name'])['CompletedWork'].sum().reset_index()
        total_hours = grouped.groupby('Employee ID')['CompletedWork'].sum().reset_index()
        total_hours = total_hours.rename(columns={'CompletedWork': 'TotalHours'})
        merged = pd.merge(grouped, total_hours, on='Employee ID')
        merged['Percentage'] = (merged['CompletedWork'] / merged['TotalHours']) * 100

        print(merged.count())
        for i, row in dfTFSEmpty.iterrows():
            employeedata = merged[merged['Employee ID'] == row['Employee ID']]
            max_completed_work_idx = employeedata.groupby('Employee ID')['CompletedWork'].idxmax()
            df_max_completed_work = employeedata.loc[max_completed_work_idx]
            if len(df_max_completed_work) > 0:
                dfTFSEmpty.at[i, 'Budget Code'] = df_max_completed_work.iloc[0]['Budget Code']
                dfTFSEmpty.at[i, 'Epic Name'] = df_max_completed_work.iloc[0]['Epic Name']
        final_result = pd.concat([dfTFSEmpty, merged])
        final_result.reset_index(drop=True, inplace=True)
        return final_result

class FolderManager:
    @staticmethod
    def create_folder(path: str) -> bool:
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
