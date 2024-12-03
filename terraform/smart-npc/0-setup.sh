#!/usr/bin/env sh

# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

GCP_PROJECT_ID="$(terraform output -raw google-project-id)"
GCS_BUCKET="$(terraform output -raw image_upload_gcs_bucket)"
DB_INSTANCE=pgvector-db
GCP_REGION="$(terraform output -raw google-default-region)"

SVC_EMAIL=$(gcloud sql instances describe "${DB_INSTANCE}" --project="${GCP_PROJECT_ID}" --format="value(serviceAccountEmailAddress)")

echo "[Info]GCP_PROJECT_ID=${GCP_PROJECT_ID}"
echo "[Info]SVC_EMAIL=${SVC_EMAIL}"
echo "[Info]GCS_BUCKET=${GCS_BUCKET}"
echo "[Info]DB_INSTANCE=${DB_INSTANCE}"

gcloud storage buckets add-iam-policy-binding "gs://${GCS_BUCKET}" --member="serviceAccount:${SVC_EMAIL}" --role="roles/storage.legacyObjectReader"
gcloud storage buckets add-iam-policy-binding "gs://${GCS_BUCKET}" --member="serviceAccount:${SVC_EMAIL}" --role="roles/storage.objectViewer"

gsutil iam ch serviceAccount:"${SVC_EMAIL}":objectAdmin gs://"${GCS_BUCKET}"

DATABASE_USER_NAME="$(terraform output -raw database_user_name)"

if [ -f "../data-ingestion/config-secrets.toml" ]; then
  echo "[Info]../data-ingestion/config-secrets.toml exists."
  echo "[Info]Back up ../data-ingestion/config-secrets.toml exists."
  mv ../data-ingestion/config-secrets.toml ../data-ingestion/config-secrets.toml.bak
fi

cat <<EOF >>../data-ingestion/database-secret.toml
[global]
DATABASE_CONNECTION_NAME="${GCP_PROJECT_ID}:${GCP_REGION}:${DB_INSTANCE}"
DATABASE_NAME="postgres"
DATABASE_USER_NAME="${DATABASE_USER_NAME}"
DATABASE_PWD_KEY="pgvector-password"
EOF

cat <<EOF >>../data-ingestion/gcp.toml
[gcp]
projectId="${GCP_PROJECT_ID}"
region="${GCP_REGION}"
image_bucket="${GCS_BUCKET}"
EOF

echo "[Info]Import Procedure Completed"
