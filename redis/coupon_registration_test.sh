#!/bin/bash

# Redis 컨테이너 정보 설정
REDIS_CONTAINER_NAME="redis1"
COUPON_KEY="coupon:event1"
MAX_USERS=20

echo "========================================================"
echo "Redis 선착순 쿠폰 등록 테스트 시작"
echo "========================================================"

echo "기존 데이터 초기화 중..."
docker exec $REDIS_CONTAINER_NAME redis-cli FLUSHDB

echo "쿠폰 한도 설정: $MAX_USERS"
docker exec $REDIS_CONTAINER_NAME redis-cli SET $COUPON_KEY:limit $MAX_USERS

CURRENT_LIMIT=$(docker exec $REDIS_CONTAINER_NAME redis-cli GET $COUPON_KEY:limit)
echo "설정된 쿠폰 한도 확인: $CURRENT_LIMIT"

# 동시 접속 시뮬레이션을 위한 병렬 테스트 함수
test_coupon_registration() {
    local user_id=$1
    local result=$(docker exec $REDIS_CONTAINER_NAME redis-cli EVAL "
        local coupon_key = KEYS[1]
		local limit_key = KEYS[2]
        local user_id = ARGV[1]
        local max_limit = tonumber(redis.call('GET', limit_key) or 0)
        
        -- 현재 등록된 사용자 수 확인
        local current_count = redis.call('SCARD', coupon_key)
        
        if current_count < max_limit then
            -- 사용자가 이미 등록되었는지 확인 (중복 방지)
            if redis.call('SISMEMBER', coupon_key, user_id) == 0 then
                redis.call('SADD', coupon_key, user_id)
                return current_count + 1  -- 성공, 순번 반환
            else
                return -1  -- 이미 등록된 사용자
            end
        else
            return -2  -- 선착순 마감
        end
    " 2 $COUPON_KEY $COUPON_KEY:limit $user_id)
    
    echo "$user_id:$result"
}

echo "병렬 테스트 시작"

# 백그라운드에서 동시에 실행
for i in {1..50}; do
    test_coupon_registration "user_$i" &
done

# 모든 백그라운드 작업 완료 대기
wait

echo "========================================================"
echo "테스트 결과 분석"
echo "========================================================"

registered_count=$(docker exec $REDIS_CONTAINER_NAME redis-cli SCARD $COUPON_KEY)
echo "최종 등록된 사용자 수: $registered_count"

echo "등록된 사용자 목록:"
docker exec $REDIS_CONTAINER_NAME redis-cli SMEMBERS $COUPON_KEY