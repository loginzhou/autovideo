import json
import re
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config_center import config
from .logger import log

class ContentAuditor:
    """内容自动审核系统"""
    
    def __init__(self):
        self.enable_audit = config.get("content_auditor.enable_audit", True)
        self.quality_threshold = config.get("content_auditor.quality_threshold", 0.7)
        self.consistency_threshold = config.get("content_auditor.consistency_threshold", 0.8)
        self.compliance_threshold = config.get("content_auditor.compliance_threshold", 0.9)
        self.banned_words = self._load_banned_words()
    
    def _load_banned_words(self):
        """加载违禁词列表"""
        banned_words = []
        banned_words_path = config.get("content_auditor.banned_words_path", "config/banned_words.txt")
        if os.path.exists(banned_words_path):
            try:
                with open(banned_words_path, 'r', encoding='utf-8') as f:
                    banned_words = [line.strip() for line in f if line.strip()]
            except Exception as e:
                log.error(f"加载违禁词列表失败：{str(e)}")
        return banned_words
    
    def audit_screenplay(self, screenplay):
        """审核剧本质量"""
        if not self.enable_audit:
            return {"passed": True, "score": 1.0, "reasons": []}
        
        score = 1.0
        reasons = []
        
        # 检查剧本结构
        if 'beats' not in screenplay or not screenplay['beats']:
            score -= 0.2
            reasons.append("剧本结构不完整，缺少beats")
        else:
            # 检查beats数量
            beat_count = len(screenplay['beats'])
            if beat_count < 3:
                score -= 0.1
                reasons.append(f"beats数量不足，当前{beat_count}个，建议至少3个")
            
            # 检查beat类型分布
            beat_types = [beat['beat_type'] for beat in screenplay['beats']]
            required_types = ['hook', 'setup', 'escalation', 'cliffhanger']
            missing_types = [t for t in required_types if t not in beat_types]
            if missing_types:
                score -= 0.1 * len(missing_types)
                reasons.append(f"缺少必要的beat类型：{', '.join(missing_types)}")
        
        # 检查内容质量
        for beat in screenplay.get('beats', []):
            content = beat.get('content', '')
            if len(content) < 50:
                score -= 0.05
                reasons.append(f"beat内容过短：{content[:20]}...")
            if len(content) > 500:
                score -= 0.05
                reasons.append(f"beat内容过长：{content[:20]}...")
        
        # 检查违禁词
        content_text = ' '.join([beat.get('content', '') for beat in screenplay.get('beats', [])])
        for word in self.banned_words:
            if word in content_text:
                score -= 0.2
                reasons.append(f"包含违禁词：{word}")
        
        # 检查语法和标点
        if not re.search(r'[.!?。！？]', content_text):
            score -= 0.05
            reasons.append("缺少标点符号")
        
        score = max(0, score)
        passed = score >= self.quality_threshold
        
        return {
            "passed": passed,
            "score": score,
            "reasons": reasons
        }
    
    def audit_storyboard(self, storyboard):
        """审核分镜质量"""
        if not self.enable_audit:
            return {"passed": True, "score": 1.0, "reasons": []}
        
        score = 1.0
        reasons = []
        
        # 检查分镜结构
        if 'storyboard' not in storyboard or not storyboard['storyboard']:
            score -= 0.2
            reasons.append("分镜结构不完整，缺少storyboard")
        else:
            # 检查镜头数量
            shot_count = len(storyboard['storyboard'])
            if shot_count < 3:
                score -= 0.1
                reasons.append(f"镜头数量不足，当前{shot_count}个，建议至少3个")
            
            # 检查每个镜头的完整性
            for i, shot in enumerate(storyboard['storyboard']):
                if 'shot_id' not in shot:
                    score -= 0.05
                    reasons.append(f"镜头{i+1}缺少shot_id")
                if 'visual_prompt' not in shot:
                    score -= 0.1
                    reasons.append(f"镜头{i+1}缺少visual_prompt")
                if 'audio_prompt' not in shot:
                    score -= 0.05
                    reasons.append(f"镜头{i+1}缺少audio_prompt")
                if 'shot_type' not in shot:
                    score -= 0.05
                    reasons.append(f"镜头{i+1}缺少shot_type")
                if 'camera_angle' not in shot:
                    score -= 0.05
                    reasons.append(f"镜头{i+1}缺少camera_angle")
                if 'lighting_setup' not in shot:
                    score -= 0.05
                    reasons.append(f"镜头{i+1}缺少lighting_setup")
                if 'transition_effect' not in shot:
                    score -= 0.05
                    reasons.append(f"镜头{i+1}缺少transition_effect")
                if 'location' not in shot:
                    score -= 0.05
                    reasons.append(f"镜头{i+1}缺少location")
        
        # 检查视觉提示词质量
        for shot in storyboard.get('storyboard', []):
            visual_prompt = shot.get('visual_prompt', '')
            if len(visual_prompt) < 50:
                score -= 0.05
                reasons.append(f"视觉提示词过短：{visual_prompt[:20]}...")
            if len(visual_prompt) > 500:
                score -= 0.05
                reasons.append(f"视觉提示词过长：{visual_prompt[:20]}...")
            if "--ar 9:16" not in visual_prompt:
                score -= 0.05
                reasons.append("视觉提示词缺少横竖屏参数")
        
        score = max(0, score)
        passed = score >= self.quality_threshold
        
        return {
            "passed": passed,
            "score": score,
            "reasons": reasons
        }
    
    def audit_audio_design(self, audio_design):
        """审核音频设计质量"""
        if not self.enable_audit:
            return {"passed": True, "score": 1.0, "reasons": []}
        
        score = 1.0
        reasons = []
        
        # 检查音频设计结构
        if not audio_design:
            score -= 0.2
            reasons.append("音频设计为空")
        else:
            # 检查每个音频设计的完整性
            for i, audio in enumerate(audio_design):
                if 'shot_id' not in audio:
                    score -= 0.05
                    reasons.append(f"音频设计{i+1}缺少shot_id")
                if 'audio_prompt' not in audio:
                    score -= 0.1
                    reasons.append(f"音频设计{i+1}缺少audio_prompt")
                else:
                    audio_prompt = audio['audio_prompt']
                    required_fields = ['Spatial', 'EQ', 'Ambience', 'SFX', 'Music', 'Dialogue']
                    for field in required_fields:
                        if field not in audio_prompt:
                            score -= 0.05
                            reasons.append(f"音频设计{i+1}缺少{field}")
        
        score = max(0, score)
        passed = score >= self.quality_threshold
        
        return {
            "passed": passed,
            "score": score,
            "reasons": reasons
        }
    
    def audit_consistency(self, current_content, previous_content):
        """审核内容一致性"""
        if not self.enable_audit:
            return {"passed": True, "score": 1.0, "reasons": []}
        
        score = 1.0
        reasons = []
        
        # 检查内容一致性
        if not previous_content:
            return {"passed": True, "score": 1.0, "reasons": []}
        
        # 检查角色一致性
        current_characters = self._extract_characters(current_content)
        previous_characters = self._extract_characters(previous_content)
        
        missing_characters = [c for c in previous_characters if c not in current_characters]
        if missing_characters:
            score -= 0.1 * len(missing_characters)
            reasons.append(f"缺少之前出现的角色：{', '.join(missing_characters)}")
        
        # 检查场景一致性
        current_scenes = self._extract_scenes(current_content)
        previous_scenes = self._extract_scenes(previous_content)
        
        missing_scenes = [s for s in previous_scenes if s not in current_scenes]
        if missing_scenes:
            score -= 0.1 * len(missing_scenes)
            reasons.append(f"缺少之前出现的场景：{', '.join(missing_scenes)}")
        
        score = max(0, score)
        passed = score >= self.consistency_threshold
        
        return {
            "passed": passed,
            "score": score,
            "reasons": reasons
        }
    
    def audit_compliance(self, content):
        """审核内容合规性"""
        if not self.enable_audit:
            return {"passed": True, "score": 1.0, "reasons": []}
        
        score = 1.0
        reasons = []
        
        # 检查违禁词
        content_text = str(content)
        for word in self.banned_words:
            if word in content_text:
                score -= 0.2
                reasons.append(f"包含违禁词：{word}")
        
        # 检查敏感内容
        sensitive_patterns = [
            r'暴力', r'色情', r'赌博', r'毒品', r'政治',
            r'恐怖主义', r'极端主义', r'种族歧视', r'宗教歧视'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, content_text):
                score -= 0.1
                reasons.append(f"可能包含敏感内容：{pattern}")
        
        score = max(0, score)
        passed = score >= self.compliance_threshold
        
        return {
            "passed": passed,
            "score": score,
            "reasons": reasons
        }
    
    def _extract_characters(self, content):
        """从内容中提取角色"""
        characters = []
        # 简单的角色提取逻辑，实际应用中可能需要更复杂的NLP处理
        if isinstance(content, dict):
            if 'beats' in content:
                for beat in content['beats']:
                    if 'content' in beat:
                        # 这里可以添加更复杂的角色提取逻辑
                        pass
        return characters
    
    def _extract_scenes(self, content):
        """从内容中提取场景"""
        scenes = []
        # 简单的场景提取逻辑，实际应用中可能需要更复杂的NLP处理
        if isinstance(content, dict):
            if 'beats' in content:
                for beat in content['beats']:
                    if 'content' in beat:
                        # 这里可以添加更复杂的场景提取逻辑
                        pass
        return scenes

# 导出内容审核器实例
content_auditor = ContentAuditor()
