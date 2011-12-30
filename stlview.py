#!/usr/bin/python
import os
import wx,math,stltool
from wx import glcanvas
import time
import threading
        
import pyglet
pyglet.options['shadow_window'] = False
pyglet.options['debug_gl'] = False
from pyglet import gl
from pyglet.gl import *

class GLPanel(wx.Panel):

    '''A simple class for using OpenGL with wxPython.'''

    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        # Forcing a no full repaint to stop flickering
        style = style | wx.NO_FULL_REPAINT_ON_RESIZE
        #call super function
        super(GLPanel, self).__init__(parent, id, pos, size, style)

        #init gl canvas data
        self.GLinitialized = False
        attribList = (glcanvas.WX_GL_RGBA, # RGBA
                      glcanvas.WX_GL_DOUBLEBUFFER, # Double Buffered
                      glcanvas.WX_GL_DEPTH_SIZE, 24) # 24 bit
        # Create the canvas
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.canvas = glcanvas.GLCanvas(self, attribList=attribList)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        #self.sizer.Fit(self)
        self.Layout()
        
        # bind events
        self.canvas.Bind(wx.EVT_ERASE_BACKGROUND, self.processEraseBackgroundEvent)
        self.canvas.Bind(wx.EVT_SIZE, self.processSizeEvent)
        self.canvas.Bind(wx.EVT_PAINT, self.processPaintEvent)

    #==========================================================================
    # Canvas Proxy Methods
    #==========================================================================
    def GetGLExtents(self):
        '''Get the extents of the OpenGL canvas.'''
        return self.canvas.GetClientSize()

    def SwapBuffers(self):
        '''Swap the OpenGL buffers.'''
        self.canvas.SwapBuffers()

    #==========================================================================
    # wxPython Window Handlers
    #==========================================================================
    def processEraseBackgroundEvent(self, event):
        '''Process the erase background event.'''
        pass # Do nothing, to avoid flashing on MSWin

    def processSizeEvent(self, event):
        '''Process the resize event.'''
        if self.canvas.GetContext():
            # Make sure the frame is shown before calling SetCurrent.
            self.Show()
            self.canvas.SetCurrent()
            size = self.GetGLExtents()
            self.winsize = (size.width, size.height)
            self.width, self.height = size.width, size.height
            self.OnReshape(size.width, size.height)
            self.canvas.Refresh(False)
        event.Skip()

    def processPaintEvent(self, event):
        '''Process the drawing event.'''
        self.canvas.SetCurrent()
        
        # This is a 'perfect' time to initialize OpenGL ... only if we need to
        if not self.GLinitialized:
            self.OnInitGL()
            self.GLinitialized = True
        
        self.OnDraw()
        event.Skip()
        
    def Destroy(self):
        #clean up the pyglet OpenGL context
        #self.pygletcontext.destroy()
        #call the super method
        super(wx.Panel, self).Destroy()

    #==========================================================================
    # GLFrame OpenGL Event Handlers
    #==========================================================================
    def OnInitGL(self):
        '''Initialize OpenGL for use in the window.'''
        #create a pyglet context for this panel
        self.pmat=(GLdouble * 16)()
        self.mvmat=(GLdouble * 16)()
        self.pygletcontext = Context(current_context)
        self.pygletcontext.set_current()
        self.dist=1000
        self.vpmat=None
        #normal gl init
        glClearColor(0, 0, 0, 0.5)
        glColor3f(1, 0, 0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        # Uncomment this line for a wireframe view
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    
        # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
        # but this is not the case on Linux or Mac, so remember to always 
        # include it.
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        
        # Define a simple function to create ctypes arrays of floats:
        def vec(*args):
            return (GLfloat * len(args))(*args)
    
        glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
        glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
        glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))
    
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 200)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, vec(0,0.1,0,0.9))
        #create objects to draw
        #self.create_objects()
                                         
                                         
                                         
    def OnReshape(self, width, height):
        '''Reshape the OpenGL viewport based on the dimensions of the window.'''
        
        if not self.GLinitialized:
            self.OnInitGL()
            self.GLinitialized = True
        self.pmat=(GLdouble * 16)()
        self.mvmat=(GLdouble * 16)()
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., width / float(height), .1, 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        #pyglet stuff
        self.vpmat=(GLint * 4)(0,0,*list(self.GetClientSize()))
        glGetDoublev(GL_PROJECTION_MATRIX,self.pmat)
        glGetDoublev(GL_MODELVIEW_MATRIX,self.mvmat)
        #glMatrixMode(GL_PROJECTION)
        
        
        # Wrap text to the width of the window
        if self.GLinitialized:
            self.pygletcontext.set_current()
            self.update_object_resize()
            
    def OnDraw(self, *args, **kwargs):
        """Draw the window."""
        #clear the context
        self.canvas.SetCurrent()
        self.pygletcontext.set_current()
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        #draw objects
        self.draw_objects()
        #update screen
        self.SwapBuffers()
            
    #==========================================================================
    # To be implemented by a sub class
    #==========================================================================
    def create_objects(self):
        '''create opengl objects when opengl is initialized'''
        pass
        
    def update_object_resize(self):
        '''called when the window recieves only if opengl is initialized'''
        pass
        
    def draw_objects(self):
        '''called in the middle of ondraw after the buffer has been cleared'''
        pass
       
class stlview(object):
    def __init__(self, facets, batch):
        # Create the vertex and normal arrays.
        vertices = []
        normals = []

        for i in facets:
            for j in i[1]:
                vertices.extend(j)
                normals.extend(i[0])

        # Create a list of triangle indices.
        indices = range(3*len(facets))#[[3*i,3*i+1,3*i+2] for i in xrange(len(facets))]
        #print indices[:10]
        self.vertex_list = batch.add_indexed(len(vertices)//3, 
                                             GL_TRIANGLES,
                                             None,#group,
                                             indices,
                                             ('v3f/static', vertices),
                                             ('n3f/static', normals))
       
    def delete(self):
        self.vertex_list.delete()

class gcview(object):
    def __init__(self, lines, batch, w=0.5, h=0.5):
        # Create the vertex and normal arrays.
        vertices = []
        normals = []
        self.prev=[0.001,0.001,0.001,0.001]
        self.fline=1
        f=open("20cube_export.gcode")
        lines=list(f)
        f.close()
        self.layers={}
        lines=[self.transform(i) for i in lines]
        lines=[i for i in lines if i is not None]
        layertemp={}
        lasth=None
        for i in lines:
            if i[0][2] not in layertemp:
                layertemp[i[0][2]]=[[],[]]
                if lasth is not None:
                    self.layers[lasth]=pyglet.graphics.Batch()
                    indices = range(len(layertemp[lasth][0]))#[[3*i,3*i+1,3*i+2] for i in xrange(len(facets))]
                    self.layers[lasth].add_indexed(len(layertemp[lasth][0])//3, 
                                             GL_TRIANGLES,
                                             None,#group,
                                             indices,
                                             ('v3f/static', layertemp[lasth][0]),
                                             ('n3f/static', layertemp[lasth][1]))
                lasth=i[0][2]
            def vdiff(v,o):
                return map(lambda x,y:x-y,v,o)
        
            spoints,epoints,S,E=self.genline(i,h,w)
            for j in xrange(8):
                
                layertemp[i[0][2]][0].extend(spoints[(j+1)%8])
                layertemp[i[0][2]][1].extend(vdiff(spoints[(j+1)%8],S))
                layertemp[i[0][2]][0].extend(epoints[(j)%8])
                layertemp[i[0][2]][1].extend(vdiff(epoints[(j)%8],E))
                layertemp[i[0][2]][0].extend(spoints[j])
                layertemp[i[0][2]][1].extend(vdiff(spoints[j],S))
                layertemp[i[0][2]][0].extend(epoints[(j)])
                layertemp[i[0][2]][1].extend(vdiff(epoints[(j)],E))
                layertemp[i[0][2]][0].extend(spoints[(j+1)%8])
                layertemp[i[0][2]][1].extend(vdiff(spoints[j],S))
                layertemp[i[0][2]][0].extend(epoints[(j+1)%8])
                layertemp[i[0][2]][1].extend(vdiff(epoints[(j+1)%8],E))
                
                vertices.extend(spoints[(j+1)%8])
                normals.extend(vdiff(spoints[(j+1)%8],S))
                vertices.extend(epoints[(j)%8])
                normals.extend(vdiff(epoints[(j)%8],E))
                vertices.extend(spoints[j])
                normals.extend(vdiff(spoints[j],S))
                vertices.extend(epoints[(j)])
                normals.extend(vdiff(epoints[(j)],E))
                vertices.extend(spoints[(j+1)%8])
                normals.extend(vdiff(spoints[j],S))
                vertices.extend(epoints[(j+1)%8])
                normals.extend(vdiff(epoints[(j+1)%8],E))
        # Create a list of triangle indices.
        indices = range(3*16*len(lines))#[[3*i,3*i+1,3*i+2] for i in xrange(len(facets))]
        #print indices[:10]
        self.vertex_list = batch.add_indexed(len(vertices)//3, 
                                             GL_TRIANGLES,
                                             None,#group,
                                             indices,
                                             ('v3f/static', vertices),
                                             ('n3f/static', normals))
        if lasth is not None:
                    self.layers[lasth]=pyglet.graphics.Batch()
                    indices = range(len(layertemp[lasth][0]))#[[3*i,3*i+1,3*i+2] for i in xrange(len(facets))]
                    self.layers[lasth].add_indexed(len(layertemp[lasth][0])//3, 
                                             GL_TRIANGLES,
                                             None,#group,
                                             indices,
                                             ('v3f/static', layertemp[lasth][0]),
                                             ('n3f/static', layertemp[lasth][1]))
                
       
    def genline(self,i,h,w):
        S=i[0][:3]
        E=i[1][:3]
        v=map(lambda x,y:x-y,E,S)
        vlen=math.sqrt(float(sum(map(lambda a:a*a, v[:3]))))
        
        if vlen==0:
            vlen=0.01
        sq2=math.sqrt(2.0)/2.0
        htw=float(h)/w
        d=w/2.0
        if i[1][3]==i[0][3]:
            d=0.05
        points=[[d,0,0],
        [sq2*d,sq2*d,0],
        [0,d,0],
        [-sq2*d,sq2*d,0],
        [-d,0,0],
        [-sq2*d,-sq2*d,0],
        [0,-d,0],
        [sq2*d,-sq2*d,0]
        ]
        axis=stltool.cross([0,0,1],v)
        alen=math.sqrt(float(sum(map(lambda a:a*a, v[:3]))))
        if alen>0:
            axis=map(lambda m:m/alen,axis)
            angle=math.acos(v[2]/vlen)
            def vrot(v,axis,angle):
                kxv=stltool.cross(axis,v)
                kdv=sum(map(lambda x,y:x*y,axis,v))
                return map(lambda x,y,z:x*math.cos(angle)+y*math.sin(angle)+z*kdv*(1.0-math.cos(angle)),v,kxv,axis)
            points=map(lambda x:vrot(x,axis,angle),points)
        points=map(lambda x:[x[0],x[1],htw*x[2]],points)
        
        def vadd(v,o):
            return map(lambda x,y:x+y,v,o)
        spoints=map(lambda x:vadd(S,x),points)
        epoints=map(lambda x:vadd(E,x),points)
        return spoints,epoints,S,E
       
    def transform(self,line):
            line=line.split(";")[0]
            cur=self.prev[:]
            if len(line)>0:
                if "G1" in line or "G0" in line or "G92" in line:
                    if("X" in line):
                        cur[0]=float(line.split("X")[1].split(" ")[0])
                    if("Y" in line):
                        cur[1]=float(line.split("Y")[1].split(" ")[0])
                    if("Z" in line):
                        cur[2]=float(line.split("Z")[1].split(" ")[0])
                    if("E" in line):
                        cur[3]=float(line.split("E")[1].split(" ")[0])
                    if self.prev==cur:
                        return None
                    if self.fline or "G92" in line:
                        self.prev=cur
                        self.fline=0
                        return None
                    else:
                        r=[self.prev,cur]
                        self.prev=cur
                        return r
        
       
    def delete(self):
        self.vertex_list.delete()


def trackball(p1x, p1y, p2x, p2y, r):
    TRACKBALLSIZE=r
#float a[3]; /* Axis of rotation */
#float phi;  /* how much to rotate about axis */
#float p1[3], p2[3], d[3];
#float t;

    if (p1x == p2x and p1y == p2y):
        return [0.0,0.0,0.0,1.0]

    p1=[p1x,p1y,project_to_sphere(TRACKBALLSIZE,p1x,p1y)]
    p2=[p2x,p2y,project_to_sphere(TRACKBALLSIZE,p2x,p2y)]
    a=stltool.cross(p2,p1)
    
    d=map(lambda x,y:x-y,p1,p2)
    t = math.sqrt(sum(map(lambda x:x*x, d))) / (2.0*TRACKBALLSIZE)

    if (t > 1.0): t = 1.0
    if (t < -1.0): t = -1.0
    phi = 2.0 * math.asin(t)

    return axis_to_quat(a,phi)

def vec(*args):
    return (GLfloat * len(args))(*args)
    
def axis_to_quat(a,phi):
    #print a, phi
    lena=math.sqrt(sum(map(lambda x:x*x, a)))
    q=map(lambda x:x*(1/lena),a)
    q=map(lambda x:x*math.sin(phi/2.0),q)
    q.append(math.cos(phi/2.0))
    return q
    
def build_rotmatrix(q):
    m=(GLdouble * 16)()
    m[0] = 1.0 - 2.0 * (q[1] * q[1] + q[2] * q[2])
    m[1] = 2.0 * (q[0] * q[1] - q[2] * q[3]);
    m[2] = 2.0 * (q[2] * q[0] + q[1] * q[3]);
    m[3] = 0.0;

    m[4] = 2.0 * (q[0] * q[1] + q[2] * q[3]);
    m[5]= 1.0 - 2.0 * (q[2] * q[2] + q[0] * q[0]);
    m[6] = 2.0 * (q[1] * q[2] - q[0] * q[3]);
    m[7] = 0.0;

    m[8] = 2.0 * (q[2] * q[0] - q[1] * q[3]);
    m[9] = 2.0 * (q[1] * q[2] + q[0] * q[3]);
    m[10] = 1.0 - 2.0 * (q[1] * q[1] + q[0] * q[0]);
    m[11] = 0.0;

    m[12] = 0.0;
    m[13] = 0.0;
    m[14] = 0.0;
    m[15] = 1.0;
    return m

def project_to_sphere(r, x, y):
    d = math.sqrt(x*x + y*y)
    if (d < r * 0.70710678118654752440):
        return math.sqrt(r*r - d*d)
    else:
        t = r / 1.41421356237309504880
        return t*t / d
        
def mulquat(q1,rq):
    return [q1[3] * rq[0] + q1[0] * rq[3] + q1[1] * rq[2] - q1[2] * rq[1],
                    q1[3] * rq[1] + q1[1] * rq[3] + q1[2] * rq[0] - q1[0] * rq[2],
                    q1[3] * rq[2] + q1[2] * rq[3] + q1[0] * rq[1] - q1[1] * rq[0],
                    q1[3] * rq[3] - q1[0] * rq[0] - q1[1] * rq[1] - q1[2] * rq[2]]


class TestGlPanel(GLPanel):
    
    def __init__(self, parent, size,id=wx.ID_ANY,):
        super(TestGlPanel, self).__init__(parent, id, wx.DefaultPosition, size, 0)
        self.batches=[]
        self.rot=0
        self.canvas.Bind(wx.EVT_MOUSE_EVENTS,self.move)
        self.canvas.Bind(wx.EVT_LEFT_DCLICK,self.double)
        self.initialized=1
        self.canvas.Bind(wx.EVT_MOUSEWHEEL,self.wheel)
        self.parent=parent
        self.initp=None
        self.dist=200
        self.bedsize=[200,200]
        self.transv=[0, 0, -self.dist]
        self.basequat=[0,0,0,1]
        wx.CallAfter(self.forceresize)
        self.mousepos=[0,0]
        
    def double(self, event):
        p=event.GetPositionTuple()
        sz=self.GetClientSize()
        v=map(lambda m,w,b:b*m/w,p,sz,self.bedsize)
        v[1]=self.bedsize[1]-v[1]
        v+=[300]
        print v
        self.add_file("../prusa/metric-prusa/x-end-idler.stl",v)
        
        
    def forceresize(self):
        self.SetClientSize((self.GetClientSize()[0],self.GetClientSize()[1]+1))
        self.SetClientSize((self.GetClientSize()[0],self.GetClientSize()[1]-1))
        threading.Thread(target=self.update).start()
        self.initialized=0
    
    def move(self, event):
        if event.Dragging() and event.LeftIsDown():
            if self.initp==None:
                self.initp=event.GetPositionTuple()
            else:
                if not event.ShiftDown():
                    i=self.parent.l.GetSelection()
                    if i<0:
                        return
                    p1=list(self.initp)
                    p1[1]*=-1
                    self.initp=None
                    p2=list(event.GetPositionTuple())
                    p2[1]*=-1
                    m=self.parent.models[self.parent.l.GetString(i)]
                    m.offsets=map(lambda old,new,original:original+(new-old), list(p1)+[0],list(p2)+[0],m.offsets)
                    return
                #print self.initp
                p1=self.initp
                self.initp=None
                p2=event.GetPositionTuple()
                sz=self.GetClientSize()
                p1x=(float(p1[0])-sz[0]/2)/(sz[0]/2)
                p1y=-(float(p1[1])-sz[1]/2)/(sz[1]/2)
                p2x=(float(p2[0])-sz[0]/2)/(sz[0]/2)
                p2y=-(float(p2[1])-sz[1]/2)/(sz[1]/2)
                #print p1x,p1y,p2x,p2y
                quat=trackball(p1x, p1y, p2x, p2y, -self.transv[2]/250.0)
                if self.rot:
                    self.basequat=mulquat(self.basequat,quat)
                #else:
                glGetDoublev(GL_MODELVIEW_MATRIX,self.mvmat)
                #self.basequat=quatx
                mat=build_rotmatrix(self.basequat)
                glLoadIdentity()
                glTranslatef(self.transv[0],self.transv[1],0)
                glTranslatef(0,0,self.transv[2])
                glMultMatrixd(mat)
                glGetDoublev(GL_MODELVIEW_MATRIX,self.mvmat)
                self.rot=1
            
        elif event.ButtonUp(wx.MOUSE_BTN_LEFT):
            if self.initp is not None:
                self.initp=None
        elif event.ButtonUp(wx.MOUSE_BTN_RIGHT):
            if self.initp is not None:
                self.initp=None
                
        
        elif event.Dragging() and event.RightIsDown() and event.ShiftDown():
                if self.initp is None:
                    self.initp=event.GetPositionTuple()
                else:
                    p1=self.initp
                    p2=event.GetPositionTuple()
                    sz=self.GetClientSize()
                    p1=list(p1)
                    p2=list(p2)
                    p1[1]*=-1
                    p2[1]*=-1
                    
                    self.transv=map(lambda x,y,z,c:c-self.dist*(x-y)/z, list(p1)+[0], list(p2)+[0], list(sz)+[1], self.transv)
                    
                    glLoadIdentity()
                    glTranslatef(self.transv[0],self.transv[1],0)
                    glTranslatef(0,0,self.transv[2])
                    if(self.rot):
                        glMultMatrixd(build_rotmatrix(self.basequat))
                    glGetDoublev(GL_MODELVIEW_MATRIX,self.mvmat)
                    self.rot=1
                    self.initp=None
        else:
            #mouse is moving without a button press
            p=event.GetPositionTuple()
            sz=self.GetClientSize()
            v=map(lambda m,w,b:b*m/w,p,sz,self.bedsize)
            v[1]=self.bedsize[1]-v[1]
            self.mousepos=v
        
    def wheel(self,event):
        z=event.GetWheelRotation()
        delta=10
        if not event.ShiftDown():
            i=self.parent.l.GetSelection()
                    
            if i<0:
                return
            m=self.parent.models[self.parent.l.GetString(i)]
                    
            if z > 0:
                m.rot+=delta/2
            else:
                m.rot-=delta/2
            return
        if z > 0:
            self.transv[2]+=delta
        else:
            self.transv[2]-=delta
        
        glLoadIdentity()
        glTranslatef(*self.transv)
        if(self.rot):
            glMultMatrixd(build_rotmatrix(self.basequat))
        glGetDoublev(GL_MODELVIEW_MATRIX,self.mvmat)
        self.rot=1
    
                
    def update(self):
        while(1):
            dt=0.05
            time.sleep(0.05)
            try:
                wx.CallAfter(self.Refresh)
            except:
                return
            
    def anim(self,obj):
        g=50*9.8
        v=20
        dt=0.05
        basepos=obj.offsets[2]
        obj.offsets[2]+=obj.animoffset
        while obj.offsets[2]>-1:
            time.sleep(dt)
            obj.offsets[2]-=v*dt
            v+=g*dt
            if(obj.offsets[2]<0):
                obj.scale[2]*=1-3*dt
        #return
        v=v/4
        while obj.offsets[2]<basepos:
            time.sleep(dt)
            obj.offsets[2]+=v*dt
            v-=g*dt
            obj.scale[2]*=1+5*dt
        obj.scale[2]=1.0
    
    def create_objects(self):
        '''create opengl objects when opengl is initialized'''
        self.initialized=1
        wx.CallAfter(self.Refresh)
        
    def drawmodel(self,m,n):
        batch = pyglet.graphics.Batch()
        stl = stlview(m.facets, batch=batch)
        m.batch=batch
        m.animoffset=300
        #print m
        #threading.Thread(target=self.anim,args=(m,)).start()
        wx.CallAfter(self.Refresh)
        
        
        
    def update_object_resize(self):
        '''called when the window recieves only if opengl is initialized'''
        pass
        
    def draw_objects(self):
        '''called in the middle of ondraw after the buffer has been cleared'''
        if self.vpmat is None:
            return
        if not self.initialized:
            self.create_objects()
        
        #glLoadIdentity()
        #print list(self.pmat)
        if self.rot==1:
            glLoadIdentity()
            glMultMatrixd(self.mvmat)
        else:
            glLoadIdentity()
            glTranslatef(*self.transv)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.2, 0.2, 0.2, 1))
        glBegin(GL_LINES)
        glNormal3f(0,0,1)
        rows=10
        cols=10
        zheight=50
        for i in xrange(-rows,rows+1):
            if i%5==0:
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.6, 0.6, 0.6, 1))
            else:
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.2, 0.2, 0.2, 1))
            glVertex3f(10*-cols, 10*i,0)
            glVertex3f(10*cols, 10*i,0)
        for i in xrange(-cols,cols+1):
            if i%5==0:
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.6, 0.6, 0.6, 1))
            else:
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.2, 0.2, 0.2, 1))
            glVertex3f(10*i, 10*-rows,0)
            glVertex3f(10*i, 10*rows,0)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.6, 0.6, 0.6, 1))
        glVertex3f(10*-cols, 10*-rows,0)
        glVertex3f(10*-cols, 10*-rows,zheight)
        glVertex3f(10*cols, 10*rows,0)
        glVertex3f(10*cols, 10*rows,zheight)
        glVertex3f(10*cols, 10*-rows,0)
        glVertex3f(10*cols, 10*-rows,zheight)
        glVertex3f(10*-cols, 10*rows,0)
        glVertex3f(10*-cols, 10*rows,zheight)
        
        glVertex3f(10*-cols, 10*rows,zheight)
        glVertex3f(10*cols, 10*rows,zheight)
        glVertex3f(10*cols, 10*rows,zheight)
        glVertex3f(10*cols, 10*-rows,zheight)
        glVertex3f(10*cols, 10*-rows,zheight)
        glVertex3f(10*-cols, 10*-rows,zheight)
        glVertex3f(10*-cols, 10*-rows,zheight)
        glVertex3f(10*-cols, 10*rows,zheight)
        
        glEnd()
        glPushMatrix()
        glTranslatef(self.mousepos[0]-self.bedsize[0]/2,self.mousepos[1]-self.bedsize[1]/2,0)
        glBegin(GL_TRIANGLES)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(1, 0, 0, 1))
        glNormal3f(0,0,1)
        glVertex3f(2,2,0)
        glVertex3f(-2,2,0)
        glVertex3f(-2,-2,0)
        glVertex3f(2,-2,0)
        glVertex3f(2,2,0)
        glVertex3f(-2,-2,0)
        glEnd()
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.3, 0.7, 0.5, 1))
        #glTranslatef(0,40,0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(-100,-100,0)
        
        for i in self.parent.models.values():
            glPushMatrix()
            glTranslatef(*(i.offsets))
            glRotatef(i.rot,0.0,0.0,1.0)
            glScalef(*i.scale)
            
            try:
                if i.curlayer in i.gc.layers:
                    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.23, 0.57, 0.35, 1))
                    [i.gc.layers[j].draw() for j in i.gc.layers.keys() if j<i.curlayer]
                    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0.9, 0.7, 1))
                    b=i.gc.layers[i.curlayer]
                    b.draw()
                else:
                    i.batch.draw()
            except:
                i.batch.draw()
        glPopMatrix()
        glPopMatrix()
        #print "drawn batch"
class TestFrame(wx.Frame):
    '''A simple class for using OpenGL with wxPython.'''

    def __init__(self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
        super(TestFrame, self).__init__(parent, ID, title, pos, (size[0]+150,size[1]), style)
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel=wx.Panel(self,-1,size=(150,600),pos=(0,0))
        self.panel.SetBackgroundColour((10,10,10))
        self.SetBackgroundColour((10,10,10))
        self.mainsizer.Add(self.panel)
        #self.mainsizer.AddSpacer(10)
        class d:
            def GetSelection(self):
                return -1
        
        m=d()
        m.offsets=[0,0,0]
        m.rot=0
        m.curlayer=1.0
        m.scale=[1.,1.,1.]
        m.batch=pyglet.graphics.Batch()
        m.gc=gcview([], batch=m.batch)
        self.models={"":m}
        self.l=d()
        self.GLPanel1 = TestGlPanel(self,size)
        self.mainsizer.Add(self.GLPanel1, 1, wx.EXPAND)
        #self.GLPanel2 = TestGlPanel(self, wx.ID_ANY, (20, 20))
        #self.mainsizer.Add(self.GLPanel2, 1, wx.EXPAND)
        self.SetSizer(self.mainsizer)
        #self.mainsizer.Fit(self)
        self.Layout()
        
        

if __name__=="__main__":
    rx = ry = rz = 0
    
    app = wx.App(redirect=False)
    frame = TestFrame(None, wx.ID_ANY, 'GL Window', size=(400,400))
    #frame = wx.Frame(None, -1, "GL Window", size=(400,400))
    #panel = TestGlPanel(frame)
    frame.Show(True)
    app.MainLoop()
    app.Destroy()
    
