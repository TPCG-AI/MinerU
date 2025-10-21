# 1. 기본 이미지 지정
# 특정 버전 대신 주요 버전 태그를 사용하면 최신 버그 수정 사항을 포함할 수 있습니다.
# v0.10.1.1 버전을 꼭 사용해야 한다면 원래대로 유지하셔도 좋습니다.
FROM vllm/vllm-openai:v0.10.1

# 2. 시스템 패키지 설치 및 폰트 설정
# - RUN 명령어를 하나로 합쳐 Docker 이미지 레이어 수를 줄여줍니다.
# - --no-install-recommends 플래그로 불필요한 패키지 설치를 방지합니다.
# - apt-get clean 및 캐시 삭제를 마지막에 실행하여 이미지 크기를 최적화합니다.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fonts-noto-core \
        fonts-noto-cjk \
        fontconfig \
        libgl1 \
        curl \
        ca-certificates \
        gsutil && \
    fc-cache -fv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. Python 패키지 설치
# - editable mode로 설치하여 volume mount된 소스 코드 변경사항 즉시 반영
COPY . /workspace/mineru
WORKDIR /workspace/mineru
RUN python3 -m pip install -e '.[core]' --break-system-packages --no-cache-dir

# 4. 애플리케이션 디렉토리 설정 및 파일 복사
WORKDIR /app
COPY mineru-config.json /app/mineru.json
COPY entrypoint.sh /app/entrypoint.sh

# 5. 실행 권한 부여
RUN chmod +x /app/entrypoint.sh

# 6. 환경 변수 설정
ENV MINERU_MODEL_SOURCE=local \
    MINERU_TOOLS_CONFIG_JSON=/app/mineru.json \
    MODEL_PATH=/tmp/models \
    # BUCKET_NAME은 빌드 시점에 --build-arg 또는 docker-compose.yml 등에서 전달받는 것이 좋습니다.
    BUCKET_NAME="" \
    PORT=8080 \
    PYTHONUNBUFFERED=1

# 7. 컨테이너 시작 명령어
# - 복잡한 로직을 entrypoint.sh 스크립트로 분리하여 가독성과 유지보수성을 높입니다.
ENTRYPOINT ["/app/entrypoint.sh"]
