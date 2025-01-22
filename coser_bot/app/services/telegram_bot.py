"""
Telegram Bot服务模块
处理Telegram Bot的核心功能和命令
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from app.core.config import get_settings
from app.core.redis import redis_client, RateLimit
from app.services.blacklist import BlacklistService
from app.services.user import UserService
from app.services.verification import VerificationService
from app.services.points import PointsService
from app.db.database import SessionLocal
from app.i18n.translations import Language, get_text
import random
import string
import re

settings = get_settings()

class TelegramBotService:
    """Telegram Bot服务类"""
    
    def __init__(self):
        """初始化Bot服务"""
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.admin_id = settings.TELEGRAM_ADMIN_ID
        self.log_group_id = settings.TELEGRAM_LOG_GROUP_ID
        self.user_languages = {}
        
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        处理按钮回调查询
        
        参数:
            update: Telegram更新对象
            context: 回调上下文
        """
        query = update.callback_query
        await query.answer()  # 响应回调查询
        data = query.data
        user_id = update.effective_user.id
        
        # 处理语言切换
        if data == "lang_zh":
            await self.set_language_zh(update, context)
        elif data == "lang_en":
            await self.set_language_en(update, context)
        elif data == "lang_ru":
            await self.set_language_ru(update, context)
        # 处理验证流程
        elif data == "verify_start":
            await self.verify_command(update, context)
        elif data == "verify_cancel":
            lang = self.get_user_language(user_id)
            # 清除验证状态
            redis_client.delete(f"verify_status:{user_id}")
            redis_client.delete(f"verify_code:{user_id}")
            # 发送取消消息
            await query.message.reply_text(get_text(lang, "buttons")["cancel"])
            
    async def setup(self):
        """设置Bot应用程序"""
        self.application = Application.builder().token(self.token).build()
        
        # 注册命令处理器
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("verify", self.verify_command))
        self.application.add_handler(CommandHandler("checkin", self.checkin_command))
        self.application.add_handler(CommandHandler("points", self.points_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # 注册语言切换命令
        self.application.add_handler(CommandHandler("lang_zh", self.set_language_zh))
        self.application.add_handler(CommandHandler("lang_en", self.set_language_en))
        self.application.add_handler(CommandHandler("lang_ru", self.set_language_ru))
        
        # 注册按钮回调处理器
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # 注册消息处理器
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
    def get_user_language(self, user_id: int) -> Language:
        """
        获取用户语言设置
        如果缓存中没有，从Redis获取，默认中文
        """
        if user_id not in self.user_languages:
            lang_code = redis_client.get(f"user_lang:{user_id}")
            if lang_code:
                self.user_languages[user_id] = Language(lang_code)
            else:
                self.user_languages[user_id] = Language.ZH
        return self.user_languages[user_id]
        
    async def set_language_zh(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """设置中文"""
        user_id = update.effective_user.id
        self.user_languages[user_id] = Language.ZH
        redis_client.set(f"user_lang:{user_id}", Language.ZH.value)
        await update.message.reply_text(get_text(Language.ZH, "lang_changed"))
        # 发送更新后的帮助信息
        await self.help_command(update, context)
        
    async def set_language_en(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """设置英文"""
        user_id = update.effective_user.id
        self.user_languages[user_id] = Language.EN
        redis_client.set(f"user_lang:{user_id}", Language.EN.value)
        await update.message.reply_text(get_text(Language.EN, "lang_changed"))
        # 发送更新后的帮助信息
        await self.help_command(update, context)
        
    async def set_language_ru(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """设置俄语"""
        user_id = update.effective_user.id
        self.user_languages[user_id] = Language.RU
        redis_client.set(f"user_lang:{user_id}", Language.RU.value)
        await update.message.reply_text(get_text(Language.RU, "lang_changed"))
        # 发送更新后的帮助信息
        await self.help_command(update, context)
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/start命令"""
        user_id = update.effective_user.id
        lang = self.get_user_language(user_id)
        welcome_text = get_text(lang, "welcome")
        # 发送欢迎消息和语言选择按钮
        await update.message.reply_text(
            welcome_text,
            reply_markup=self.get_language_keyboard()
        )
        # 同时显示主菜单按钮
        await update.message.reply_text(
            get_text(lang, "buttons")["help"],
            reply_markup=self.get_main_menu_keyboard(lang)
        )
        
    async def verify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/verify命令"""
        user_id = update.effective_user.id
        
        # 检查IP限流
        ip = update.message.from_user.id  # 使用用户ID作为限流标识
        lang = self.get_user_language(user_id)
        if not await VerificationService.check_retry_limit(f"ip:{ip}"):
            await update.message.reply_text(get_text(lang, "rate_limit"))
            return
            
        # 检查用户是否已存在
        db = SessionLocal()
        try:
            user = await UserService.get_user_by_telegram_id(db, str(user_id))
            if not user:
                user = await UserService.create_user(db, str(user_id))
                
            # 检查用户邮箱是否在黑名单中
            if user.email and await BlacklistService.is_email_blacklisted(user.email):
                await update.message.reply_text(get_text(lang, "blacklist"))
                return
                
            # 生成验证码
            verification_code = ''.join(random.choices(string.digits, k=6))
            
            # 存储验证码（10分钟有效期）
            redis_client.setex(f"verify_code:user:{user_id}", 600, verification_code)
            
            # 获取用户群组成员信息
            member_info = await UserService.get_chat_member_info(
                context.bot,
                self.log_group_id,
                user_id
            )
            
            # 发送验证码和说明
            instruction_text = get_text(
                lang,
                "verify_start",
                code=verification_code,
                email=settings.SMTP_USERNAME
            )
            await update.message.reply_text(
                instruction_text,
                reply_markup=self.get_verify_keyboard(lang)
            )
            
            # 存储用户验证状态
            redis_client.setex(
                f"verify_status:user:{user_id}",
                600,  # 10分钟有效期
                "pending"  # 等待用户发送验证码到邮箱
            )
            
            # 记录到日志群组
            log_text = (
                f"用户 {user_id} 请求了验证码\n"
                f"群组成员状态: {member_info.status if member_info else '未知'}"
            )
            await context.bot.send_message(chat_id=self.log_group_id, text=log_text)
            
        finally:
            db.close()
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理普通消息"""
        user_id = update.effective_user.id
        message_text = update.message.text
        lang = self.get_user_language(user_id)
        
        # 检查用户是否在验证流程中
        verify_status = redis_client.get(f"verify_status:user:{user_id}")
        if verify_status == "pending":
            # 检查消息是否为验证码格式（6位数字）
            if re.match(r'^\d{6}$', message_text):
                # 验证验证码
                if await VerificationService.verify_code(f"user:{user_id}", message_text, lang):
                    # 更新用户状态
                    db = SessionLocal()
                    try:
                        user = await UserService.get_user_by_telegram_id(db, str(user_id))
                        if user:
                            # 清除验证状态
                            redis_client.delete(f"verify_status:user:{user_id}")
                            redis_client.delete(f"verify_code:user:{user_id}")
                            
                            # 发送成功消息
                            success_message = get_text(lang, "verify_success")
                            await update.message.reply_text(success_message)
                            
                            # 记录到日志
                            log_text = (
                                f"用户 {user_id} 验证成功\n"
                                f"验证码: {message_text}"
                            )
                            await context.bot.send_message(
                                chat_id=self.log_group_id,
                                text=log_text
                            )
                    finally:
                        db.close()
                else:
                    # 发送失败消息
                    fail_message = get_text(lang, "verify_failed")
                    await update.message.reply_text(fail_message)
                    
                    # 记录失败到日志
                    log_text = (
                        f"用户 {user_id} 验证失败\n"
                        f"尝试的验证码: {message_text}"
                    )
                    await context.bot.send_message(
                        chat_id=self.log_group_id,
                        text=log_text
                    )
        
    async def checkin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/checkin命令"""
        user_id = update.effective_user.id
        lang = self.get_user_language(user_id)
        
        db = SessionLocal()
        try:
            user = await UserService.get_user_by_telegram_id(db, str(user_id))
            if not user:
                user = await UserService.create_user(db, str(user_id))
                
            success, points, message = await PointsService.daily_checkin(db, user.id)
            await update.message.reply_text(
                get_text(lang, "checkin_success" if success else "checkin_already", points=points, bonus=message),
                reply_markup=self.get_main_menu_keyboard(lang)
            )
            
        finally:
            db.close()
            
    async def points_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/points命令"""
        user_id = update.effective_user.id
        lang = self.get_user_language(user_id)
        
        db = SessionLocal()
        try:
            user = await UserService.get_user_by_telegram_id(db, str(user_id))
            if not user:
                user = await UserService.create_user(db, str(user_id))
                
            # 获取连续签到天数
            streak = redis_client.get(f"checkin_streak:{user.id}") or 0
            
            # 获取用户总积分
            total_points = await PointsService.get_user_points(db, user.id)
            
            # 发送积分信息
            await update.message.reply_text(
                get_text(
                    lang,
                    "points_info",
                    total_points=total_points,
                    streak=streak
                ),
                reply_markup=self.get_main_menu_keyboard(lang)
            )
            
        finally:
            db.close()
            
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/help命令"""
        user_id = update.effective_user.id
        lang = self.get_user_language(user_id)
        await update.message.reply_text(
            get_text(lang, "help"),
            reply_markup=self.get_main_menu_keyboard(lang)
        )
            
    async def run(self):
        """运行Bot服务"""
        try:
            await self.setup()
            await self.application.initialize()
            await self.application.start()
            print("Telegram Bot服务已启动")
            await self.application.updater.start_polling()
        except Exception as e:
            print(f"Telegram Bot启动失败: {e}")
            # 不抛出异常，让应用程序继续运行
            pass

    def get_language_keyboard(self) -> InlineKeyboardMarkup:
        """
        生成语言选择键盘
        
        返回:
            InlineKeyboardMarkup: 包含三种语言选项的内联键盘
        """
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("中文", callback_data="lang_zh"),
             InlineKeyboardButton("English", callback_data="lang_en"),
             InlineKeyboardButton("Русский", callback_data="lang_ru")]
        ])
        
    def get_main_menu_keyboard(self, lang: Language) -> ReplyKeyboardMarkup:
        """
        生成主菜单键盘
        
        参数:
            lang: 用户语言设置
            
        返回:
            ReplyKeyboardMarkup: 包含主要功能按钮的持久键盘
        """
        return ReplyKeyboardMarkup([
            [get_text(lang, "buttons")["checkin"], get_text(lang, "buttons")["points"]],
            [get_text(lang, "buttons")["verify"], get_text(lang, "buttons")["help"]]
        ], resize_keyboard=True)
        
    def get_verify_keyboard(self, lang: Language) -> InlineKeyboardMarkup:
        """
        生成验证流程键盘
        
        参数:
            lang: 用户语言设置
            
        返回:
            InlineKeyboardMarkup: 包含验证相关按钮的内联键盘
        """
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(get_text(lang, "buttons")["verify"], callback_data="verify_start")],
            [InlineKeyboardButton(get_text(lang, "buttons")["cancel"], callback_data="verify_cancel")]
        ])

# 创建Bot服务实例
bot_service = TelegramBotService()
