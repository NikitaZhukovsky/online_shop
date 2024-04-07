import pytest
from rest_framework.test import APITestCase
from django.shortcuts import reverse
from conftest import EVERYTHING_EQUALS_NOT_NONE


pytest = [pytest.mark.django_db]


class TestCategoriesEndpoints(APITestCase):
    fixtures = ['catalog/test/fixtures/categories_fixture.json',

                ]

    def test_categories_list_endpoints(self):
        url = reverse('categories')
        response = self.client.get(url)
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert response.data == [
            {
                "id": 1,
                "name": EVERYTHING_EQUALS_NOT_NONE,
                "description": EVERYTHING_EQUALS_NOT_NONE
            },
            {
                "id": 2,
                "name": EVERYTHING_EQUALS_NOT_NONE,
                "description": EVERYTHING_EQUALS_NOT_NONE
            },
            {
                "id": 3,
                "name": EVERYTHING_EQUALS_NOT_NONE,
                "description": EVERYTHING_EQUALS_NOT_NONE
            }
        ]


class TestProductsEndpoints(APITestCase):
    fixtures = ['catalog/test/fixtures/categories_fixture.json',
                'catalog/test/fixtures/discounts_fixture.json',
                'catalog/test/fixtures/images_fixture.json',
                'catalog/test/fixtures/products_fixture.json',
                'catalog/test/fixtures/sellers_fixture.json',
                ]

    def test_category_products(self):
        url = reverse('category-products', kwargs={'category_id': 1})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data == [
            {
                "id": 1,
                "name": EVERYTHING_EQUALS_NOT_NONE,
                "price": EVERYTHING_EQUALS_NOT_NONE,
                "article": EVERYTHING_EQUALS_NOT_NONE,
                "description": EVERYTHING_EQUALS_NOT_NONE,
                "count_on_stock": EVERYTHING_EQUALS_NOT_NONE,
                "discount": EVERYTHING_EQUALS_NOT_NONE,
                "category": EVERYTHING_EQUALS_NOT_NONE,
                "seller": EVERYTHING_EQUALS_NOT_NONE,

            }
        ]
        assert response.data[0]["discount"] == {
            "id": 1,
            "name": EVERYTHING_EQUALS_NOT_NONE,
            "percent": EVERYTHING_EQUALS_NOT_NONE,
            "date_start": EVERYTHING_EQUALS_NOT_NONE,
            "date_end": EVERYTHING_EQUALS_NOT_NONE
        }
