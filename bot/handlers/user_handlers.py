# Default imports
import structlog

# File imports
from bot import keyboards
from bot.database.database import db
from bot.states import AnonymousMessage

# Aiogram imports
from aiogram import Router, Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router()
logger = structlog.get_logger()


@router.message(Command('start', 'restart'))
async def cmd_start(
    message: types.Message,
    command: CommandObject,
    state: FSMContext,
    bot: Bot) -> None:

    try:
        
        bot_info = await bot.get_me()
        user = message.from_user
        res = await db.get_user(user.id)
        
        
        if not res:
            await db.add_user(user.id, user.full_name, user.username)
            
            
        if command.args:
            target = command.args
            
            
            if not target.isdigit():
                await message.reply(
                    text='<b>❌ Ссылка повреждена, ID получателя должен быть числом...</b>',
                    parse_mode='HTML'
                )
                return
            
            
            target_user = await db.get_user(target)
            
            
            if not target_user:
                await message.reply(
                    text='<b>❌ Пользователь не найден. Возможно он еще не зарегистрирован в боте.</b>',
                    parse_mode='HTML'
                )
                return
            
            
            await state.update_data(target_user_id = target)
            await state.set_state(AnonymousMessage.waiting_for_message)
            
            await message.answer(
                text='🚀 Здесь можно отправить <b>анонимное сообщение</b> человеку, который опубликовал эту ссылку\n\n'
                    '🖊 <b>Напишите сюда всё, что хотите ему передать,</b> и через несколько секунд он получит ваше сообщение, но не будет знать от кого\n\n'
                    '<b>Отправить можно пока что только текст...</b>',
                parse_mode='HTML'
            )
            return
        
        
        markup = await keyboards.get_share_keyboard(message, bot)
        await message.answer(
            text=f'<b>Начните получать анонимные вопросы прямо сейчас!</b>\n\n👉 t.me/{bot_info.username}?start={user.id}\n\n<b>Разместите эту ссылку</b> ☝️ в описании своего профиля Telegram, TikTok, Instagram (stories), <b>чтобы вам могли написать</b> 💬',
            parse_mode='HTML',
            reply_markup=markup
        )
        
        
    except Exception as e:
        logger.info(f'ERROR: {e}')


@router.message(AnonymousMessage.waiting_for_message, F.text)
async def handle_anonymous_message(
    message: types.Message,
    state: FSMContext,
    bot: Bot
    ) -> None:
    
    
    builder = InlineKeyboardBuilder()
    builder.button(
    text='💬 Ответить анонимно',
    callback_data=f'reply_{message.from_user.id}'
        )
    reply_kb = builder.as_markup()
    
    
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    
    
    if not target_user_id:
        await message.answer(
            text='<b>❌ Ошибка, не указан получатель.</b>',
            parse_mode='HTML'
        )
        await state.clear()
        return
    
    
    try:
        
        await bot.send_message(
            chat_id=target_user_id,
            text=f'📰 <b>Вам пришло анонимное сообщение:</b>\n\n{message.text}',
            parse_mode='HTML',
            reply_markup=reply_kb
        )
        
        await message.answer('✅ <b>Ваше сообщение было успешно отправлено!</b>', 'HTML')
        logger.info(f'USER: {message.from_user.id} SEND: {message.text} TO: {target_user_id}')


    except Exception as e:
        await message.answer(
            text = '<b>❌ Произошла ошибка! Попробуйте позже...</b>',
            parse_mode='HTML'   
        )
        return logger.info(f'ERROR: {e}')
    
    await state.clear()


@router.callback_query(F.data.startswith('reply_'))
async def handle_reply_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    sender_id = callback.data.split('_')[1]
    
    if not sender_id:
        await callback.answer('❌ Некорректный ID отправителя...')
        return
    
    await state.update_data(target_user_id=sender_id)
    await state.set_state(AnonymousMessage.waiting_for_reply)
    
    await callback.message.answer(
        text='🚀 Здесь можно отправить <b>анонимное сообщение</b> человеку, который опубликовал эту ссылку\n\n'
            '🖊 <b>Напишите сюда всё, что хотите ему передать,</b> и через несколько секунд он получит ваше сообщение, но не будет знать от кого\n\n'
            '<b>Отправить можно пока что только текст...</b>',
        parse_mode='HTML'
    )
    await callback.answer()


@router.message(AnonymousMessage.waiting_for_reply, F.text)
async def handle_reply_message(
    message: types.Message,
    state: FSMContext,
    bot: Bot
) -> None:
    
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    
    if not target_user_id:
        await message.answer('<b>❌ Ошибка! Не указан отправитель.</b>')
        return
    
    try:
        await bot.send_message(
            chat_id=int(target_user_id),
            text=f'<b>📰 Вам ответили анонимно:</b>\n\n{message.text}',
            parse_mode='HTML'
        )
        
        await message.answer(
            text = '✅ <b>Ваш ответ был отправлен...</b>', 
            parse_mode='HTML'
        )
        logger.info(f'USER: {message.from_user.id} REPLY TO: {target_user_id} TEXT: {message.text}')
        
        
    except Exception as e:
        await message.answer(
            text = '❌ <b>Произошла ошибка, попробуйте позже...</b>',
            parse_mode='HTML'
        )
        return logger.info(f'ERROR: {e}')
    
    await state.clear()