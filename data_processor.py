class DataProcessor:
    """Helper class for processing data related to budget codes and employees."""

    def __init__(self):
        pass

    @staticmethod
    def levenshtein_distance(str1: str, str2: str) -> int:
        """Calculate the Levenshtein distance between two strings."""
        import Levenshtein
        return Levenshtein.distance(str1, str2)

    @staticmethod
    def update_employee_code(df_metric):
        """Update employee code using a reference CSV."""
        import pandas as pd

        df_employee_code = pd.read_csv('report model/EmployeeCode.csv')
        df_metric = df_metric.rename(columns={'userName': 'Name', 'TimeInHours': 'CompletedWork'})
        df_metric['Employee ID'] = ""
        df_metric['Name TFS'] = ""

        for i, row in df_metric.iterrows():
            index = -1
            distance = 1000000
            for j, row2 in df_employee_code.iterrows():
                distance1 = DataProcessor.levenshtein_distance(row['Name'], row2['Name'])
                if distance1 < distance:
                    distance = distance1
                    index = j
            df_metric.at[i, 'Employee ID'] = df_employee_code.iloc[index]['Employee ID']
            df_metric.at[i, 'Name TFS'] = df_employee_code.iloc[index]['Name']

        df_metric = df_metric.drop(columns={'Name'})
        df_metric = df_metric.rename(columns={'Name TFS': 'Name'})
        return df_metric

    @staticmethod
    def update_epic_name(df, df_source):
        for index, row in df.iterrows():
            df_result = df_source[df_source['Budget Code'] == row['Budget Code']]
            if len(df_result) != 0:
                df.at[index, 'Epic Name'] = df_result.iloc[0]['Product']
            else:
                print(row['Budget Code'], row['Epic Name'])
        return df

    @staticmethod
    def update_budget_codes(df_codes, df_data, code_col='Budget Code'):
        """Update budget codes in df_data based on mapping in df_codes."""
        code_map = df_codes.set_index('Budget Code')['New Budget code'].to_dict()
        print("Budget code mapping:", code_map)
        df_data_updated = df_data.copy()
        df_data_updated[code_col] = df_data_updated[code_col].replace(code_map)
        return df_data_updated

    @staticmethod
    def update_team(df, df_source):
        for index, row in df.iterrows():
            df_result = df_source[df_source['Employee ID'] == row['Employee ID']]
            if len(df_result):
                df.at[index, 'Team'] = df_result.iloc[0]['Team']
        return df

    @staticmethod
    def update_portfolio(df, df_source):
        print(df.dtypes)
        print(df_source.dtypes)
        df['Portfolio'] = ""
        for index, row in df.iterrows():
            df_result_p = df_source[df_source['Budget Code'] == row['Budget Code']]
            if len(df_result_p):
                if row['Employee ID'] == '311032':
                    print(df_result_p.iloc[0]['Portfolio'])
                df.iloc[index, 6] = df_result_p.iloc[0]['Portfolio']
            else:
                print("No row", row['Budget Code'], row['Employee ID'])
        return df

    @staticmethod
    def process_data(df):
        df_tfs_empty = df[df['Budget Code'].isna()]
        df_tfs_empty['TotalHours'] = 0
        df_tfs_empty['Percentage'] = 0

        grouped = df.groupby(['Budget Code', 'Epic Name', 'Employee ID', 'Name'])['CompletedWork'].sum().reset_index()
        total_hours = grouped.groupby('Employee ID')['CompletedWork'].sum().reset_index()
        total_hours = total_hours.rename(columns={'CompletedWork': 'TotalHours'})
        merged = grouped.merge(total_hours, on='Employee ID')
        merged['Percentage'] = (merged['CompletedWork'] / merged['TotalHours']) * 100

        print(merged.count())
        merged.head()

        for i, row in df_tfs_empty.iterrows():
            employee_data = merged[merged['Employee ID'] == row['Employee ID']]
            max_completed_work_idx = employee_data.groupby('Employee ID')['CompletedWork'].idxmax()
            df_max_completed_work = employee_data.loc[max_completed_work_idx]
            if len(df_max_completed_work) > 0:
                df_tfs_empty.at[i, 'Budget Code'] = df_max_completed_work.iloc[0]['Budget Code']
                df_tfs_empty.at[i, 'Epic Name'] = df_max_completed_work.iloc[0]['Epic Name']

        final_result = pd.concat([df_tfs_empty, merged])
        final_result.reset_index(drop=True, inplace=True)
        return final_result


class FileHelper:
    """Utilities for file handling."""

    @staticmethod
    def create_folder(path: str) -> bool:
        import os
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
