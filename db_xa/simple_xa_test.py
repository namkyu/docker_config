#!/usr/bin/env python3
"""
간단한 XA 트랜잭션 테스트 - XAER_OUTSIDE 오류 진단용
"""

import time

import mysql.connector
from mysql.connector import Error


def test_single_xa_transaction():
    """단일 DB에 대한 XA 트랜잭션 테스트"""
    print("=== 단일 DB XA 트랜잭션 테스트 ===")

    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root_password',
        'database': 'testdb1',
        'autocommit': False,
        'use_pure': True
    }

    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**config)
        print("✅ 데이터베이스 연결 성공")

        # XA 트랜잭션 ID
        xid = f"simple_test_{int(time.time())}"

        cursor = conn.cursor()

        # 1. XA START
        print(f"1. XA START '{xid}'")
        cursor.execute(f"XA START '{xid}'")

        # 2. 간단한 INSERT 작업
        test_id = int(time.time()) % 1000000
        print(f"2. INSERT 작업 실행 (ID: {test_id})")
        cursor.execute("INSERT INTO user (id, username, email) VALUES (%s, %s, %s)",
                       (test_id, f"test_user_{test_id}", f"test{test_id}@example.com"))

        # 3. XA END
        print(f"3. XA END '{xid}'")
        cursor.execute(f"XA END '{xid}'")

        # 4. XA PREPARE
        print(f"4. XA PREPARE '{xid}'")
        cursor.execute(f"XA PREPARE '{xid}'")

        # 5. XA COMMIT
        print(f"5. XA COMMIT '{xid}'")
        cursor.execute(f"XA COMMIT '{xid}'")

        print("🎉 단일 DB XA 트랜잭션 성공!")
        return True

    except Error as e:
        print(f"❌ XA 트랜잭션 실패: {e}")
        if cursor:
            try:
                cursor.execute(f"XA ROLLBACK '{xid}'")
                print("🔄 XA ROLLBACK 완료")
            except:
                pass
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("🔌 연결 해제 완료")


def test_xa_recover():
    """XA RECOVER 테스트"""
    print("\n=== XA RECOVER 테스트 ===")

    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root_password',
        'database': 'testdb1',
        'autocommit': False,
        'use_pure': True
    }

    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        print("XA RECOVER 실행:")
        cursor.execute("XA RECOVER")
        results = cursor.fetchall()

        if results:
            for row in results:
                print(f"  미완료 XA: {row}")
        else:
            print("  미완료 XA 트랜잭션 없음")

    except Error as e:
        print(f"❌ XA RECOVER 실패: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    print("🚀 XA 트랜잭션 진단 테스트 시작\n")

    # 1. XA RECOVER로 미완료 트랜잭션 확인
    test_xa_recover()

    # 2. 단일 DB XA 트랜잭션 테스트
    success = test_single_xa_transaction()

    if success:
        print("\n✅ 단일 DB XA 트랜잭션이 정상 작동합니다.")
        print("분산 트랜잭션 문제는 다른 원인일 가능성이 높습니다.")
    else:
        print("\n❌ 기본 XA 트랜잭션도 실패합니다.")
        print("MySQL 설정 또는 권한 문제를 확인해주세요.")

    print("\n🏁 진단 테스트 완료")
