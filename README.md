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

# 🎯 Преимущества ESYBOT-DEC перед обычной ветвой

## 📋 **Декларативный vs Императивный подход**

### **🔄 Основное отличие:**
- **Обычная ветвь** говорит **"КАК делать"** (последовательность команд)
- **ESYBOT-DEC** говорит **"ЧТО должно быть"** (конфигурация желаемого состояния)

## ✅ **Ключевые преимущества ESYBOT-DEC**

### **1. 📝 Конфигурация вместо кода**

**Обычная ветвь:**
```esybot
menu main_menu {
    button "📊 Статистика" "stats"
    button "🎲 Случайное число" "random" new_row=true
    button "🌐 Сайт" url="https://example.com"
}

on_callback stats {
    edit "📊 Статистика: $user_count пользователей"
    answer_callback "Обновлено!"
}
```

**ESYBOT-DEC:**
```yaml
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

handlers:
  - name: "stats_handler"
    trigger: "stats"
    effects:
      - edit:
          text: "📊 Статистика: $user_count пользователей"
      - answer_callback:
          text: "Обновлено!"
```

### **2. 🔧 Простота модификации**

**Преимущества:**
- **Изменение без перезапуска** - горячая перезагрузка YAML
- **Визуальная структура** - легко увидеть всю логику
- **Меньше ошибок** - валидация схемы конфигурации
- **Быстрое прототипирование** - изменил YAML и готово

### **3. 🔄 Переиспользование компонентов**

**ESYBOT-DEC позволяет:**
```yaml
# Общие клавиатуры для всех ботов
common_keyboards: &common
  - name: "help_menu"
    type: "inline"
    buttons:
      - text: "❓ Помощь"
        callback_data: "help"

# Бот 1 использует общие клавиатуры
bot1:
  keyboards: *common
  
# Бот 2 тоже использует их
bot2:
  keyboards: *common
```

### **4. 📊 A/B тестирование и эксперименты**

**Легко менять варианты:**
```yaml
# Версия A
handlers:
  - name: "welcome"
    trigger: "/start"
    effects:
      - send:
          text: "Привет! 👋"

# Версия B (просто заменить файл)
handlers:
  - name: "welcome"
    trigger: "/start"
    effects:
      - send:
          text: "Добро пожаловать! 🎉"
```

### **5. 🎯 Работающие клавиатуры "из коробки"**

**В обычной ветви:** нужно было исправлять callback обработчики, отступы Python, парсинг кнопок

**В ESYBOT-DEC:** клавиатуры **гарантированно работают**, потому что:
- ✅ **Автоматическая генерация** безопасных callback_data
- ✅ **Валидация** структуры кнопок при загрузке
- ✅ **Правильная регистрация** обработчиков
- ✅ **Нет проблем с отступами** - только конфигурация

### **6. 🔍 Лучшая отладка**

**ESYBOT-DEC предоставляет:**
```bash
# Валидация конфигурации
python esybot_dec.py bot.yaml --validate

# Подробная отладка
python esybot_dec.py bot.yaml --debug

# Просмотр структуры
python esybot_dec.py bot.yaml --show-structure
```

### **7. 📈 Масштабируемость**

**Обычная ветвь:**
- Один большой .esi файл
- Смешанная логика и конфигурация
- Сложно поддерживать

**ESYBOT-DEC:**
```yaml
# Можно разделить на модули
config: !include config.yaml
keyboards: !include keyboards.yaml
handlers: !include handlers.yaml
variables: !include variables.yaml
```

### **8. 🔒 Безопасность и валидация**

**Автоматические проверки:**
- ✅ Валидация токена бота
- ✅ Проверка структуры клавиатур
- ✅ Контроль длины callback_data (64 байта лимит)
- ✅ Проверка ссылок на несуществующие клавиатуры
- ✅ Валидация типов переменных

## 🚀 **Конкретный пример: рабочая клавиатура**

### **Проблемы в обычной ветви:**
```esybot
# Могли быть проблемы:
menu broken_menu {
    button "🎯 Кнопка с emoji" "target_btn"  # ❌ Проблемы с emoji в callback
    button "Длинная кнопка с очень длинным названием" "very_long_callback_data_that_exceeds_telegram_limit"  # ❌ Превышает лимит
}

on_callback target_btn {
    # ❌ Могли быть проблемы с обработкой
    python {
        # ❌ Проблемы с отступами
    if condition:
        result = "test"
    }
    edit $result
}
```

### **Решение в ESYBOT-DEC:**
```yaml
keyboards:
  - name: "working_menu"
    type: "inline"
    buttons:
      - text: "🎯 Кнопка с emoji"
        callback_data: "target_btn"  # ✅ Автоматически безопасный
      - text: "Длинная кнопка с очень длинным названием"
        callback_data: "long_btn"    # ✅ Автоматически сокращается если нужно

handlers:
  - name: "target_handler"
    trigger: "target_btn"            # ✅ Точное соответствие
    python: |                        # ✅ Нормализация отступов автоматически
      if condition:
          result = "test"
    effects:
      - edit:
          text: "$result"            # ✅ Правильная замена переменных
```

## 📋 **Итоговое сравнение**

| Аспект | Обычная ветвь | ESYBOT-DEC |
|--------|---------------|------------|
| **Клавиатуры** | Не работают | ✅ Работают гарантированно |
| **Python блоки** | Могут быть проблемы с отступами | ✅ Автонормализация |
| **Модификация** | Нужен перезапуск | ✅ JIT и горячая перезагрузка |
| **Отладка** | Сложная | ✅ Встроенные инструменты |
| **Переиспользование** | Копипаст | ✅ Модульная архитектура |
| **Валидация** | Только во время выполнения | ✅ При загрузке |
| **Читаемость** | Смешанный код | ✅ Чистая конфигурация |
| **A/B тестирование** | Сложно | ✅ Замена файла |

## 🎯 **Вывод**

**ESYBOT-DEC превосходит обычную ветвь по всем ключевым параметрам:**

1. **🔧 Надежность** - клавиатуры и обработчики работают без исправлений
2. **⚡ Скорость разработки** - изменения без перезапуска
3. **📖 Читаемость** - структура видна сразу
4. **🔄 Гибкость** - легко экспериментировать
5. **📈 Масштабируемость** - модульная архитектура

**ESYBOT-DEC - это эволюция подхода к созданию ботов, где конфигурация заменяет сложный код!** 🚀
