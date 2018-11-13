'''
*
* Tkinter counter based on the stopwatch module provided by:
* http://code.activestate.com/recipes/124894-stopwatch-in-tkinter/
* 
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Dec. 20th, 2016 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Oct. 16th, 2018 Year of Our Lord
*
'''

# Import Modules
from    Tkinter                     import  *               # Import Tkinter
import  time

class counter( Frame ):  
    """ Implements counter frame widget. """                                                                
    def __init__(self, parent=None, **kw):        
        Frame.__init__(self, parent, kw)
        self.direction  = "N/A"        
        self.revolutions= 0.0
        self.height     = 0.0
        self.ToF_height = 0.0
        self.status_str = StringVar()               
        self.makeWidgets()      

    def makeWidgets(self):                         
        """ Make the label. """
        l = Label(self, textvariable=self.status_str, bg="black", 
                  fg="white", width=200, font=("Courier", 72), anchor='center')
        l.pack(fill=BOTH, expand=YES, pady=2, padx=2)
    

    def set_str(self):
        """ Set the string"""
        direction   = self.direction
        revolutions = int( self.revolutions )
        height      = self.height
        ToF         = int( self.ToF_height )
        self.status_str.set( "DIR:%s, REV:%i, H:%.2f, TOF:%i" %(direction, revolutions, height, ToF) )

''' 
def main():
    root = Tk()
    sw = counter(root)
    sw.pack(side=TOP)
    
    Button(root, text='Update'  , command=sw.set_str).pack(side=LEFT)
    Button(root, text='Quit'    , command=root.quit).pack(side=LEFT)

    root.mainloop()


if __name__ == '__main__':
    main()
'''
