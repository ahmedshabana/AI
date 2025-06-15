"""Main script for generating reports using DataProcessor classes."""
import pandas as pd
from analysis_module import StringUtils, DataProcessor, FolderManager


def run(month: str) -> None:
    """Run the analysis pipeline for a given month."""
    FolderManager.create_folder(f"Result/{month}")

    df_tfs = pd.read_excel(f"Data/{month}/Medad TFS.xlsx")
    df_product_codes = pd.read_csv("backup/oldresult.csv")
    processor = DataProcessor(df_product_codes)

    df_processed = processor.process_data(df_tfs)
    df_processed = processor.update_epic_name(df_processed)
    df_processed.to_csv(f"Result/{month}/tsfresult.csv", index=False)


if __name__ == "__main__":
    run("May")
