import pandas as pd
from extract import extract_resume_features

def parse_files(files: list) -> list:
    """Extract structured data and format for proper transformation."""
    records = []
    for file in files:
        result = extract_resume_features(file)
        if result:  # Only append non-empty results
            formatted_result = {
                "ID": result["ID"],
                "Name": result['Name'],
                "ability": result["Ability"].replace(" | ", ", "),
                "skill": result["Skill"].replace(" | ", ", "),
                "program": result["Education"].replace(" | ", ", ")
            }
            records.append(formatted_result)
    return records

def to_dataframe(records: list) -> pd.DataFrame:
    """Convert structured data into a clean Pandas DataFrame."""
    return pd.DataFrame(records)

def save_transformed_data(df: pd.DataFrame, output_csv: str) -> None:
    """Save structured resume data to CSV."""
    df.to_csv(output_csv, index=False)
    print(f"\n✅ Transformed data saved to: {output_csv}")

def transform_data(df: pd.DataFrame, output_csv: str = "structured_data.csv"):
    """Transform extracted resume data and save structured output."""
    records = []
    
    for _, row in df.iterrows():
        formatted_result = {
            "ID": row["ID"],
            "Name": row['Name'],
            "ability": row["Ability"].replace(" | ", ", "),
            "skill": row["Skill"].replace(" | ", ", "),
            "program": row["Education"].replace(" | ", ", ")
        }
        records.append(formatted_result)

    transformed_df = pd.DataFrame(records)
    transformed_df.to_csv(output_csv, index=False)
    print(f"\n✅ Transformed data saved to: {output_csv}")

    return transformed_df

