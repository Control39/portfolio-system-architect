#!/bin/bash
# PostgreSQL Backup Script
# Creates daily backups to GCS bucket

set -e

# Configuration
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-portfolio}
GCS_BUCKET=${GCS_BUCKET:-portfolio-backups}
BACKUP_DIR="/backups"
RETENTION_DAYS=${RETENTION_DAYS:-30}

# Create backup directory
mkdir -p $BACKUP_DIR

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/portfolio_${TIMESTAMP}.sql.gz"
LOG_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.log"

echo "Starting PostgreSQL backup at $(date)" | tee -a $LOG_FILE

# Create backup
if PGPASSWORD=$DB_PASSWORD pg_dump \
  -h $DB_HOST \
  -p $DB_PORT \
  -U $DB_USER \
  -d $DB_NAME \
  --verbose \
  --format=plain \
  | gzip > $BACKUP_FILE 2>> $LOG_FILE; then

  FILE_SIZE=$(du -h $BACKUP_FILE | cut -f1)
  echo "✅ Backup completed successfully: $FILE_SIZE" | tee -a $LOG_FILE

  # Upload to GCS
  if gsutil cp $BACKUP_FILE gs://$GCS_BUCKET/; then
    echo "✅ Uploaded to gs://$GCS_BUCKET/" | tee -a $LOG_FILE
  else
    echo "❌ Upload to GCS failed" | tee -a $LOG_FILE
    exit 1
  fi

  # Clean up old backups (local)
  find $BACKUP_DIR -name "portfolio_*.sql.gz" -mtime +$RETENTION_DAYS -delete
  echo "✅ Cleaned up backups older than $RETENTION_DAYS days" | tee -a $LOG_FILE

else
  echo "❌ Backup failed" | tee -a $LOG_FILE
  exit 1
fi

echo "Backup process completed at $(date)" | tee -a $LOG_FILE
