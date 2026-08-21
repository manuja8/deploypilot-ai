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

        history_item = PredictionHistory(
            **clean_data
        )

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