from src.ingest.weather_ingest import run_ingest
from src.database.insert_data import insert_raw_data
from src.transform.clean_transform import clean_transform
from src.transform.daily_batch import run_daily_batch
from src.analysis.city_ispa_joined import build_city_ispa

def run_pipeline():
    print("\n==============================")
    print("      AIR QUALITY PIPELINE    ")
    print("==============================\n")

    # 1. Ingest WeatherAPI (cuaca + polusi)
    print("[1] Ingesting data from WeatherAPI...")
    run_ingest()
    print("✓ Ingest completed.\n")

    # 2. Insert raw JSON → raw_air_quality
    print("[2] Inserting RAW JSON into PostgreSQL...")
    insert_raw_data()
    print("✓ Raw insert completed.\n")

    # 3. Clean transform → clean_air_quality
    print("[3] Transforming & cleaning data...")
    clean_transform()
    print("✓ Clean transform completed.\n")

    # 4. Agregasi harian per kota → daily_air_quality
    print("[4] Running daily aggregation per city...")
    run_daily_batch()
    print("✓ Daily aggregation completed.\n")

    # 5. Join polusi per kota dengan ISPA provinsi → city_ispa_joined
    print("[5] Building city-level ISPA join...")
    build_city_ispa()
    print("✓ city_ispa_joined completed.\n")

    print("===========================================")
    print("     PIPELINE FINISHED SUCCESSFULLY!")
    print("===========================================\n")

if __name__ == "__main__":
    run_pipeline()
