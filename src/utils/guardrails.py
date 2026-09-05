"""兽医用药安全与极值拦截护栏模块。

校验 Agent 输出的处方是否超量或违规。
"""

from typing import List, Tuple
from src.schemas.response import TreatmentRecommendation
from src.utils.logger import log_guardrail_alert

# 禁用兽药与需强红线拦截列表
FORBIDDEN_DRUGS = ["瘦肉精", "克伦特罗", "氯霉素", "孔雀石绿"]


def validate_treatment_plan(
    session_id: str,
    cow_id: str,
    recommendations: List[TreatmentRecommendation]
) -> Tuple[bool, List[str]]:
    """校验处置建议是否违反用药禁忌或安全规范。

    入参 3 个，符合规范约束。
    """
    violations = []

    for rec in recommendations:
        dosage_text = rec.suggested_dosage.lower()
        action_text = rec.action.lower()

        # 检查是否包含禁用兽药
        for drug in FORBIDDEN_DRUGS:
            if drug in dosage_text or drug in action_text:
                msg = f"拦截违规禁用兽药: {drug}"
                violations.append(msg)
                log_guardrail_alert(session_id, cow_id, "FORBIDDEN_DRUG", msg)

    is_safe = len(violations) == 0
    return is_safe, violations
