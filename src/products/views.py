from django.shortcuts import render
from django.db.models import Q
from products.models import (
    Product,
    Category,
    Size,
    Brand,
    UnitofMeasure,
    ProductImage, ProductWeight
)
from rest_framework import status, viewsets, mixins, generics
from products.filterset import ProductFilter
from products.serializers import (
    ProductSerializer,
    CategorySerializer,
    BrandSerializer,
    UoMSerializer,
    SizeSerializer,
    ProductImageSerializer,
    ProductSingleSerializer,
    ProductWeightSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from googletrans import Translator

from rest_framework.permissions import AllowAny, IsAuthenticated
from common.models import User, Address
from orders.models import ContactAddress
from orders.serializers import ContactAddressSerializer
from CartSystem.models import AddToCart
from vendor.models import Vendor, VendorAddress
from vendor.serializers import VendorProfileAddressSerializer
import geopy.distance

translator = Translator()


# ListAPI View of Product-Category.
class CategoryListApiView(ListAPIView):
    # authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,
                       )
    search_fields = ("name")
    # ordering_fields = ("created_at")
    queryset = Category.objects.all()


# RetrieveAPI View of Product_Category
class CategoryAPIView(RetrieveAPIView):
    # authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = {}
        for k, v in serializer.data.items():
            data = translator.translate(str(v), dest='ar').text

        return Response(data)


"""class CategoryInfo(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [AllowAny, ]

    def retrieve(self, request, pk):
        queryset = self.get_queryset()
        try:
            instance = self.get_object()
            category_info = {
                "id": instance.id,
                "Name": instance.name,
                "image": instance.categoryImage.url
            }
            return Response({"status": True, "data": category_info}, status=status.HTTP_200_OK)
        except (Exception) as e:
            print(e)
            return Response({"status": False, "data": {"msg": "Category not found."}}, status=status.HTTP_404_NOT_FOUND)"""


# CreateAPI View of Product-Category.
class CategoryCreateAPIView(APIView):
    pass


class ProductView(APIView):
    """ API for Product """

    # permission_classes = [IsAuthenticated]
    def get(self, request):
        userObj = User.objects.get(id=self.request.user.id)
        category = self.request.query_params.get('category')
        if category:
            queryset = Product.objects.filter(category__id=category)
        else:
            queryset = Product.objects.all()

        serializer = ProductSerializer(queryset, many=True)
        listData = []
        for oneProduct in serializer.data:
            try:
                cartObj = AddToCart.objects.get(user=userObj, product_id=oneProduct["id"])
                oneProduct["selectedQuantity"] = cartObj.quantity
                oneProduct["cartId"] = cartObj.id

            except (AddToCart.DoesNotExist, Exception) as e:
                oneProduct["selectedQuantity"] = 0
                oneProduct["cartId"] = 0

            listData.append(oneProduct)

        return Response({'count': len(serializer.data), 'data': listData})


# Product List According to Category
class CategoryProductList(APIView):

    def get(self, request):
        category = self.request.query_params.get('category')
        # category= Category.objects.get(id=cat_id)
        data = Product.objects.filter(category__id=category).order_by('-id')
        # data = Product.objects.filter(category=category)
        return Response(
            request,
            {
                'data': data,
            }
        )


# Product List According to Brand
def brand_product_list(request, brand_name_id):
    brand = Brand.objects.get(id=brand_name_id)
    data = Product.objects.filter(brand=brand).order_by('-id')
    return render(request,
                  {
                      'data': data,
                  }
                  )


class ProductbyBrandView(APIView):
    """ API for Productbybrand """

    def get(self, request):
        brand = self.request.query_params.get('brand_name')
        if brand:
            queryset = Product.objects.filter(brand_name__id=brand)
        else:
            queryset = Product.objects.all()
        serializer = ProductSerializer(queryset, many=True)
        return Response({'count': len(serializer.data), 'data': serializer.data})


class ProductsByCategory(ListAPIView):
    serializer_class = ProductSerializer
    # permission_classes = (AllowAny,)

    """
    Returns products under a single category in `slug`
    Endpoint: `api/store/category/<slug>`
    """

    def get_queryset(self):
        return Product.objects.filter(category=self.kwargs["id"])
        # category__in=Category.objects.get(id=self.kwargs["id"]).get_descendants(include_self=True)
        # category__in=Category.objects.get(id=self.kwargs["slug"]).get_descendants(include_self=True)


# Product Listing and Filter by category, brand, and max_min price
class ProductListAPIView(ListAPIView):
    # authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter

    search_fields = ("category", "brand")
    ordering_fields = ("-id")


# Product Images by ProductId
class ProductImagesByProductId(ListAPIView):
    serializer_class = ProductImageSerializer
    # permission_classes = (AllowAny,)

    """
    Returns product images that share product `id`
    Endpoint: `api/store/images/<id>`
    """

    def get_queryset(self):
        return ProductImage.objects.filter(product=self.kwargs["id"])


# Brand List
class BrandListApiView(ListAPIView):
    # authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()

    '''def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = {}
        for k, v in serializer.data.items():
            data = translator.translate(str(v), dest='ar').text

        return Response({'count' : len(serializer.data), "data":data}, status=status.HTTP_200_OK)'''


# Particular Product By Product id
class ProductRetrieveView(RetrieveAPIView):
    # authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    serializer_class = ProductSingleSerializer
    queryset = Product.objects.all()


# Product Detail

# RetrieveAPI View of Product Unit Of Measure
class UoMAPIView(RetrieveAPIView):
    # authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    serializer_class = UoMSerializer
    queryset = UnitofMeasure.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = {}
        for k, v in serializer.data.items():
            data = translator.translate(str(v), dest='ar').text

        return Response({'count': len(serializer.data), "data": data}, status=status.HTTP_200_OK)


# ListAPI View of UoM List.
class UoMAPIListApiView(ListAPIView):
    # authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    serializer_class = UoMSerializer
    queryset = UnitofMeasure.objects.all()


# ListAPI View of Product Size
class SizeAPIView(ListAPIView):
    # authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    serializer_class = SizeSerializer
    queryset = Size.objects.all()

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     data = {}
    #     for k, v in serializer.data.items():
    #         data = translator.translate(str(v), dest='ar').text
    #
    #     return Response({'count' : len(serializer.data), "data":data}, status=status.HTTP_200_OK)


# ProductByLocation
class ProductByLocationAPIView(APIView):
    """ API for Product """

    # permission_classes = [IsAuthenticated]

    def get(self, request):

        # Get User Object
        if self.request.user.id:
            userObj = User.objects.get(id=self.request.user.id)

            # Get UserAddress Object
            userAddressObj = ContactAddress.objects.get(user=userObj, is_default=True)

            # get Useraddress serialized data
            userAddressSerializerObj = ContactAddressSerializer(userAddressObj, many=False)
            userAddress = userAddressSerializerObj.data
            user_pin_code = userAddressObj.postcode

            # we get user coordinates using user latitude, longitude
            userAddressCords = (userAddress["map_lat"], userAddress["map_lng"])

            # category query params for filter product by category
            category = self.request.query_params.get('category')
            if category:
                queryset = Product.objects.filter(category__id=category)
            else:
                queryset = Product.objects.all()

            serializer = ProductSerializer(queryset, many=True)

            # Put one product data inside a listdata
            listData = []
            for oneProduct in serializer.data:
                prodobj = Product.objects.get(id=oneProduct['id'])
                product_query_set = ProductWeight.objects.filter(product=prodobj)
                product_weights = ProductWeightSerializer(product_query_set, many=True)
                oneProduct['quantities'] = []
                for product_weight in product_weights.data:
                    product_weight['offer_price'] = product_weight['price'] - product_weight['discount_price']
                    oneProduct['quantities'].append(product_weight)

                # get Vendor Object
                vendorObj = Vendor.objects.get(id=oneProduct["vendor"])
                try:
                    vendor_pin_codes = [pin_code.strip() for pin_code in vendorObj.delivering_pincodes.split(",")]
                except:
                    vendor_pin_codes = []

                # get Vendor Address Object and vendorAddress serialzized data
                vendorAddressObj = VendorAddress.objects.get(vendor=vendorObj)
                vendorAddressSerializerObj = VendorProfileAddressSerializer(vendorAddressObj, many=False)
                vendorAddress = vendorAddressSerializerObj.data

                # we get vendor coordinates using vendor latitude and longitude
                vendorAddressCords = (vendorAddress["map_lat"], vendorAddress["map_lng"])

                # calculate distance in kilometer by iser and vendor coordinate
                distanceBetweenVendorAndUser = geopy.distance.geodesic(userAddressCords, vendorAddressCords).km
                # distance of vendor is less than or equal than mention(vendorObj.distance) km
                if user_pin_code in vendor_pin_codes:
                    try:
                        # get cart Product to check product already exist or not, quantity, cart_id
                        cartObj = AddToCart.objects.get(user=userObj, product_id=oneProduct["id"])
                        oneProduct["selectedQuantity"] = cartObj.quantity
                        oneProduct["cartId"] = cartObj.id

                    except (AddToCart.DoesNotExist, Exception) as e:
                        oneProduct["selectedQuantity"] = 0
                        oneProduct["cartId"] = 0

                    # add distance in product data
                    # oneProduct["vendorAddress"] = vendorAddress
                    oneProduct["vendorDistance"] = distanceBetweenVendorAndUser
                    listData.append(
                        oneProduct)  # append(add) that product in list  which is less than vendorObj.distance
        else:
            category = self.request.query_params.get('category')
            if category:
                queryset = Product.objects.filter(category__id=category)
            else:
                queryset = Product.objects.all()
            serializer = ProductSerializer(queryset, many=True)
            listData = []

            for oneProduct in serializer.data:
                print(oneProduct)
                oneProduct['offer_price'] = oneProduct['price'] - oneProduct['discount_price']
                del oneProduct['discount_price']
                prodobj = Product.objects.get(id=oneProduct['id'])
                product_query_set = ProductWeight.objects.filter(product=prodobj)
                product_weights = ProductWeightSerializer(product_query_set, many=True)
                oneProduct['quantities'] = []
                for product_weight in product_weights.data:
                    product_weight['offer_price'] = product_weight['price'] - product_weight['discount_price']
                    oneProduct['quantities'].append(product_weight)
                prodobj = Product.objects.get(id=oneProduct['id'])
                product_weights = ProductWeight.objects.filter(product=prodobj)
                oneProduct['quantities'] = []
                for product_weight in product_weights:
                    different_quantities = {}
                    different_quantities['id'] = product_weight.id
                    different_quantities['weight'] = product_weight.weight
                    different_quantities['price'] = product_weight.price

                    oneProduct['quantities'].append(different_quantities)
                listData.append(oneProduct)  # append(add) that product in list  which is less than vendorObj.distance

        return Response(
            {'count': len(listData),
             'data': listData,
             })


class ProductBySearchAPIView(APIView):
    """
    This class lists the products for Search API functionality
    """

    def get(self, request):
        string_query = self.request.query_params.get('q')
        category = self.request.query_params.get('category')
        # queryset = Product.objects.filter(category__id=1)
        print(string_query, category)
        if string_query:
            querySet = Product.objects.filter(Q(name__icontains=string_query))

            if category:
                category_query_set = querySet.filter(category__id=category)
                serializer = ProductSerializer(category_query_set, many=True).data
                new_data = []
                for data in serializer:
                    prodobj = Product.objects.get(id=data['id'])
                    prodweightobj = ProductWeight.objects.filter(product=prodobj)
                    product_weights = ProductWeightSerializer(prodweightobj, many=True)
                    data['quantities'] = []
                    for dat in product_weights.data:
                        dat['offer_price'] = dat['price'] - dat['discount_price']
                        data['quantities'].append(dat)

                    new_data.append(data)
            else:
                serializer = ProductSerializer(querySet, many=True).data
                new_data = []
                for data in serializer:
                    prodobj = Product.objects.get(id=data['id'])
                    prodweightobj = ProductWeight.objects.filter(product=prodobj)
                    product_weights = ProductWeightSerializer(prodweightobj, many=True)
                    data['quantities'] = []
                    for dat in product_weights.data:
                        dat['offer_price'] = dat['price'] - dat['discount_price']
                        data['quantities'].append(dat)

                    new_data.append(data)
        else:
            if category:
                category_query_set = Product.objects.filter(category__id=category)
                serializer = ProductSerializer(category_query_set, many=True).data
                # serializer = ProductSerializer(category_query_set, many=True)
                new_data = []
                for data in serializer:
                    prodobj = Product.objects.get(id=data['id'])
                    prodweightobj = ProductWeight.objects.filter(product=prodobj)
                    product_weights = ProductWeightSerializer(prodweightobj, many=True)
                    data['quantities'] = []
                    for dat in product_weights.data:
                        dat['offer_price'] = dat['price'] - dat['discount_price']
                        data['quantities'].append(dat)

                    new_data.append(data)
            else:
                query = Product.objects.all()
                serializer = ProductSerializer(query, many=True).data
                new_data = []
                for data in serializer:
                    prodobj = Product.objects.get(id=data['id'])
                    prodweightobj = ProductWeight.objects.filter(product=prodobj)
                    product_weights = ProductWeightSerializer(prodweightobj, many=True)
                    data['quantities'] = []
                    for dat in product_weights.data:
                        dat['offer_price'] = dat['price'] - dat['discount_price']
                        data['quantities'].append(dat)

                    new_data.append(data)

        return Response({'count': len(new_data),
                         'data': new_data})
