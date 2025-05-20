# continuous_simulator.py
import random
from scipy.stats import truncnorm

class ContinuousSimulatorMixin:
    """평균 회귀 + 작은 노이즈 + 희박한 이상치 발생 로직을 공유"""
    # ── 하위 클래스가 오버라이드할 매개변수 ───────────────────
    SENSOR_TYPE = None          # "temp" / "humid" / ...
    MU          = None          # 평균
    SIGMA       = None          # 표준편차
    LOWER       = None          # 최소 허용값
    UPPER       = None          # 최대 허용값
    OUTLIER_P   = 0.03          # 기본 이상치 확률 3%
    DRIFT_THETA = 0.1           # 평균 회귀 강도 ** 데이터 정상범위 유지하는 중요 데이터터
    SMALL_SIGMA_RATIO = 0.1     # 정상 구간 변동폭 (σ의 10 %)

    # ── 내부 상태 초기화 ─────────────────────────────────────
    def _reset_state(self):
        a, b = (self.LOWER - self.MU) / self.SIGMA, (self.UPPER - self.MU) / self.SIGMA
        first = truncnorm.rvs(a, b, loc=self.MU, scale=self.SIGMA/3)
        self.prev_val = round(first, 2)

    # ── 핵심 데이터 생성 로직 ─────────────────────────────────
    def _generate_continuous_val(self):
        if not hasattr(self, "prev_val"):
            self._reset_state()

        # 1) 평균 회귀 + 작은 노이즈
        mean_revert = self.MU + (self.prev_val - self.MU) * (1 - self.DRIFT_THETA)
        small_sigma = self.SIGMA * self.SMALL_SIGMA_RATIO
        val = random.gauss(mean_revert, small_sigma)

        # 2) 이상치
        if random.random() < self.OUTLIER_P:
            val = random.gauss(self.MU, self.SIGMA)

        # 3) 범위 클램프 & 저장
        val = round(max(self.LOWER, min(self.UPPER, val)), 2)
        self.prev_val = val
        return val
