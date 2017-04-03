# -*- coding: utf-8 -*-

from scrapy.item import Item,Field

#Item Class to store Data
class CollegeInfoItem(Item):
    University = Field()
    Website=Field()
    Email=Field()
    Type=Field()
    Fax=Field()
    Telephone=Field()
    Address=Field()
    City=Field()
    Credential_Type=Field()
    Joint_Credential_Type = Field()
    Toll_Free=Field()
    Program_Level=Field()
    Joint_Program_Level=Field()


