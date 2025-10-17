# MinerU Cloud Run 배포 가이드

GCS Bucket 기반 모델 로드 방식으로 Cloud Run GPU에 MinerU를 배포하는 가이드입니다.

## 📋 사전 준비

### 1. GCP 리소스 생성 완료 ✅
- [x] GCS Bucket: `cloud-bucket-kangmin-test-20251015`
- [x] Artifact Registry: `artifact-registry-kangmin-test-20251015`
- [x] 모델 업로드 완료 (4.62 GiB)

### 2. 필요한 도구 설치
```bash
# Docker 설치 확인
docker --version

# gcloud CLI 설치 확인
gcloud --version

# gcloud 인증
gcloud auth login
gcloud auth configure-docker us-central1-docker.pkg.dev
```

---

## 🚀 배포 방법

### 방법 1: 자동 배포 스크립트 (추천)

```bash
cd docker/deploy

# GCP 프로젝트 ID 설정
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"

# 배포 스크립트 실행
bash deploy.sh
```

### 방법 2: 수동 단계별 배포

#### Step 1: Cloud Build로 이미지 빌드 및 푸시
```bash
cd docker/deploy

# 프로젝트 ID 설정
PROJECT_ID="your-project-id"
REGION="us-central1"

# Cloud Build로 빌드 & Artifact Registry에 자동 푸시
gcloud builds submit \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/artifact-registry-kangmin-test-20251015/mineru-cloudrun:latest \
  --timeout=30m \
  --machine-type=e2-highcpu-8 \
  --disk-size=100 \
  .
```

**Cloud Build 설정:**
- `--machine-type=e2-highcpu-8`: 8 vCPU (빌드 속도 향상)
- `--timeout=30m`: 최대 30분 (기본 10분은 부족할 수 있음)
- `--disk-size=100`: 100GB 디스크 (큰 이미지 빌드용)

#### Step 2: Cloud Run 배포
```bash
gcloud run deploy mineru-api \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/artifact-registry-kangmin-test-20251015/mineru-cloudrun:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --execution-environment gen2 \
  --gpu 1 \
  --gpu-type nvidia-l4 \
  --cpu 4 \
  --memory 16Gi \
  --timeout 600 \
  --concurrency 1 \
  --min-instances 0 \
  --max-instances 3 \
  --add-volume name=gcs-models,type=cloud-storage,bucket=cloud-bucket-kangmin-test-20251015 \
  --add-volume-mount volume=gcs-models,mount-path=/gcs \
  --set-env-vars MINERU_MODEL_SOURCE=local,MINERU_TOOLS_CONFIG_JSON=/app/mineru.json
```

---

## 🧪 로컬 테스트 (Docker Compose)

배포 전에 로컬에서 테스트하려면:

```bash
cd docker/deploy

# GPU가 있는 경우
docker compose -f docker-compose.cloudrun.yml up mineru-api

# Gradio WebUI 테스트
docker compose -f docker-compose.cloudrun.yml up mineru-gradio
```

**접속:**
- API: http://localhost:8080/docs
- Gradio: http://localhost:7860

---

## 📁 파일 구조

```
docker/deploy/
├── Dockerfile.cloudrun          # Cloud Run용 Dockerfile (GCS 기반)
├── mineru-config.json           # GCS 모델 경로 설정
├── docker-compose.cloudrun.yml  # 로컬 테스트용
├── deploy.sh                    # 자동 배포 스크립트
└── README.md                    # 이 파일
```

---

## 🔧 주요 설정

### 1. GCS 버킷 구조
```
gs://cloud-bucket-kangmin-test-20251015/
└── mineru-models/
    ├── pipeline/  (2.46 GiB) - CPU 가능
    └── vlm/       (2.16 GiB) - GPU 전용
```

### 2. 모델 경로 (mineru-config.json)
```json
{
  "models-dir": {
    "pipeline": "/gcs/mineru-models/pipeline/models--opendatalab--PDF-Extract-Kit-1.0/snapshots/...",
    "vlm": "/gcs/mineru-models/vlm/models--opendatalab--MinerU2.5-2509-1.2B/snapshots/..."
  }
}
```

### 3. Cloud Run 리소스
- **GPU**: NVIDIA L4 x 1
- **CPU**: 4 vCPU
- **메모리**: 16 GiB
- **타임아웃**: 600초 (10분)
- **동시성**: 1 (GPU 독점 사용)

---

## 📊 비용 예상

| 리소스 | 사양 | 시간당 비용 (예상) |
|--------|------|-------------------|
| GPU (L4) | 1개 | ~$0.70 |
| CPU | 4 vCPU | ~$0.10 |
| 메모리 | 16 GiB | ~$0.02 |
| GCS 스토리지 | 4.62 GiB | ~$0.0001 |
| **총합** | | **~$0.82/hr** |

**최소 인스턴스 0**으로 설정되어 있어, 사용하지 않을 때는 비용이 발생하지 않습니다.

---

## 🐛 트러블슈팅

### 1. 이미지 푸시 실패
```bash
# Docker 인증 재설정
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 2. GPU 쿼터 부족
```bash
# 쿼터 확인
gcloud compute project-info describe --project=YOUR_PROJECT_ID
```
→ GCP 콘솔에서 GPU 쿼터 증가 요청

### 3. GCS 마운트 실패
- Cloud Run 서비스 계정에 GCS 버킷 읽기 권한 확인
- `gsutil iam get gs://cloud-bucket-kangmin-test-20251015`

### 4. Cold Start 느림
- Cloud Run은 첫 요청 시 컨테이너 시작 (콜드 스타트)
- 예상 시간: 10-30초
- 해결: `--min-instances 1` 설정 (항상 1개 인스턴스 유지, 비용 증가)

---

## ✅ 배포 후 확인

```bash
# 서비스 URL 확인
gcloud run services describe mineru-api --region us-central1 --format 'value(status.url)'

# Health Check
curl https://YOUR-SERVICE-URL/health

# API 문서 접속
# https://YOUR-SERVICE-URL/docs
```

---

## 🎯 다음 단계

- [ ] Cloud Monitoring 설정
- [ ] Cloud Logging 필터 설정
- [ ] CI/CD 파이프라인 구축 (Cloud Build)
- [ ] Load Balancer + CDN 설정
- [ ] 커스텀 도메인 연결

---

## 📚 참고 문서

- [Cloud Run GPU 문서](https://cloud.google.com/run/docs/configuring/services/gpu)
- [GCS FUSE 마운트](https://cloud.google.com/run/docs/configuring/services/cloud-storage-volume-mounts)
- [MinerU 공식 문서](https://opendatalab.github.io/MinerU/)
