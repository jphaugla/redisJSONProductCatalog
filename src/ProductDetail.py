class ProductDetail(object):
    def __init__ (self):
        self.Code = ""
        self.HighPic = ""
        self.HighPicHeight = ""
        self.HighPicSize = ""
        self.HighPicWidth = ""
        self.ID = ""
        self.LowPic = ""
        self.LowPicHeight = ""
        self.LowPicSize = ""
        self.LowPicWidth = ""
        self.Name = ""
        self.IntName = ""
        self.LocalName = ""
        self.Pic500x500 = ""
        self.Pic500x500Height = ""
        self.Pic500x500Size = ""
        self.Pic500x500Width = ""
        self.Prod_id = ""
        self.Quality = ""
        self.ReleaseDate = ""
        self.ThumbPic = ""
        self.ThumbPicSize = ""
        self.Title = ""
        self.GeneratedIntTitle = ""
        self.GeneratedLocalTitle = ""
        self.BrandLocalTitle = ""

    def __init__(self, **kwargs):
        self.Code = ""
        self.HighPic = ""
        self.HighPicHeight = ""
        self.HighPicSize = ""
        self.HighPicWidth = ""
        self.ID = ""
        self.LowPic = ""
        self.LowPicHeight = ""
        self.LowPicSize = ""
        self.LowPicWidth = ""
        self.Name = ""
        self.IntName = ""
        self.LocalName = ""
        self.Pic500x500 = ""
        self.Pic500x500Height = ""
        self.Pic500x500Size = ""
        self.Pic500x500Width = ""
        self.Prod_id = ""
        self.Quality = ""
        self.ReleaseDate = ""
        self.ThumbPic = ""
        self.ThumbPicSize = ""
        self.Title = ""
        self.GeneratedIntTitle = ""
        self.GeneratedLocalTitle = ""
        self.BrandLocalTitle = ""
        self.key_name = ""
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __str__(self):
        return str(self.__dict__)

    def set_key(self):
            self.key_name = "prodDet:" + str(self.ID)

