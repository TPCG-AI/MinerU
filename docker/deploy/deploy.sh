#!/bin/bash

# ====================================
# MinerU Cloud Run 배포 스크립트
# ====================================

set -e  # 에러 발생 시 즉시 중단

# 설정값 (본인 환경에 맞게 수정)
PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
REGION="${GCP_REGION:-asia-northeast3}"
BUCKET_NAME="${GCS_BUCKET_NAME:-your-gcs-bucket-name}"
ARTIFACT_REGISTRY="${ARTIFACT_REGISTRY:-your-artifact-registry}"
IMAGE_NAME="mineru-cloudrun"
SERVICE_NAME="mineru-api"

# 색상 출력
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}MinerU Cloud Run 배포 시작${NC}"
echo -e "${GREEN}=====================================${NC}"
echo -e "${BLUE}프로젝트: ${PROJECT_ID}${NC}"
echo -e "${BLUE}리전: ${REGION}${NC}"
echo -e "${BLUE}버킷: ${BUCKET_NAME}${NC}"
echo -e "${BLUE}Artifact Registry: ${ARTIFACT_REGISTRY}${NC}"
echo ""

# 1. GCP 프로젝트 설정
echo -e "${YELLOW}[1/4] GCP 프로젝트 설정...${NC}"
gcloud config set project ${PROJECT_ID}

# 2. Cloud Build로 이미지 빌드 & 푸시
echo -e "${YELLOW}[2/4] Cloud Build로 Docker 이미지 빌드 및 푸시 중...${NC}"
cd "$(dirname "$0")"
FULL_IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY}/${IMAGE_NAME}:latest"
echo -e "${BLUE}이미지 경로: ${FULL_IMAGE_PATH}${NC}"

gcloud builds submit \
  --tag ${FULL_IMAGE_PATH} \
  --timeout=30m \
  --machine-type=e2-highcpu-8 \
  --disk-size=100 \
  .

echo -e "${GREEN}✅ 이미지 빌드 및 푸시 완료${NC}"

# 3. 빌드된 이미지 확인
echo -e "${YELLOW}[3/4] 빌드된 이미지 확인...${NC}"
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY} \
  --filter="${IMAGE_NAME}" \
  --limit=1

# 4. Cloud Run 배포 (YAML 방식 - 확실한 volume mount)
echo -e "${YELLOW}[4/4] Cloud Run에 배포 중 (YAML 방식)...${NC}"

# YAML 파일에 이미지 경로 주입
sed "s|PLACEHOLDER_IMAGE|${FULL_IMAGE_PATH}|g" service.yaml > service-deployed.yaml

echo -e "${BLUE}배포할 서비스 정의:${NC}"
cat service-deployed.yaml

# YAML로 배포
gcloud run services replace service-deployed.yaml \
  --region us-central1 \
  --platform managed

# IAM 정책 설정 (unauthenticated 허용)
gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# gcloud run deploy ${SERVICE_NAME} \
#   --image ${FULL_IMAGE_PATH} \
#   --region us-central1 \
#   --platform managed \
#   --allow-unauthenticated \
#   --execution-environment gen2 \
#   --gpu 1 \
#   --gpu-type nvidia-l4 \
#   --cpu 4 \
#   --memory 16Gi \
#   --timeout 600 \
#   --concurrency 1 \
#   --min-instances 0 \
#   --max-instances 3 \
#   --add-volume name=models,type=cloud-storage,bucket=${BUCKET_NAME} \
#   --add-volume-mount volume=models,mount-path="/mnt/models" \
#   --set-env-vars MINERU_MODEL_SOURCE=local,MINERU_TOOLS_CONFIG_JSON=/app/mineru.json

# 배포 완료
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}✅ 배포 완료!${NC}"
echo -e "${GREEN}=====================================${NC}"

# 서비스 URL 출력
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo -e "${GREEN}🌐 서비스 URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}📖 API 문서: ${SERVICE_URL}/docs${NC}"
echo -e "${GREEN}🔍 Health Check: ${SERVICE_URL}/health${NC}"
echo ""
echo -e "${BLUE}테스트 명령어:${NC}"
echo -e "curl ${SERVICE_URL}/health"
