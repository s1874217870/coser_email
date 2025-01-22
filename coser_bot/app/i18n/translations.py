"""
多语言翻译模块
管理多语言文本内容
"""
from enum import Enum

class Language(Enum):
    """支持的语言枚举"""
    ZH = "zh"  # 中文
    EN = "en"  # 英文
    RU = "ru"  # 俄语

# 多语言文本配置
TRANSLATIONS = {
    Language.ZH: {
        "welcome": (
            "欢迎使用Coser展馆社区机器人！\n\n"
            "请使用以下命令：\n"
            "/verify - 开始邮箱验证\n"
            "/checkin - 每日签到\n"
            "/points - 查看积分\n"
            "/help - 帮助信息\n\n"
            "切换语言：\n"
            "/lang_zh - 中文\n"
            "/lang_en - English\n"
            "/lang_ru - Русский"
        ),
        "buttons": {
            "verify": "开始验证",
            "cancel": "取消",
            "checkin": "每日签到",
            "points": "查看积分",
            "help": "帮助",
            "back": "返回",
            "confirm": "确认"
        },
        "email_subject": "Coser展馆社区 - 邮箱验证码",
        "email_body": (
            "您好！\n\n"
            "您的Coser展馆社区邮箱验证码是：{code}\n"
            "验证码有效期为10分钟。\n\n"
            "如果这不是您的操作，请忽略此邮件。\n\n"
            "祝您使用愉快！\n"
            "Coser展馆社区团队"
        ),
        "verify_start": (
            "您的验证码是：{code}\n\n"
            "请将此验证码发送至以下邮箱进行验证：\n"
            "{email}\n\n"
            "验证码有效期为10分钟。"
        ),
        "rate_limit": "您的验证请求过于频繁，请稍后再试。",
        "blacklist": "您的邮箱已被列入黑名单，请联系管理员。",
        "lang_changed": "已切换到中文。",
        "verify_success": "验证成功！您现在可以使用社区功能了。",
        "verify_failed": "验证失败，请检查验证码是否正确。如需重新获取验证码，请使用 /verify 命令。",
        "checkin_success": "签到成功！获得{points}积分{bonus}",
        "checkin_already": "今日已签到，明天再来吧！",
        "checkin_streak_7": "，获得连续7天奖励20积分",
        "checkin_streak_30": "，获得连续30天奖励100积分",
        "points_info": (
            "您的积分信息：\n"
            "当前积分：{total_points}\n"
            "连续签到：{streak}天\n"
            "————————————\n"
            "积分规则：\n"
            "每日签到：10积分\n"
            "连续7天：+20积分\n"
            "连续30天：+100积分\n"
            "活动参与：20-100积分\n"
            "内容发布：5-50积分"
        ),
        "help": (
            "命令说明：\n"
            "/verify - 邮箱验证\n"
            "/checkin - 每日签到\n"
            "/points - 查看积分\n"
            "/lang_zh - 切换到中文\n"
            "/lang_en - Switch to English\n"
            "/lang_ru - Переключить на русский\n"
            "/help - 显示此帮助"
        ),
    },
    Language.EN: {
        "welcome": (
            "Welcome to Coser Gallery Community Bot!\n\n"
            "Available commands:\n"
            "/verify - Start email verification\n"
            "/checkin - Daily check-in\n"
            "/points - View points\n"
            "/help - Help information\n\n"
            "Change language:\n"
            "/lang_zh - 中文\n"
            "/lang_en - English\n"
            "/lang_ru - Русский"
        ),
        "buttons": {
            "verify": "Verify Email",
            "cancel": "Cancel",
            "checkin": "Daily Check-in",
            "points": "View Points",
            "help": "Help",
            "back": "Back",
            "confirm": "Confirm"
        },
        "email_subject": "Coser Gallery Community - Email Verification Code",
        "email_body": (
            "Hello!\n\n"
            "Your Coser Gallery Community verification code is: {code}\n"
            "This code will expire in 10 minutes.\n\n"
            "If you didn't request this code, please ignore this email.\n\n"
            "Best regards,\n"
            "Coser Gallery Community Team"
        ),
        "verify_start": (
            "Your verification code is: {code}\n\n"
            "Please send this code to the following email:\n"
            "{email}\n\n"
            "The code will expire in 10 minutes."
        ),
        "rate_limit": "Too many verification requests. Please try again later.",
        "blacklist": "Your email is blacklisted. Please contact administrator.",
        "lang_changed": "Switched to English.",
        "verify_success": "Verification successful! You can now use community features.",
        "verify_failed": "Verification failed. Please check your code. Use /verify command to get a new code.",
        "checkin_success": "Check-in successful! You got {points} points{bonus}",
        "checkin_already": "You've already checked in today. Come back tomorrow!",
        "checkin_streak_7": ", earned 20 bonus points for 7-day streak",
        "checkin_streak_30": ", earned 100 bonus points for 30-day streak",
        "points_info": (
            "Your Points Information:\n"
            "Current Points: {total_points}\n"
            "Check-in Streak: {streak} days\n"
            "————————————\n"
            "Points Rules:\n"
            "Daily Check-in: 10 points\n"
            "7 Days Streak: +20 points\n"
            "30 Days Streak: +100 points\n"
            "Event Participation: 20-100 points\n"
            "Content Publishing: 5-50 points"
        ),
        "help": (
            "Command Guide:\n"
            "/verify - Email verification\n"
            "/checkin - Daily check-in\n"
            "/points - View points\n"
            "/lang_zh - Switch to Chinese\n"
            "/lang_en - Switch to English\n"
            "/lang_ru - Switch to Russian\n"
            "/help - Show this help"
        ),
    },
    Language.RU: {
        "welcome": (
            "Добро пожаловать в бота сообщества Coser Gallery!\n\n"
            "Доступные команды:\n"
            "/verify - Подтверждение email\n"
            "/checkin - Ежедневная отметка\n"
            "/points - Просмотр баллов\n"
            "/help - Справка\n\n"
            "Изменить язык:\n"
            "/lang_zh - 中文\n"
            "/lang_en - English\n"
            "/lang_ru - Русский"
        ),
        "buttons": {
            "verify": "Подтвердить Email",
            "cancel": "Отмена",
            "checkin": "Отметиться",
            "points": "Баллы",
            "help": "Справка",
            "back": "Назад",
            "confirm": "Подтвердить"
        },
        "email_subject": "Coser Gallery Community - Код подтверждения email",
        "email_body": (
            "Здравствуйте!\n\n"
            "Ваш код подтверждения Coser Gallery Community: {code}\n"
            "Срок действия кода - 10 минут.\n\n"
            "Если вы не запрашивали этот код, проигнорируйте это письмо.\n\n"
            "С уважением,\n"
            "Команда Coser Gallery Community"
        ),
        "verify_start": (
            "Ваш код подтверждения: {code}\n\n"
            "Отправьте этот код на следующий email:\n"
            "{email}\n\n"
            "Срок действия кода - 10 минут."
        ),
        "rate_limit": "Слишком много запросов. Попробуйте позже.",
        "blacklist": "Ваш email в черном списке. Обратитесь к администратору.",
        "lang_changed": "Переключено на русский язык.",
        "verify_success": "Проверка прошла успешно! Теперь вы можете использовать функции сообщества.",
        "verify_failed": "Ошибка проверки. Проверьте код. Используйте команду /verify для получения нового кода.",
        "checkin_success": "Отметка успешна! Вы получили {points} баллов{bonus}",
        "checkin_already": "Вы уже отметились сегодня. Приходите завтра!",
        "checkin_streak_7": ", получено 20 бонусных баллов за 7 дней подряд",
        "checkin_streak_30": ", получено 100 бонусных баллов за 30 дней подряд",
        "points_info": (
            "Информация о баллах:\n"
            "Текущие баллы: {total_points}\n"
            "Серия отметок: {streak} дней\n"
            "————————————\n"
            "Правила начисления:\n"
            "Ежедневная отметка: 10 баллов\n"
            "7 дней подряд: +20 баллов\n"
            "30 дней подряд: +100 баллов\n"
            "Участие в мероприятиях: 20-100 баллов\n"
            "Публикация контента: 5-50 баллов"
        ),
        "help": (
            "Справка по командам:\n"
            "/verify - Подтверждение email\n"
            "/checkin - Ежедневная отметка\n"
            "/points - Просмотр баллов\n"
            "/lang_zh - Переключить на китайский\n"
            "/lang_en - Переключить на английский\n"
            "/lang_ru - Переключить на русский\n"
            "/help - Показать справку"
        ),
    }
}

def get_text(lang: Language, key: str, **kwargs) -> str:
    """
    获取指定语言的文本
    
    参数:
        lang: 语言
        key: 文本键值
        kwargs: 格式化参数
    """
    text = TRANSLATIONS.get(lang, TRANSLATIONS[Language.EN]).get(key, "")
    return text.format(**kwargs) if kwargs else text
