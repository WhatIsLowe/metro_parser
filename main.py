import csv
import json
import requests
from typing import List, Union


class MetroParser:
    def __init__(self) -> None:
        self.session = requests.Session()
        # self.headers = {
        #     'authority': 'api.metro-cc.ru',
        #     'accept': 'application/json, text/plain, */*',
        #     'accept-language': 'ru-AU,ru;q=0.9,en-VI;q=0.8,en;q=0.7,ru-RU;q=0.6,en-US;q=0.5',
        #     'content-type': 'application/json',
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        #                   '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        # }

        self.headers = {
            "content-type": "application/json",
            "accept": "application/json, text/plain, */*",
        }
        # Эндпоинт для GraphQL
        self.url = "https://api.metro-cc.ru/products-api/graph"

    def _is_category_in_json(self, categori):
        def search_categories(data, categori):
            if isinstance(data, dict):
                for category in categori[:]:  # Создаем копию списка, чтобы избежать ошибки изменения размера списка во время итерации
                    if category in data:
                        categori.remove(category)
                for key, value in data.items():
                    if isinstance(value, dict):
                        search_categories(value, categori)

        try:
            with open("categories.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
                search_categories(data, categori)
                if categori:
                    print(f"Не найденные категории: {categori}")
                    return False
                else:
                    return True
        except FileNotFoundError:
            raise FileNotFoundError("Файл categories.json не найден")

    def _form_query(self, slug, store_id, count_per_request, from_num):
        # Формируем запрос к GraphQL
        json_query = {
            'query': '\n  query Query($storeId: Int!, $slug: String!, $attributes:[AttributeFilter], $filters: [FieldFilter], $from: Int!, $size: Int!, $sort: InCategorySort, $in_stock: Boolean, $eshop_order: Boolean, $is_action: Boolean, $price_levels: Boolean) {\n    category (storeId: $storeId, slug: $slug, inStock: $in_stock, eshopAvailability: $eshop_order, isPromo: $is_action, priceLevels: $price_levels) {\n      id\n      name\n      slug\n      id\n      parent_id\n      meta {\n        description\n        h1\n        title\n        keywords\n      }\n      disclaimer\n      description {\n        top\n        main\n        bottom\n      }\n#      treeBranch {\n#        id\n#        name\n#        slug\n#        children {\n#          category_type\n#          id\n#          name\n#          slug\n#          children {\n#            category_type\n#            id\n#            name\n#            slug\n#            children {\n#              category_type\n#              id\n#              name\n#              slug\n#              children {\n#                category_type\n#                id\n#                name\n#                slug\n#              }\n#            }\n#          }\n#        }\n#      }\n      breadcrumbs {\n        category_type\n        id\n        name\n        parent_id\n        parent_slug\n        slug\n      }\n      promo_banners {\n        id\n        image\n        name\n        category_ids\n        virtual_ids\n        type\n        sort_order\n        url\n        is_target_blank\n        analytics {\n          name\n          category\n          brand\n          type\n          start_date\n          end_date\n        }\n      }\n\n\n      dynamic_categories(from: 0, size: 9999) {\n        slug\n        name\n        id\n      }\n      filters {\n        facets {\n          key\n          total\n          filter {\n            id\n            name\n            display_title\n            is_list\n            is_main\n            text_filter\n            is_range\n            category_id\n            category_name\n            values {\n              slug\n              text\n              total\n            }\n          }\n        }\n      }\n      total\n      prices {\n        max\n        min\n      }\n      pricesFiltered {\n        max\n        min\n      }\n      products(attributeFilters: $attributes, from: $from, size: $size, sort: $sort, fieldFilters: $filters)  {\n        health_warning\n        limited_sale_qty\n        id\n        slug\n        name\n        name_highlight\n        article\n        is_target\n        category_id\n        url\n        images\n        pick_up\n        icons {\n          id\n          badge_bg_colors\n          caption\n          image\n          type\n          is_only_for_sales\n          stores\n          caption_settings {\n            colors\n            text\n          }\n          stores\n          sort\n          image_png\n          image_svg\n          description\n          end_date\n          start_date\n          status\n        }\n        manufacturer {\n          id\n          image\n          name\n        }\n        packing {\n          size\n          type\n          pack_factors {\n            instamart\n          }\n        }\n        stocks {\n          value\n          text\n          eshop_availability\n          scale\n          prices_per_unit {\n            old_price\n            offline {\n              price\n              old_price\n              type\n              offline_discount\n              offline_promo\n            }\n            price\n            is_promo\n            levels {\n              count\n              price\n            }\n            discount\n          }\n          prices {\n            price\n            is_promo\n            old_price\n            offline {\n              old_price\n              price\n              type\n              offline_discount\n              offline_promo\n            }\n            levels {\n              count\n              price\n            }\n            discount\n          }\n        }\n      }\n    }\n  }\n',
            "variables": {
                "isShouldFetchOnlyProducts": True,
                "sort": "default",
                "filters": [],
                "attributes": [],
                "in_stock": True,
                "eshop_order": False
            }
        }

        json_query['variables']['slug'] = slug
        json_query['variables']['storeId'] = store_id
        json_query['variables']['size'] = count_per_request
        json_query['variables']['from'] = from_num

        return json_query

    def _parse_json(self, json_data: dict):
        products_data = json_data['data']['category']['products']
        parsed_products = []
        for product in products_data:
            p_id = product['id']
            brand = product['manufacturer']['name']
            name = product['name']
            count = product['stocks'][0]['value']

            product_prices = product['stocks'][0]['prices']

            if product_prices['is_promo']:
                price = product_prices['old_price']
                promo_price = product_prices['price']
            else:
                price = product_prices['price']
                promo_price = 0

            parsed_products.append([p_id, brand, name, count, price, promo_price])
        return parsed_products

    def _scrape(self, slug: str, count_per_request: int, store_id: int):
        from_num = 0
        total_results = 0
        # Делаем первый запрос, чтобы получить кол-во результатов
        # Формирует запрос к GraphQL
        json_query = self._form_query(slug=slug, store_id=store_id, count_per_request=count_per_request,
                                      from_num=from_num)
        # Отправляем запрос на эндпоинт GraphQL
        response = self.session.post(url=self.url, headers=self.headers, json=json_query)
        if response.status_code == 200:
            try:
                total_results = response.json()['data']['category']['total']
            except Exception as e:
                print(e)
        else:
            print(f"Неверный запрос.\n{response.text}")

        data = []
        # Повторяем запросы, уеличивая сдвиг (from_num) на count_per_request
        while from_num < total_results:
            json_query = self._form_query(slug=slug, store_id=store_id, count_per_request=count_per_request,
                                          from_num=from_num)
            response = self.session.post(url=self.url, headers=self.headers, json=json_query)
            if response.status_code == 200:
                try:
                    data.append(self._parse_json(response.json()))
                    from_num += count_per_request
                except requests.JSONDecodeError:
                    raise requests.JSONDecodeError
            else:
                raise requests.RequestException("Ошибка при отправке запроса")
        return data

    def _save_to_csv(self, filename, data):
        headers = ["ID", "Brand", "Name", "Count", "Price", "Promo Price"]
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Бренд', 'Наименование', 'Количество', 'Цена', 'Цена по акции'])

            for sublist in data:
                for row in sublist:
                    writer.writerow(row)
        print(f"Файл '{filename}' успешно сохранен!")

    def start_scraping(self, store_id: Union[int, List[int]], category: Union[str, List[str]],
                       count_per_request: int = 1000):
        # Преобразуем данные в список
        store_ids = [store_id] if isinstance(store_id, (int, str)) else store_id
        categories = [category] if isinstance(category, str) else category
        categori = categories.copy()
        if self._is_category_in_json(categori):
            for store in store_ids:
                for cat in categories:
                    data = self._scrape(slug=cat, count_per_request=count_per_request, store_id=store)
                    filename = f"{store}_{cat}.csv"
                    self._save_to_csv(filename, data)
        else:
            return


if __name__ == "__main__":
    mt = MetroParser()
    mt.start_scraping(store_id=[10, 15], category=['vino'])
