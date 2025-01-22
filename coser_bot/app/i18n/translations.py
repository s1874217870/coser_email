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
        'welcome': '欢迎使用Coser展馆社区机器人！\n\n您可以使用以下命令：\n/verify - 邮箱验证\n/checkin - 每日签到\n/points - 查看积分\n/help - 帮助信息',
        'email_verify': '请输入您的邮箱地址进行验证',
        'verify_processing': '正在处理您的请求，请稍候...',
        'verify_code_sent': '验证码已发送至您的邮箱，请查收\n\n请在10分钟内完成验证',
        'verify_success': '✅ 邮箱验证成功！\n\n您现在可以使用所有功能了',
        'verify_failed': '❌ 验证失败\n可能的原因：\n1. 验证码不正确\n2. 验证码已过期\n3. 验证码已使用\n\n请重新获取验证码',
        'points_processing': '正在查询积分信息...',
        'points_info_detail': '📊 积分详情\n\n总积分：{total}\n连续签到：{streak}天\n\n最近记录：\n{history}',
        'points_type_1': '每日签到',
        'points_type_2': '活动奖励',
        'points_type_3': '积分转移',
        'checkin_processing': '正在处理签到请求...',
        'checkin_success_detail': '✅ 签到成功！\n\n获得积分：{points}\n额外奖励：{bonus}\n连续签到：{streak}天\n当前总积分：{total}',
        'checkin_already_detail': '❗ 今日已签到\n\n连续签到：{streak}天\n当前总积分：{total}\n下次可签到时间：{next_time}',
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
        'welcome': 'Welcome to Coser Gallery Community Bot!\n\nAvailable commands:\n/verify - Email verification\n/checkin - Daily check-in\n/points - View points\n/help - Help',
        'email_verify': 'Please enter your email address for verification',
        'verify_processing': 'Processing your request, please wait...',
        'verify_code_sent': 'Verification code has been sent to your email\n\nPlease complete verification within 10 minutes',
        'verify_success': '✅ Email verification successful!\n\nYou can now use all features',
        'verify_failed': '❌ Verification failed\nPossible reasons:\n1. Incorrect code\n2. Code expired\n3. Code already used\n\nPlease request a new code',
        'points_processing': 'Retrieving points information...',
        'points_info_detail': '📊 Points Details\n\nTotal Points: {total}\nStreak: {streak} days\n\nRecent History:\n{history}',
        'points_type_1': 'Daily Check-in',
        'points_type_2': 'Event Reward',
        'points_type_3': 'Points Transfer',
        'checkin_processing': 'Processing check-in request...',
        'checkin_success_detail': '✅ Check-in Successful!\n\nPoints Earned: {points}\nBonus: {bonus}\nStreak: {streak} days\nTotal Points: {total}',
        'checkin_already_detail': '❗ Already Checked In\n\nStreak: {streak} days\nTotal Points: {total}\nNext Check-in: {next_time}',
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
        'welcome': 'Добро пожаловать в бот сообщества Coser Gallery!\n\nДоступные команды:\n/verify - Проверка email\n/checkin - Ежедневная регистрация\n/points - Просмотр баллов\n/help - Помощь',
        'email_verify': 'Пожалуйста, введите ваш email для верификации',
        'verify_processing': 'Обработка вашего запроса, пожалуйста, подождите...',
        'verify_code_sent': 'Код подтверждения отправлен на ваш email\n\nЗавершите проверку в течение 10 минут',
        'verify_success': '✅ Проверка email прошла успешно!\n\nТеперь вы можете использовать все функции',
        'verify_failed': '❌ Проверка не удалась\nВозможные причины:\n1. Неверный код\n2. Код просрочен\n3. Код уже использован\n\nЗапросите новый код',
        'points_processing': 'Получение информации о баллах...',
        'points_info_detail': '📊 Детали Баллов\n\nВсего баллов: {total}\nСерия: {streak} дней\n\nПоследние операции:\n{history}',
        'points_type_1': 'Ежедневная регистрация',
        'points_type_2': 'Награда за событие',
        'points_type_3': 'Перевод баллов',
        'checkin_processing': 'Обработка запроса регистрации...',
        'checkin_success_detail': '✅ Регистрация успешна!\n\nПолучено баллов: {points}\nБонус: {bonus}\nСерия: {streak} дней\nВсего баллов: {total}',
        'checkin_already_detail': '❗ Уже зарегистрированы\n\nСерия: {streak} дней\nВсего баллов: {total}\nСледующая регистрация: {next_time}',
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
