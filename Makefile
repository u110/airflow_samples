airflow-version:=1.10.3

docker/%:
	AIRFLOW_VERSION=$(airflow-version) \
	docker-compose -f docker-compose-CeleryExecutor.yml \
		$(@F)

up: docker/up\ -d

stop: docker/stop

remove: docker/rm

airflow/%:
	AIRFLOW_VERSION=$(airflow-version) \
	docker-compose -f docker-compose-CeleryExecutor.yml \
		exec webserver \
		airflow $(@F)