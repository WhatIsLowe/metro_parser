# MetroParser

MetroParser - это инструмент для сбора информации о продуктах с веб-сайта Metro Cash & Carry. Этот парсер использует GraphQL API для извлечения данных о продуктах из определенных категорий.

## Описание

Это тестовое задание на позицию Младший специалист отдела разработки (Python) / Специалист по парсингу данных. 

В файле `categories.json` хранится структура категорий сайта online.metro-cc.ru. Для указания категорий для парсинга можно брать любые категории из указанного файла. Можно указывать от 1 категории в виде строки до списка различных категорий. `store_id` это id магазинов, в которых будет искать, и в данном случае, указаны id 10 - Москва, и 15 - Санкт-Петербург.

### Экспорт в CSV

После завершения парсинга, данные будут сохранены в формате CSV в текущей директории под названием `<store_id>_<category>.csv`.

## Пример использования

```python
if __name__ == "__main__":
    mt = MetroParser()
    mt.start_scraping(store_id=[10, 15], category=['vino'])
```
В данном примере, передаются следующие указания для парсинга: 
`store_id=[10, 15]` - указаны 2 id: 10 - Москва, 15 - Санкт-Петербург.
`category=['vino']` - указывается категория товаров (можно перечислить все интересующие категории).

В файле `categories.json` хранится вся структура категорий сайта. В `category` можно передать любой ключ из этого файла, при этом, иерархия остается. К примеру, если указать `"viski"` - то результатом будут только виски, а если указать `"alkogolnaya-produkciya"` - то результатом будет вся алкогольная продукция данного магазина.
