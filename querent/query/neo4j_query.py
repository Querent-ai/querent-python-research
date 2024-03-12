import networkx as nx
import networkx
import pandas as pd
from pyvis.network import Network

from neo4j import GraphDatabase
from querent.logging.logger import setup_logger


class Neo4jConnection:
    
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        self.logger = setup_logger(__name__, "Neo4jConnection")
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(user, pwd))
        except Exception as e:
            self.logger.error("Failed to create the driver:", e)
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
        
    def query(self, query, parameters=None, db=None):
        session = None
        response = []
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            result = session.run(query, parameters)
            for record in result:
                response.append(record)
        except Exception as e:
            self.logger.error("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response
