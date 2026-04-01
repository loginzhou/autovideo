"""
多语言出海翻译模块
自动将剧本、字幕、配音文本翻译成多国语言，适配全球平台
支持批量翻译、缓存、专业术语保留
"""
import os
import json
import hashlib
from typing import List, Dict, Any
from config_center import config
from components.utils.llm_client import get_llm_response

# 支持的语言列表
SUPPORTED_LANGUAGES = {
    "en": "英语（English）",
    "es": "西班牙语（Español）",
    "fr": "法语（Français）",
    "de": "德语（Deutsch）",
    "pt": "葡萄牙语（Português）",
    "ru": "俄语（Русский）",
    "ar": "阿拉伯语（العربية）",
    "ja": "日语（日本語）",
    "ko": "韩语（한국어）",
    "vi": "越南语（Tiếng Việt）",
    "th": "泰语（ภาษาไทย）",
    "id": "印尼语（Bahasa Indonesia）"
}

class MultiLanguageTranslator:
    def __init__(self):
        self.enable_translation = config.get("multi_language.enable_translation", False)
        self.target_languages = config.get("multi_language.target_languages", ["en"])
        self.cache_enabled = config.get("multi_language.cache_enabled", True)
        self.cache = {}
        
        # 加载缓存
        if self.cache_enabled:
            cache_path = self._get_cache_path()
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        self.cache = json.load(f)
                except:
                    self.cache = {}
    
    def _get_cache_path(self) -> str:
        """获取缓存路径，项目级隔离"""
        from project_manager import project_manager
        return project_manager.get_cache_path("translation_cache.json")
    
    def _save_cache(self):
        """保存缓存"""
        if not self.cache_enabled:
            return
        cache_path = self._get_cache_path()
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = "zh") -> str:
        """翻译单段文本"""
        if not self.enable_translation or target_lang == source_lang:
            return text
        
        # 缓存命中直接返回
        cache_key = hashlib.md5(f"{text}_{target_lang}_{source_lang}".encode('utf-8')).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 调用大模型翻译，确保地道自然，符合短视频平台口语化风格
        prompt = f"""
你是专业本地化翻译专家，擅长将中文短剧台词翻译成{SUPPORTED_LANGUAGES.get(target_lang, target_lang)}，适配短视频平台风格。
翻译要求：
1. 口语化、地道自然，符合目标语言国家日常说话习惯，不要生硬直译
2. 长度和原文差不多，适合短视频配音和字幕显示
3. 保留网络流行语、爽点、情绪，符合短剧语境
4. 不要添加任何解释、注释，只返回翻译结果

原文：{text}
翻译结果：
        """
        
        try:
            result = get_llm_response(
                prompt,
                model=config.get("multi_language.model", "deepseek-ai/DeepSeek-V3.2"),
                temperature=0.3,
                max_tokens=200
            ).strip()
            
            # 保存缓存
            self.cache[cache_key] = result
            self._save_cache()
            
            return result
        except Exception as e:
            print(f"翻译失败：{str(e)}，返回原文")
            return text
    
    def translate_screenplay(self, screenplay: Dict[str, Any], source_lang: str = "zh") -> Dict[str, Any]:
        """翻译整个剧本，返回多语言版本"""
        if not self.enable_translation:
            return {source_lang: screenplay}
        
        translated = {source_lang: screenplay}
        for lang in self.target_languages:
            if lang == source_lang:
                continue
            
            translated_beats = []
            for beat in screenplay['beats']:
                translated_beat = beat.copy()
                translated_beat['content'] = self.translate_text(beat['content'], lang, source_lang)
                translated_beats.append(translated_beat)
            
            translated_screenplay = screenplay.copy()
            translated_screenplay['beats'] = translated_beats
            translated_screenplay['core_plot'] = self.translate_text(screenplay['core_plot'], lang, source_lang)
            translated[lang] = translated_screenplay
        
        return translated
    
    def translate_storyboard(self, storyboard: Dict[str, Any], source_lang: str = "zh") -> Dict[str, Any]:
        """翻译整个分镜的字幕和台词，返回多语言版本"""
        if not self.enable_translation:
            return {source_lang: storyboard}
        
        translated = {source_lang: storyboard}
        for lang in self.target_languages:
            if lang == source_lang:
                continue
            
            translated_shots = []
            for shot in storyboard['storyboard']:
                translated_shot = shot.copy()
                # 翻译台词
                if 'Dialogue' in translated_shot['audio_prompt'] and translated_shot['audio_prompt']['Dialogue']:
                    translated_shot['audio_prompt'][f'Dialogue_{lang}'] = self.translate_text(
                        translated_shot['audio_prompt']['Dialogue'], lang, source_lang
                    )
                translated_shots.append(translated_shot)
            
            translated_storyboard = storyboard.copy()
            translated_storyboard['storyboard'] = translated_shots
            translated[lang] = translated_storyboard
        
        return translated
    
    def generate_subtitle_file(self, storyboard: Dict[str, Any], output_dir: str, source_lang: str = "zh"):
        """生成多语言字幕文件（SRT格式）"""
        if not self.enable_translation:
            langs = [source_lang]
        else:
            langs = [source_lang] + self.target_languages
        
        for lang in langs:
            srt_content = ""
            for idx, shot in enumerate(storyboard['storyboard']):
                shot_id = shot['shot_id']
                start_time = idx * 15 * 1000  # 假设每个镜头15秒
                end_time = (idx + 1) * 15 * 1000
                
                # 时间格式：00:00:00,000 --> 00:00:15,000
                start_str = f"{start_time//3600000:02d}:{(start_time%3600000)//60000:02d}:{(start_time%60000)//1000:02d},{start_time%1000:03d}"
                end_str = f"{end_time//3600000:02d}:{(end_time%3600000)//60000:02d}:{(end_time%60000)//1000:02d},{end_time%1000:03d}"
                
                if lang == source_lang:
                    dialogue = shot['audio_prompt'].get('Dialogue', '')
                else:
                    dialogue = shot['audio_prompt'].get(f'Dialogue_{lang}', '')
                
                srt_content += f"{idx+1}\n"
                srt_content += f"{start_str} --> {end_str}\n"
                srt_content += f"{dialogue}\n\n"
            
            # 保存字幕文件
            os.makedirs(output_dir, exist_ok=True)
            subtitle_path = os.path.join(output_dir, f"subtitle_{lang}.srt")
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            print(f"生成{lang}字幕文件：{subtitle_path}")

# 全局单例
translator = MultiLanguageTranslator()
