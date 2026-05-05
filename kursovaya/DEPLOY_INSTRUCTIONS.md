# 🚀 Загрузка сайта на PythonAnywhere

## 📋 Что уже готово:
✅ `requirements.txt` - зависимости Python  
✅ `wsgi.py` - WSGI конфигурация  
✅ Все файлы проекта готовы

## 🌐 Пошаговая инструкция:

### Шаг 1: Регистрация на PythonAnywhere
1. Перейдите на [pythonanywhere.com](https://www.pythonanywhere.com/)
2. Нажмите "Create a free account"
3. Заполните форму:
   - Email: ваша почта
   - Username: придумайте логин
   - Password: создайте пароль
4. Подтвердите email

### Шаг 2: Создание Web приложения
1. В личном кабинете нажмите "Web" → "Add a new web app"
2. Выберите "Manual configuration"
3. Настройте:
   - **Python version**: 3.9 или 3.10
   - **Web framework**: Flask
   - **PythonAnywhere username**: ваш логин
   - **Application name**: amirkhan-events

### Шаг 3: Загрузка файлов
**Способ А: Через Web интерфейс**
1. В разделе "Files" создайте папку `amirkhan-events`
2. Загрузите все файлы из папки `kursovaya`
3. Убедитесь что загружены:
   - `app.py`
   - `wsgi.py`
   - `requirements.txt`
   - папка `templates/`
   - папка `static/`
   - `events.db`

**Способ Б: Через Git (рекомендуется)**
1. Создайте репозиторий на GitHub
2. Загрузите файлы проекта
3. В PythonAnywhere: "Consoles" → "Bash"
4. Выполните команды:
   ```bash
   git clone https://github.com/ВАШ_ЛОГИН/amirkhan-events.git
   cd amirkhan-events
   ```

### Шаг 4: Установка зависимостей
1. Откройте Bash консоль: "Consoles" → "Bash"
2. Выполните команды:
   ```bash
   cd amirkhan-events
   pip3 install --user -r requirements.txt
   ```

### Шаг 5: Настройка WSGI
1. В разделе "Web" найдите ваше приложение
2. В поле "WSGI configuration file" укажите:
   ```
   /var/www/ВАШ_ЛОГИН_amirkhan-events/wsgi.py
   ```
3. Нажмите "Reload" иконку 🔄

### Шаг 6: Проверка работы
1. Ваш сайт будет доступен по адресу:
   ```
   https://ВАШ_ЛОГИН.pythonanywhere.com/
   ```

## 🔧 Если возникли проблемы:

### Ошибка "Module not found":
```bash
pip3 install --user flask
```

### Ошибка "Database locked":
```bash
chmod 664 events.db
```

### Ошибка "Static files not found":
В WSGI файле добавьте:
```python
app.static_folder = 'static'
```

## 📱 Мобильная версия:
Сайт автоматически адаптирован для мобильных устройств!

## 🎯 Функционал после загрузки:
- ✅ 10 мероприятий с разными дизайнами
- ✅ Регистрация пользователей
- ✅ Админ-панель
- ✅ Многоязычность (RU/KZ/EN)
- ✅ Мобильная адаптация

## 💡 Быстрый старт:
1. **Зарегистрируйтесь** на PythonAnywhere (5 минут)
2. **Загрузите файлы** через Web интерфейс (10 минут)
3. **Установите зависимости** в Bash (2 минуты)
4. **Перезапустите** WSGI (1 клик)

**Итого: ~20 минут и ваш сайт работает 24/7!**

## 📞 Поддержка:
Если возникнут вопросы:
- WhatsApp: +7 775 463 1285
- Email: amirkhan.events@local
