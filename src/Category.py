class Category(object):
    CATEGORY_PREFIX = "Category:"

    def __init__(self):
        self.ID = None
        self.LowPic = ""
        self.ThumbPic = ""
        self.Name = ""
        self.Score = ""
        self.ParentCategoryName = ""
        self.ParentCategoryID = ""

    def __str__(self):
        return str(self.__dict__)

    def set_category_name(self, category_name):
        self.Name = category_name

    def get_key(self):
        return str(self.CATEGORY_PREFIX + self.ID)
