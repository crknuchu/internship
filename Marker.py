import numpy as np
import matplotlib

class Marker():
    #marker contains marker object and annotation
    def __init__(self,ax,style,color):
        self.ax = ax
        self.style = style
        self.color = color
        self.xdata = None
        self.ydata = None
        self.markerObj = None
        self.annotation = None
        self.type = None
    
    def set_visible(self,bool):
        if self.markerObj is not None:
            self.markerObj.set_visible(bool)
        if self.annotation is not None:
            self.annotation.set_visible(bool)
    
    def contains(self,event):
        if self.markerObj is not None:
            return self.markerObj.contains(event)
    
    def remove(self):
        if self.annotation is not None:
            self.annotation.remove()
        if self.markerObj is not None:    
            self.markerObj.remove()

class DotMarker(Marker):
    #dot marker that is put on lines
    def __init__(self, ax, xdata, ydata, style, color,line):
        super().__init__(ax, style, color)
        self.type = "dot"
        self.xdata = xdata
        self.ydata = ydata
        self.parentLine = line
    
        listoflines = self.ax.plot(self.xdata,self.ydata,style,picker=6)
        self.markerObj = listoflines[0]
        parentcolor = self.parentLine.lineObj.get_color()
        self.color = parentcolor
        self.markerObj.set_color(self.color)
        self.annotation = self.ax.annotate(f"({self.xdata:.2f},{self.ydata:.2f})",(self.xdata,self.ydata))
        self.name = self.markerObj.get_label()
    
        self.endoflineleft = self.parentLine.lineObj.get_xdata()[0] #left edge of line
        self.endoflineright = self.parentLine.lineObj.get_xdata()[-1] #right edge of line

    def move(self,xdata):
        if xdata is None:
            return
        if(xdata<self.endoflineleft or xdata>self.endoflineright):
            return
        self.markerObj.set_xdata(xdata)
        estimated_ydata = np.interp(xdata,self.parentLine.lineObj.get_xdata(),self.parentLine.lineObj.get_ydata()) #gets intersection of x and parend line
        self.xdata = xdata
        self.ydata = estimated_ydata
        self.markerObj.set_ydata(self.ydata) 
        self.annotation.set_x(self.xdata) #moves the text of annotation
        self.annotation.set_y(self.ydata)
        self.annotation.set_text(f"({self.xdata:.2f},{self.ydata:.2f})")
        self.annotation.xy = (self.xdata,self.ydata) #moves the annotation itself

        self.checkEdges(self.xdata,self.ydata)
    
    def checkEdges(self,xdata,ydata):
        if (ydata > self.ax.get_ylim()[1] or ydata < self.ax.get_ylim()[0] or\
            xdata > self.ax.get_xlim()[1] or xdata < self.ax.get_xlim()[0]): #turns off annotation if marker leaves canvas
            self.annotation.set_visible(False)
        else:
            self.annotation.set_visible(True)

class LineMarker(Marker):
    #dashed line marker
    def __init__(self,ax,style,color):
        super().__init__(ax,style,color)
    
class HorizontalMarker(LineMarker):
    def __init__(self, ax, ydata, style, color):
        super().__init__(ax, style, color)
        self.ydata = ydata
        self.type = "horizontal"

        tform = matplotlib.transforms.blended_transform_factory(self.ax.transAxes,self.ax.transData) #x uses [0,1] range, y uses range of data

        self.markerObj = self.ax.axhline(self.ydata,picker=True)
        self.markerObj.set_linestyle(self.style)
        self.markerObj.set_color(self.color)
        self.annotation = self.ax.annotate(f"({self.ydata:.2f})",(0,self.ydata),xycoords=tform) #xycords=tform not transform=tform

        self.name = self.markerObj.get_label()

    def move(self,ydata):
        if ydata is None:
            return
        self.markerObj.set_ydata(ydata) 
        self.annotation.set_y(ydata)
        self.annotation.set_text(f"({ydata:.2f})")    

class VerticalMarker(LineMarker):
    def __init__(self, ax, xdata, style, color):
        super().__init__(ax, style, color)
        self.xdata = xdata
        self.type = "vertical"

        tform = matplotlib.transforms.blended_transform_factory(self.ax.transData,self.ax.transAxes)

        self.markerObj = self.ax.axvline(self.xdata,picker=True)
        self.markerObj.set_linestyle(self.style)
        self.markerObj.set_color(self.color)
        self.annotation = self.ax.annotate(f"({self.xdata:.2f})",(self.xdata,0),xycoords=tform)

        self.name = self.markerObj.get_label()

    def move(self,xdata):
        if xdata is None:
            return
        self.markerObj.set_xdata(xdata) 
        self.annotation.set_x(xdata)
        self.annotation.set_text(f"({xdata:.2f})")