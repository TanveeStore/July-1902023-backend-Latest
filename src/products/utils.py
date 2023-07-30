availability_choice = (
    ('in_stock', 'In stock'),
    ('out_of_stock', 'Out of stock'),
)


size = (
    (1, 'XS'),
    (2, 'SM'),
    (3, 'M'),
    (4, 'L'),
    (5, 'XL'),
    (6, 'XXL'),
    (7, 'XXXL'),
)


notice_status = (
    (True, "Send Notice Now"),
    (False, "Don't Send Notice Now"),
)

importance_status = (
    (1, "Critical"),
    (2, "Very Important"),
    (3, "Important")
)

soft_delete = (
    (True, "Soft Deleted"),
    (False, "Not Deleted")
)
