
class MainLine():
    #has line object and list of markers on the line
    def __init__(self,lineObj):
        self.lineObj = lineObj
        self.markerList = [] #list of dotMarkers on the mainLine
        self.name = self.lineObj.get_label()
    
    def set_visible(self,bool):
        self.lineObj.set_visible(bool)
        for marker in self.markerList:
            marker.set_visible(bool)

    def get_visible(self):
        return self.lineObj.get_visible()
    
    def contains(self,event):
        return self.lineObj.contains(event)