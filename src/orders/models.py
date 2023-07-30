from django.db import models
from common.models import User, TimeStampMixin
from CartSystem.models import AddToCart
from Offers.models import Offer
from products.models import Product, ProductWeight
from Wallet.models import MyWallet
import decimal
from deliveryExecutive.models import DeliveryExecutive
from vendor.models import Vendor
from .utils import (
    order_status_choice,
    payment_method,
    save_address_as,
    payment_status,
    orderUserProductstatusChoice,
    orderSuperAdminstatusChoice,
    userRemarkStatus,
)
import random, datetime


# Contact Address
class ContactAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField("Full name", max_length=255, blank=False, null=False)
    contact_number = models.CharField("Mobile No", max_length=20, blank=False, null=False)
    postcode = models.CharField("Post/Zip-code", max_length=64, blank=True, null=True)
    address_line = models.CharField("Address", max_length=255,
                                    help_text=("Address (House No, Building, Street, Area)"), blank=False, null=True)
    locality = models.CharField("Locality/Town", max_length=255, )
    city = models.CharField("City/District", max_length=255, help_text=("City/District"), blank=False, null=False)
    state = models.CharField("State", max_length=255, help_text=("State"), blank=False, null=False)
    save_address_as = models.CharField("Save Address As", max_length=200, choices=save_address_as, default="Home")
    is_default = models.BooleanField(default=False)
    map_lat = models.CharField("Map Lat", max_length=50, blank=False, null=False, default="0.0")
    map_lng = models.CharField("Map Lng", max_length=50, blank=False, null=False, default="0.0")

    class Meta:
        verbose_name_plural = 'Contact Address'

    def __str__(self):
        return str(("Name: {}, Address line: {}, Locality: {}, City: {}, State: {}, Post Code: {}").format(
            self.name, self.address_line, self.locality, self.city, self.state, self.postcode))


# OrderNumber
class OrderNumber(models.Model):
    order_number = models.CharField(max_length=25, unique=True, editable=False, blank=True, null=True)

    def __str__(self):
        return str(self.order_number)

    class Meta:
        """This model will not create any Database Table"""
        abstract = True

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.po_id_generator()
            while OrderDetail.objects.filter(order_number=self.order_number).exists():
                self.order_number = self.po_id_generator()
        super(OrderNumber, self).save(*args, **kwargs)

    def po_id_generator(self):
        """if prev_order_number:
            prev_order_number += 1
            return prev_po_no"""
        return "ORD" + str(random.randint(2345678900, 99234567890))


# OrderDetail Model
class OrderDetail(TimeStampMixin, OrderNumber):
    user = models.ForeignKey(User, related_name="Customer", on_delete=models.CASCADE, blank=False, null=False)
    address = models.ForeignKey(ContactAddress,
                                related_name="ShippingAddress",
                                on_delete=models.PROTECT,
                                blank=False, null=False)
    price = models.DecimalField("Products Price", editable=False, blank=True, null=True, max_digits=12,
                                decimal_places=2, default=0.00)
    shipping_charge = models.DecimalField("Shipping Charges", editable=False, blank=True, null=True, max_digits=12,
                                          decimal_places=2, default=0.00)
    tax = models.DecimalField("Total Tax", editable=False, blank=True, null=True, max_digits=12, decimal_places=2,
                              default=0.00)
    grand_total = models.DecimalField("Grand Total", editable=False, blank=True, null=True, max_digits=12,
                                      decimal_places=2, default=0.00)
    offer_code = models.CharField("Offer Code", max_length=20, blank=True, null=True, default="N/A")

    # offer_code = models.ForeignKey(Offer, related_name="Offers", on_delete=models.CASCADE, blank=True, null=True, default="---")
    offer_discount = models.DecimalField("Discount Amount",
                                         max_digits=12, decimal_places=2,
                                         blank=True, null=True, default=0.00)
    totalOrderdQty = models.PositiveIntegerField("Total Orderd Quantity", null=True, blank=True, default=0)
    payment_method = models.CharField(
        "Payment Methods", max_length=200, choices=payment_method, null=True, blank=False, default="COD")
    payment_status = models.CharField(
        "Payment Status", max_length=50, choices=payment_status, null=True, blank=False,
        default="Pending")
    order_status = models.CharField("Order Status",
                                    max_length=100,
                                    choices=order_status_choice,
                                    blank=False, null=False, default="Pending")
    userRemark = models.CharField("User Remark",
                                  max_length=100,
                                  choices=userRemarkStatus,
                                  blank=True, null=True, default="None")
    delivery_exe = models.ForeignKey(DeliveryExecutive,
                                     related_name="Delivery_executive",
                                     on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return str(self.order_number)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Order Details"


# OrderDetail Model
class OrderProductDetail(TimeStampMixin):
    order = models.ForeignKey(OrderDetail, related_name="Order", on_delete=models.CASCADE, blank=False, null=False)
    product = models.ForeignKey(Product, related_name="Product", on_delete=models.CASCADE, blank=False, null=False)
    product_weight = models.ForeignKey(ProductWeight, related_name="product_Weight", on_delete=models.CASCADE,
                                       blank=True, null=True)
    uom = models.CharField("Unit of Measure", max_length=20, blank=True, null=True, default="N/A")

    price = models.DecimalField("Products Price", editable=False, blank=True, null=True, max_digits=12,
                                decimal_places=2,
                                default=0.00)

    quantity = models.PositiveIntegerField("Quantity", null=False, blank=False, default=1)
    # total_price = models.DecimalField("Total Price", editable=False, blank=True, null=True, max_digits=12,
    #                             decimal_places=2,
    #                             default=0.00)

    taxRate = models.DecimalField("Tax Rate", editable=False, blank=True, null=True, max_digits=12, decimal_places=2,
                                  default=0.00)
    total_price = models.DecimalField("Total Price", editable=False, blank=True, null=True, max_digits=12,
                                      decimal_places=2,
                                      default=0.00)

    # userOrderedProductStatus = models.CharField("User Order Status",
    #                                 max_length=100,
    #                                 choices=orderUserProductstatusChoice,
    #                                 blank=False, null=False, default= "None")
    # userRemarkStatus = models.CharField("User Remark Status",
    #                                 max_length=100,
    #                                 choices=userRemarkStatus,
    #                                 blank=False, null=False, default= "None")
    # returnQty = models.PositiveIntegerField("Return Quantity", null=True, blank=True, default=0)
    # returnId = models.CharField("Return Id", max_length=25, editable=False, blank=True, null=True, default="None")
    # adminRemarkStatus = models.CharField("Admin Remark",
    #                                 max_length=100,
    #                                 choices=orderSuperAdminstatusChoice,
    #                                 blank=False, null=False, default= "None")

    def __str__(self):
        return str(self.order)

    def __int__(self):
        return self.product_weight.price

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Order Product Details"

    def save(self, *args, **kwargs):
        self.price = self.product_weight.price
        self.total_price = self.quantity * self.product_weight.price
        self.uom = self.product_weight.uom.short_name
        self.price = (decimal.Decimal(self.product_weight.price) - decimal.Decimal(self.product_weight.discount_price))
        # self.total_price = self.quantity * self.product.price

        total_amt = self.quantity * (decimal.Decimal(self.product_weight.price) - decimal.Decimal(self.product_weight.discount_price))
        self.taxRate = decimal.Decimal(decimal.Decimal(total_amt) * (decimal.Decimal(self.product.tax) / 100))
        self.total_price = decimal.Decimal(total_amt) + self.taxRate

        # if self.order.offer_discount >= 0:

        #     oneProductDiscountValue = decimal.Decimal(((decimal.Decimal(self.order.offer_discount))/(decimal.Decimal(self.order.grand_total-self.taxRate)))*100)
        #     returnValue = decimal.Decimal(self.total_price - (oneProductDiscountValue*(decimal.Decimal(self.quantity))))

        #     print(returnValue)
        #     # return returnValue
        # else:
        #     returnValue = decimal.Decimal(self.total_price)
        #     print(returnValue)
        # return returnValue

        # if self.order.offer_discount >= 0:

        #     # oneProductDiscountValue = decimal.Decimal(((decimal.Decimal(self.order.offer_discount))/(decimal.Decimal(self.order.grand_total-self.taxRate)))*100)
        #     # returnValue = decimal.Decimal(self.total_price - oneProductDiscountValue)
        #     # print(returnValue)
        #     # #return returnValue
        #     returnProductAmtWithTaxandReturnQty = ((decimal.Decimal(self.total_price)/decimal.Decimal(self.quantity))*(decimal.Decimal(self.returnQty)))
        #     returnQtyWithDiscountAmt = ((decimal.Decimal(self.order.offer_discount))/(decimal.Decimal(self.order.totalOrderdQty)))*(decimal.Decimal(self.returnQty))
        #     returnValue = decimal.Decimal(returnProductAmtWithTaxandReturnQty - returnQtyWithDiscountAmt)
        #     print(returnProductAmtWithTaxandReturnQty)
        #     print(returnQtyWithDiscountAmt)
        #     print(returnValue)
        # else:
        #     returnValue = (decimal.Decimal(self.total_price)/(decimal.Decimal(self.quantity)))*(decimal.Decimal(self.returnQty))
        #     print(returnValue)

        # if self.userRemarkStatus == "None":
        #     self.returnId = self.returnId
        #     # while OrderProductDetail.objects.filter(returnId=self.returnId).exists():
        #     #     self.returnId = self.txn_id_generator()
        # elif self.userRemarkStatus == "Fully Return":
        #     self.returnId = self.txn_id_generator()
        #     while OrderProductDetail.objects.filter(returnId=self.returnId).exists():
        #         self.returnId = self.txn_id_generator()
        # elif self.userRemarkStatus == "Partially Return":
        #     self.returnId = self.txn_id_generator()
        #     while OrderProductDetail.objects.filter(returnId=self.returnId).exists():
        #         self.returnId = self.txn_id_generator()
        # elif self.userRemarkStatus == "Replace":
        #     self.returnId = self.txn_id_generator()
        #     while OrderProductDetail.objects.filter(returnId=self.returnId).exists():
        #         self.returnId = self.txn_id_generator()

        # # if self.order.payment_method == "wallet":
        # #     if self.userOrderedProductStatus == "Returned" and self.adminRemarkStatus == "Approved":
        # #         addWalletMoney = MyWallet(user=self.order.user, trasactionAmt=returnValue, transactionType="credit", orderNumber=self.order.order_number, status="active")
        # #         addWalletMoney.save()

        # if self.order.payment_method == "wallet":
        #     if self.userRemarkStatus == "Fully Return" or "Partially Return" and self.adminRemarkStatus == "Approved" and self.order.userRemark == "Fully Return" or "Partially Return":
        #         addWalletMoney = MyWallet(user=self.order.user, trasactionAmt=returnValue, transactionType="credit", orderNumber=self.order.order_number, status="active")
        #         addWalletMoney.save()
        super(OrderProductDetail, self).save(*args, **kwargs)

    # def txn_id_generator(self):
    #     return "TANVEE"+str(random.randint(1001234567, 9000102345))


# Delivery Executive live data details model created here because the circular import problem
class DeliveryExeLiveData(TimeStampMixin):
    DeliveryExeLiveStatus = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("intransit", "In Transit"),
    )
    delivery_exe = models.OneToOneField(DeliveryExecutive, on_delete=models.CASCADE, primary_key=False)
    live_map_lat = models.CharField("Map Lat", max_length=50, blank=False, null=False)
    live_map_lng = models.CharField("Map Lng", max_length=50, blank=False, null=False)
    live_oder = models.ForeignKey(OrderDetail, on_delete=models.CASCADE, blank=True, null=True)
    live_status = models.CharField("Live Status", max_length=20, choices=DeliveryExeLiveStatus, default="inactive")

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Delivery Exe. Live Data'

    def __str__(self):
        return str(self.delivery_exe)


class VendorOrderDetails(TimeStampMixin):
    statusChoice = (
        ("Waiting For Pickup", "Waiting For Pickup"),
        ("Picked Up", "Picked Up"),
        ("Delivered", "Delivered"),
    )

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=False, null=False)
    order = models.ForeignKey(OrderDetail, on_delete=models.CASCADE, blank=False, null=False)
    total_items = models.IntegerField("Total Items", default=0, blank=False, null=False)
    total_quantity = models.IntegerField("Total Quantity", default=0, blank=False, null=False)
    total_price = models.DecimalField("Total Price", max_digits=10, decimal_places=2, default=00.00, blank=False,
                                      null=False)
    total_tax = models.DecimalField("Total Tax", max_digits=10, decimal_places=2, default=00.00, blank=False,
                                    null=False)
    grand_total = models.DecimalField("Grand Total", max_digits=10, decimal_places=2, default=00.00, blank=True,
                                      null=False)
    order_status = models.CharField(max_length=50, choices=statusChoice, default="Waiting for Pickup", blank=False,
                                    null=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Vendor Orders'

    def __str__(self):
        return str(self.order)


# ReturnProduct Model
class ReturnProduct(TimeStampMixin):
    orderNumber = models.CharField(max_length=30, editable=True, blank=True, null=True)
    orderedProduct = models.ForeignKey(OrderProductDetail, on_delete=models.CASCADE, blank=True, null=True)
    return_id = models.CharField("Return Number", unique=True, max_length=25, editable=False, blank=True, null=True)
    returnQty = models.PositiveIntegerField("Return Quantity", null=True, blank=True, default=0)
    userRemarkStatus = models.CharField("User Remark Status",
                                        max_length=100,
                                        choices=userRemarkStatus,
                                        blank=False, null=False, default="None")
    refundAmt = models.DecimalField("Refund Amount", max_digits=10, decimal_places=2, default=00.00, blank=True,
                                    null=True)
    adminRemarkStatus = models.CharField("Admin Remark",
                                         max_length=100,
                                         choices=orderSuperAdminstatusChoice,
                                         blank=False, null=False, default="None")

    def __str__(self):
        return str(self.return_id)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Return Product'

    def save(self, *args, **kwargs):
        # self.price = self.product.price
        # total_amt = self.quantity * self.product.price
        # self.taxRate = decimal.Decimal(decimal.Decimal(total_amt)*(decimal.Decimal(self.product.tax)/100))
        # self.total_price = decimal.Decimal(total_amt) + self.taxRate

        if self.orderedProduct.order.offer_discount >= 0:

            returnProductAmtWithTaxandReturnQty = ((decimal.Decimal(self.orderedProduct.total_price) / decimal.Decimal(
                self.orderedProduct.quantity)) * (decimal.Decimal(self.returnQty)))
            returnQtyWithDiscountAmt = ((decimal.Decimal(self.orderedProduct.order.offer_discount)) / (
                decimal.Decimal(self.orderedProduct.order.totalOrderdQty))) * (decimal.Decimal(self.returnQty))
            returnValue = decimal.Decimal(returnProductAmtWithTaxandReturnQty - returnQtyWithDiscountAmt)
            self.refundAmt = returnValue
            print(returnProductAmtWithTaxandReturnQty)
            print(returnQtyWithDiscountAmt)
            print(self.refundAmt)
        else:
            returnValue = (decimal.Decimal(self.orderedProduct.total_price) / (
                decimal.Decimal(self.orderedProduct.quantity))) * (decimal.Decimal(self.returnQty))
            self.refundAmt = returnValue
            print(self.refundAmt)

        if not self.return_id:
            self.return_id = self.txn_id_generator()
            while ReturnProduct.objects.filter(return_id=self.return_id).exists():
                self.return_id = self.txn_id_generator()

        if self.orderedProduct.order.payment_method == "wallet" and self.orderedProduct.order.payment_status == "Paid":
            if self.userRemarkStatus == "Fully Return" and self.adminRemarkStatus == "Approved" and self.orderedProduct.order.userRemark == "Fully Return":
                # returnValue = decimal.Decimal(self.order.grand_total)
                addWalletMoney = MyWallet(user=self.orderedProduct.order.user, trasactionAmt=self.refundAmt,
                                          transactionType="credit", orderNumber=self.orderedProduct.order.order_number,
                                          status="active")
                addWalletMoney.save()

                orderObj = OrderDetail.objects.get(order_number=self.orderNumber)
                print(orderObj.order_number)
                orderObj.order_status = "Fully Return"
                orderObj.save()

            elif self.userRemarkStatus == "Partially Return" and self.adminRemarkStatus == "Approved" and self.orderedProduct.order.userRemark == "Partially Return":
                # returnValue = decimal.Decimal(self.order.grand_total)
                addWalletMoney = MyWallet(user=self.orderedProduct.order.user, trasactionAmt=self.refundAmt,
                                          transactionType="credit", orderNumber=self.orderedProduct.order.order_number,
                                          status="active")
                addWalletMoney.save()

                orderObj = OrderDetail.objects.get(order_number=self.orderNumber)
                print(orderObj.order_number)
                orderObj.order_status = "Partially Return"
                orderObj.save()

            elif self.userRemarkStatus == "Fully Return" and self.adminRemarkStatus == "Approved" and self.orderedProduct.order.userRemark == "Partially Return":
                # returnValue = decimal.Decimal(self.order.grand_total)
                addWalletMoney = MyWallet(user=self.orderedProduct.order.user, trasactionAmt=self.refundAmt,
                                          transactionType="credit", orderNumber=self.orderedProduct.order.order_number,
                                          status="active")
                addWalletMoney.save()

                orderObj = OrderDetail.objects.get(order_number=self.orderNumber)
                print(orderObj.order_number)
                orderObj.order_status = "Partially Return"
                orderObj.save()

            if self.userRemarkStatus == "Cancelled" and self.adminRemarkStatus == "Approved":
                addWalletMoney = MyWallet(user=self.orderedProduct.order.user, trasactionAmt=self.refundAmt,
                                          transactionType="credit", orderNumber=self.orderedProduct.order.order_number,
                                          status="active")
                addWalletMoney.save()

                orderObj = OrderDetail.objects.get(order_number=self.orderNumber)
                print(orderObj.order_number)
                orderObj.order_status = self.orderedProduct.order.userRemark
                orderObj.save()
            else:
                print("Something went to wrong")

        elif self.orderedProduct.order.payment_method == "COD":
            if self.orderedProduct.order.userRemark == self.orderedProduct.order.userRemark and self.adminRemarkStatus == "Approved":
                orderObj = OrderDetail.objects.get(order_number=self.orderNumber)
                print(orderObj.order_number)
                orderObj.order_status = self.orderedProduct.order.userRemark
                orderObj.save()

        elif self.orderedProduct.order.payment_method == "Razorpay" and self.orderedProduct.order.payment_status == "Paid":
            if self.orderedProduct.order.userRemark == self.orderedProduct.order.userRemark and self.adminRemarkStatus == "Approved":
                orderObj = OrderDetail.objects.get(order_number=self.orderNumber)
                print(orderObj.order_number)
                orderObj.order_status = self.orderedProduct.order.userRemark
                orderObj.save()
        else:
            print("Order Detail Not Found")

        super(ReturnProduct, self).save(*args, **kwargs)

    def txn_id_generator(self):
        return "TANVEE" + str(random.randint(1001234567, 9000102345))
