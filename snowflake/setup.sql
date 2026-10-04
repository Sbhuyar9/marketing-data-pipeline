-- One-time Snowflake setup: warehouse, schemas, S3 stage, Snowpipe -> BRONZE
create warehouse if not exists TRANSFORM_WH warehouse_size = 'XSMALL' auto_suspend = 60 auto_resume = true;
create database if not exists MARKETING;
create schema if not exists MARKETING.BRONZE;
create schema if not exists MARKETING.SILVER;
create schema if not exists MARKETING.GOLD;

create role if not exists TRANSFORMER;
grant usage on warehouse TRANSFORM_WH to role TRANSFORMER;
grant all on database MARKETING to role TRANSFORMER;

-- Storage integration (run as ACCOUNTADMIN; then configure the IAM trust policy)
create storage integration if not exists S3_MARKETING_INT
  type = external_stage storage_provider = 'S3' enabled = true
  storage_aws_role_arn = 'arn:aws:iam::<ACCOUNT_ID>:role/snowflake-marketing-read'
  storage_allowed_locations = ('s3://<BUCKET>/marketing/raw/');

create or replace stage MARKETING.BRONZE.RAW_STAGE
  url = 's3://<BUCKET>/marketing/raw/' storage_integration = S3_MARKETING_INT;

create or replace file format MARKETING.BRONZE.JSON_FF type = 'JSON';
create or replace file format MARKETING.BRONZE.CSV_FF  type = 'CSV' skip_header = 1 field_optionally_enclosed_by = '"';

-- Bronze tables: VARIANT keeps raw JSON schemas untouched
create table if not exists MARKETING.BRONZE.GA_EVENTS (
  PAYLOAD_JSON variant, _LOADED_AT timestamp_ntz default current_timestamp(), _SOURCE_FILE string);
create table if not exists MARKETING.BRONZE.CRM_CUSTOMERS (
  CUSTOMER_ID string, EMAIL string, FIRST_NAME string, LAST_NAME string, REGION string,
  SIGNUP_DATE string, UPDATED_AT string, _LOADED_AT timestamp_ntz default current_timestamp(), _SOURCE_FILE string);
create table if not exists MARKETING.BRONZE.CAMPAIGN_SPEND (
  SPEND_DATE string, CAMPAIGN_ID string, SPEND_USD string,
  _LOADED_AT timestamp_ntz default current_timestamp(), _SOURCE_FILE string);

-- Snowpipes (auto_ingest -> wire S3 event notifications to the pipe's SQS ARN)
create or replace pipe MARKETING.BRONZE.PIPE_GA_EVENTS auto_ingest = true as
  copy into MARKETING.BRONZE.GA_EVENTS (PAYLOAD_JSON, _SOURCE_FILE)
  from (select $1, metadata$filename from @MARKETING.BRONZE.RAW_STAGE/ga_events/)
  file_format = (format_name = 'MARKETING.BRONZE.JSON_FF');

create or replace pipe MARKETING.BRONZE.PIPE_CRM auto_ingest = true as
  copy into MARKETING.BRONZE.CRM_CUSTOMERS (CUSTOMER_ID,EMAIL,FIRST_NAME,LAST_NAME,REGION,SIGNUP_DATE,UPDATED_AT,_SOURCE_FILE)
  from (select $1,$2,$3,$4,$5,$6,$7, metadata$filename from @MARKETING.BRONZE.RAW_STAGE/crm_customers/)
  file_format = (format_name = 'MARKETING.BRONZE.CSV_FF');

create or replace pipe MARKETING.BRONZE.PIPE_SPEND auto_ingest = true as
  copy into MARKETING.BRONZE.CAMPAIGN_SPEND (SPEND_DATE,CAMPAIGN_ID,SPEND_USD,_SOURCE_FILE)
  from (select $1,$2,$3, metadata$filename from @MARKETING.BRONZE.RAW_STAGE/campaign_spend/)
  file_format = (format_name = 'MARKETING.BRONZE.CSV_FF');
