from airflow import DAG
from airflow.contrib.operators.gcp_sql_operator import CloudSqlInstanceExportOperator
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.utils.dates import days_ago

args = {
    'owner': 'packt-developer',
}

GCP_PROJECT_ID = 'packt-data-eng-on-gcp'


with DAG(
    dag_id='level_2_dag_load_bigquery',
    default_args=args,
    schedule_interval='0 5 * * *',
    start_date=days_ago(1),
) as dag:

    

    gcs_to_bq_example = GoogleCloudStorageToBigQueryOperator(
    task_id                             = "gcs_to_bq_example",
    bucket                              = 'files_dag_creation',
    source_objects                      = ['stations.csv'],
    destination_project_dataset_table   ='raw_bikesharing.stations',
    schema_fields=[
        {'name': 'station_id', 'type': 'STRING', 'mode': 'NULLABLE'},
        {'name': 'name', 'type': 'STRING', 'mode': 'NULLABLE'},
        {'name': 'region_id', 'type': 'STRING', 'mode': 'NULLABLE'},
        {'name': 'capacity', 'type': 'INTEGER', 'mode': 'NULLABLE'}
    ],
    write_disposition='WRITE_TRUNCATE'
    )

    bq_to_bq  = BigQueryOperator(
        task_id                     = "bq_to_bq",
        sql                         = "SELECT count(*) as count FROM `raw_bikesharing.stations`",
        destination_dataset_table   = 'dwh_bikesharing.temporary_stations_count',
        write_disposition           = 'WRITE_TRUNCATE',
        create_disposition          = 'CREATE_IF_NEEDED',
        use_legacy_sql              = False,
        priority                    = 'BATCH'
    )

    sql_export_task >> gcs_to_bq_example >> bq_to_bq

if __name__ == "__main__":
    dag.cli()
