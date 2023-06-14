# encost_test_task

### Технологии:
Python 3.7, PlotlyDash 2.9, Pandas 2.0

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
https://github.com/ika11ika/encost_test_task
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Перейти в папку проекта

```
cd test_task/
```

Запустить проект:

```
python app.py
```

### Исходное задание
https://disk.yandex.ru/d/W-0zt5fzowrJAg
В папке проекта (test_task) находится заготовка web-приложения на фреймворке PlotlyDash. В файле testDB.db находится тестовая база данных sqlite (описание полей базы данных представлено ниже).
Задание заключается в разработке приложения, которое позволяет просматривать данные из бд в различных форматах:
-	Вывод общей информации в правой верхней карточке
-	Вывод в виде круговой диаграммы причин состояний (plotly.express.pie)
-	Вывод диаграммы ганта длительностей состояний (plotly.express.timeline)
-	Вывод дополнительной информации для длительностей при наведении (свойство hovertemplate)
-	Дополнительно: фильтрация по состояниям (необходимо использование callback).
