# encoding: utf-8

###########################################################################################################
#
#	by Olli Meier
#	Reporter Plugin: Show Node Close To Alignmentzone
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from math import atan2, cos, pi, sin, degrees

tolerance = 4

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

def closeEnough(value1, value2, tolerance):
	diff = value1 - value2

	if diff <= tolerance and diff >= -tolerance:
		return True
	else:
		return False

def drawTriangle(node):
	size = 5
	position = (node.x, node.y)
	x, y = position

	NSColor.colorWithCalibratedRed_green_blue_alpha_( 0.9, 0.1, 0.0, 0.85 ).set()
	t = NSAffineTransform.transform()
	t.translateXBy_yBy_(x, y)
	myPath = NSBezierPath.alloc().init()

	myPath.moveToPoint_(( 0, 0))
	myPath.relativeLineToPoint_( (10*size, 50*size))
	myPath.relativeLineToPoint_( (40*size, -40*size))

	myPath.closePath()
	myPath.transformUsingAffineTransform_(t)
	myPath.fill()

def nodeHasIssues(i, path, node):
	hasIssues = False
	# make it more spart with checking the node before and after if offcurve point or not.
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
			hasIssues = True

		if nodeBefore.type == 'offcurve' and nodeAfter.type == 'offcurve':
			if closeEnough(node.y, nodeBefore.y, 10) or closeEnough(node.y, nodeAfter.y, 10):
				hasIssues = True

		if nodeBefore.type == 'offcurve' and nodeAfter.type != 'offcurve':
			if closeEnough(node.y, nodeBefore.y, 10):
				hasIssues = True

		if nodeBefore.type != 'offcurve' and nodeAfter.type == 'offcurve':
			if closeEnough(node.y, nodeAfter.y, 10):
				hasIssues = True

	elif nodeBefore and not nodeAfter:
		if nodeBefore.type != 'offcurve':
			hasIssues = True

		if nodeBefore.type == 'offcurve':
			if closeEnough(node.y, nodeBefore.y, 10):
				hasIssues = True

	elif nodeAfter and not nodeBefore:
		if nodeAfter.type != 'offcurve':
			hasIssues = True

		if nodeAfter.type == 'offcurve':
			if closeEnough(node.y, nodeAfter.y, 10):
				hasIssues = True

	else:
		hasIssues = True

	if hasIssues:
		return True
	else:
		return False


class nodesCloseToZone(ReporterPlugin):

	def settings(self):
		self.menuName = Glyphs.localize({'en': u'Nodes Close To Zones'})
		self.generalContextMenus = [
			{'name': Glyphs.localize({'en': u'New Tab: Nodes Close to Zone'}), 'action': self.newTabNodesCloseToZone},
		]

	def drawText(self, layer):
		font = Glyphs.font
		for path in layer.paths:
			for i, node in enumerate(path.nodes):
				master = layer.associatedFontMaster()
				for zone in master.alignmentZones:
					if node.type != 'offcurve':
						if closeToArea(tolerance, zone.position, zone.size, node.y):
							if nodeHasIssues(i, path, node):
								self.drawTextAtPoint('Close to Alignmentzone', NSPoint(node.x, node.y))

	def drawShape(self, layer):
		#font = NSApplication.sharedApplication().font
		font = Glyphs.font
		for path in layer.paths:
			for i, node in enumerate(path.nodes):
				master = layer.associatedFontMaster()
				for zone in master.alignmentZones:
					if node.type != 'offcurve':
						if closeToArea(tolerance, zone.position, zone.size, node.y):
							if nodeHasIssues(i, path, node):
								drawTriangle(node)


	def newTabNodesCloseToZone(self):
		font = Glyphs.font
		collectNames = ''
		for g in font.glyphs:
			hasIssues = False
			for layer in g.layers:
				for path in layer.paths:
					for i, node in enumerate(path.nodes):
						master = layer.associatedFontMaster()
						for zone in master.alignmentZones:
							if node.type != 'offcurve':
								if closeToArea(tolerance, zone.position, zone.size, node.y):
									hasIssues = nodeHasIssues(i, path, node)
			if hasIssues:
				collectNames += '/%s' %g.name

		font.newTab(collectNames)

	def foreground(self, layer):
		self.drawText(layer)

	def inactiveLayerForeground(self, layer):
		self.drawShape(layer)

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
