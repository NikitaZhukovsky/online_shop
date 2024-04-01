from rest_framework import serializers
from catalog.models import Category, Product, ProductImage, Seller, Discount


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('image',)


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, source='productimage_set')
    class Meta:
        model = Product
        fields = ('id', 'article', 'name', 'price', 'images')


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ('id', 'name', 'description', 'contact')


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ('id', 'name', 'percent', 'date_start', 'date_end')
