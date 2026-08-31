from api.models import PredictionHistory


class HistoryRepository:

    def __init__(self, database):
        self.database = database

    def save(self, prediction_data):
        allowed_fields = {
            column.name
            for column in PredictionHistory.__table__.columns
            if column.name != "id"
        }

        clean_data = {
            key: value
            for key, value in prediction_data.items()
            if key in allowed_fields
        }

        history_item = PredictionHistory(**clean_data)

        self.database.add(history_item)
        self.database.commit()
        self.database.refresh(history_item)

        return history_item

    def get_all(self):
        return (
            self.database
            .query(PredictionHistory)
            .order_by(PredictionHistory.id.desc())
            .all()
        )

    def get_meaningful_repository_history(
        self,
        repository,
        limit=10,
        exclude_run_id=None,
    ):

        if not repository:
            return []

        query = (
            self.database
            .query(PredictionHistory)
            .filter(PredictionHistory.repository == repository)
            .filter(PredictionHistory.source == "GITHUB_ACTIONS")
            .filter(PredictionHistory.actual_result.in_(["PASS", "FAIL"]))
        )

        if exclude_run_id:
            query = query.filter(PredictionHistory.run_id != exclude_run_id)

        return (
            query
            .order_by(PredictionHistory.id.desc())
            .limit(limit)
            .all()
        )

    def get_repository_history_summary(
        self,
        repository,
        minimum_runs=3,
        limit=10,
        exclude_run_id=None,
    ):

        runs = self.get_meaningful_repository_history(
            repository=repository,
            limit=limit,
            exclude_run_id=exclude_run_id,
        )

        run_count = len(runs)
        cold_start = run_count < minimum_runs

        if cold_start:
            failure_rate = 0.0
        else:
            failures = sum(
                1
                for run in runs
                if str(run.actual_result).upper() == "FAIL"
            )
            failure_rate = round(failures / run_count, 3)

        return {
            "meaningful_history_runs": run_count,
            "minimum_history_runs": minimum_runs,
            "cold_start": cold_start,
            "previous_failure_rate": failure_rate,
        }
