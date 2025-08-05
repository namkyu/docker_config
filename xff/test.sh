#!/bin/bash

echo "🚀 X-Forwarded-For 테스트 시나리오"
echo "================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 기본 URL
BASE_URL="http://localhost:8082"

echo -e "\n${BLUE}📋 테스트 환경:${NC}"
echo "- Proxy1: localhost:8080 (외부 접근점)"
echo "- Proxy2: Docker 내부 네트워크"
echo "- Backend: Docker 내부 네트워크"
echo ""

# 함수: HTTP 응답 코드 확인
check_response() {
    local url=$1
    local expected_code=${2:-200}
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" -eq "$expected_code" ]; then
        echo -e "${GREEN}✅ $url - HTTP $response${NC}"
        return 0
    else
        echo -e "${RED}❌ $url - HTTP $response (예상: $expected_code)${NC}"
        return 1
    fi
}

# 함수: JSON 출력을 예쁘게 포맷
pretty_json() {
    python3 -m json.tool 2>/dev/null || jq . 2>/dev/null || cat
}

echo -e "${YELLOW}🔍 테스트 1: 헬스체크${NC}"
echo "각 서비스가 정상적으로 동작하는지 확인합니다."
check_response "$BASE_URL/health"
echo ""

echo -e "${YELLOW}🔍 테스트 3: XFF 헤더 정보 확인${NC}"
echo "프록시 체인을 통과한 헤더 정보를 확인합니다."
check_response "$BASE_URL/headers"

echo -e "\n${BLUE}📡 실제 헤더 정보:${NC}"
curl -s "$BASE_URL/headers" | pretty_json
echo ""

echo -e "${YELLOW}🔍 테스트 4: 다양한 클라이언트 IP로 테스트${NC}"
echo "X-Forwarded-For 헤더를 직접 설정하여 테스트합니다."

echo -e "\n${BLUE}4-1. 기본 요청 (XFF 헤더 없음):${NC}"
curl -s -H "User-Agent: Test-Client-1" "$BASE_URL/headers" | pretty_json

echo -e "\n${BLUE}4-2. XFF 헤더를 직접 설정한 요청:${NC}"
curl -s -H "X-Forwarded-For: 211.168.1.100" -H "User-Agent: Test-Client-2" "$BASE_URL/headers" | pretty_json

echo -e "\n${BLUE}4-3. 여러 IP가 포함된 XFF 헤더:${NC}"
curl -s -H "X-Forwarded-For: 10.0.0.1, 211.168.1.100" -H "User-Agent: Test-Client-3" "$BASE_URL/headers" | pretty_json