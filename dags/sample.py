from datetime import timedelta

import airflow
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.subdag_operator import SubDagOperator


args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2),
    'provide_context': True,
}


DAG_NAME = __file__.split("/")[-1].replace(".py", "")


def do_something(**kwargs):
    response = kwargs.get("response")
    print("**kwargs")
    print(kwargs)
    return response


dag = DAG(
    dag_id=DAG_NAME,
    default_args=args,
    schedule_interval='@daily',
    dagrun_timeout=timedelta(minutes=60),
)

start = PythonOperator(
    task_id="start",
    python_callable=do_something,
    op_kwargs={"response": "start: {{ds}}"},
    dag=dag,
)

print_date_task = PythonOperator(
    task_id="print_date",
    python_callable=do_something,
    op_kwargs={"response": "ds: {{ds}}"},
    dag=dag,
)

start >> print_date_task


def get_sub_task(parent_dag, child_dag, args):
    with DAG(
        dag_id="%s.%s" % (parent_dag, child_dag),
        default_args=args,
    ) as dag:
        sleep_seconds = [1, 3, 5]
        for sleep_sec in sleep_seconds:
            task = BashOperator(
                task_id="sleep_%s" % sleep_sec,
                bash_command="sleep {num} && echo sleep_{num}".format(
                    num=sleep_sec
                ),
                xcom_push=True
            )
            task
        return dag


sub_task = SubDagOperator(
    task_id="sub_task",
    subdag=get_sub_task(DAG_NAME, "sub_task", args),
    dag=dag
)

start >> sub_task


def pull_xcom(**kwargs):
    ti = kwargs.get("ti")
    dag_id = kwargs.get("dag_id")
    task_id = kwargs.get("task_id")
    key = kwargs.get("key")

    res = ti.xcom_pull(dag_id=dag_id, task_ids=task_id, key=key)
    print(res)
    return res


puller = PythonOperator(
    task_id="puller",
    python_callable=pull_xcom,
    op_kwargs={
        "dag_id": "sample.sub_task",
        "task_id": "sleep_1"
    },
    dag=dag
)

start >> puller
