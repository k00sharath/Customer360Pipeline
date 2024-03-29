# Customer360Pipeline

### Description
A data pipeline that is built for filtering closed order data and pushing the data to Hive and Hbase on a scheduled basis with a notification for success and failure of a pipeline
<br><br>
![image](https://github.com/k00sharath/Customer360Pipeline/blob/main/pipeline.png)
 
### Technology Stack:
<img align="left" alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white">
<img align="left" alt="Docker" src="https://img.shields.io/badge/Docker-2496ED.svg?style=for-the-badge&logo=Docker&logoColor=white">
<img align="left" alt="HBase" src="https://img.shields.io/badge/HBase-D22128.svg?style=for-the-badge&logo=apache&logoColor=#D22128">
<img align="left" alt="Airflow" src="https://img.shields.io/badge/Apache%20Airflow-017CEE.svg?style=for-the-badge&logo=apacheairflow&logocolor=green">

<br><br>

<img align="left" alt="Hadoop" src="https://img.shields.io/badge/Apache%20Hadoop-66CCFF.svg?style=for-the-badge&logo=Apache-Hadoop&logoColor=black">
<img align="left" alt="Hive" src="https://img.shields.io/badge/Apache%20Hive-FDEE21.svg?style=for-the-badge&logo=Apache-Hive&logoColor=black">
<img align="left" alt="Slack" src="https://img.shields.io/badge/Slack-4A154B.svg?style=for-the-badge&logo=Slack&logoColor=white">


<img align="left" alt="AWSEC2" src="https://img.shields.io/badge/Amazon%20EC2-FF9900.svg?style=for-the-badge&logo=Amazon-EC2&logoColor=white">


<br>

### Steps involved in the Pipeline
   1. Fetching the orders data from S3 bucket
   2. Creating a customers info table in mysql by loading the data from customers info file [link]
   3. Loading the customers information from mysql database to hive using sqoop
   4. Filtering the orders data for closed orders by processing the data with spark
   5. Creating table for the closed orders in hive
   6. Joining the closed orders table along with customers table in hive (The data is stored in hbase it is possible because of the hive-hbase integration)
   7. Send success or failure notification to slack channel


### Installation
   1. Installing hadoop,hive,mysql db and hbase in an EC2 instance and creating a connection id in airflow for executing the pipeline in EC2 instance
      
         i.    <a href="https://www.guru99.com/how-to-install-hadoop.html" >Refer to this article for hadoop installation on ubuntu </a>
         <br><br>
         ii.   <a href="https://www.guru99.com/installation-configuration-hive-mysql.html">Refer to this article for hive installation on ubuntu </a>
         <br><br>
         iii.  <a href="https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04">Refer to this article for mysql installation on ubuntu </a>
         <br><br>
         iv.   <a href="https://www.guru99.com/hbase-installation-guide.html">Refer to this article for hbase installation on ubuntu</a>
      
   2. Installing docker for running airflow container

         i.   <a href="https://docs.docker.com/engine/install/">Refer to this documentation for installing docker</a>
         <br><br>
         ii. For running airflow container use the docker-compose.yaml
         ```bash
             
              # Clone the repo and open a terminal and cd into repo folder and run the following command

              docker-compose up
         ```
   
   4. Create a SSH connection id for connecting to EC2 instance <a href="https://docs.aws.amazon.com/mwaa/latest/userguide/samples-ssh.html">refer to this article  </a>
      (Note: go to [airflow-ui](https://localhost:8080) for accessing the Airflow UI)
   5. Create a Slack webhook integration and configure slack webhook connection in airflow (To create a connection goto admin section in Airflow UI and click on connections)
       
         i.   <a href="https://api.slack.com/messaging/webhooks">Refer to this article for creating slack webhook</a><br><br>
         ii.  <a href="https://airflow.apache.org/docs/apache-airflow-providers-slack/stable/connections/slack-incoming-webhook.html">Refer to this article for configuring slack webhook in airflow</a>
  
  
      
              
