"""
多语言支持模块
"""
from typing import Dict, Any

# 支持的语言
SUPPORTED_LANGUAGES = ['zh', 'en', 'ru']

# 翻译字典
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'zh': {
        'welcome': '欢迎使用Coser展馆社区机器人！',
        'email_verify': '请输入您的邮箱地址进行验证',
        'verify_code_sent': '验证码已发送至您的邮箱，请查收',
        'verify_success': '邮箱验证成功！',
        'verify_failed': '验证失败，请重试',
        'points_info': '您当前的积分为: {points}',
        'checkin_success': '签到成功！获得{points}积分',
        'already_checkin': '今天已经签到过了哦',
    },
    'en': {
        'welcome': 'Welcome to Coser Gallery Community Bot!',
        'email_verify': 'Please enter your email address for verification',
        'verify_code_sent': 'Verification code has been sent to your email',
        'verify_success': 'Email verification successful!',
        'verify_failed': 'Verification failed, please try again',
        'points_info': 'Your current points: {points}',
        'checkin_success': 'Check-in successful! Earned {points} points',
        'already_checkin': 'You have already checked in today',
    },
    'ru': {
        'welcome': 'Добро пожаловать в бот сообщества Coser Gallery!',
        'email_verify': 'Пожалуйста, введите ваш email для верификации',
        'verify_code_sent': 'Код подтверждения отправлен на ваш email',
        'verify_success': 'Проверка email прошла успешно!',
        'verify_failed': 'Проверка не удалась, попробуйте еще раз',
        'points_info': 'Ваши текущие баллы: {points}',
        'checkin_success': 'Регистрация успешна! Получено {points} баллов',
        'already_checkin': 'Вы уже зарегистрировались сегодня',
    }
}

def get_text(key: str, lang: str = 'zh', **kwargs: Any) -> str:
    """
    获取指定语言的文本
    
    Args:
        key: 文本键值
        lang: 语言代码
        **kwargs: 格式化参数
    
    Returns:
        str: 翻译后的文本
    """
    if lang not in SUPPORTED_LANGUAGES:
        lang = 'zh'
    
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['zh'].get(key, key))
    return text.format(**kwargs) if kwargs else text
