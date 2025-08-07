import logging
import time
import uuid
from typing import Optional

import mysql.connector
from mysql.connector import Error

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class XATransactionTester:
    """XA 분산 트랜잭션 테스터"""

    def __init__(self, db1_config: dict, db2_config: dict):
        """
        두 개의 데이터베이스 연결 설정

        Args:
            db1_config: 첫 번째 DB 연결 설정 (user 테이블)
            db2_config: 두 번째 DB 연결 설정 (user_profile 테이블)
        """
        self.db1_config = db1_config
        self.db2_config = db2_config
        self.conn1: Optional[mysql.connector.MySQLConnection] = None
        self.conn2: Optional[mysql.connector.MySQLConnection] = None

    def setup(self):
        """데이터베이스 연결 설정"""
        try:
            print("🔗 데이터베이스 연결 중...")
            self.conn1 = mysql.connector.connect(**self.db1_config)
            self.conn2 = mysql.connector.connect(**self.db2_config)

            # XA 지원 확인
            self._check_xa_support()
            print("✅ 데이터베이스 연결 완료")

        except Error as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            raise

    def teardown(self):
        """연결 정리"""
        if self.conn1 and self.conn1.is_connected():
            self.conn1.close()
        if self.conn2 and self.conn2.is_connected():
            self.conn2.close()
        print("🔌 데이터베이스 연결 종료")

    def _check_xa_support(self):
        """XA 트랜잭션 지원 확인"""
        try:
            with self.conn1.cursor() as cursor:
                cursor.execute("SHOW ENGINES")
                engines = cursor.fetchall()
                innodb_xa = any('InnoDB' in str(engine) and 'YES' in str(engine) for engine in engines)

            with self.conn2.cursor() as cursor:
                cursor.execute("SHOW ENGINES")
                engines = cursor.fetchall()
                innodb_xa2 = any('InnoDB' in str(engine) and 'YES' in str(engine) for engine in engines)

            if not (innodb_xa and innodb_xa2):
                raise Exception("InnoDB 엔진이 활성화되지 않았습니다. XA 트랜잭션을 지원하지 않습니다.")

        except Error as e:
            print(f"⚠️ XA 지원 확인 중 오류: {e}")

    def _generate_xid(self, suffix: str = "") -> str:
        """고유한 XA 트랜잭션 ID 생성"""
        timestamp = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex[:8]
        return f"xa_test_{timestamp}_{unique_id}{suffix}"

    def _check_xa_status(self, conn, xid: str) -> bool:
        """XA 트랜잭션 상태 확인"""
        try:
            with conn.cursor() as cursor:
                cursor.execute("XA RECOVER")
                recovered = cursor.fetchall()
                return any(xid in recover_data for recover_data in recovered)
        except Error:
            logger.warning(f"XA 상태 확인 실패 ({xid})")
        return False

    def _xa_rollback_safe(self, conn, xid: str) -> bool:
        """안전한 XA 롤백"""
        try:
            # XA 상태 확인 후 롤백
            if self._check_xa_status(conn, xid):
                with conn.cursor() as cursor:
                    cursor.execute(f"XA ROLLBACK '{xid}'")
                return True
        except Error as e:
            logger.warning(f"XA ROLLBACK 실패 ({xid}): {e}")
        return False

    def test_xa_commit_success(self) -> bool:
        """XA 트랜잭션 성공 케이스 테스트"""
        print("\n" + "=" * 60)
        print("📋 TEST: XA 트랜잭션 커밋 성공 테스트")
        print("=" * 60)

        # XA 트랜잭션 ID 생성
        xid1 = self._generate_xid("_db1")
        xid2 = self._generate_xid("_db2")

        try:
            # 테스트 데이터 준비
            timestamp = int(time.time())
            new_username = f"xa_success_{timestamp}"
            new_email = f"{new_username}@example.com"
            user_id = timestamp % 1000000

            print(f"🎯 생성할 사용자: {new_username} (ID: {user_id})")

            # Phase 1: XA START
            print("\n📋 Phase 1: XA 트랜잭션 시작")
            with self.conn1.cursor() as cursor:
                cursor.execute(f"XA START '{xid1}'")
                print(f"   ✅ DB1 XA START: {xid1}")

            with self.conn2.cursor() as cursor:
                cursor.execute(f"XA START '{xid2}'")
                print(f"   ✅ DB2 XA START: {xid2}")

            # 트랜잭션 작업 수행
            print("\n💼 트랜잭션 작업 수행")

            # DB1: user 테이블에 삽입
            with self.conn1.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user (id, username, email) VALUES (%s, %s, %s)",
                    (user_id, new_username, new_email)
                )
                print(f"   ✅ DB1: user 삽입 완료 (ID: {user_id})")

            # DB2: user_profile 테이블에 삽입
            with self.conn2.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user_profile (user_id, first_name, last_name, phone) VALUES (%s, %s, %s, %s)",
                    (user_id, "XA", "Success", "010-1111-2222")
                )
                print(f"   ✅ DB2: user_profile 삽입 완료 (user_id: {user_id})")

            # XA END
            print("\n🔚 XA END 수행")
            with self.conn1.cursor() as cursor:
                cursor.execute(f"XA END '{xid1}'")
                print(f"   ✅ DB1 XA END: {xid1}")

            with self.conn2.cursor() as cursor:
                cursor.execute(f"XA END '{xid2}'")
                print(f"   ✅ DB2 XA END: {xid2}")

            # Phase 2: XA PREPARE
            print("\n🎯 Phase 2: XA PREPARE")
            with self.conn1.cursor() as cursor:
                cursor.execute(f"XA PREPARE '{xid1}'")
                print(f"   ✅ DB1 XA PREPARE 성공")

            with self.conn2.cursor() as cursor:
                cursor.execute(f"XA PREPARE '{xid2}'")
                print(f"   ✅ DB2 XA PREPARE 성공")

            print("   🎉 모든 노드에서 PREPARE 성공!")

            # Phase 3: XA COMMIT
            print("\n✅ Phase 3: XA COMMIT")
            with self.conn1.cursor() as cursor:
                cursor.execute(f"XA COMMIT '{xid1}'")
                print(f"   ✅ DB1 XA COMMIT 성공")

            with self.conn2.cursor() as cursor:
                cursor.execute(f"XA COMMIT '{xid2}'")
                print(f"   ✅ DB2 XA COMMIT 성공")

            print(f"\n🎉 XA 트랜잭션 성공! 사용자 '{new_username}' 생성 완료")
            return True

        except Error as e:
            print(f"\n❌ XA 트랜잭션 실패: {e}")
            print("🔄 롤백 시도...")

            self._xa_rollback_safe(self.conn1, xid1)
            self._xa_rollback_safe(self.conn2, xid2)
            return False

    def test_xa_rollback_scenario(self):
        """XA 트랜잭션 롤백 시나리오 테스트"""
        print("\n" + "=" * 60)
        print("🔄 TEST: XA 트랜잭션 롤백 테스트")
        print("=" * 60)

        xid1 = self._generate_xid("_rollback1")
        xid2 = self._generate_xid("_rollback2")

        try:
            timestamp = int(time.time() * 1000)
            new_username = f"xa_rollback_{timestamp}"
            new_email = f"{new_username}@example.com"
            user_id = timestamp % 1000000

            print(f"🎯 테스트 사용자: {new_username} (ID: {user_id})")

            # Phase 1: XA START
            print("\n📋 Phase 1: XA 트랜잭션 시작")
            with self.conn1.cursor() as cursor:
                cursor.execute(f"XA START '{xid1}'")
                print(f"   ✅ DB1 XA START: {xid1}")

            with self.conn2.cursor() as cursor:
                cursor.execute(f"XA START '{xid2}'")
                print(f"   ✅ DB2 XA START: {xid2}")

            # 트랜잭션 작업 수행
            print("\n💼 트랜잭션 작업 수행")

            # DB1: user 테이블에 삽입
            with self.conn1.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user (id, username, email) VALUES (%s, %s, %s)",
                    (user_id, new_username, new_email)
                )
                print(f"   ✅ DB1: user 삽입 완료 (ID: {user_id})")

            # DB2: user_profile 테이블에 삽입
            with self.conn2.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user_profile (user_id, first_name, last_name, phone) VALUES (%s, %s, %s, %s)",
                    (user_id, "XA", "Success", "010-1111-2222")
                )
                print(f"   ✅ DB2: user_profile 삽입 완료 (user_id: {user_id})")

            # XA END
            print("\n🔚 XA END 수행")
            with self.conn1.cursor() as cursor:
                cursor.execute(f"XA END '{xid1}'")
                print(f"   ✅ DB1 XA END: {xid1}")

            with self.conn2.cursor() as cursor:
                cursor.execute(f"XA END '{xid2}'")
                print(f"   ✅ DB2 XA END: {xid2}")

            # Phase 2: XA PREPARE
            print("\n🎯 Phase 2: XA PREPARE")
            with self.conn1.cursor() as cursor:
                cursor.execute(f"XA PREPARE '{xid1}'")
                print(f"   ✅ DB1 XA PREPARE 성공")

            with self.conn2.cursor() as cursor:
                cursor.execute(f"XA PREPARE '{xid2}'")
                print(f"   ✅ DB2 XA PREPARE 성공")

            print("   🎉 모든 노드에서 PREPARE 성공!")

            # 의도적으로 롤백 실행 (비즈니스 로직 실패 시뮬레이션)
            print("\n💥 비즈니스 로직 오류 시뮬레이션 - 강제 롤백")
            raise Exception("비즈니스 로직 검증 실패 (시뮬레이션)")

        except Exception as e:
            print(f"❌ 예상된 오류: {e}")
            print("\n🔄 XA ROLLBACK 수행")

            rollback1 = self._xa_rollback_safe(self.conn1, xid1)
            rollback2 = self._xa_rollback_safe(self.conn2, xid2)

            if rollback1 and rollback2:
                print("✅ 모든 노드에서 롤백 성공")
                return True
            else:
                print("❌ 일부 노드에서 롤백 실패")
                return False

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 XA 분산 트랜잭션 테스트 시작")
        print("=" * 60)

        results = []

        # 성공 케이스 테스트
        results.append(("커밋 성공", self.test_xa_commit_success()))

        # 롤백 시나리오 테스트
        results.append(("롤백 시나리오", self.test_xa_rollback_scenario()))

        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)

        passed = 0
        for test_name, result in results:
            status = "✅ 성공" if result else "❌ 실패"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1

        print(f"\n🎯 전체 결과: {passed}/{len(results)} 테스트 통과")

        if passed == len(results):
            print("🎉 모든 XA 분산 트랜잭션 테스트 성공!")
        else:
            print("⚠️ 일부 테스트가 실패했습니다.")

        return passed == len(results)


def main():
    """메인 실행 함수"""

    # 데이터베이스 연결 설정
    db1_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root_password',
        'database': 'testdb1',
        'autocommit': False,
        'charset': 'utf8mb4'
    }

    db2_config = {
        'host': 'localhost',
        'port': 3307,
        'user': 'root',
        'password': 'root_password',
        'database': 'testdb2',
        'autocommit': False,
        'charset': 'utf8mb4'
    }

    # XA 테스터 생성 및 실행
    tester = XATransactionTester(db1_config, db2_config)

    try:
        tester.setup()
        success = tester.run_all_tests()

        if success:
            print("\n🎊 전체 테스트 완료!")
        else:
            print("\n🔧 일부 테스트를 재검토해주세요.")

    except Exception as e:
        print(f"\n💥 테스트 실행 중 오류 발생: {e}")
    finally:
        tester.teardown()


if __name__ == "__main__":
    main()
