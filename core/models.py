# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#from django.db import models


# Create your models here.
# from neo4django.db import models
# import neo4django

from bulbs.neo4jserver import Graph
# from bulbs.model import Node, Relationship
# from bulbs.property import String, Integer, DateTime
# from bulbs.utils import current_datetime
#
# class System(Node):
#     name = String(nullable=False);
#     # age = models.IntegerProperty()
#
#     # neighbour = models.Relationship('self',rel_type='is_connected')
#
# class isConnected(Relationship):
#     neighbour = DateTime(default=current_datetime, nullable=False)


from neomodel import (config, StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo, RelationshipFrom, Relationship)

config.DATABASE_URL = 'bolt://neo4j:Neo4j@localhost:7687'

class Machine(StructuredNode):
    uid = UniqueIdProperty()
    ip = StringProperty(unique_index=True)
    subnet = StringProperty(unique_index=True)
    hostname = StringProperty(unique_index=True)
    tag = StringProperty(unique_index=True)
    distance = IntegerProperty()
    queue = IntegerProperty()
    connected = Relationship('Machine','IS_CONNECTED')
    # objects = StructuredNode.Manager()
    # age = IntegerProperty(index=True, default=0)
    def __str__(self):
        return self.hostname
