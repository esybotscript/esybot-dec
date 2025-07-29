#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ESYBOT-DEC: Декларативный интерпретатор Telegram ботов
Конфигурационный подход к созданию ботов
"""

import asyncio
import sys
import os
import re
import random
import datetime
import json
import math
import time
import yaml
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

@dataclass
class BotConfig:
    """Конфигурация бота"""
    token: str
    name: str = "ESYBOT-DEC"
    description: str = ""
    version: str = "1.0.0"

@dataclass
class Variable:
    """Переменная бота"""
    name: str
    value: Any
    type: str = "auto"
    description: str = ""

@dataclass
class Button:
    """Кнопка клавиатуры"""
    text: str
    action: str = ""
    url: str = ""
    new_row: bool = False
    callback_data: str = ""

@dataclass
class Keyboard:
    """Клавиатура"""
    name: str
    type: str  # "inline" или "reply"
    buttons: List[Button] = field(default_factory=list)
    resize: bool = True

@dataclass
class Effect:
    """Эффект (действие)"""
    type: str  # "send", "reply", "edit", "increment", etc.
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Handler:
    """Обработчик событий"""
    name: str
    trigger: str  # "start", "message", "callback", etc.
    condition: str = ""
    effects: List[Effect] = field(default_factory=list)
    python_code: str = ""

@dataclass
class BotDeclaration:
    """Полная декларация бота"""
    config: BotConfig
    variables: List[Variable] = field(default_factory=list)
    keyboards: List[Keyboard] = field(default_factory=list)
    handlers: List[Handler] = field(default_factory=list)

class ESYBOTDeclarativeInterpreter:
    """Декларативный интерпретатор ESYBOT"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug = debug_mode
        self.declaration: Optional[BotDeclaration] = None
        self.variables: Dict[str, Any] = {}
        self.keyboards: Dict[str, Any] = {}
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        
    def debug_print(self, message: str) -> None:
        if self.debug:
            print(message)
            
    def load_declaration(self, config_path: str) -> bool:
        """Загрузка декларативной конфигурации"""
        try:
            config_file = Path(config_path)
            
            if config_file.suffix.lower() == '.yaml' or config_file.suffix.lower() == '.yml':
                return self._load_yaml_config(config_path)
            elif config_file.suffix.lower() == '.json':
                return self._load_json_config(config_path)
            elif config_file.suffix.lower() == '.esi':
                return self._load_legacy_esi_config(config_path)
            else:
                print(f"❌ Неподдерживаемый формат файла: {config_file.suffix}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигурации: {e}")
            return False
    
    def _load_yaml_config(self, config_path: str) -> bool:
        """Загрузка YAML конфигурации"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            print(f"📝 Загрузка YAML конфигурации: {config_path}")
            
            # Создаем BotConfig
            bot_config = BotConfig(
                token=config_data['config']['token'],
                name=config_data['config'].get('name', 'ESYBOT-DEC'),
                description=config_data['config'].get('description', ''),
                version=config_data['config'].get('version', '1.0.0')
            )
            
            # Создаем переменные
            variables = []
            for var_data in config_data.get('variables', []):
                variables.append(Variable(
                    name=var_data['name'],
                    value=var_data['value'],
                    type=var_data.get('type', 'auto'),
                    description=var_data.get('description', '')
                ))
                self.variables[var_data['name']] = var_data['value']
            
            # Создаем клавиатуры
            keyboards = []
            for kb_data in config_data.get('keyboards', []):
                buttons = []
                for btn_data in kb_data['buttons']:
                    buttons.append(Button(
                        text=btn_data['text'],
                        action=btn_data.get('action', ''),
                        url=btn_data.get('url', ''),
                        new_row=btn_data.get('new_row', False),
                        callback_data=btn_data.get('callback_data', btn_data.get('action', btn_data['text'].lower().replace(' ', '_')))
                    ))
                
                keyboard = Keyboard(
                    name=kb_data['name'],
                    type=kb_data['type'],
                    buttons=buttons,
                    resize=kb_data.get('resize', True)
                )
                keyboards.append(keyboard)
                self.keyboards[keyboard.name] = self._create_keyboard_markup(keyboard)
            
            # Создаем обработчики
            handlers = []
            for handler_data in config_data.get('handlers', []):
                effects = []
                for effect_data in handler_data.get('effects', []):
                    if isinstance(effect_data, dict):
                        effect_type = list(effect_data.keys())[0]
                        effect_params = effect_data[effect_type]
                        if isinstance(effect_params, str):
                            effect_params = {'text': effect_params}
                    else:
                        effect_type = str(effect_data)
                        effect_params = {}
                    
                    effects.append(Effect(type=effect_type, params=effect_params))
                
                handlers.append(Handler(
                    name=handler_data['name'],
                    trigger=handler_data['trigger'],
                    condition=handler_data.get('condition', ''),
                    effects=effects,
                    python_code=handler_data.get('python', '')
                ))
            
            # Создаем полную декларацию
            self.declaration = BotDeclaration(
                config=bot_config,
                variables=variables,
                keyboards=keyboards,
                handlers=handlers
            )
            
            print(f"✅ Декларация загружена:")
            print(f"   🤖 Бот: {bot_config.name} v{bot_config.version}")
            print(f"   📊 Переменных: {len(variables)}")
            print(f"   ⌨️ Клавиатур: {len(keyboards)}")
            print(f"   🎯 Обработчиков: {len(handlers)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка парсинга YAML: {e}")
            return False
    
    def _load_json_config(self, config_path: str) -> bool:
        """Загрузка JSON конфигурации"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            print(f"📝 Загрузка JSON конфигурации: {config_path}")
            # Аналогичная логика как для YAML
            return True
            
        except Exception as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            return False
    
    def _load_legacy_esi_config(self, config_path: str) -> bool:
        """Загрузка legacy ESI конфигурации"""
        print(f"📝 Конвертация legacy ESI в декларативный формат...")
        # Здесь можно добавить конвертер из старого формата
        return False
    
    def _create_keyboard_markup(self, keyboard: Keyboard) -> Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]:
        """Создание разметки клавиатуры"""
        if keyboard.type == "inline":
            builder = InlineKeyboardBuilder()
            for button in keyboard.buttons:
                if button.url:
                    builder.button(text=button.text, url=button.url)
                else:
                    builder.button(text=button.text, callback_data=button.callback_data)
                if button.new_row:
                    builder.row()
            return builder.as_markup()
        else:
            builder = ReplyKeyboardBuilder()
            for button in keyboard.buttons:
                builder.button(text=button.text)
                if button.new_row:
                    builder.row()
            return builder.as_markup(resize_keyboard=keyboard.resize)
    
    async def _execute_effects(self, effects: List[Effect], context: Dict[str, Any]) -> None:
        """Выполнение эффектов"""
        for effect in effects:
            try:
                await self._execute_effect(effect, context)
            except Exception as e:
                print(f"❌ Ошибка выполнения эффекта {effect.type}: {e}")
    
    async def _execute_effect(self, effect: Effect, context: Dict[str, Any]) -> None:
        """Выполнение одного эффекта"""
        effect_type = effect.type
        params = effect.params
        
        if effect_type == "send":
            text = self._replace_variables(params.get('text', ''), context)
            keyboard_name = params.get('keyboard')
            parse_mode = params.get('parse_mode')
            
            reply_markup = None
            if keyboard_name and keyboard_name in self.keyboards:
                reply_markup = self.keyboards[keyboard_name]
            
            await self.bot.send_message(
                chat_id=context['chat_id'],
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            
        elif effect_type == "reply":
            text = self._replace_variables(params.get('text', ''), context)
            update = context.get('update')
            if update:
                await update.reply(text)
                
        elif effect_type == "edit":
            text = self._replace_variables(params.get('text', ''), context)
            keyboard_name = params.get('keyboard')
            parse_mode = params.get('parse_mode')
            
            reply_markup = None
            if keyboard_name and keyboard_name in self.keyboards:
                reply_markup = self.keyboards[keyboard_name]
            
            update = context.get('update')
            if update and isinstance(update, CallbackQuery):
                await update.message.edit_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
                
        elif effect_type == "answer_callback":
            text = self._replace_variables(params.get('text', ''), context)
            show_alert = params.get('alert', False)
            
            update = context.get('update')
            if update and isinstance(update, CallbackQuery):
                await update.answer(text=text, show_alert=show_alert)
                
        elif effect_type == "increment":
            var_name = params if isinstance(params, str) else params.get('variable')
            amount = params.get('amount', 1) if isinstance(params, dict) else 1
            if var_name in self.variables:
                self.variables[var_name] += amount
                
        elif effect_type == "decrement":
            var_name = params if isinstance(params, str) else params.get('variable')
            amount = params.get('amount', 1) if isinstance(params, dict) else 1
            if var_name in self.variables:
                self.variables[var_name] -= amount
                
        elif effect_type == "set":
            var_name = params.get('variable')
            value = params.get('value')
            if isinstance(value, str):
                value = self._replace_variables(value, context)
            self.variables[var_name] = value
    
    def _replace_variables(self, text: str, context: Dict[str, Any]) -> str:
        """Замена переменных в тексте"""
        # Замена переменных бота
        for var_name, var_value in self.variables.items():
            text = text.replace(f'${var_name}', str(var_value))
        
        # Замена системных переменных
        text = text.replace('$user_id', str(context.get('user_id', 0)))
        text = text.replace('$chat_id', str(context.get('chat_id', 0)))
        text = text.replace('$first_name', str(context.get('first_name', '')))
        text = text.replace('$username', str(context.get('username', '')))
        text = text.replace('$text', str(context.get('text', '')))
        text = text.replace('$data', str(context.get('data', '')))
        
        return text
    
    async def _create_handler(self, handler: Handler) -> None:
        """Создание обработчика из декларации"""
        async def handler_func(update: Union[Message, CallbackQuery], state: FSMContext = None):
            try:
                # Создаем контекст
                context = {
                    'update': update,
                    'user_id': 0,
                    'first_name': '',
                    'username': '',
                    'text': '',
                    'data': '',
                    'chat_id': 0,
                }
                
                if isinstance(update, CallbackQuery):
                    context.update({
                        'user_id': update.from_user.id,
                        'first_name': update.from_user.first_name or '',
                        'username': f"@{update.from_user.username}" if update.from_user.username else '',
                        'chat_id': update.message.chat.id if update.message else update.from_user.id,
                        'text': update.data or '',
                        'data': update.data or '',
                    })
                    print(f"🔥 CALLBACK: {handler.name} от пользователя {context['user_id']}")
                    
                elif isinstance(update, Message):
                    context.update({
                        'user_id': update.from_user.id if update.from_user else 0,
                        'first_name': update.from_user.first_name or '' if update.from_user else '',
                        'username': f"@{update.from_user.username}" if update.from_user and update.from_user.username else '',
                        'chat_id': update.chat.id,
                        'text': update.text or '',
                        'data': '',
                    })
                    print(f"🔥 MESSAGE: {handler.name} от пользователя {context['user_id']}")
                
                # Проверяем условие (если есть)
                if handler.condition:
                    # Простая проверка условий
                    pass
                
                # Выполняем Python код (если есть)
                if handler.python_code:
                    await self._execute_python_code(handler.python_code, context)
                
                # Выполняем эффекты
                await self._execute_effects(handler.effects, context)
                
            except Exception as e:
                print(f"❌ Ошибка в обработчике {handler.name}: {e}")
        
        # Регистрируем обработчик
        trigger = handler.trigger.lower()
        
        if trigger == "start" or trigger == "/start":
            self.dp.message.register(handler_func, Command(commands=["start"]))
        elif trigger.startswith("callback:"):
            callback_data = trigger[9:]  # Убираем "callback:"
            self.dp.callback_query.register(handler_func, F.data == callback_data)
        elif trigger.startswith("command:"):
            command = trigger[8:]  # Убираем "command:"
            self.dp.message.register(handler_func, Command(commands=[command]))
        elif trigger == "message":
            self.dp.message.register(handler_func, F.text)
        elif trigger == "photo":
            self.dp.message.register(handler_func, F.photo)
        elif trigger == "document":
            self.dp.message.register(handler_func, F.document)
        elif trigger == "voice":
            self.dp.message.register(handler_func, F.voice)
        elif trigger == "sticker":
            self.dp.message.register(handler_func, F.sticker)
        else:
            # Предполагаем, что это callback_data
            self.dp.callback_query.register(handler_func, F.data == trigger)
    
    async def _execute_python_code(self, code: str, context: Dict[str, Any]) -> None:
        """Выполнение Python кода"""
        try:
            local_vars = {
                **context,
                **self.variables,
                'bot': self.bot,
                'random': random,
                'datetime': datetime,
                'json': json,
                'math': math,
                'time': time,
            }
            
            exec(code, {'__builtins__': __builtins__}, local_vars)
            
            # Обновляем переменные
            for var_name in self.variables.keys():
                if var_name in local_vars:
                    self.variables[var_name] = local_vars[var_name]
                    
        except Exception as e:
            print(f"❌ Ошибка выполнения Python кода: {e}")
    
    async def run_bot(self) -> None:
        """Запуск бота"""
        if not self.declaration:
            print("❌ Декларация не загружена!")
            return
        
        # Создаем бота
        self.bot = Bot(self.declaration.config.token)
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Регистрируем обработчики
        for handler in self.declaration.handlers:
            await self._create_handler(handler)
        
        print(f"🚀 {self.declaration.config.name} v{self.declaration.config.version} запущен!")
        print("=" * 60)
        print(f"📋 Декларативный подход: эффекты описаны как конфигурация")
        print(f"🔗 Обработчиков сообщений: {len(self.dp.message.handlers)}")
        print(f"🔗 Обработчиков callback: {len(self.dp.callback_query.handlers)}")
        print(f"⌨️ Клавиатур: {len(self.keyboards)}")
        print(f"📊 Переменных: {len(self.variables)}")
        
        try:
            await self.dp.start_polling(self.bot, skip_updates=True)
        except KeyboardInterrupt:
            print("\n⏹️ Бот остановлен")
        finally:
            await self.bot.session.close()

def main():
    """Главная функция"""
    print("📋 ESYBOT-DEC: Декларативный интерпретатор")
    print("=" * 60)
    
    debug_mode = '--debug' in sys.argv
    if debug_mode:
        sys.argv.remove('--debug')
    
    if len(sys.argv) < 2:
        print("📚 Использование: python esybot_dec.py <config.yaml> [--debug]")
        print("🔧 Поддерживаемые форматы: .yaml, .yml, .json")
        print("\n📋 ДЕКЛАРАТИВНЫЙ ПОДХОД:")
        print("   • Конфигурация вместо кода")
        print("   • Эффекты как описание желаемого состояния")
        print("   • YAML/JSON конфигурация")
        print("   • Переиспользуемые компоненты")
        return
    
    interpreter = ESYBOTDeclarativeInterpreter(debug_mode=debug_mode)
    
    try:
        if not interpreter.load_declaration(sys.argv[1]):
            return
        
        asyncio.run(interpreter.run_bot())
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
