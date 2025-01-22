"""
多语言支持模块
处理多语言翻译
"""
from enum import Enum
from typing import Dict, Any

class Language(str, Enum):
    """支持的语言枚举"""
    ZH = "zh"
    EN = "en"
    RU = "ru"

# 翻译字典
TRANSLATIONS: Dict[str, Dict[str, str | Dict[str, str]]] = {
    'zh': {
        'welcome': '欢迎使用Coser展馆社区机器人！',
        'email_verify': '请输入您的邮箱地址进行验证',
        'verify_code_sent': '验证码已发送至您的邮箱，请查收',
        'verify_success': '邮箱验证成功！',
        'verify_failed': '验证失败，请重试',
        'points_info': '您当前的积分为: {points}，连续签到: {streak}天',
        'checkin_success': '签到成功！获得{points}积分',
        'already_checkin': '今天已经签到过了哦',
        'help': (
            '可用命令列表：\n'
            '/verify - 邮箱验证\n'
            '/checkin - 每日签到\n'
            '/points - 查看积分\n'
            '/help - 显示帮助'
        ),
        'buttons': {
            'verify': '开始验证',
            'cancel': '取消',
            'checkin': '每日签到',
            'points': '我的积分',
            'help': '帮助'
        },
        'lang_changed': '已切换到中文',
        'rate_limit': '请求过于频繁，请稍后再试',
        'blacklist': '您的账号已被限制使用此功能'
    },
    'en': {
        'welcome': 'Welcome to Coser Gallery Community Bot!',
        'email_verify': 'Please enter your email address for verification',
        'verify_code_sent': 'Verification code has been sent to your email',
        'verify_success': 'Email verification successful!',
        'verify_failed': 'Verification failed, please try again',
        'points_info': 'Your current points: {points}, Streak: {streak} days',
        'checkin_success': 'Check-in successful! Earned {points} points',
        'already_checkin': 'You have already checked in today',
        'help': (
            'Available commands:\n'
            '/verify - Email verification\n'
            '/checkin - Daily check-in\n'
            '/points - View points\n'
            '/help - Show help'
        ),
        'buttons': {
            'verify': 'Start Verification',
            'cancel': 'Cancel',
            'checkin': 'Daily Check-in',
            'points': 'My Points',
            'help': 'Help'
        },
        'lang_changed': 'Switched to English',
        'rate_limit': 'Too many requests, please try again later',
        'blacklist': 'Your account is restricted from using this feature'
    },
    'ru': {
        'welcome': 'Добро пожаловать в бот сообщества Coser Gallery!',
        'email_verify': 'Пожалуйста, введите ваш email для верификации',
        'verify_code_sent': 'Код подтверждения отправлен на ваш email',
        'verify_success': 'Проверка email прошла успешно!',
        'verify_failed': 'Проверка не удалась, попробуйте еще раз',
        'points_info': 'Ваши текущие баллы: {points}, Серия: {streak} дней',
        'checkin_success': 'Регистрация успешна! Получено {points} баллов',
        'already_checkin': 'Вы уже зарегистрировались сегодня',
        'help': (
            'Доступные команды:\n'
            '/verify - Проверка email\n'
            '/checkin - Ежедневная регистрация\n'
            '/points - Просмотр баллов\n'
            '/help - Показать помощь'
        ),
        'buttons': {
            'verify': 'Начать проверку',
            'cancel': 'Отмена',
            'checkin': 'Регистрация',
            'points': 'Мои баллы',
            'help': 'Помощь'
        },
        'lang_changed': 'Переключено на русский',
        'rate_limit': 'Слишком много запросов, повторите попытку позже',
        'blacklist': 'Ваша учетная запись ограничена в использовании этой функции'
    }
}

def get_text(lang: Language, key: str, **kwargs: Any) -> str | dict:
    """
    获取指定语言的文本
    
    参数:
        lang: 语言代码
        key: 文本键值
        **kwargs: 格式化参数
        
    返回:
        str | dict: 翻译文本或按钮字典
    """
    if lang not in Language.__members__.values():
        lang = Language.ZH
        
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS[Language.ZH].get(key, key))
    if isinstance(text, dict):
        return text  # 返回按钮字典
    return text.format(**kwargs) if kwargs else str(text)
