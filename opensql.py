#####################################
# OpenSQL API Wrapper
# Get an API Key at https://opensql.org/account
# Use `~.ODB.query()` for SQL Commands
# 
# Created by Johanna C. Heidel
# Note: Website is down at the moment
#####################################

import requests

class ProtocolType:
    opensql = "opensql"

class ODB:
    def __init__(self,auth):
        self.auth = auth
    
    def query(self,_query):
        """
        The query function takes a SQL query as an argument and returns the results of that query.
        
        :param self: Used to Access variables that belongs to the class.
        :param _query: Used to Pass the query string to the api.
        :return: The result of the query as a List.
        
        """
        
        res = requests.post("http://127.0.0.1:5000/api/sql",headers={
            'SECRET_KEY':self.auth,
            'QUERY_STRING':_query
        })
        return res.json().get('result') if 'result' in res.json() else res.json()
