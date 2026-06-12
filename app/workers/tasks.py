import os
import json
import logging
import pandas as pd
from datetime import datetime
from app.workers.celery_app import celery
from app.db.session import SessionLocal
from app.db.models.job import Job
from app.db.models.transaction import Transaction
from app.db.models.job_summary import JobSummary
from app.services.transaction_processor.cleaner import DataCleaner
from app.services.anomaly_detector.engine import AnomalyDetector
from app.services.llm import get_llm_provider
from app.services.summary.generator import SummaryGenerator
from app.core.config import settings

logger = logging.getLogger(__name__)

@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=3)
def process_transactions_job(self, job_id_str: str, filepath: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id_str).first()
        if not job:
            logger.error(f"Job {job_id_str} not found in DB.")
            return

        job.status = "PROCESSING"
        db.commit()

        # Data Cleaning
        logger.info(f"Starting data cleaning for job {job_id_str}")
        cleaner = DataCleaner(filepath)
        df = cleaner.clean()
        
        job.row_count_raw = len(pd.read_csv(filepath))
        job.row_count_clean = len(df)
        
        if df.empty:
            job.status = "COMPLETED"
            job.completed_at = datetime.utcnow()
            db.commit()
            return

        # Anomaly Detection
        logger.info(f"Running anomaly detection for job {job_id_str}")
        detector = AnomalyDetector()
        df = detector.detect(df)
        
        # LLM Categorization
        logger.info(f"Running LLM categorization for job {job_id_str}")
        llm = get_llm_provider()
        
        # Filter for Uncategorised
        mask_uncat = df['category'] == 'Uncategorised'
        uncat_df = df[mask_uncat]
        
        if not uncat_df.empty:
            # Prepare batches
            batch_size = settings.LLM_BATCH_SIZE
            records = uncat_df.to_dict('records')
            categories = []
            
            # Format for LLM: reduce payload size by picking only necessary fields
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                llm_batch = [{"merchant": r.get("merchant"), "amount": r.get("amount"), "date": str(r.get("date"))} for r in batch]
                
                try:
                    cats = llm.categorize_transactions(llm_batch)
                    categories.extend(cats)
                except Exception as e:
                    logger.error(f"LLM batch failed: {str(e)}")
                    categories.extend(["Other"] * len(batch))
                    df.loc[mask_uncat, 'llm_failed'] = True
                    
            df.loc[mask_uncat, 'category'] = categories

        # Save Transactions to DB
        logger.info(f"Saving transactions to DB for job {job_id_str}")
        transactions_to_insert = []
        for _, row in df.iterrows():
            # handle NaN/NaT
            date_val = None if pd.isna(row.get('date')) else row.get('date')
            amount_val = None if pd.isna(row.get('amount')) else row.get('amount')
            
            txn = Transaction(
                job_id=job.id,
                txn_id=row.get('txn_id') if 'txn_id' in row and not pd.isna(row['txn_id']) else None,
                date=date_val,
                merchant=row.get('merchant') if 'merchant' in row and not pd.isna(row['merchant']) else None,
                amount=amount_val,
                currency=row.get('currency') if 'currency' in row and not pd.isna(row['currency']) else None,
                status=row.get('status') if 'status' in row and not pd.isna(row['status']) else None,
                category=row.get('category') if 'category' in row and not pd.isna(row['category']) else None,
                account_id=row.get('account_id') if 'account_id' in row and not pd.isna(row['account_id']) else None,
                notes=row.get('notes') if 'notes' in row and not pd.isna(row['notes']) else None,
                is_anomaly=row.get('is_anomaly', False),
                anomaly_reason=row.get('anomaly_reason') if 'anomaly_reason' in row and not pd.isna(row['anomaly_reason']) else None,
                llm_failed=row.get('llm_failed', False)
            )
            transactions_to_insert.append(txn)
            
        db.bulk_save_objects(transactions_to_insert)
        
        # Summary Generation
        logger.info(f"Generating summary for job {job_id_str}")
        anomaly_count = int(df['is_anomaly'].sum())
        summary_gen = SummaryGenerator()
        summary_data = summary_gen.generate(df, len(df), anomaly_count)
        
        summary = JobSummary(
            job_id=job.id,
            total_spend_inr=summary_data['total_spend_inr'],
            total_spend_usd=summary_data['total_spend_usd'],
            top_merchants=summary_data['top_merchants'],
            spend_by_category=summary_data['spend_by_category'],
            anomaly_count=summary_data['anomaly_count'],
            risk_level=summary_data['risk_level'],
            narrative=summary_data['narrative']
        )
        db.add(summary)
        
        # Mark Completed
        job.status = "COMPLETED"
        job.completed_at = datetime.utcnow()
        db.commit()
        logger.info(f"Job {job_id_str} completed successfully.")
        
        # Cleanup file
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            logger.warning(f"Could not remove file {filepath}: {str(e)}")
            
    except Exception as e:
        db.rollback()
        logger.exception(f"Job {job_id_str} failed: {str(e)}")
        # We need to load job again to update status
        try:
            job = db.query(Job).filter(Job.id == job_id_str).first()
            if job:
                job.status = "FAILED"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception as inner_e:
            logger.error(f"Failed to update job status to FAILED: {str(inner_e)}")
            
        raise self.retry(exc=e)
    finally:
        db.close()
