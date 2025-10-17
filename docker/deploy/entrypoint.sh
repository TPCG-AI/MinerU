#!/bin/bash
set -e

echo "🔍 환경 변수 확인:"
echo "  BUCKET_NAME: ${BUCKET_NAME}"
echo "  GCS_MOUNT_PATH: ${GCS_MOUNT_PATH}"

if [ -z "${BUCKET_NAME}" ]; then
  echo "❌ BUCKET_NAME env not set"
  exit 1
fi

if [ -z "${GCS_MOUNT_PATH}" ]; then
  echo "❌ GCS_MOUNT_PATH env not set"
  exit 1
fi

echo "✅ GCS Bucket이 FUSE로 마운트되었습니다: ${GCS_MOUNT_PATH}"
echo ""

echo "📂 마운트된 GCS 버킷 구조 확인:"
echo "=== Root (${GCS_MOUNT_PATH}/) ==="
ls -la "${GCS_MOUNT_PATH}/" 2>&1 | head -10 || echo "❌ 마운트 경로 없음"
echo ""
echo "=== Pipeline (${GCS_MOUNT_PATH}/pipeline/) ==="
ls -la "${GCS_MOUNT_PATH}/pipeline/" 2>&1 | head -10 || echo "⚠️  pipeline/ 없음"
echo ""
echo "=== Pipeline/models (${GCS_MOUNT_PATH}/pipeline/models/) ==="
ls -la "${GCS_MOUNT_PATH}/pipeline/models/" 2>&1 | head -10 || echo "⚠️  pipeline/models/ 없음"
echo ""
echo "=== VLM (${GCS_MOUNT_PATH}/vlm/) ==="
ls -la "${GCS_MOUNT_PATH}/vlm/" 2>&1 | head -5 || echo "⚠️  vlm/ 없음"
echo ""
echo "=== ✅ 최종 확인: MFD 모델 경로 ==="
if [ -f "${GCS_MOUNT_PATH}/pipeline/models/MFD/YOLO/yolo_v8_ft.pt" ]; then
  echo "✅ ${GCS_MOUNT_PATH}/pipeline/models/MFD/YOLO/yolo_v8_ft.pt 존재!"
  ls -lh "${GCS_MOUNT_PATH}/pipeline/models/MFD/YOLO/yolo_v8_ft.pt"
else
  echo "❌ MFD 모델을 찾을 수 없습니다!"
  echo "경로 확인: ${GCS_MOUNT_PATH}/pipeline/models/MFD/YOLO/"
  ls -la "${GCS_MOUNT_PATH}/pipeline/models/MFD/YOLO/" 2>&1 || echo "디렉토리 자체가 없음"
fi
echo ""

echo "🚀 vLLM 서버를 백그라운드에서 시작합니다..."
mineru-vllm-server \
  --model "${GCS_MOUNT_PATH}/vlm" \
  --host 127.0.0.1 \
  --port 30000 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096 \
  --trust-remote-code &

VLLM_PID=$!
echo "✅ vLLM 서버 시작됨 (PID: ${VLLM_PID})"

# vLLM 서버가 준비될 때까지 대기
echo "⏳ vLLM 서버 준비 대기 중..."
for i in {1..60}; do
  if curl -s http://127.0.0.1:30000/v1/models >/dev/null 2>&1; then
    echo "✅ vLLM 서버 준비 완료!"
    break
  fi
  echo "  대기 중... ($i/60)"
  sleep 2
done

echo "🚀 MinerU API를 시작합니다..."
exec mineru-api --host 0.0.0.0 --port "${PORT}" --backend vlm-http-client --url http://127.0.0.1:30000
