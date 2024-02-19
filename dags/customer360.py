from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.utils.dates import timedelta
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.operators.empty import EmptyOperator
from airflow import settings
from airflow.models import Connection
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

def get_url():
    session = settings.Session()
    operator = session.query(Connection).filter(Connection.conn_id == "orders_s3").first()
    return f"{operator.schema}://{operator.host}/orders.csv"

def downloadCommand():
    
    return f"rm -rf airflow_project && mkdir airflow_project && cd airflow_project && wget --user-agent=Mozilla {get_url()}" 

def sqoopImportCustomerData():
    
    commandOne = "hive -e 'DROP TABLE customers'"
    commandTwo = "hdfs dfs -rm -r -f /user/ubuntu/customers"
    commandThree = "sqoop import \
        --connect jdbc:mysql://localhost:3306/retail_db \
        --username hiveuser \
        --password hivepassword \
        --table customers \
        --hive-import \
        --create-hive-table \
        --hive-table customers"
    
    return f'{commandOne} && {commandTwo} && {commandThree}' 

dag = DAG(
    dag_id = "customer_360_pipeline",
    start_date=days_ago(1)
)


http_sensor = HttpSensor(
    
    task_id="detect_s3_orders",
    http_conn_id="orders_s3",
    endpoint = "orders.csv" ,
    response_check=lambda response:response.status_code == 200,
    dag = dag,
    poke_interval = 10,
    timeout = 300
    
)

download_file = SSHOperator(
    dag=dag,
    ssh_conn_id="ec2_airflow",
    command = downloadCommand(),
    task_id="download_orders"
)


importTable = SSHOperator( dag=dag,
    ssh_conn_id="ec2_airflow",
    command = sqoopImportCustomerData(),
    task_id="importCustomerData",
    cmd_timeout=200
)
hdfsInputDir = "airflow_input"

hdfsOutputDir = "airflow_output"

copyFileTOHdfs = SSHOperator(
    
    ssh_conn_id="ec2_airflow",
    command = f"hdfs dfs -rm -R -f {hdfsInputDir} && hdfs dfs -mkdir {hdfsInputDir} && hdfs dfs -put ./airflow_project/orders.csv {hdfsInputDir}/",
    task_id="copyFiletoHdfs",
    dag=dag
)

sparkProcessing = SSHOperator(
    
    ssh_conn_id = "ec2_airflow",
    command = f"cd /home/ubuntu && hdfs dfs -rm -R -f {hdfsOutputDir} && spark-submit --class closedorders airflowcode.jar {hdfsInputDir} {hdfsOutputDir}",
    task_id = "sparkProcessFile",
    dag = dag
    
    
    
)

def createclosedOrdersTable():
    command = 'hive -e "CREATE EXTERNAL TABLE IF NOT EXISTS \
    closedorders(order_id int,order_date string,customer_id int,order_status string) \
    ROW FORMAT DELIMITED FIELDS TERMINATED BY \',\' \
    STORED AS TEXTFILE LOCATION \'/user/ubuntu/airflow_output\' \
    TBLPROPERTIES(\'skip.header.line.count\'=\'1\')"'
    return command


def createHiveHbaseTable():
    createCommand = 'hive -e "CREATE TABLE IF NOT EXISTS orders_joined_with_customers(order_id int,customer_fname string,customer_lname string,customer_id int,order_date string) \
        STORED BY \'org.apache.hadoop.hive.hbase.HBaseStorageHandler\' \
        WITH SERDEPROPERTIES(\'hbase.columns.mapping\'=\':key,personal:customer_fname,personal:customer_lname,personal:customer_id,personal:order_date\')"'
    
    insertcommand = 'hive -e "INSERT OVERWRITE TABLE orders_joined_with_customers  SELECT co.order_id,c.customer_fname,c.customer_lname,c.customer_id,co.order_date FROM customers c JOIN closedorders co ON (c.customer_id = co.customer_id)"'
    
    return f"{createCommand} && {insertcommand}"


createOrdersTable = SSHOperator(
    
    ssh_conn_id = "ec2_airflow",
    command = createclosedOrdersTable(),
    dag = dag,
    task_id = "closedordertablecreation",
    cmd_timeout = 200
    
)


loadHbaseTable = SSHOperator(
    ssh_conn_id = "ec2_airflow",
    command = createHiveHbaseTable(),
    dag = dag,
    task_id = "loadhbasetable",
    cmd_timeout = 200,
)


dataLoadSuccessNotifier = SlackWebhookOperator(
    dag = dag,
    task_id = "slack_notification_success_task",
    slack_webhook_conn_id = "slack_webhook",
    message = "Pipeline execution succeded and data successfully loaded into Hbase",
    trigger_rule = "all_success"
)

dataLoadFailureNotifier = SlackWebhookOperator(
    dag = dag,
    task_id = "slack_notification_failure_task",
    slack_webhook_conn_id = "slack_webhook",
    message = "Pipeline execution failed and data load into Hbase failed",
    trigger_rule = "one_failed"
)







http_sensor >> download_file >> copyFileTOHdfs  >> sparkProcessing >> createOrdersTable >> loadHbaseTable 
importTable >> loadHbaseTable >> [dataLoadSuccessNotifier,dataLoadFailureNotifier]