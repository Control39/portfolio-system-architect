# Disaster Recovery Runbook
# Instructions for recovery scenarios

## Table of Contents
1. [Database Recovery](#database-recovery)
2. [Cluster Recovery](#cluster-recovery)
3. [Data Corruption](#data-corruption)
4. [Complete Rebuild](#complete-rebuild)

---

## Database Recovery

### Scenario: PostgreSQL Data Loss or Corruption

**Time to Recovery: 5-10 minutes**

```bash
# 1. SSH to backup location (GCS)
gsutil ls gs://portfolio-backups/ | tail -1

# 2. Download latest backup
gsutil cp gs://portfolio-backups/portfolio_LATEST.sql.gz /tmp/

# 3. Restore to K8s cluster
kubectl exec -it postgres-0 -n portfolio -- bash

# Inside pod:
PGPASSWORD=$DB_PASSWORD pg_restore \
  -U postgres \
  -d portfolio \
  --clean \
  /tmp/portfolio_LATEST.sql.gz

# 4. Verify recovery
kubectl exec -it postgres-0 -n portfolio -- \
  psql -U postgres -d portfolio -c "SELECT COUNT(*) FROM information_schema.tables;"
```

---

## Cluster Recovery

### Scenario: GKE Cluster Failure

**Time to Recovery: 15-30 minutes**

```bash
# 1. Create new GKE cluster
gcloud container clusters create portfolio-recovery \
  --zone us-central1-a \
  --num-nodes 3

# 2. Get credentials
gcloud container clusters get-credentials portfolio-recovery

# 3. Deploy all services
kubectl apply -k deployment/k8s/overlays/prod

# 4. Restore database
kubectl cp /tmp/portfolio_LATEST.sql.gz \
  postgres-0:/tmp/ \
  -n portfolio

kubectl exec -it postgres-0 -n portfolio -- \
  psql -U postgres -d portfolio < /tmp/portfolio_LATEST.sql.gz

# 5. Verify services are running
kubectl get pods -n portfolio
kubectl get svc -n portfolio
```

---

## Data Corruption

### Scenario: Corrupted Data in Production

**Time to Recovery: 2-5 minutes (point-in-time restore)**

```bash
# 1. Identify corruption point
kubectl logs -n portfolio decision-engine-0 | tail -100

# 2. Find backup timestamp before corruption
gsutil ls -l gs://portfolio-backups/ | grep "portfolio_"

# 3. Restore from specific point in time
BACKUP_TIMESTAMP="20240319_100000"  # Before corruption
gsutil cp gs://portfolio-backups/portfolio_${BACKUP_TIMESTAMP}.sql.gz /tmp/

# 4. Restore in parallel environment first (test)
kubectl create namespace portfolio-test
kubectl cp /tmp/portfolio_${BACKUP_TIMESTAMP}.sql.gz \
  postgres-0-test:/tmp/ \
  -n portfolio-test

# 5. After verification, swap services
kubectl delete ns portfolio
kubectl mv-resources portfolio-test portfolio
```

---

## Complete Rebuild

### Scenario: Complete Infrastructure Failure

**Time to Recovery: 30-45 minutes**

**Prerequisites:**
- GCS bucket with backups: `gs://portfolio-backups/`
- Terraform configs: `packages/terraform/`
- K8s manifests: `deployment/k8s/`

```bash
# 1. Destroy old infrastructure
cd packages/terraform
terraform destroy -var-file="prod.tfvars"

# 2. Create new infrastructure
terraform apply -var-file="prod.tfvars"

# 3. Get credentials
gcloud container clusters get-credentials \
  portfolio-gke-prod \
  --zone us-central1-a

# 4. Deploy K8s resources
kubectl apply -k deployment/k8s/overlays/prod

# 5. Restore database from GCS
kubectl exec -it postgres-0 -n portfolio -- bash
gsutil cp gs://portfolio-backups/portfolio_LATEST.sql.gz /tmp/
PGPASSWORD=$DB_PASSWORD pg_restore \
  -U postgres \
  -d portfolio \
  --clean \
  /tmp/portfolio_LATEST.sql.gz

# 6. Verify services
kubectl get pods -n portfolio
kubectl get svc -n portfolio
curl http://localhost/it-compass

# 7. Re-establish DNS/LB
# Update DNS records to new Load Balancer IP
kubectl get svc ingress-nginx -n ingress-nginx
```

---

## Backup Verification (Monthly)

```bash
# 1. List recent backups
gsutil ls -l gs://portfolio-backups/ | tail -5

# 2. Test restore in isolated namespace
kubectl create namespace test-restore
gsutil cp gs://portfolio-backups/portfolio_LATEST.sql.gz /tmp/
kubectl cp /tmp/portfolio_LATEST.sql.gz postgres-test-0:/tmp/ -n test-restore
kubectl exec -it postgres-test-0 -n test-restore -- \
  pg_restore -U postgres -d portfolio /tmp/portfolio_LATEST.sql.gz

# 3. Run smoke tests
kubectl run curl-test --image=curlimages/curl -n test-restore \
  -- /bin/sh -c "curl http://it-compass:8501"

# 4. Clean up
kubectl delete ns test-restore
```

---

## Alerting

**Critical Alerts (page on-call):**
- ❌ Backup failed for >24 hours
- ❌ Database connection lost >5 minutes
- ❌ Cluster node unavailable >10 minutes

**Monitor Backup Status:**
```bash
# Check latest backup
gsutil stat gs://portfolio-backups/portfolio_LATEST.sql.gz

# Monitor GCS bucket size
gsutil du -s gs://portfolio-backups/
```

---

## Contact & Escalation

**Tier 1: Try automated recovery**
- Run backup restore script
- Check Prometheus alerts
- Review logs

**Tier 2: Manual intervention**
- SSH to K8s master
- Access GCS bucket
- Query database directly

**Tier 3: Escalation**
- GCP Support: https://cloud.google.com/support
- Team Lead: [contact info]

---

**Last Updated:** 2026-03-19
**Next DR Drill:** 2026-04-19
