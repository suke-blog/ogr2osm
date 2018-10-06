#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
from lxml import etree
from geom import *
from datetime import datetime


class Osmxml(object):
    def __init__(self, filename, sequentialOutputMode=False, \
                 noUploadFalse=True, osmVersion=False, timestamp=False,\
                 significantDigits=9, roundingDigits=7, addVisible=False):
        self.filename = filename
        self.sequentialOutputMode = sequentialOutputMode
        self.noUploadFalse = noUploadFalse
        self.significantDigits = significantDigits
        self.roundingDigits = roundingDigits
        self.addVisible = addVisible

        if sequentialOutputMode:
            self.fileNode = open(filename + '_nodes', 'w')
            self.fileWay = open(filename + '_ways', 'w+')
            self.fileRelation = open(filename + '_relations', 'w+')
        else:
            self.fileNode = open(filename, 'w')
            self.fileWay = self.fileRelation = self.fileNode

        self.attributes = {}
        if osmVersion:
            self.attributes.update({'version' : '1'})
        if timestamp:
            self.attributes.update({'timestamp' : datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')})
        if addVisible:
            self.attributes.update({'visible' : 'true'})
        self.isPython2 = sys.version_info < (3, 0)
        self.outputHeader()

    def outputHeader(self):
        f = self.fileNode
        if self.noUploadFalse:
            f.write('<?xml version="1.0"?>\n<osm version="0.6" generator="uvmogr2osm">\n')
        else:
            f.write('<?xml version="1.0"?>\n<osm version="0.6" upload="false" generator="uvmogr2osm">\n')

    def outputNodes(self, nodes, featuresmap):
        f = self.fileNode
        for node in nodes:
            xmlattrs = {'id': str(node.id), 'lat': str(node.y * 10 ** -self.significantDigits),
                        'lon': str(node.x * 10 ** -self.significantDigits)}
            xmlattrs.update(self.attributes)

            xmlobject = etree.Element('node', xmlattrs)

            if node in featuresmap:
                for (key, value) in featuresmap[node].tags.items():
                    tag = etree.Element('tag', {'k': key, 'v': value})
                    xmlobject.append(tag)
            if self.isPython2:
                f.write(etree.tostring(xmlobject))
            else:
                f.write(etree.tostring(xmlobject, encoding='unicode'))
            f.write('\n')

    def outputWays(self, ways, featuresmap):
        f = self.fileWay
        for way in ways:
            xmlattrs = {'visible': 'true', 'id': str(way.id)}
            xmlattrs.update(self.attributes)

            xmlobject = etree.Element('way', xmlattrs)

            for node in way.points:
                nd = etree.Element('nd', {'ref': str(node.id)})
                xmlobject.append(nd)
            if way in featuresmap:
                for (key, value) in featuresmap[way].tags.items():
                    tag = etree.Element('tag', {'k': key, 'v': value})
                    xmlobject.append(tag)

            if self.isPython2:
                f.write(etree.tostring(xmlobject))
            else:
                f.write(etree.tostring(xmlobject, encoding='unicode'))
            f.write('\n')

    def outputRelations(self, relations, featuresmap):
        f = self.fileRelation
        for relation in relations:
            xmlattrs = {'visible': 'true', 'id': str(relation.id)}
            xmlattrs.update(self.attributes)

            xmlobject = etree.Element('relation', xmlattrs)

            for (member, role) in relation.members:
                member = etree.Element('member', {'type': 'way', 'ref': str(member.id), 'role': role})
                xmlobject.append(member)

            tag = etree.Element('tag', {'k': 'type', 'v': 'multipolygon'})
            xmlobject.append(tag)
            if relation in featuresmap:
                for (key, value) in featuresmap[relation].tags.items():
                    tag = etree.Element('tag', {'k': key, 'v': value})
                    xmlobject.append(tag)

            if self.isPython2:
                f.write(etree.tostring(xmlobject))
            else:
                f.write(etree.tostring(xmlobject, encoding='unicode'))
            f.write('\n')


    def outputFooter(self):
        f = self.fileRelation
        f.write('</osm>')

    def output(self, geometries, features):
        # First, set up a few data structures for optimization purposes
        nodes = [geom for geom in geometries if type(geom) == Point]
        ways = [geom for geom in geometries if type(geom) == Way]
        relations = [geom for geom in geometries if type(geom) == Relation]
        featuresmap = {feature.geometry: feature for feature in features}
        self.outputNodes(nodes, featuresmap)
        self.outputWays(ways, featuresmap)
        self.outputRelations(relations, featuresmap)

    def finish(self):
        node = self.fileNode
        way = self.fileWay
        relation = self.fileRelation
        limit = 50000000

        self.outputFooter()
        # merge separate files
        if self.sequentialOutputMode:
            way.seek(0)
            data = way.read(limit)
            while data:
                node.write(data)
                data = way.read(limit)
            way.close()
            relation.seek(0)
            data = relation.read(limit)
            while data:
                node.write(data)
                data = relation.read(limit)
            relation.close()
            os.rename(self.filename + '_nodes', self.filename)
            os.remove(self.filename + '_ways')
            os.remove(self.filename + '_relations')
        node.close()
