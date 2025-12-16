import sqlite3
import pandas as pd
from src.log_config import logger

class DatabaseAdapter:
    """use SQLite to handle DB operations"""


    def __init__ (self, 
                  db_path = 'health_dashboard.db', 
                  table_name = 'dashboard_data'):
        self.db_path = db_path
        self.table_name = table_name
        logger.info(f"DatabaseAdapter initialized with DB: {self.db_path}, Table: {self.table_name}")


    def _get_connection(self):
        if isinstance(self.db_path, sqlite3.Connection):
            return self.db_path
        
        return sqlite3.connect(self.db_path)
        

    def save_data (self, data: pd.DataFrame):
        """save DataFrame to SQLite DB"""

        conn = self._get_connection()
        try:
            data.to_sql(
                self.table_name, 
                conn, 
                if_exists='replace',
                index=False
                )
            
            if not isinstance(self.db_path, sqlite3.Connection):
                conn.commit()

            logger.info(f"Successfully saved {len(data)} records to table {self.table_name}")

        except Exception as e:
            logger.error(f"Error saving data to DB table {self.table_name}: {e}")
            print(f"Error saving data to DB: {e}")

        finally:
            if not isinstance(self.db_path, sqlite3.Connection):
                conn.close()


    def load_data(self) -> pd.DataFrame:
        """load data from SQLite DB into DataFrame"""

        conn = self._get_connection()


        try:
            query = f"SELECT * FROM {self.table_name}"
            logger.info(f"Executing query: {query}")

            df = pd.read_sql_query(query, conn)
            logger.info(f"Successfully loaded {len(df)} records from table {self.table_name}")
            return df
            
        except pd.io.sql.DatabaseError as e:
            logger.warning(f"Database table {self.table_name} not found")
            return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Error loading data from DB table {self.table_name}: {e}")
            print(f"Error loading data from DB: {e}")
            return pd.DataFrame()
        
        finally:
            if not isinstance(self.db_path, sqlite3.Connection):
                conn.close()
        

    def drop_table_if_exists(self):

        conn = self._get_conncetion()

        try:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
            conn.commit()
            logger.info(f"Dropped table {self.table_name} if it existed.")

        except Exception as e:
            logger.error(f"Error dropping table {self.table_name}: {e}")

        finally:
            if not isinstance(self.db_path, sqlite3Connection()):
                conn.close()