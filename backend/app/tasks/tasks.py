import os
import time
import logging
from datetime import datetime, timezone, timedelta
from app.extensions import celery_app, db
from app.services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.escalate_stuck_assignments")
def escalate_stuck_assignments(age_hours=24):
    """Celery background task checking for assignments remaining unaccepted."""
    logger.info("Starting background task: escalate_stuck_assignments")
    try:
        workflow_svc = WorkflowService()
        count = workflow_svc.check_and_escalate_assignments(age_hours)
        logger.info(f"Background task finished. Escalated {count} assignments.")
        return {"escalated_count": count}
    except Exception as e:
        logger.error(f"Error executing escalate_stuck_assignments: {str(e)}", exc_info=True)
        raise e


@celery_app.task(name="tasks.cleanup_temp_files")
def cleanup_temp_files(max_age_hours=24):
    """Deletes temporary files left in the uploads or temp folders."""
    logger.info("Starting background task: cleanup_temp_files")
    from app.models.file_attachment import FileAttachment
    try:
        threshold = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        # Find files marked is_deleted
        deleted_files = db.session.query(FileAttachment).filter(
            FileAttachment.is_deleted == True,
            FileAttachment.created_at <= threshold
        ).all()
        
        removed_count = 0
        for f in deleted_files:
            if os.path.exists(f.storage_path):
                os.remove(f.storage_path)
            db.session.delete(f)
            removed_count += 1
            
        db.session.commit()
        logger.info(f"Background task finished. Cleaned up {removed_count} files.")
        return {"cleaned_count": removed_count}
    except Exception as e:
        logger.error(f"Error executing cleanup_temp_files: {str(e)}", exc_info=True)
        db.session.rollback()
        raise e


@celery_app.task(name="tasks.retrain_predictive_models")
def retrain_predictive_models():
    """Celery background task that retrains Scikit-Learn RandomForest models daily."""
    logger.info("Starting background task: retrain_predictive_models")
    try:
        from app.services.prediction_service import PredictionService
        pred_svc = PredictionService()
        result = pred_svc.train_models()
        logger.info(f"Background task finished. Model training result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error executing retrain_predictive_models: {str(e)}", exc_info=True)
        raise e

