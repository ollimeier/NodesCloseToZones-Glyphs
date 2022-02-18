# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#	by Olli Meier
#	Reporter Plugin: Show Nodes Close To Alignmentzone
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################

import objc
from AppKit import NSRange
from GlyphsApp import *
from GlyphsApp.plugins import *
from math import atan2, cos, pi, sin, degrees

tolerance = 4

@objc.python_method
def closeToArea(tol, pos, size, y):

	if size >= 0:
		pos1 = pos - tol
		pos2 = pos

		size1 = pos + size
		size2 = size1 + tol
	
		if y >= pos1 and y < pos2 or y > size1 and y <= size2:
			return True
		else:
			return False
	else:
		pos1 = pos
		pos2 = pos + tol	

		size1 = pos + size - tol
		size2 = pos + size 
	
		if (y > pos1 and y <= pos2) or (y >= size1 and y < size2):
			return True
		else:
			return False

@objc.python_method
def closeEnough(value1, value2, tolerance):
	diff = value1 - value2

	if diff <= tolerance and diff >= -tolerance:
		return True
	else:
		return False

@objc.python_method
def drawTriangle(node, scale):
	size = 1 * scale
	position = (node.x, node.y)
	x, y = position

	NSColor.colorWithCalibratedRed_green_blue_alpha_( 0.9, 0.1, 0.0, 0.85 ).set()
	t = NSAffineTransform.transform()
	t.translateXBy_yBy_(x, y)
	myPath = NSBezierPath.alloc().init()

	myPath.moveToPoint_( (0,0) )
	myPath.relativeLineToPoint_( (10*size, 50*size) )
	myPath.relativeLineToPoint_( (40*size, -40*size) )

	myPath.closePath()
	myPath.transformUsingAffineTransform_(t)
	myPath.fill()

@objc.python_method
def extremPoint(i, path, node):
	xPoint = False
	# make it more smart with checking the node before and after if offcurve point or not.
	try:
		nodeBefore = path.nodes[i-1]
	except:
		nodeBefore = False
	try:
		nodeAfter = path.nodes[i+1]
	except:
		nodeAfter = False

	if (nodeBefore and nodeAfter):
		if nodeBefore.type != 'offcurve' and nodeAfter.type != 'offcurve':
			if closeEnough(node.y, nodeBefore.y, 20) or closeEnough(node.y, nodeAfter.y, 20):
				xPoint = True

		if nodeBefore.type == 'offcurve' and nodeAfter.type == 'offcurve':
			if closeEnough(node.y, nodeBefore.y, 10) or closeEnough(node.y, nodeAfter.y, 10):
				xPoint = True

		if nodeBefore.type == 'offcurve' and nodeAfter.type != 'offcurve':
			if closeEnough(node.y, nodeBefore.y, 10):
				xPoint = True

		if nodeBefore.type != 'offcurve' and nodeAfter.type == 'offcurve':
			if closeEnough(node.y, nodeAfter.y, 10):
				xPoint = True

	elif nodeBefore and not nodeAfter:
		if nodeBefore.type != 'offcurve':
			xPoint = True

		if nodeBefore.type == 'offcurve':
			if closeEnough(node.y, nodeBefore.y, 10):
				xPoint = True

	elif nodeAfter and not nodeBefore:
		if nodeAfter.type != 'offcurve':
			xPoint = True

		if nodeAfter.type == 'offcurve':
			if closeEnough(node.y, nodeAfter.y, 10):
				xPoint = True

	else:
		xPoint = True

	if xPoint:
		return True
	else:
		return False

@objc.python_method
def _get_tolerance(master):
	'''
	Based on GlyphsApp 3 stems, adjust the tolerance
	:param master: GlyphsApp master
	:return: value of stems thinkness (avarage) or None
	'''
	stem_values = []
	try:
		for s in master.stems:
			stem_values.append(s)
	except Exception:
		# return None if GlyphsApp version does not support .stems
		pass

	if len(stem_values) == 0:
		return tolerance

	avarage = sum(stem_values) / len(stem_values)
	if avarage >= tolerance:
		return tolerance

	avarage = avarage - 1
	if avarage < 1:
		avarage = 1

	return avarage

@objc.python_method
def allNodesWithIssues(layer):
	nodes = []

	master = layer.associatedFontMaster()
	if layer.hasCorners():
		layer = layer.copyDecomposedLayer() #orphan layer

	tol = _get_tolerance(master)

	l_copy = layer.copy()
	l_copy.removeOverlap()

	for path in l_copy.paths:
		for i, node in enumerate(path.nodes):
			if node.type != 'offcurve':
				for zone in master.alignmentZones:
					if closeToArea(tol, zone.position, zone.size, node.y):
						if extremPoint(i, path, node):
							nodes.append(node)
	return nodes

class nodesCloseToZone(ReporterPlugin):
	
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': 'Nodes Close To Zones',
			'de': 'Punkte knapp neben Zonen',
			'fr': 'nœuds proches des zones',
			'es': 'nodos cerca de zonas',
			'pt': 'nós perto de zonas',
			})
		self.generalContextMenus = [
			{
				'name': Glyphs.localize({
					'en': 'New Tab with %s'%self.menuName,
					'de': 'Neuer Tab mit Punkten knapp neben Zonen',
					'fr': 'Nouveau onglet avec %s'%self.menuName,
					'es': 'Nuevo pestaña con %s'%self.menuName,
					'pt': 'Nova guia %s'%self.menuName,
					}), 
				'action': self.newTabNodesCloseToZone_,
			},
		]
		self.warningString = Glyphs.localize({
			'en': 'close to zone',
			'de': 'knapp neben Zone',
			'fr': 'proche de zone',
			'es': 'cerca de zona',
			'pt': 'perto de zona',
			})

	@objc.python_method
	def drawText(self, layer):
		nodesWithIssues = allNodesWithIssues(layer)
		for node in nodesWithIssues:
			self.drawTextAtPoint(self.warningString,node.position)
	
	@objc.python_method
	def drawShape(self, layer):
		scale =  1 #0.5 / self.getScale()
		nodesWithIssues = allNodesWithIssues(layer)
		for node in nodesWithIssues:
			drawTriangle(node, scale)

	def newTabNodesCloseToZone_(self, sender=None):
		font = Glyphs.font
		collectNames = []
		collectLayerID = []
		for g in font.glyphs:
			for layer in g.layers:
				if allNodesWithIssues(layer):
					collectNames.append('/%s' % g.name)
					collectLayerID.append(layer.layerId)

		Glyphs.currentDocument.windowController().addTabWithString_("".join(collectNames))
		for i, character in enumerate(collectNames):
			rangeHighest = NSRange()
			rangeHighest.location = i
			rangeHighest.length = 1
			currentEditViewController = Glyphs.currentDocument.windowController().activeEditViewController()
			currentTab = currentEditViewController.graphicView()
			Attributes = { "GSLayerIdAttrib": collectLayerID[i] }
			currentTab.textStorage().text().addAttributes_range_( Attributes, rangeHighest )

	@objc.python_method
	def foreground(self, layer):
		self.drawText(layer)
	
	@objc.python_method
	def inactiveLayerForeground(self, layer):
		self.drawShape(layer)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
