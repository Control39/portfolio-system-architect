#!/bin/bash
# PostgreSQL Restore Script
# Restores database from backup

set -e

# Configuration
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-portfolio}
GCS_BUCKET=${GCS_BUCKET:-portfolio-backups}
BACKUP_DIR="/backups"

if [ $# -eq 0 ]; then
  echo "Usage: restore-postgres.sh <backup_file_or_timestamp>"
  echo ""
  echo "Examples:"
  echo "  # Restore from local file"
  echo "  ./restore-postgres.sh /backups/portfolio_20240319_120000.sql.gz"
  echo ""
  echo "  # Restore from GCS (download and restore)"
  echo "  ./restore-postgres.sh gs://$GCS_BUCKET/portfolio_20240319_120000.sql.gz"
  echo ""
  echo "  # List available backups in GCS"
  echo "  gsutil ls gs://$GCS_BUCKET/"
  exit 1
fi

BACKUP_FILE=$1

# Download from GCS if needed
if [[ $BACKUP_FILE == gs://* ]]; then
  LOCAL_FILE="$BACKUP_DIR/$(basename $BACKUP_FILE)"
  echo "Downloading from GCS..."
  gsutil cp $BACKUP_FILE $LOCAL_FILE
  BACKUP_FILE=$LOCAL_FILE
fi

if [ ! -f $BACKUP_FILE ]; then
  echo "❌ Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "Starting restore from $BACKUP_FILE at $(date)"

# Drop existing database (CAUTION!)
read -p "⚠️  This will DROP the existing database. Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Restore cancelled"
  exit 0
fi

echo "Dropping existing database..."
PGPASSWORD=$DB_PASSWORD psql \
  -h $DB_HOST \
  -p $DB_PORT \
  -U $DB_USER \
  -c "DROP DATABASE IF EXISTS $DB_NAME;"

echo "Creating new database..."
PGPASSWORD=$DB_PASSWORD psql \
  -h $DB_HOST \
  -p $DB_PORT \
  -U $DB_USER \
  -c "CREATE DATABASE $DB_NAME;"

echo "Restoring from backup..."
if gunzip -c $BACKUP_FILE | PGPASSWORD=$DB_PASSWORD psql \
  -h $DB_HOST \
  -p $DB_PORT \
  -U $DB_USER \
  -d $DB_NAME; then
  echo "✅ Restore completed successfully at $(date)"
else
  echo "❌ Restore failed"
  exit 1
fi
