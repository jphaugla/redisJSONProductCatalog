class ProductTitle(object):
    # 			Brand			Quality			Category			Model Name			EAN			Market Presence			Family			Title
    def __init__(self, **kwargs) -> object:
        self.Partnumber = ""
        self.Brand = ""
        self.Quality = ""
        self.Category = ""
        self.ModelName = ""
        self.EAN = ""
        self.MarketPresence = ""
        self.Family = ""
        self.Title = ""
        for key in kwargs:
            if key == "Part number":
                objkey = "Partnumber"
            elif key == "Model Name":
                objkey = "ModelName"
            elif key == "Market Presence":
                objkey = "MarketPresence"
            else:
                objkey = key
            setattr(self, objkey, kwargs[key])

    def __str__(self):
        return str(self.__dict__)
