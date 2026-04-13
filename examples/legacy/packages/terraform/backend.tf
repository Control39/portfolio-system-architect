# Terraform Backend Configuration for Remote State Management

# This file configures remote state storage in GCS (Google Cloud Storage)
# Benefits:
# - Shared state across team members
# - State versioning and backup
# - Locking to prevent concurrent modifications

# To use:
# 1. Create GCS bucket: gsutil mb gs://portfolio-terraform-state
# 2. Enable versioning: gsutil versioning set on gs://portfolio-terraform-state
# 3. Configure backend in terraform block of main.tf

# Example GCS bucket configuration:
# gsutil lifecycle set - << 'EOF'
# {
#   "lifecycle": [
#     {
#       "action": {"type": "Delete"},
#       "condition": {"age": 90, "numNewerVersions": 10}
#     }
#   ]
# }
# EOF
