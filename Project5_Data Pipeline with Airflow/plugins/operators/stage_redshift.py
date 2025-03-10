from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    template_fields = ("s3_key",) 

    CopySqlStageToRedshift = """
        COPY {}
        FROM '{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        {}
        ;
    """
    
    @apply_defaults
    def __init__(self,
                redshift_conn_id="",
                aws_credentials_id="",
                table="",
                s3_bucket="",
                s3_key="",
                extra_params="",
                *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.extra_params = extra_params

    def execute(self, context):

        if not (self.file_format == 'csv' or self.file_format == 'json'):
            raise ValueError(f"file format {self.file_format} is not csv or json")
        if self.file_format == 'json':

            file_format = "format json '{}'".format(self.json_path)
        else:
            file_format = "format CSV"

        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        

        self.log.info("Remove data from Redshift table")
        redshift.run("DELETE FROM {}".format(self.table)) 

        self.log.info("Copying data from S3 to Redshift")
        rendered_key = self.s3_key.format(**context)
        s3_path = "s3://{}/{}".format(self.s3_bucket, rendered_key)
        formatted_sql = StageToRedshiftOperator.CopySqlStageToRedshift.format(
            self.table,
            s3_path,
            credentials.access_key,
            credentials.secret_key,
            self.extra_params
        )

        self.log.info(f"Execute {insert_sql} ...")
        redshift.run(insert_sql)

        self.log.info('StageToRedshiftOperator not implemented yet')





