from telnetlib import STATUS
from django.db import models
from common.models import User, TimeStampMixin
import random
import decimal
from django.db.models import Sum


trasactionTypeChoice = (
        ("debit", "Debit"),
        ("credit", "Credit"),
    )


WalletStatusChoice = (
    ("pending", "Pending"),
    ("active", "Active"),
    ("inactive", "Inactive"),
)

# My Wallet Model
class MyWallet(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    walletBalance = models.DecimalField("Wallet Balance", editable=False, blank=True, null=True, max_digits=12,
                                          decimal_places=2, default=0.00)
    
    transactionId = models.CharField(max_length=25, unique=True, editable=False, blank=True, null=True)
    trasactionAmt = models.DecimalField("Tnx Amount", editable=False, blank=False, null=False, max_digits=12,
                                          decimal_places=2, default=0.00)
    transactionType = models.CharField("Transaction Type", choices=trasactionTypeChoice, max_length=25, default="credit")
    orderNumber = models.CharField("Order Number", max_length=25, editable=False, blank=True, null=True)
    razopayPaymentId = models.CharField("Razor PaymentId", max_length=50, editable=False, blank=True, null=True)
    razopayOrderId = models.CharField("Razorpay Order Id", max_length=50, editable=False, blank=True, null=True)
    status = models.CharField("Wallet status", editable=False, choices=WalletStatusChoice, max_length=25, default="pending")



    def __str__(self):
        return str(self.user.first_name + " " + self.user.last_name) +"'s wallet"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'My Wallet'

    
    def calculateWalletBalance(self):
        totalCreditAmt = MyWallet.objects.filter(user=self.user, transactionType="credit", status = "active").aggregate(Sum('trasactionAmt'))['trasactionAmt__sum']
        totalDebitAmt = MyWallet.objects.filter(user=self.user, transactionType="debit", status = "active").aggregate(Sum('trasactionAmt'))['trasactionAmt__sum']
        totalCreditAmt = 0 if totalCreditAmt is None else totalCreditAmt
        totalDebitAmt = 0 if totalDebitAmt is None else totalDebitAmt
        walletBalance = float(totalCreditAmt)-float(totalDebitAmt)
        
        if self.status == "active":
            if self.transactionType == "credit":
                walletBalance+=float(self.trasactionAmt)
            else:
                walletBalance-=float(self.trasactionAmt)
        
        elif self.status == "pending":
            if self.transactionType == "credit":
                walletObject = MyWallet.objects.filter(user=self.user, status = "active").first()
                walletBalance = float(walletObject.walletBalance)
            else:
                walletBalance=float(self.walletBalance)
        else:
            if self.transactionType == "credit":
                walletBalance=float(self.walletBalance)
            else:
                walletBalance=float(self.walletBalance)
        #print(walletBalance)
        return walletBalance

    def save(self, *args, **kwargs):
        if not self.transactionId:
            self.transactionId = self.txn_id_generator()
            while MyWallet.objects.filter(transactionId=self.transactionId).exists():
                self.transactionId = self.txn_id_generator()

        self.walletBalance = self.calculateWalletBalance()
        super(MyWallet, self).save(*args, **kwargs)

    def txn_id_generator(self):
        return "WALTNX"+str(random.randint(1001234567, 9000102345))
