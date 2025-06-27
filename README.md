# Python Documentation Parser

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.9.3-orange)
![Requests](https://img.shields.io/badge/Requests-2.27.1-green)
![Requests-Cache](https://img.shields.io/badge/Requests--Cache-1.0.0-yellow)


Парсер официальной документации Python с возможностью анализа PEP, получения новостей о версиях и загрузки PDF-документации.


## Основные функции

- Сбор ссылок на статьи о нововведениях в Python, переход по ним и сбор информации об авторах и редакторах статей.
- Сбор информации о статусах версий Python.
- Скачивание архивов с актуальной документацией.
- Парсинг документов PEP.
- Вывод данных в файл.
- Вывод данных в формате PrettyTable.
- Обработка и логирование ошибок.

## Развертывание

Подготовьте виртуальное окружение к работе — установите библиотеки из списка зависимостей:
```
(venv) ...$ pip install -r requirements.txt
```

Для проверки, запустите тесты из корневой директории:
```
(venv) .../bs4_parser_pep $ pytest
```




## Доступные режимы:

| Режим             | Описание                                   |
| ----------------- | ------------------------------------------ |
| `pep`             | Парсинг PEP и подсчет статусов             |
| `whats-new`       | Получение новостей из раздела "What's New" |
| `latest-versions` | Список последних версий Python             |
| `download`        | Загрузка PDF архива документации           |

## Примеры запуска

Перейдите в папку src:

```
(venv) ...$ cd src
```

Запуск с очисткой кеша:
```
(venv) ...$ python main.py whats-new -c
```

Вывод данных в формате PrettyTable:
```
(venv) ...$ python main.py latest-versions --pretty 
```

Запись данных в файл:
```
(venv) ...$ python main.py whats-new --output file
```

Парсинг документов PEP:
```
(venv) ...$ python main.py pep -o file
```