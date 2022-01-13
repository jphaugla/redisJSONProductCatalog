class Cart(object):
    def __init__(self, **kwargs):
        self.key_name = ""
        self.path = ""
        self.cart_id = ""
        self.updated = ""
        self.quality = ""
        self.supplier_id = ""
        self.prod_id = ""
        self.catid = ""
        self.m_prod_id = ""
        self.ean_upc = ""
        self.on_market = ""
        self.country_market = ""
        self.model_name = ""
        self.cart_view = ""
        self.high_pic = ""
        self.high_pic_size = ""
        self.high_pic_width = ""
        self.high_pic_height = ""
        self.m_supplier_id = ""
        self.m_supplier_name = ""
        self.ean_upc_is_approved = ""
        self.Limited = ""
        self.Date_Added = ""
        self.key_name = ""
        self.category_name = ""
        self.parent_category_name = ""
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __str__(self):
        return str(self.__dict__)

