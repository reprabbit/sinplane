#!/usr/bin/python





# This is statement is required by the build system to query build info
if __name__ == '__build__':
	raise Exception

import string
__version__ = string.split('$Revision: 1.1.1.1 $')[1]
__date__ = string.join(string.split('$Date: 2007/02/15 19:25:21 $')[1:3], ' ')
__author__ = 'Tarn Weisner Burton <twburton@users.sourceforge.net>'

#
# Ported to PyOpenGL 2.0 by Tarn Weisner Burton 10May2001
#
# This code was created by Richard Campbell '99 (ported to Python/PyOpenGL by John Ferguson and Tony Colston 2000)
# To be honst I stole all of John Ferguson's code and just added the changed stuff for lesson 5. So he did most
# of the hard work.
#
# The port was based on the PyOpenGL tutorial module: dots.py  
#
# If you've found this code useful, please let me know (email John Ferguson at hakuin@voicenet.com).
# or Tony Colston (tonetheman@hotmail.com)
#
# See original source and C based tutorial at http:#nehe.gamedev.net
#
# Note:
# -----
# This code is not a good example of Python and using OO techniques.  It is a simple and direct
# exposition of how to use the Open GL API in Python via the PyOpenGL package.  It also uses GLUT,
# which in my opinion is a high quality library in that it makes my work simpler.  Due to using
# these APIs, this code is more like a C program using function based programming (which Python
# is in fact based upon, note the use of closures and lambda) than a "good" OO program.
#
# To run this code get and install OpenGL, GLUT, PyOpenGL (see http:#www.python.org), and NumPy.
# Installing PyNumeric means having a C compiler that is configured properly, or so I found.  For 
# Win32 this assumes VC++, I poked through the setup.py for Numeric, and chased through disutils code
# and noticed what seemed to be hard coded preferences for VC++ in the case of a Win32 OS.  However,
# I am new to Python and know little about disutils, so I may just be not using it right.
#
# NumPy is not a hard requirement, as I am led to believe (based on skimming PyOpenGL sources) that
# PyOpenGL could run without it. However preformance may be impacted since NumPy provides an efficient
# multi-dimensional array type and a linear algebra library.
#
# BTW, since this is Python make sure you use tabs or spaces to indent, I had numerous problems since I 
# was using editors that were not sensitive to Python.
#
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
from math import sin,sqrt,cos
import time

import numpy # or Numeric
# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0

# Rotation angle for the triangle. 
rtri = 0.0
upscale=1000.0
asize=30
dsize=asize+1
sqsiz=upscale*.1
elevate=8
xof=0.0
yof=0.0
ax=0
ay=0
vtilt=5.0
zoom=-900.0
ww=640
wh=480
# Rotation angle for the quadrilateral.
t = 0.0
lasttime=time.time()
dkeys={'a':False,'s':False,'d':False,'w':False,'e':False,'q':False,'r':False,'f':False,'x':False,'z':False,'p':False,}
dontskip=True
points=numpy.zeros([dsize,dsize,4], 'f')
wateron=True
waterl=5.0
floatlevel=waterl-1
waterl*=elevate
camback=0.0
playx=0.0
playy=0.0
playz=10.0
ptheta=0.0
planemode=False

walk=0.07


# A general OpenGL initialization function.  Sets all of the initial parameters. 

def InitGL(Width, Height):				# We call this right after our OpenGL window is created.
	global wh,ww
	ww=Width
	wh=Height
	glClearColor(0.0, 0.0, 0.0, 0.0)	# This Will Clear The Background Color To Black
	glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
	glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
	glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
	glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
	
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()					# Reset The Projection Matrix
	#Calculate The Aspect Ratio Of The Window
	gluPerspective(90.0, float(Width)/float(Height), 0.1, 5000.0)
	#glEnable(GL_LIGHTING)
	#glEnable(GL_LIGHT0)
	glMatrixMode(GL_MODELVIEW)
	glutWarpPointer(ww/2,wh/2)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
	global wh,ww
	ww=Width
	wh=Height
	if Height == 0:						# Prevent A Divide By Zero If The Window Is Too Small 
		Height = 1

	glViewport(0, 0, Width, Height)		# Reset The Current Viewport And Perspective Transformation
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(90.0, float(Width)/float(Height), 0.1, 5000.0)
	
	#glEnable(GL_LIGHTING)
	#glEnable(GL_LIGHT0)
	dontskip=True
	glMatrixMode(GL_MODELVIEW)
	glutWarpPointer(ww/2,wh/2)

# The main drawing function. 

def getoff(x,y,a):
	global points,ax,ay,dsize
	#ax,ay specify the corrdinates returned if x,y are zero
	tx=(x+ax)%dsize 	#true x
	ty=(y+ay)%dsize	#true y
	return points[tx][ty][a]
	
	
def putoff(x,y,a,value):
	global dsize,points,ax,ay
	tx=(x+ax)%dsize 	#true x
	ty=(y+ay)%dsize	#true y
	points[tx][ty][a]=value

def calcaray():
	global dsize
	for i in range(0,dsize):
		for j in range(0,dsize):
			calcpoint(i,j)

def calcpoint(i,j):
			x=((i-asize/2)+(xof-(xof%1.0)))/2
			y=((j-asize/2)+(yof-(yof%1.0)))/2
			z=zfunc(x,y)
			putoff(i,j,0, z*elevate)	
			putoff(i,j,1,(z/10)+.5) 			#red
			putoff(i,j,2,(z/10)%0.8+.48) 	#green
			putoff(i,j,3,sin(z)%0.08+.5)#blue
		
def zfunc(x,y):
			#z=(sin(x*.76)*.5+sin(y*1.42)*.4+sin(x*3.2141)*.4+sin(y*2.518)*.3) * 5
			#sin(x*6)*.2++sin(y*5.4)*.1
			xcom=sin(x*0.518)*.3+sin(x*1.85)*.3+sin(x*1.42)*.2+sin(x*2.22)*.2
			ycom=sin(y)*.2+sin(y*1.42)*.4+sin(y*1.6141)*.4+sin(y*2.31)*.3
			#rcom=sin(sqrt(x*x+y*y))
			dcom=sin(x+y)*.4+sin(x+y*2)*.4+sin(x+x+y)*.4
			z=(xcom+ycom+dcom)*8
		#	z=(sin(y*.75)+sin(x))*7					#simplify
			return z

def movearay(dir):
	global ax,ay,asize
	#j+
	#123
	#4 6
	#789i+
	if dir==2: 
	#j+
		ay+=1
#		iline(asize)
	if dir==8:
	#j-
		ay-=1
#		iline(0)
	if dir==4: 
	#i-
		ax-=1
#		jline(0)
	if dir==6: 
	#i+ x+ 0,j no longer relevant, recaluclate 21,j
		ax+=1
#		jline(asize)


	
def jline(i):
	global dsize
	for j in range(0,dsize):
		calcpoint(i,j)
		
def iline(j):
	global dsize
	for i in range(0,dsize):
		calcpoint(i,j)
	
def drawjet(x=0,y=0,z=0,scale=1.0):
		glColor3f(1.0+x,0.5,0.0)
		glBegin(GL_TRIANGLE_STRIP);
		glVertex3f(scale*0.0+x,scale*0.0+y,scale*-5.0+z)		#lead point
		glVertex3f(scale*2.0+x,scale*0.0+y,scale*0.0+z)				#right
		glColor3f(1.0,0.0,0.0)#COLOR
		glVertex3f(scale*0.0+x,scale*1.0+y,scale*0.0+z)			#top engine
		glColor3f(2.0,0.0,0.0)#COLOR
		glVertex3f(scale*-2.0+x,scale*0.0+y,scale*0.0+z)	#left
		glColor3f(0.5,0.5,0.0)#COLOR
		glVertex3f(scale*0.0+x,scale*0.0+y,scale*-5.0+z)		#lead point
		glVertex3f(scale*2.0+x,scale*0.0+y,scale*0.0+z)				#right 
		glEnd();				# Done Drawing The Jetplane

def drawtarget():
		glColor3f(1.0,0.0,0.0)
		glBegin(GL_TRIANGLE_STRIP);
		
		glVertex3f(1.0,0.0,-10.0) 
		glVertex3f(-1.0,0.0,-10.0)
		glVertex3f(0.1,0.1,-10.0)
		glVertex3f(0.1,0.0,-10.0)
		glVertex3f(0.0,-1.0,-10.0) 
		glVertex3f(0.1,1.0,-10.0)
		
		glEnd();				# Done Drawing The Jetplane
		
def drawaxis():
		glColor3f(0.0,0.0,1.0)
		glBegin(GL_TRIANGLE_STRIP);
		
		glVertex3f(1.0,0.0,0.0) 
		glVertex3f(1.0,-2000.0,0.0)
		glVertex3f(-1.0,0.0,0.0)
		glVertex3f(-1.0,-2000.0,0.0) 
		
		
		glEnd();				# Done Drawing The Jetplane

def DrawGLScene():
	global rtri, t,upscale,asize,sqsiz,elevate,xof,yof,points,dsize,lasttime,dkeys,vtilt,zoom
	global playx,playy,playz,ptheta,dontskip,wateron,waterl,floatlevel,walk,planemode,camback
	timesince=time.time()-lasttime
	t = timesince*7.0		 # Decrease The Rotation Variable For The Quad
	lasttime=time.time()
	oxo=xof%1.0
	oyo=yof%1.0
	ox=xof
	oy=yof
	
	
	
	
	
	
	if planemode==True:
		#print "plane"
		walk=0.3
		rotaccel=10.0
		skiprender=True
		pilot=False
		#print dkeys.keys()
		if dkeys['a']==True:
			ptheta-=t*rotaccel
			pilot=True
		if dkeys['d']==True:
			ptheta+=t*rotaccel
			skiprender=False
		if dkeys['w']==True:
			yof-=t*cos(-ptheta*3.14/180)*walk
			xof-=t*sin(-ptheta*3.14/180)*walk
			pilot=True
		if dkeys['s']==True:	
			yof+=t*cos(-ptheta*3.14/180)*walk
			xof+=t*sin(-ptheta*3.14/180)*walk
			pilot=True
		if dkeys['q']==True:
			rtri+=t*rotaccel	
			pilot=True
		if dkeys['e']==True:
			rtri-=t*rotaccel	
			pilot=True
		if dkeys['r']==True:
			vtilt-=t	* rotaccel/2
			pilot=True
		if dkeys['f']==True:
			vtilt+=t	* rotaccel/2	
			pilot=True	
		if dkeys['z']==True:
			zoom+=t	*rotaccel*3
			skiprender=False	
		if dkeys['x']==True:
			zoom-=t	*rotaccel	*3
			skiprender=False
		if dontskip==True:
			skiprender=False
			dontskip=False	
#		if dkeys['p']==True:
#			planemode=False
		yof-=t*cos(-ptheta*3.14/180)*walk*cos(-vtilt*3.14/180)
		xof-=t*sin(-ptheta*3.14/180)*walk*cos(-vtilt*3.14/180)
		
		
		
		zad=t*sin(-vtilt*3.14/180)*walk*elevate
		playz+=zad
		if pilot==False:
			##autopilot stuff
			vtilt*=(1-t*0.02)

			#print vtilt
			if playz<25:
				playz+=t*0.4
			if playz>50:
				playz-=t*0.4
		
		
		skiprender=False
		opz=playz
		#((j-asize/2)+(yof-(yof%1.0)))/2
		playx=((xof-asize/2)/2)
		playy=((yof-asize/2)/2)
		if playz<-zfunc(xof/2,yof/2):
			planemode=False
			dontskip=True
		walk=0.3
		#slope= playz-opz
		if playz<-floatlevel:
			playz=-floatlevel
			walk*=0.2
			planemode=False
			dontskip=True
		#elif playz>opz:
		#	walk-=slope*3
		#	print walk
		#if walk<0.01:
		#	walk=0.01

	else:
		#print "walk"
		rotaccel=10.0
		skiprender=True
		#print dkeys.keys()
		if dkeys['a']==True:
			yof+=t*sin(-ptheta*3.14/180)*walk
			xof-=t*cos(-ptheta*3.14/180)*walk
			skiprender=False
		if dkeys['d']==True:
			yof-=t*sin(-ptheta*3.14/180)*walk
			xof+=t*cos(-ptheta*3.14/180)*walk
			skiprender=False
		if dkeys['w']==True:
			yof-=t*cos(-ptheta*3.14/180)*walk
			xof-=t*sin(-ptheta*3.14/180)*walk
			skiprender=False
		if dkeys['s']==True:	
			yof+=t*cos(-ptheta*3.14/180)*walk
			xof+=t*sin(-ptheta*3.14/180)*walk
			skiprender=False
		if dkeys['q']==True:
			rtri+=t*rotaccel	
			skiprender=False
		if dkeys['e']==True:
			rtri-=t*rotaccel	
			skiprender=False
		if dkeys['r']==True:
			vtilt-=t	* rotaccel/2
			skiprender=False
		if dkeys['f']==True:
			vtilt+=t	* rotaccel/2	
			skiprender=False	
		if dkeys['z']==True:
			zoom+=t	*rotaccel*3
			skiprender=False	
		if dkeys['x']==True:
			zoom-=t	*rotaccel	*3
			skiprender=False
		if dontskip==True:
			skiprender=False
			dontskip=False	
		if dkeys['p']==True:
			planemode=True

		opz=playz
		#((j-asize/2)+(yof-(yof%1.0)))/2
		playx=((xof-asize/2)/2)
		playy=((yof-asize/2)/2)
		playz=-zfunc(xof/2,yof/2)+2
		walk=0.07
		slope= playz-opz
		if playz<-floatlevel:
			playz=-floatlevel
			walk*=0.3
	#	elif playz>opz:
	#		walk-=slope*3
		#	print walk
		if walk<0.01:
			walk=0.01
		
	


	cxo=xof%1.0
	cyo=yof%1.0
	if skiprender==True:
		time.sleep(.01)
		return 1
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)	# Clear The Screen And The Depth Buffer
	glLoadIdentity()					# Reset The View
	
	
	if planemode==False:
		drawtarget()
#	glRotatef(rtri,0.0,1.0,0.0);			# Rotate The Pyramid On It's Y Axis
	# flatten
	
#		if camback>0.0:
		camback=0.0
	#	glTranslatef(0,0,-camback);
		
		glRotatef(vtilt,1.0,0.0,0.0);				# tilt		
	if planemode==True:
		if camback<300.0:
			camback+=8
		
		glTranslatef(0,-camback/3,-camback);
		glRotatef(20,1.0,0.0,0.0);
		glRotatef(-vtilt,1.0,0.0,0.0);
		glScalef(5,5,5)
		drawjet()
		glScalef(0.20,0.20,0.20)
		glRotatef(vtilt,1.0,0.0,0.0);
		
		
		drawaxis()

		
		
	
	glRotatef(ptheta,0.0,1.0,0.0);			# Rotate The Pyramid On It's Y Axis
	glRotatef(90,1.0,0.0,0.0);		



	glTranslatef(0,0,playz*elevate);				# Move up above terrain


	
#	glTranslatef(sqsiz*asize/2,sqsiz*asize/2,0);
#	glBegin(GL_TRIANGLES);					# Start Drawing The Pyramid
	# Set up the stationary light
	
	#light = [ 150.0, 150.0, 100.0, 1.0 ]  #// Position of light
	#glLightfv(GL_LIGHT0, GL_POSITION, light)
	#glLightfv(GL_LIGHT0, GL_AMBIENT, [1.0,1.0,1.0,1.0])
#	glBegin(GL_QUADS)				
	# Front Face (note that the texture's corners have to match the quad's corners)

#	calcaray()
#	iline(0)
#	iline(20)	
#	jline(0)
#	jline(20)	
#	if xof%1.0<oxo and xof>ox and yof%1.0<oyo and yof>oy:
#		movearay(3)
	if cyo<oyo and yof>oy:
		movearay(2)
	elif cyo>oyo and yof<oy:
		movearay(8)

	if cxo<oxo and xof>ox:
		movearay(6)
	
#	elif xof%1.0>oxo and xof<ox and yof%1.0>oyo and yof<oy:
#		movearay(7)
	elif cxo>oxo and xof<ox:
		movearay(4)

	iline(0)
	iline(asize)	
	jline(0)
	jline(asize)	

#	elif xof%1.0>oxo and xof<ox and yof%1.0<oyo and yof>oy:
#		movearay(1)
#	elif xof%1.0<oxo and xof>ox and yof%1.0>oyo and yof<oy:
#		movearay(9)
	if wateron==True:
		glBegin(GL_QUADS)
		glColor3f(0,0,.5)
		waters=((asize)*sqsiz)
		glVertex3f(waters,waters,waterl)
		glVertex3f(waters,-waters,waterl)
		glVertex3f(-waters,-waters,waterl)
		glVertex3f(-waters,waters,waterl)
		glEnd();				# Done Drawing The Cube
	
	
	

	for i in range(0,asize):
		glBegin(GL_TRIANGLE_STRIP);
		for j in range(0,asize):
			y=((j-asize/2-(yof%1.0))/(10/upscale))
			x=((i-asize/2-(xof%1.0))/(10/upscale))
			
			glColor3f(getoff(i,j,1),getoff(i,j,2),getoff(i,j,3))
			glVertex3f(x,y,	getoff(i,j,0))
			
	#		glColor3f(getoff(i,j+1,1),getoff(i,j+1,2),getoff(i,j+1,3))
	#		glVertex3f(x,y+sqsiz,	getoff(i,j+1,0))

			glColor3f(getoff(i+1,j,1),getoff(i+1,j,2),getoff(i+1,j,3))
			glVertex3f(x+sqsiz,y,	getoff(i+1,j,0))
			
	#	glColor3f(getoff(i+1,j+1,1),getoff(i+1,j+1,2),getoff(i+1,j+1,3))
	#	glVertex3f(x+sqsiz,y+sqsiz,getoff(i+1,j+1,0))
		glEnd();				# Done Drawing The Cube

	for i in range(-asize/2,asize/2,10):
		for j in range(-asize/2,asize/2,10):
			jox=xof-(xof%10)+i
			joy=yof-(yof%10)+j
			jy=(sin(jox)*3+5)	
			jx=(sin(joy*2.345)*4+1)
			jy-=(jy%1.0)#round to integers
			jx-=(jx%1.0)
			pjx=(jox+jx)
			pjy=(joy+jy)
			fjx=(jx-xof+jox)*sqsiz
			fjy=(jy-yof+joy)*sqsiz
			fjz=-zfunc(pjx/2,pjy/2)*elevate*-1.0	
			#print fjz
			if fjz<-floatlevel:
				drawjet(fjx,fjy,fjz,10.0)
				if planemode==False:
					#print abs(playx-fjx),abs(playy-fjy)
					if abs(playx-fjx)-10<30.0 and abs(playy-fjy)-10<30.0:
						planemode=True
						vtilt=-15
	


	# What values to use?  Well, if you have a FAST machine and a FAST 3D Card, then
	# large values make an unpleasant display with flickering and tearing.  I found that
	# smaller values work better, but this was based on my experience.



	#  since this is double buffered, swap the buffers to display what just got drawn. 
	glutSwapBuffers()

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
	global dkeys
	# If escape is pressed, kill everything.
	if args[0] == ESCAPE:
		sys.exit()
	dkeys[args[0]]=True


def Mousemove(x,y):
	glutSetCursor(GLUT_CURSOR_NONE) 
	global ww,wh,vtilt,ptheta,dontskip
	mx=ww/2-x
	my=wh/2-y
	ptheta=ptheta-mx/10.0
	vtilt=vtilt-my/10.0
	#print mx,my
	dontskip=True
	
	#DrawGLScene()
	
	if mx!=0 or my!=0:
		glutWarpPointer(ww/2,wh/2)
		
def Mouserelease(x,y):
	glutSetCursor(GLUT_CURSOR_INHERIT) 	

def keyReleased(*args):
	global dkeys
	# If escape is pressed, kill everything.
	dkeys[args[0]]=False
		
		


def main():
	global window
	glutInit(sys.argv)
	calcaray()
	# Select type of Display mode:   
	#  Double buffer 
	#  RGBA color
	# Alpha components supported 
	# Depth buffer
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
	
	# get a 640 x 480 window 
	glutInitWindowSize(640, 480)
	
	# the window starts at the upper left corner of the screen 
	glutInitWindowPosition(0, 0)
	
	# Okay, like the C version we retain the window id to use when closing, but for those of you new
	# to Python (like myself), remember this assignment would make the variable local and not global
	# if it weren't for the global declaration at the start of main.
	window = glutCreateWindow("Landscape")

   	# Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
	# set the function pointer and invoke a function to actually register the callback, otherwise it
	# would be very much like the C version of the code.	
	glutDisplayFunc(DrawGLScene)
	
	# Uncomment this line to get full screen.
	# glutFullScreen()

	# When we are doing nothing, redraw the scene.
	glutIdleFunc(DrawGLScene)
	
	# Register the function called when our window is resized.
	glutReshapeFunc(ReSizeGLScene)
	
	# Register the function called when the keyboard is pressed.  
	glutKeyboardFunc(keyPressed)
	glutKeyboardUpFunc(keyReleased)
	glutMotionFunc(Mousemove)
	glutPassiveMotionFunc(Mouserelease)
	# Initialize our window. 
	InitGL(640, 480)

	# Start Event Processing Engine	
	glutMainLoop()

# Print message to console, and kick off the main to get it rolling.
print "Hit ESC key to quit."
main()
		
