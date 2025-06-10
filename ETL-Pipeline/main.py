# main.py
import pandas as pd
from pathlib import Path
from extract import extract_resume_features
from transform import transform_data
from predict import predict

def main(data_dir: str = "dummy", output_csv: str = "resume_output.csv"):
    data_path = Path(data_dir)
    records = []

    for file in data_path.iterdir():
        if file.is_file():
            extracted = extract_resume_features(file)
            if extracted:  # hanya tambahkan jika tidak kosong
                records.append(extracted)

    
    # Convert extracted data to a DataFrame
    df_extract = pd.DataFrame(records)

    # Apply transformation and save structured data
    transformed = transform_data(df_extract, output_csv)
    df_clean = pd.DataFrame(transformed)
    # df_clean.to_csv(output_csv, index=False)
    prediction = predict(df_clean, output_csv)
    df = pd.DataFrame(prediction)
    df.to_csv(output_csv, index=False)
    print(f"\n✅ Saved to: {output_csv}")
    print(df.head())
    return df
    # return df_clean

if __name__ == "__main__":
    main()
