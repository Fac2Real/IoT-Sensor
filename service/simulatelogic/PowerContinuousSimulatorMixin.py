import random
from scipy.stats import truncnorm

class PowerContinuousSimulatorMixin:
    MU = None
    SIGMA = None
    LOWER = 0
    UPPER = None
    OUTLIER_P = 0.005
    DRIFT_THETA = 0.2
    SMALL_SIGMA_RATIO = 0.07

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
    
        # 2) 이상치 발생 - 이상치는 upper의 80~100%로 튀게
        if random.random() < self.OUTLIER_P:
            val = random.uniform(self.UPPER * 0.8, self.UPPER)

        # 3) 범위 클램프 & 저장
        val = round(max(self.LOWER, min(self.UPPER, val)), 2)
        self.prev_val = val
        return val
    # ── 파라미터를 받는 전력값 생성 메서드 추가 ─────────────────────────────────
    def _generate_power_val(self, mu, sigma, lower, upper):
        """특정 파라미터로 전력값 생성 (독립적인 상태 관리)"""
        state_key = f"prev_val_{mu}_{sigma}"
        
        if not hasattr(self, state_key):
            a, b = (lower - mu) / sigma, (upper - mu) / sigma
            first = truncnorm.rvs(a, b, loc=mu, scale=sigma/3)
            setattr(self, state_key, round(first, 2))

        prev_val = getattr(self, state_key)
        
        # 1) 평균 회귀 + 작은 노이즈
        mean_revert = mu + (prev_val - mu) * (1 - self.DRIFT_THETA)
        small_sigma = sigma * self.SMALL_SIGMA_RATIO
        val = random.gauss(mean_revert, small_sigma)
    
        # 2) 이상치 발생 - 이상치는 upper의 80~100%로 튀게
        if random.random() < self.OUTLIER_P:
            val = random.uniform(upper * 0.8, upper)

        # 3) 범위 클램프 & 저장
        val = round(max(lower, min(upper, val)), 2)
        setattr(self, state_key, val)
        return val