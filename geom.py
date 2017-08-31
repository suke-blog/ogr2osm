# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2013 Paul Norman
# <penorman@mac.com>
# Released under the MIT license: http://opensource.org/licenses/mit-license.php

# Classes
class Geometry(object):
    elementIdCounter = 0
    elementIdCounterIncr = -1
    geometries = []
    def __init__(self):
        #self.id = getNewID()
        self.parents = set()
        Geometry.geometries.append(self)
    def replacejwithi(self, i, j):
        pass
    def addparent(self, parent):
        self.parents.add(parent)
    def removeparent(self, parent, shoulddestroy=True):
        self.parents.discard(parent)
        if shoulddestroy and len(self.parents) == 0:
            Geometry.geometries.remove(self)
    def getNewID(self):
        Geometry.elementIdCounter += Geometry.elementIdCounterIncr
        return Geometry.elementIdCounter

## Helper function to get a new ID
#def getNewID():
#    Geometry.elementIdCounter += Geometry.elementIdCounterIncr
#    return Geometry.elementIdCounter

class Point(Geometry):
    idCounter = None
    def __init__(self, x, y):
        Geometry.__init__(self)
        self.id = self.getNewID()
        self.x = x
        self.y = y
    def replacejwithi(self, i, j):
        pass
    def getNewID(self):
        if Point.idCounter is None:
            return super(Point, self).getNewID()
        else:
            Point.idCounter += Geometry.elementIdCounterIncr
            return Point.idCounter

class Way(Geometry):
    idCounter = None
    def __init__(self):
        Geometry.__init__(self)
        self.id = self.getNewID()
        self.points = []
    def replacejwithi(self, i, j):
        self.points = [i if x == j else x for x in self.points]
        j.removeparent(self)
        i.addparent(self)
    def getNewID(self):
        if Way.idCounter is None:
            return super(Way, self).getNewID()
        else:
            Way.idCounter += Geometry.elementIdCounterIncr
            return Way.idCounter

class Relation(Geometry):
    idCounter = None
    def __init__(self):
        Geometry.__init__(self)
        self.id = self.getNewID()
        self.members = []
    def replacejwithi(self, i, j):
        self.members = [(i, x[1]) if x[0] == j else x for x in self.members]
        j.removeparent(self)
        i.addparent(self)
    def getNewID(self):
        if Relation.idCounter is None:
            return super(Relation, self).getNewID()
        else:
            Relation.idCounter += Geometry.elementIdCounterIncr
            return Relation.idCounter

class Feature(object):
    features = []
    def __init__(self):
        self.geometry = None
        self.tags = {}
        Feature.features.append(self)
    def replacejwithi(self, i, j):
        if self.geometry == j:
            self.geometry = i
        j.removeparent(self)
        i.addparent(self)
