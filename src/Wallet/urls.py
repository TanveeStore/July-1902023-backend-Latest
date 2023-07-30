from django.urls import path
from Wallet import views

app_name = 'Wallet'

urlpatterns = [
    
    # Wallet urls
    path("customer/my-wallet/", views.WalletLastUpdatedTnxApi.as_view()),
    path("customer/wallet-transaction-history/", views.WalletTnxAllHistoryApi.as_view()),
    # path("customer/my-wallet_test/", views.AddUpdateMoneyAPIView.as_view()),
    # path("customer/wallet-transaction-history/", views.TransactionWalletDetailAPIView.as_view()),
    # path("customer/wallet-add-money/", views.AddUpdateWalletAmountAPIView.as_view()),
    path("customer/wallet-add-money/", views.AddMoneyInWallet.as_view()),
    path("customer/wallet-debit-money/", views.CreateOrderDebitWalletBalance.as_view()),
    path("customer/wallet-money-verifiy/", views.VerifyWalletMoneyAndActiveAPIView.as_view()),

]