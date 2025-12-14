import pytest
import pandas as pd
import sqlite3
import os
from src.database import DatabaseAdapter

TEST_DB = ':memory:'
TEST_TABLE = 'dashboard_data'

@pytest.fixture
def setup_teardown_db():
    # fixture to set up and tear down the database

    # create database object
    db_adapter = DatabaseAdapter(dp_path = TEST_DB, table_name = TEST_TABLE)
    db_adapter.drop_table_if_exists()  # ensure clean state

    #yield gives the object to the test function
    yield db_adapter


    # teardown after test (cleanup)
    db_adapter.drop_table_if_exists()

def test_save_and_load_data_integrity(setup_teardown_db):
    """US4 - test data can be saved to the DB and loaded correctly"""

    # receive the db adapter from the fixture
    db_adapter = setup_teardown_db

    # create sample data 
    data_to_save = pd.DataFrame({
        'state' : ['Alaska', 'California'],
        'flu_deaths' : [5, 20],
        'Total_Hospital_Beds' : [1000, 5000],
        'ICU_Beds' : [50, 200],
        'Stress_Index' : [10.0, 15.0],
        'date':['2024-04-21', '2024-04-21']
    })

    # save and load data
    db_adapter.save_data(data_to_save)
    loaded_data = db_adapter.load_data()

    # check if data loaded
    assert not loaded_data.empty
    assert len(loaded_data) == 2

    # check data integrity
    assert loaded_data.iloc[0]['state'] == 'Alaska'
    assert loaded_data.iloc[1]['Stress_Index'] == 15.0

    # Check structural integrity
    assert 'index' not in loaded_data.columns.str.lower()