import os
import sys
import json
from pprint import pprint
from functools import reduce

# get people
# get Active people
# get user by guid
# check if user has a X friend
# change user balance

class UserController():
    
    def __init__(self, data_source = 'data.json'):
        self.load_data(data_source)
    
    def load_data(self, data_source):
        try:
            with open('data.json') as data_file:    
                self.users = json.load(data_file)
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            raise ValueError('Problem reading file')
            
    def get_users(self):
        return self.users
        
    def get_active_users(self):
        # @todo: read about Lambda
        # @todo: read about filter
        return list(filter(lambda user: user["isActive"] == True, self.users))
        
    def get_user_by_id(self, guid):
        # @todo: read about Lambda
        # @todo: read about next()
        return next(filter(lambda user: user["guid"] == guid, self.users))
        
    def check_if_user_has_friend(self, user, friend_name):
        friend = list(filter(lambda friend: friend["name"] == friend_name, user["friends"]))
        return len(friend) > 0
        
    def change_user_balance(self, user, balance_modif):
        balance =  float(user["balance"][1:].replace(',',''))
        balance += float(balance_modif)
        
        user["balance"] = balance
        # find this user by guid
        # change balance for the user in self.users
        return balance
    
    def balance_to_number(self, user):
        if type(user) is float:
            return user
        return float(user["balance"][1:].replace(',',''))
        
    def get_total_balance(self):
        balances = self.get_balances
        return reduce(lambda b1, b2: b1 + b2, balances)
      
users = UserController()

pprint(users.get_users())
print('————')
pprint(users.get_active_users())
print('——————')
swanson = users.get_user_by_id("cee8aaa9-eea3-45bf-b1c6-0f8595567a49")
pprint(swanson)
print('----')
print(users.check_if_user_has_friend(swanson, "Leigh Byrd"))
print(users.check_if_user_has_friend(swanson, "Leigh Brat"))
print('----')
print(users.change_user_balance(swanson, "-2000"))
pprint(swanson)
swanson2 = users.get_user_by_id("cee8aaa9-eea3-45bf-b1c6-0f8595567a49")
pprint(swanson2)
print(users.get_total_balance())
#print(users.change_user_balance(swanson, "-1"))

