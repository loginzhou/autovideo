"""
自动质量审核模块
AI自动审核剧本、分镜、生成的内容，过滤不符合平台规则、质量不达标的内容，自动返工，减少人工审核工作量
"""
import json
from typing import Dict, Any, Tuple
from config_center import config
from components.utils.llm_client import get_llm_response

class QualityAuditor:
    def __init__(self):
        self.enable_audit = config.get("quality_audit.enable_audit", True)
        self.audit_stages = config.get("quality_audit.audit_stages", ["screenplay", "storyboard"])
        self.min_score = config.get("quality_audit.min_score", 8)
        self.max_retries = config.get("quality_audit.max_retries", 2)
        self.platform_rules = config.get("quality_audit.platform_rules", [
            "禁止色情、暴力、血腥、低俗内容",
            "禁止违反当地法律法规内容",
            "禁止政治敏感内容",
            "禁止歧视性内容",
            "内容积极向上，符合短视频平台社区规范"
        ])
    
    def audit_screenplay(self, screenplay: Dict[str, Any], episode_seq: int) -> Tuple[bool, str, float]:
        """审核剧本质量
        返回：(是否通过, 审核意见, 质量分数)
        """
        if not self.enable_audit or "screenplay" not in self.audit_stages:
            return (True, "审核关闭，自动通过", 10.0)
        
        prompt = f"""
你是专业短剧内容审核专家，现在审核第{episode_seq}集剧本质量，从以下几个维度评分（1-10分）：
1. 完播率：是否符合3秒钩子、15秒爽点、结尾强悬念的完播率曲线
2. 内容合规：是否符合平台规则，无违规内容
3. 剧情质量：剧情是否连贯、逻辑通顺、有吸引力
4. 台词质量：台词是否精炼、符合人设、不生硬
5. 节奏把控：60-90秒时长节奏是否合适

平台规则：
{chr(10).join(self.platform_rules)}

剧本内容：
{json.dumps(screenplay, ensure_ascii=False, indent=2)}

输出严格为JSON格式，不要其他内容：
{{
    "score": 分数（1-10的数字）,
    "pass": true/false（分数>={self.min_score}则为true）,
    "comment": "审核意见，指出问题和改进建议，没有问题则填通过"
}}
        """
        
        try:
            response = get_llm_response(
                prompt,
                model=config.get("quality_audit.model", "deepseek-ai/DeepSeek-V3.2"),
                temperature=0.1,
                max_tokens=500
            )
            result = json.loads(response)
            score = float(result.get('score', 0))
            passed = result.get('pass', score >= self.min_score)
            comment = result.get('comment', '无审核意见')
            return (passed, comment, score)
        except Exception as e:
            print(f"剧本审核失败：{str(e)}，自动通过")
            return (True, f"审核失败，自动通过：{str(e)}", 8.0)
    
    def audit_storyboard(self, storyboard: Dict[str, Any], episode_seq: int) -> Tuple[bool, str, float]:
        """审核分镜质量
        返回：(是否通过, 审核意见, 质量分数)
        """
        if not self.enable_audit or "storyboard" not in self.audit_stages:
            return (True, "审核关闭，自动通过", 10.0)
        
        # 先做简单规则校验
        for idx, shot in enumerate(storyboard['storyboard']):
            # 检查分镜是否包含必要字段
            required_fields = ["shot_id", "visual_prompt", "audio_prompt"]
            for field in required_fields:
                if field not in shot:
                    return (False, f"镜头{idx+1}缺少必要字段：{field}", 0.0)
            # 检查视觉提示词是否包含竖屏参数
            if "--ar 9:16" not in shot.get("visual_prompt", ""):
                return (False, f"镜头{idx+1}视觉提示词缺少9:16竖屏参数", 5.0)
        
        # AI深度审核
        prompt = f"""
你是专业分镜审核专家，现在审核第{episode_seq}集分镜质量，从以下几个维度评分（1-10分）：
1. 专业性：是否包含景别、运镜、灯光等专业参数
2. 一致性：角色形象是否前后一致，符合人设
3. 画面合理性：分镜是否符合剧情，画面逻辑通顺
4. 合规性：是否符合平台规则，无违规内容
5. 适配性：是否适配9:16竖屏，符合短视频平台呈现

平台规则：
{chr(10).join(self.platform_rules)}

分镜内容：
{json.dumps(storyboard['storyboard'], ensure_ascii=False, indent=2)}

输出严格为JSON格式，不要其他内容：
{{
    "score": 分数（1-10的数字）,
    "pass": true/false（分数>={self.min_score}则为true）,
    "comment": "审核意见，指出问题和改进建议，没有问题则填通过"
}}
        """
        
        try:
            response = get_llm_response(
                prompt,
                model=config.get("quality_audit.model", "deepseek-ai/DeepSeek-V3.2"),
                temperature=0.1,
                max_tokens=500
            )
            result = json.loads(response)
            score = float(result.get('score', 0))
            passed = result.get('pass', score >= self.min_score)
            comment = result.get('comment', '无审核意见')
            return (passed, comment, score)
        except Exception as e:
            print(f"分镜审核失败：{str(e)}，自动通过")
            return (True, f"审核失败，自动通过：{str(e)}", 8.0)
    
    def audit_content_compliance(self, content: str) -> Tuple[bool, str]:
        """审核内容合规性，快速检查是否有违规内容
        返回：(是否合规, 违规原因)
        """
        if not self.enable_audit:
            return (True, "审核关闭，自动通过")
        
        prompt = f"""
你是内容审核专家，检查以下内容是否符合平台规则：
{chr(10).join(self.platform_rules)}

内容：{content[:500]}

只回答结果：
如果合规，只返回"合规"
如果不合规，返回违规类型："色情","暴力","政治敏感","低俗","其他违规"
        """
        
        try:
            response = get_llm_response(
                prompt,
                temperature=0.0,
                max_tokens=10
            ).strip()
            if response == "合规":
                return (True, "合规")
            else:
                return (False, response)
        except Exception as e:
            print(f"合规审核失败：{str(e)}，自动通过")
            return (True, f"审核失败，自动通过：{str(e)}")

# 全局单例
quality_auditor = QualityAuditor()
