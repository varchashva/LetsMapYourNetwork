# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
    action = StringProperty()
    enum = StringProperty()
    cloud = StringProperty()
    connected = Relationship('Machine','IS_CONNECTED')
    def __str__(self):
        return self.hostname
