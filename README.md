# 🎯 ESYBOT-DEC: Декларативный фреймворк для Telegram ботов

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**ESYBOT-DEC** - это революционный подход к созданию Telegram ботов через декларативное описание их поведения. Вместо написания императивного кода, вы описываете **что должно происходить**, а не **как это делать**.

## 📋 **Особенности**

### ✅ **Декларативный подход**
- Конфигурация вместо кода
- YAML/JSON описание поведения бота
- Переиспользуемые компоненты
- Простота модификации и тестирования

### ✅ **Мощные возможности**
- Полная совместимость с Telegram Bot API
- Inline и Reply клавиатуры
- Система переменных и состояний
- Python вставки для сложной логики
- Условная логика и эффекты

### ✅ **Простота использования**
- Минимальный порог входа
- Автоматическая валидация конфигурации
- Подробные сообщения об ошибках
- Горячая перезагрузка конфигурации

## 🚀 **Быстрый старт**

### 1. Установка зависимостей

```
pip install aiogram pyyaml
```

### 2. Создание конфигурации

Создайте файл `bot.yaml`:

```
config:
  token: "YOUR_BOT_TOKEN"
  name: "Мой декларативный бот"
  description: "Пример ESYBOT-DEC бота"
  version: "1.0.0"

variables:
  - name: "user_count"
    value: 0
    type: "integer"
    description: "Количество пользователей"
  
  - name: "welcome_message"
    value: "🎯 Добро пожаловать в ESYBOT-DEC!"
    type: "string"
    description: "Приветственное сообщение"

keyboards:
  - name: "main_menu"
    type: "inline"
    buttons:
      - text: "📊 Статистика"
        callback_data: "stats"
      - text: "🎲 Случайное число"
        callback_data: "random"
        new_row: true
      - text: "🌐 Сайт"
        url: "https://example.com"

  - name: "reply_keyboard"
    type: "reply"
    resize: true
    buttons:
      - text: "🏠 Главная"
      - text: "❓ Помощь"
        new_row: true

handlers:
  - name: "start_handler"
    trigger: "/start"
    effects:
      - increment: "user_count"
      - send:
          text: $welcome_message
          keyboard: "main_menu"
          parse_mode: "HTML"

  - name: "stats_handler"
    trigger: "stats"
    effects:
      - edit:
          text: "📊 **Статистика бота**\n\n👥 Пользователей: $user_count"
          parse_mode: "Markdown"
      - answer_callback:
          text: "Статистика обновлена!"

  - name: "random_handler"
    trigger: "random"
    python: |
      import random
      random_number = random.randint(1, 100)
    effects:
      - set:
          variable: "last_random"
          value: "$random_number"
      - edit:
          text: "🎲 Ваше случайное число: **$random_number**"
          parse_mode: "Markdown"
      - answer_callback:
          text: "Число сгенерировано!"

  - name: "help_handler"
    trigger: "command:help"
    effects:
      - send:
          text: |
            🆘 **Справка по боту**
            
            Доступные команды:
            -  /start - Запуск бота
            -  /help - Эта справка
            
            Используйте кнопки для взаимодействия!
          parse_mode: "Markdown"
          keyboard: "reply_keyboard"

  - name: "photo_handler" 
    trigger: "photo"
    effects:
      - reply:
          text: "📷 Красивое фото! Спасибо за отправку."

  - name: "message_handler"
    trigger: "message"
    effects:
      - reply:
          text: "📨 Получено сообщение: '$text'"
```

### 3. Запуск бота

```
python esybot_dec.py bot.yaml
```

## 📋 **Документация**

### **Структура конфигурации**

#### **Config (конфигурация бота)**
```
config:
  token: "string"        # Токен бота (обязательно)
  name: "string"         # Название бота
  description: "string"  # Описание
  version: "string"      # Версия
```

#### **Variables (переменные)**
```
variables:
  - name: "variable_name"    # Имя переменной
    value: any_value         # Значение
    type: "auto|string|integer|float|boolean"
    description: "string"    # Описание
```

#### **Keyboards (клавиатуры)**
```
keyboards:
  - name: "keyboard_name"    # Уникальное имя
    type: "inline|reply"     # Тип клавиатуры
    resize: boolean          # Авторазмер (только для reply)
    buttons:
      - text: "Button Text"        # Текст кнопки
        callback_data: "string"    # Callback данные (для inline)
        url: "string"              # URL (для inline)
        new_row: boolean           # Новая строка
```

#### **Handlers (обработчики)**
```
handlers:
  - name: "handler_name"     # Уникальное имя
    trigger: "string"        # Триггер события
    condition: "string"      # Условие (опционально)
    python: "string"         # Python код (опционально)
    effects:                 # Список эффектов
      - effect_type: params
```

### **Доступные триггеры**
- `"/start"` - команда /start
- `"command:help"` - команда /help  
- `"message"` - любое текстовое сообщение
- `"callback_data"` - нажатие на inline кнопку
- `"photo"` - отправка фото
- `"document"` - отправка документа
- `"voice"` - голосовое сообщение
- `"sticker"` - стикер

### **Доступные эффекты**

#### **Отправка сообщений**
```
- send:
    text: "Текст сообщения"
    keyboard: "keyboard_name"
    parse_mode: "HTML|Markdown"

- reply:
    text: "Ответ на сообщение"

- edit:
    text: "Новый текст"
    keyboard: "keyboard_name"
    parse_mode: "HTML|Markdown"
```

#### **Callback ответы**
```
- answer_callback:
    text: "Текст уведомления"
    alert: true|false
```

#### **Работа с переменными**
```
- increment: "variable_name"
- decrement: "variable_name"
- set:
    variable: "variable_name" 
    value: "new_value"
```

### **Системные переменные**
- `$user_id` - ID пользователя
- `$chat_id` - ID чата  
- `$first_name` - Имя пользователя
- `$username` - Username пользователя
- `$text` - Текст сообщения
- `$data` - Callback данные

## 🔄 **Сравнение подходов**

### **Императивный (классический)**
```
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_count += 1
    await message.answer(
        welcome_message,
        reply_markup=main_menu_keyboard
    )
```

### **Декларативный (ESYBOT-DEC)**
```
- name: "start_handler"
  trigger: "/start"
  effects:
    - increment: "user_count"
    - send:
        text: $welcome_message
        keyboard: "main_menu"
```

## 🛠 **Расширенные возможности**

### **Python вставки**
Для сложной логики используйте Python блоки:

```
- name: "complex_handler"
  trigger: "complex"
  python: |
    import datetime
    import random
    
    # Вычисления
    current_time = datetime.datetime.now()
    random_value = random.randint(1, 100)
    
    # Условная логика
    if random_value > 50:
        result_message = f"Большое число: {random_value}"
    else:
        result_message = f"Маленькое число: {random_value}"
  effects:
    - send:
        text: "$result_message"
```

### **Условная логика**
```
- name: "conditional_handler"
  trigger: "check"
  condition: "$user_count > 10"
  effects:
    - send:
        text: "У нас много пользователей!"
```

### **Множественные форматы**
ESYBOT-DEC поддерживает:
- **YAML** (.yaml, .yml) - рекомендуемый
- **JSON** (.json) - для интеграции
- **Legacy ESI** (.esi) - совместимость

## 🎯 **Преимущества декларативного подхода**

### ✅ **Простота**
- Нет сложного кода
- Понятная структура
- Легко читается и модифицируется

### ✅ **Надежность**
- Автоматическая валидация
- Меньше ошибок
- Предсказуемое поведение

### ✅ **Гибкость**
- Горячая перезагрузка
- A/B тестирование
- Легкое развертывание

### ✅ **Переиспользование**
- Общие компоненты
- Шаблоны конфигураций
- Модульная архитектура

## 📊 **Мониторинг и отладка**

### **Режим отладки**
```
python esybot_dec.py bot.yaml --debug
```

### **Логирование**
- Подробные логи выполнения
- Трассировка эффектов
- Мониторинг переменных

## 🔧 **Инструменты разработки**

### **Валидация конфигурации**
```
python esybot_dec.py bot.yaml --validate
```

### **Генерация документации**
```
python esybot_dec.py bot.yaml --docs
```

### **Конвертация из ESI**
```
python esybot_dec.py legacy_bot.esi --convert
```

## 🤝 **Вклад в проект**

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📄 **Лицензия**

MIT License - подробности в файле `LICENSE`

## 🆘 **Поддержка**

- 📧 Email: support@esybot-dec.dev
- 💬 Telegram: @esybot_support
- 📚 Wiki: [github.com/esybot/esybot-dec/wiki](https://github.com/esybot/esybot-dec/wiki)

---

**ESYBOT-DEC** - будущее создания Telegram ботов уже здесь! 🚀
```

## 🎯 **Примеры конфигураций**

### **Пример 1: Простой бот-опросник**
```yaml
# survey_bot.yaml
config:
  token: "YOUR_TOKEN"
  name: "Survey Bot"

handlers:
  - name: "start"
    trigger: "/start"
    effects:
      - send:
          text: "Привет! Как дела? 😊"
          keyboard: "mood_keyboard"

keyboards:
  - name: "mood_keyboard"
    type: "inline"
    buttons:
      - text: "😊 Отлично"
        callback_data: "good"
      - text: "😐 Нормально" 
        callback_data: "ok"
      - text: "😞 Плохо"
        callback_data: "bad"
```

### **Пример 2: Бот с состояниями**
```yaml
# stateful_bot.yaml
config:
  token: "YOUR_TOKEN"
  name: "Stateful Bot"

variables:
  - name: "user_state"
    value: "idle"
  - name: "user_name"
    value: ""

handlers:
  - name: "ask_name"
    trigger: "/register"
    effects:
      - set:
          variable: "user_state"
          value: "asking_name"
      - send:
          text: "Как вас зовут?"

  - name: "save_name"
    trigger: "message"
    condition: "$user_state == 'asking_name'"
    effects:
      - set:
          variable: "user_name"
          value: "$text"
      - set:
          variable: "user_state" 
          value: "idle"
      - send:
          text: "Приятно познакомиться, $user_name!"
```
