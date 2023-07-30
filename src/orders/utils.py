order_status_choice = (
    ("Pending", 'Pending'),
    ("Order Placed", 'Order Placed'),
    ("On The Way", 'On The Way'),
    ("Delivered", 'Delivered'),
    ("Fully Return", 'Fully Return'),
    ("Partially Return", "Partially Return"),
    ("Replace", "Replace"),
    ("Cancelled", 'Cancelled'),
)


orderUserProductstatusChoice = (
    ("None", "None"),
    ("Pending", 'Pending'),
    ("Order Placed", 'Order Placed'),
    ("On The Way", 'On The Way'),
    ("Delivered", 'Delivered'),
    ("Cancelled", 'Cancelled'),
    # ("Returned", "Returned"),
    # ("Replace", "Replace"),
)

orderSuperAdminstatusChoice = (
    ("None", "None"),
    ("Rejected", 'Rejected'),
    ("Approved", "Approved"),
)


userRemarkStatus = (
    ("None", "None"),
    ("Fully Return", 'Fully Return'),
    ("Partially Return", "Partially Return"),
    ("Replace", "Replace"),
    ("Cancelled", 'Cancelled'),
     
)


save_address_as = (
    ("Home", "Home"),
    ("Work", "Work"),
)



payment_method = (
        ("Razorpay", "Razorpay"),
        ("COD", "Cash On Delivery"),
        ('wallet', 'Wallet'),
)

payment_status = (
        ("Pending", "Pending"),
        ("Paid", "Paid"),

)

DeliveryCharges_Name = (
    ("free_delivery", "Free Delivery"),
    ("delivery_charges", "Delivery Charges"),
)

