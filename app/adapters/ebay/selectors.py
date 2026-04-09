"""CSS selectors for eBay sold listings pages.

These target the standard eBay search results layout.
If eBay changes their DOM, update selectors here.
"""

SEARCH_RESULTS_CONTAINER = "ul.srp-results"

LISTING_ITEM = "li.s-item"

LISTING_TITLE = ".s-item__title"
LISTING_PRICE = ".s-item__price"
LISTING_SOLD_DATE = ".s-item__title--tagblock .POSITIVE"
LISTING_LINK = ".s-item__link"
LISTING_IMAGE = ".s-item__image-img"

PAGINATION_NEXT = "a.pagination__next"
