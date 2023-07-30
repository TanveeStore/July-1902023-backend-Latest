from .models import Offer
from CartSystem.common import cart_system
from .serializers import OfferSerializer, OfferSerializerInPutValidatation
from datetime import datetime, timedelta
import time
import decimal

def getOfferDiscountAmnt(request):

    returnData={}

    if OfferSerializerInPutValidatation(data=request.data).is_valid():

        offerCode = request.data["offer_code"]

        offer = Offer.objects.filter(offer_code=offerCode, offer_status="active").first()

        if offer != None:
            offerSerializerData = OfferSerializer(offer, many=False).data

            expiredDateTime = offerSerializerData["valid_upto"]
            expiredDateTime = expiredDateTime[:10] + " " + expiredDateTime[11:19]
            currentDateTime = str(datetime.now())[0:19]
            expiredTime = time.mktime(time.strptime(expiredDateTime, "%Y-%m-%d %H:%M:%S"))
            currentTime = time.mktime(time.strptime(currentDateTime, "%Y-%m-%d %H:%M:%S"))

            timeDiff = expiredTime - currentTime

            if timeDiff < 0:
                returnData["status"]="warning"
                returnData["message"]="This Coupon is expired"
                return returnData, 406


            validfromDateTime = offerSerializerData["valid_from"]
            validfromDateTime = validfromDateTime[:10] + " " + validfromDateTime[11:19]
            currentDateTime = str(datetime.now())[0:19]
            validfromTime = time.mktime(time.strptime(validfromDateTime, "%Y-%m-%d %H:%M:%S"))
            currentTime = time.mktime(time.strptime(currentDateTime, "%Y-%m-%d %H:%M:%S"))

            timeDiff = currentTime - validfromTime

            if timeDiff < 0:
                returnData["status"] = "warning"
                returnData["message"] = "This Coupon can use after " + validfromDateTime
                return returnData, 406

            cartProductAmtDetails = cart_system.get_cart_amt_detail(request)
            cartTotal = cartProductAmtDetails["cartAmt"]+cartProductAmtDetails["cartTaxAmt"]
            if cartTotal < float(offerSerializerData["min_order_amt"]):
                returnData["status"] = "warning"
                returnData["message"] = "This Coupon can use in minimum order of " + offerSerializerData["min_order_amt"]
                return returnData, 406

            totalDiscount = decimal.Decimal(cartTotal) * (decimal.Decimal(float(offerSerializerData["discount"]))/ 100)

            if totalDiscount > cartTotal:
                totalDiscount = cartTotal

            if totalDiscount > float(offerSerializerData["max_discount_amt"]):
                totalDiscount = float(offerSerializerData["max_discount_amt"])

            returnData["status"] = "success"
            returnData["message"] = "Offer code applied success"
            returnData["discount"] = totalDiscount
            return returnData, 200

        else:
            returnData["status"] = "warning"
            returnData["message"] = "Invalid Offer code!"
            return returnData, 406
    else:
        returnData["status"] = "warning"
        returnData["message"] = "Invalid inputes"
        return returnData, 406