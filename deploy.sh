#!/bin/bash

echo "🚀 Chatterbox TTS 클라우드 배포 스크립트"
echo "=========================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 배포 옵션 선택
echo "배포할 플랫폼을 선택하세요:"
echo "1) Railway (추천 - 무료 GPU)"
echo "2) Render"
echo "3) Heroku"
echo "4) AWS EC2"
echo "5) Google Cloud Run"
echo "6) DigitalOcean App Platform"
echo ""
read -p "선택 (1-6): " choice

case $choice in
    1)
        print_step "Railway 배포 시작..."
        
        # Railway CLI 설치 확인
        if ! command -v railway &> /dev/null; then
            print_warning "Railway CLI가 설치되지 않았습니다."
            echo "설치 중..."
            npm install -g @railway/cli
        fi
        
        # Railway 로그인
        print_step "Railway에 로그인 중..."
        railway login
        
        # 프로젝트 초기화
        print_step "Railway 프로젝트 초기화..."
        railway init
        
        # 배포
        print_step "배포 중..."
        railway up
        
        print_success "Railway 배포 완료!"
        echo "배포된 URL을 확인하려면: railway status"
        ;;
        
    2)
        print_step "Render 배포 시작..."
        
        # Git 저장소 확인
        if [ ! -d ".git" ]; then
            print_error "Git 저장소가 아닙니다. 먼저 git init을 실행하세요."
            exit 1
        fi
        
        print_step "Render에 연결 중..."
        echo "1. https://render.com 에서 계정 생성"
        echo "2. 'New Web Service' 클릭"
        echo "3. GitHub 저장소 연결"
        echo "4. 다음 설정 사용:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: python app.py"
        echo "   - Environment: Python 3"
        echo "   - Plan: Starter (무료)"
        
        print_success "Render 배포 가이드 완료!"
        ;;
        
    3)
        print_step "Heroku 배포 시작..."
        
        # Heroku CLI 설치 확인
        if ! command -v heroku &> /dev/null; then
            print_warning "Heroku CLI가 설치되지 않았습니다."
            echo "https://devcenter.heroku.com/articles/heroku-cli 에서 설치하세요."
            exit 1
        fi
        
        # Heroku 로그인
        print_step "Heroku에 로그인 중..."
        heroku login
        
        # 앱 생성
        read -p "Heroku 앱 이름을 입력하세요: " app_name
        heroku create $app_name
        
        # 환경 변수 설정
        heroku config:set FLASK_ENV=production
        
        # 배포
        print_step "배포 중..."
        git push heroku main
        
        print_success "Heroku 배포 완료!"
        echo "앱 URL: https://$app_name.herokuapp.com"
        ;;
        
    4)
        print_step "AWS EC2 배포 가이드..."
        
        echo "1. AWS EC2 인스턴스 생성 (t3.medium 이상 권장)"
        echo "2. 보안 그룹에서 포트 80, 443, 5000 열기"
        echo "3. 인스턴스에 접속:"
        echo "   ssh -i your-key.pem ubuntu@your-ec2-ip"
        echo "4. Docker 설치:"
        echo "   sudo apt update && sudo apt install docker.io docker-compose"
        echo "5. 프로젝트 클론 및 실행:"
        echo "   git clone your-repository"
        echo "   cd web-tts-service"
        echo "   sudo docker-compose up -d"
        
        print_success "AWS EC2 배포 가이드 완료!"
        ;;
        
    5)
        print_step "Google Cloud Run 배포 시작..."
        
        # gcloud CLI 설치 확인
        if ! command -v gcloud &> /dev/null; then
            print_warning "Google Cloud CLI가 설치되지 않았습니다."
            echo "https://cloud.google.com/sdk/docs/install 에서 설치하세요."
            exit 1
        fi
        
        # 프로젝트 ID 입력
        read -p "Google Cloud 프로젝트 ID를 입력하세요: " project_id
        gcloud config set project $project_id
        
        # Cloud Run 배포
        print_step "Cloud Run에 배포 중..."
        gcloud run deploy chatterbox-tts \
            --source . \
            --platform managed \
            --region asia-northeast1 \
            --allow-unauthenticated \
            --memory 4Gi \
            --cpu 2 \
            --timeout 900
        
        print_success "Google Cloud Run 배포 완료!"
        ;;
        
    6)
        print_step "DigitalOcean App Platform 배포 가이드..."
        
        echo "1. https://cloud.digitalocean.com/apps 에서 계정 생성"
        echo "2. 'Create App' 클릭"
        echo "3. GitHub 저장소 연결"
        echo "4. 다음 설정 사용:"
        echo "   - Source Directory: /"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Run Command: python app.py"
        echo "   - HTTP Port: 5000"
        echo "   - Plan: Basic ($5/월)"
        
        print_success "DigitalOcean 배포 가이드 완료!"
        ;;
        
    *)
        print_error "잘못된 선택입니다."
        exit 1
        ;;
esac

echo ""
print_success "배포 프로세스가 완료되었습니다!"
echo "배포된 서비스에 접속하여 TTS 기능을 테스트해보세요."
