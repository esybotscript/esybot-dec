#!/usr/bin/env python3
# esybot_unified.py - Единый интерпретатор для SIMPLE и YAML форматов

import asyncio
import sys
import os
import datetime
import re
from typing import Dict, Any, Union
from pathlib import Path

# Импорты для Telegram
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage

# Опциональный импорт YAML
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("⚠️  YAML не установлен. Установите: pip install pyyaml")

class UnifiedBotInterpreter:
    """Универсальный интерпретатор для SIMPLE и YAML форматов"""
    
    def __init__(self):
        self.config_format = None  # 'simple' или 'yaml'
        self.bot_config = {}
        self.variables = {}
        self.keyboards_config = {}
        self.handlers_config = {}
        self.python_globals = {}
        
        # Готовые клавиатуры
        self.keyboards = {}
        
    def detect_format(self, file_path: str) -> str:
        """Автоматическое определение формата файла"""
        extension = Path(file_path).suffix.lower()
        
        if extension in ['.simple', '.ini']:
            return 'simple'
        elif extension in ['.yaml', '.yml']:
            if not YAML_AVAILABLE:
                raise Exception("YAML формат недоступен. Установите: pip install pyyaml")
            return 'yaml'
        else:
            # Пытаемся определить по содержимому
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Если есть секции [NAME], то это SIMPLE
                if re.search(r'^\[.+\]', content, re.MULTILINE):
                    return 'simple'
                # Если есть YAML структуры, то это YAML
                elif re.search(r'^[a-zA-Z_][a-zA-Z0-9_]*:', content, re.MULTILINE):
                    if YAML_AVAILABLE:
                        return 'yaml'
                    else:
                        raise Exception("Файл похож на YAML, но библиотека недоступна")
                else:
                    raise Exception("Не удалось определить формат файла")
                    
            except Exception as e:
                raise Exception(f"Ошибка определения формата: {e}")
    
    def load_config(self, file_path: str) -> bool:
        """Загрузка конфигурации в любом формате"""
        try:
            self.config_format = self.detect_format(file_path)
            print(f"📝 Обнаружен формат: {self.config_format.upper()}")
            
            if self.config_format == 'simple':
                return self._load_simple_config(file_path)
            elif self.config_format == 'yaml':
                return self._load_yaml_config(file_path)
            else:
                print(f"❌ Неподдерживаемый формат: {self.config_format}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигурации: {e}")
            return False
    
    def _load_simple_config(self, file_path: str) -> bool:
        """Загрузка SIMPLE конфигурации"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим Python блоки
        content = self._parse_simple_python_blocks(content)
        
        lines = content.split('\n')
        current_section = None
        raw_config = {}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                if current_section not in raw_config:
                    raw_config[current_section] = {}
            elif '=' in line and current_section:
                key, value = line.split('=', 1)
                raw_config[current_section][key.strip()] = value.strip()
        
        # Конвертируем в унифицированный формат
        self._convert_simple_to_unified(raw_config)
        return True
    
    def _load_yaml_config(self, file_path: str) -> bool:
        """Загрузка YAML конфигурации"""
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
        
        # Конвертируем в унифицированный формат
        self._convert_yaml_to_unified(raw_config)
        return True
    
    def _parse_simple_python_blocks(self, content: str) -> str:
        """Парсинг Python блоков в SIMPLE формате"""
        def replace_python_block(match):
            python_code = match.group(1)
            lines = python_code.strip().split('\n')
            cleaned_lines = [line.strip() for line in lines]
            return f"python = {repr('\\n'.join(cleaned_lines))}"
        
        pattern = r'python\s*\{([^}]*)\}'
        content = re.sub(pattern, replace_python_block, content, flags=re.DOTALL)
        return content
    
    def _convert_simple_to_unified(self, raw_config: dict):
        """Конвертация SIMPLE конфигурации в унифицированный формат"""
        # Конфигурация бота
        if 'BOT' in raw_config:
            self.bot_config = {
                'token': raw_config['BOT'].get('token', ''),
                'name': raw_config['BOT'].get('name', 'ESYBOT Bot'),
                'debug': raw_config['BOT'].get('debug', 'false').lower() == 'true'
            }
        
        # Переменные
        if 'VARS' in raw_config:
            for key, value in raw_config['VARS'].items():
                self.variables[key] = self._parse_value(value)
        
        # Обработчики (включая START)
        for section_name, section_data in raw_config.items():
            if section_name not in ['BOT', 'VARS']:
                self.handlers_config[section_name] = self._convert_simple_handler(section_data)
                
                # Извлекаем клавиатуры из обработчиков
                keyboard_config = self._extract_keyboard_from_simple_handler(section_data)
                if keyboard_config['buttons']:
                    self.keyboards_config[f"{section_name}_keyboard"] = keyboard_config
    
    def _convert_yaml_to_unified(self, raw_config: dict):
        """Конвертация YAML конфигурации в унифицированный формат"""
        # Конфигурация бота
        if 'config' in raw_config:
            self.bot_config = raw_config['config']
        
        # Переменные
        if 'variables' in raw_config:
            for var_config in raw_config['variables']:
                self.variables[var_config['name']] = var_config.get('value', 0)
        
        # Клавиатуры
        if 'keyboards' in raw_config:
            for kb_config in raw_config['keyboards']:
                self.keyboards_config[kb_config['name']] = kb_config
        
        # Обработчики
        if 'handlers' in raw_config:
            for handler_config in raw_config['handlers']:
                self.handlers_config[handler_config['name']] = handler_config
    
    def _convert_simple_handler(self, section_data: dict) -> dict:
        """Конвертация SIMPLE обработчика в унифицированный формат"""
        handler = {
            'effects': [],
            'python': section_data.get('python', ''),
            'condition': section_data.get('if', ''),
            'else_effects': []
        }
        
        # Основные эффекты
        if 'text' in section_data:
            handler['effects'].append({
                'send': {
                    'text': section_data['text'],
                    'keyboard': f"{list(self.handlers_config.keys())[-1] if self.handlers_config else 'default'}_keyboard"
                }
            })
        
        if 'inc' in section_data:
            handler['effects'].append({'increment': section_data['inc']})
        
        if 'dec' in section_data:
            handler['effects'].append({'decrement': section_data['dec']})
        
        if 'set' in section_data:
            parts = section_data['set'].split('=', 1)
            if len(parts) == 2:
                handler['effects'].append({
                    'set': {
                        'variable': parts[0].strip(),
                        'value': parts[1].strip()
                    }
                })
        
        # Else эффекты
        if 'else_text' in section_data:
            handler['else_effects'].append({
                'send': {'text': section_data['else_text']}
            })
        
        return handler
    
    def _extract_keyboard_from_simple_handler(self, section_data: dict) -> dict:
        """Извлечение клавиатуры из SIMPLE обработчика"""
        keyboard = {
            'type': 'inline',
            'buttons': []
        }
        
        # Ищем кнопки button1, button2, etc.
        for key, value in section_data.items():
            if key.startswith('button') and '|' in value:
                parts = value.split('|', 1)
                if len(parts) == 2:
                    text, callback_data = parts[0].strip(), parts[1].strip()
                    keyboard['buttons'].append({
                        'text': text,
                        'callback_data': callback_data
                    })
        
        # Ищем else кнопки
        for key, value in section_data.items():
            if key.startswith('else_button') and '|' in value:
                parts = value.split('|', 1)
                if len(parts) == 2:
                    text, callback_data = parts[0].strip(), parts[1].strip()
                    keyboard['buttons'].append({
                        'text': text,
                        'callback_data': callback_data
                    })
        
        return keyboard
    
    def _parse_value(self, value: str) -> Any:
        """Парсинг значений"""
        value = value.strip()
        
        # Python код в кавычках
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1].replace('\\n', '\n')
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1].replace('\\n', '\n')
        
        # Булевы значения
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        
        # Числа
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        return value
    
    def build_keyboards(self):
        """Построение всех клавиатур"""
        for kb_name, kb_config in self.keyboards_config.items():
            if kb_config.get('type') == 'inline':
                builder = InlineKeyboardBuilder()
                for button in kb_config.get('buttons', []):
                    if 'url' in button:
                        builder.button(text=button['text'], url=button['url'])
                    else:
                        builder.button(text=button['text'], callback_data=button.get('callback_data', 'unknown'))
                self.keyboards[kb_name] = builder.as_markup()
            
            elif kb_config.get('type') == 'reply':
                builder = ReplyKeyboardBuilder()
                for button in kb_config.get('buttons', []):
                    builder.button(text=button['text'])
                self.keyboards[kb_name] = builder.as_markup(
                    resize_keyboard=kb_config.get('resize', True),
                    one_time_keyboard=kb_config.get('one_time', False)
                )
    
    def replace_variables(self, text: str, context: dict = {}) -> str:
        """Замена переменных в тексте"""
        if not text:
            return text
        
        # Системные переменные
        now = datetime.datetime.now()
        system_vars = {
            'user_id': context.get('user_id', 0),
            'chat_id': context.get('chat_id', 0),
            'first_name': context.get('first_name', ''),
            'username': context.get('username', ''),
            'text': context.get('text', ''),
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Все переменные
        all_vars = {**self.variables, **self.python_globals, **system_vars}
        
        for var_name, var_value in all_vars.items():
            text = text.replace(f'${{{var_name}}}', str(var_value))
            text = text.replace(f'${var_name}', str(var_value))
        
        return text
    
    def execute_python(self, code: str, context: dict = {}):
        """Выполнение Python кода"""
        if not code:
            return
        
        try:
            local_vars = {**self.variables, **context, **self.python_globals}
            
            if self.bot_config.get('debug'):
                print(f"🐍 Выполняется Python код:")
                for i, line in enumerate(code.split('\n'), 1):
                    if line.strip():
                        print(f"   {i}: {line}")
            
            exec(code, {}, local_vars)
            
            # Сохраняем переменные
            for key, value in local_vars.items():
                if key in self.variables:
                    self.variables[key] = value
                elif not key.startswith('_') and key not in context:
                    self.python_globals[key] = value
                    if self.bot_config.get('debug'):
                        print(f"   ✅ Переменная: {key} = {value}")
        
        except Exception as e:
            print(f"❌ Python ошибка: {e}")
    
    def process_effects(self, effects: list, context: dict = {}) -> dict:
        """Обработка списка эффектов"""
        result = {'text': '', 'keyboard': None, 'reply': 'OK'}
        
        for effect in effects:
            if 'send' in effect:
                send_config = effect['send']
                result['text'] = self.replace_variables(send_config.get('text', ''), context)
                
                keyboard_name = send_config.get('keyboard')
                if keyboard_name and keyboard_name in self.keyboards:
                    result['keyboard'] = self.keyboards[keyboard_name]
            
            elif 'edit' in effect:
                edit_config = effect['edit']
                result['text'] = self.replace_variables(edit_config.get('text', ''), context)
                
                keyboard_name = edit_config.get('keyboard')
                if keyboard_name and keyboard_name in self.keyboards:
                    result['keyboard'] = self.keyboards[keyboard_name]
            
            elif 'increment' in effect:
                var_name = effect['increment']
                self.variables[var_name] = self.variables.get(var_name, 0) + 1
                if self.bot_config.get('debug'):
                    print(f"📈 {var_name} = {self.variables[var_name]}")
            
            elif 'decrement' in effect:
                var_name = effect['decrement']
                self.variables[var_name] = self.variables.get(var_name, 0) - 1
                if self.bot_config.get('debug'):
                    print(f"📉 {var_name} = {self.variables[var_name]}")
            
            elif 'set' in effect:
                set_config = effect['set']
                var_name = set_config['variable']
                var_value = self.replace_variables(str(set_config['value']), context)
                self.variables[var_name] = self._parse_value(var_value)
                if self.bot_config.get('debug'):
                    print(f"📝 {var_name} = {self.variables[var_name]}")
        
        return result
    
    def check_condition(self, condition: str, context: dict = {}) -> bool:
        """Проверка условий"""
        if not condition:
            return True
        
        condition = self.replace_variables(condition, context)
        
        try:
            result = eval(condition, {}, {})
            if self.bot_config.get('debug'):
                print(f"🔍 Условие '{condition}' = {result}")
            return result
        except Exception as e:
            if self.bot_config.get('debug'):
                print(f"❌ Ошибка условия: {e}")
            return False
    
    def get_context(self, update) -> dict:
        """Получение контекста из обновления"""
        if hasattr(update, 'from_user') and update.from_user:
            return {
                'user_id': update.from_user.id,
                'chat_id': update.chat.id if hasattr(update, 'chat') and update.chat else update.from_user.id,
                'first_name': update.from_user.first_name or '',
                'username': f"@{update.from_user.username}" if update.from_user.username else '',
                'text': getattr(update, 'text', '') or ''
            }
        return {}
    
    async def run(self):
        """Запуск бота"""
        if not self.bot_config.get('token'):
            print("❌ Токен бота не указан")
            return
        
        # Построение клавиатур
        self.build_keyboards()
        
        bot = Bot(self.bot_config['token'])
        dp = Dispatcher(storage=MemoryStorage())
        
        # Обработчик /start
        @dp.message(Command("start"))
        async def start_handler(message: Message):
            context = self.get_context(message)
            
            # Ищем обработчик START или start
            handler_config = self.handlers_config.get('START') or self.handlers_config.get('start')
            if not handler_config:
                await message.answer("❌ Обработчик /start не найден")
                return
            
            # Выполняем Python если есть
            if handler_config.get('python'):
                self.execute_python(handler_config['python'], context)
            
            # Проверяем условие
            if handler_config.get('condition'):
                if not self.check_condition(handler_config['condition'], context):
                    if handler_config.get('else_effects'):
                        result = self.process_effects(handler_config['else_effects'], context)
                        if result['text']:
                            await message.answer(result['text'], reply_markup=result['keyboard'])
                    return
            
            # Выполняем основные эффекты
            if handler_config.get('effects'):
                result = self.process_effects(handler_config['effects'], context)
                if result['text']:
                    await message.answer(result['text'], reply_markup=result['keyboard'])
        
        # Обработчики callback кнопок
        for handler_name, handler_config in self.handlers_config.items():
            if handler_name not in ['START', 'start', 'MESSAGE', 'PHOTO', 'DOCUMENT', 'VOICE']:
                @dp.callback_query(F.data == handler_name)
                async def callback_handler(query: CallbackQuery, config=handler_config):
                    context = self.get_context(query)
                    
                    # Python код
                    if config.get('python'):
                        self.execute_python(config['python'], context)
                    
                    # Условие
                    if config.get('condition'):
                        if not self.check_condition(config['condition'], context):
                            if config.get('else_effects'):
                                result = self.process_effects(config['else_effects'], context)
                                if result['text']:
                                    await query.message.edit_text(result['text'], reply_markup=result['keyboard'])
                                await query.answer(result['reply'])
                            return
                    
                    # Основные эффекты
                    if config.get('effects'):
                        result = self.process_effects(config['effects'], context)
                        if result['text']:
                            await query.message.edit_text(result['text'], reply_markup=result['keyboard'])
                        await query.answer(result['reply'])
        
        # Обработка медиа (если есть соответствующие обработчики)
        if 'PHOTO' in self.handlers_config:
            @dp.message(F.content_type == ContentType.PHOTO)
            async def photo_handler(message: Message):
                context = self.get_context(message)
                handler_config = self.handlers_config['PHOTO']
                
                if handler_config.get('python'):
                    self.execute_python(handler_config['python'], context)
                
                if handler_config.get('effects'):
                    result = self.process_effects(handler_config['effects'], context)
                    if result['text']:
                        await message.answer(result['text'], reply_markup=result['keyboard'])
        
        # Обработка текстовых сообщений
        if 'MESSAGE' in self.handlers_config:
            @dp.message(F.text)
            async def message_handler(message: Message):
                if message.text.startswith('/'):
                    return
                
                context = self.get_context(message)
                context['text'] = message.text
                handler_config = self.handlers_config['MESSAGE']
                
                if handler_config.get('python'):
                    self.execute_python(handler_config['python'], context)
                
                if handler_config.get('effects'):
                    result = self.process_effects(handler_config['effects'], context)
                    if result['text']:
                        await message.answer(result['text'], reply_markup=result['keyboard'])
        
        print(f"🚀 {self.bot_config.get('name', 'ESYBOT')} запущен!")
        print(f"📊 Формат: {self.config_format.upper()}")
        print(f"📊 Переменных: {len(self.variables)}")
        print(f"⌨️ Клавиатур: {len(self.keyboards)}")
        print(f"🎯 Обработчиков: {len(self.handlers_config)}")
        
        await dp.start_polling(bot)

def main():
    if len(sys.argv) < 2:
        print("Использование: python esybot_unified.py <config_file>")
        print("\nПоддерживаемые форматы:")
        print("  • .simple - ESYBOT-SIMPLE формат")
        print("  • .yaml/.yml - ESYBOT-DEC формат")
        return
    
    config_file = sys.argv[1]
    
    if not os.path.exists(config_file):
        print(f"❌ Файл {config_file} не найден")
        return
    
    # Создаем и запускаем универсальный интерпретатор
    interpreter = UnifiedBotInterpreter()
    
    if interpreter.load_config(config_file):
        asyncio.run(interpreter.run())
    else:
        print("❌ Не удалось загрузить конфигурацию")

if __name__ == "__main__":
    main()
