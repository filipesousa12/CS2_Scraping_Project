from airflow.decorators import dag, task 
from datetime import datetime
from utils.webscrapping import extract


@dag(
    start_date = datetime(2024,10,26),
    schedule = None,
    catchup = False,
    tags = ['webscraping']
)

def extract_all():
    
    @task
    def run_extraction():
        extract()  # Call the webscraping function here

    run_extraction()  # Trigger the task

extract_all()  # Instantiate the DAG