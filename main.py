import os
import pandas as pd
from src.repository import CDCRepository
from src.database import DatabaseAdapter
from src.service import FluDashBoardService
from src.log_config import logger

API_DATA_SOURCE = "https://data.cdc.gov/resource/r8kw-7aab.json"
DATABASE_PATH = 'health_dashboard.db'
DATABASE_TABLE = 'dashboard_data'

def run_etl_process():
    logger.info ("--- Application startup: Running ETL process ---")

    try: #initialise dependencies
        repository = CDCRepository(api_url = API_DATA_SOURCE)
        db_adapter = DatabaseAdapter(db_path = DATABASE_PATH, table_name = DATABASE_TABLE)
        dashboard_service = FluDashBoardService(
            repository = repository, 
            db_adapter = db_adapter
        )

        #execute business logic
        df_result = dashboard_service.get_dashboard_data()

        # output result
        if not df_result.empty:
            print("\n ---ETL Process Completed Successfully---")
            print (f"Successfully processed {len (df_result)} records.")
            print ("\nTop 5 States by Stress Index:")
            print(df_result[['state', 'Stress_Index']].head())
            logger.info("ETL process completed successfully.")

        else:
            print("\n --- ETL Failure ---")
            print("Failed to generate dashboard data. Check logs for details. ")
            logger.error("ETL process failed to return data.")

    except Exception as e:
        logger.critical(f"Critical error during ETL process: {e}")
        print(f"\n Critical Error: {e}")

if __name__ == "__main__":
    if os.path.exists(logger.handlers[0].baseFilename):
        with open(logger.handlers[0].baseFilename, 'w'):
            pass

    run_etl_process()
