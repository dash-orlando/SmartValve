'''
*
* Display number of complete revolutions of a valve's shaft on a dial gauge
*
* Adapted from: John Harrison's original work
* Link: http://cratel.wichita.edu/cratel/python/code/SimpleVoltMeter
*
* VERSION: 0.3
*   - ADDED   : Use Finexus method to determine number of revolutions and direction
*
* KNOWN ISSUES:
*   - Non atm
* 
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Oct.  2nd, 2018 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Oct. 18th, 2018 Year of Our Lord
*
'''

# ************************************************************************
# IMPORT MODULES
# ************************************************************************

# Python modules
import  sys, argparse, pexpect                                                      # 'nuff said
from    PyQt4                           import  QtCore, QtGui, Qt                   # PyQt4 libraries required to render display
from    PyQt4.Qwt5                      import  Qwt                                 # Same here, boo-boo!
from    threading                       import  Thread                              # Run functions in "parallel"
from    Queue                           import  Queue                               # Pipe stuff out from threads
from    time                            import  sleep                               # Add delays for stability

# PD3D modules
from    dial                            import  Ui_MainWindow                       # Imports pre-built dial guage from dial.py
from    timeStamp                       import  fullStamp                           # Show date/time on console output

# ************************************************************************
# CONSTRUCT ARGUMENT PARSER 
# ************************************************************************
ap = argparse.ArgumentParser()

ap.add_argument( "-d", "--debug", action = 'store_true',
                 help = "Invoke flag to enable debugging" )

args = vars( ap.parse_args() )

##args["debug"] = True
# ************************************************************************
# SETUP PROGRAM
# ************************************************************************

class MyWindow( QtGui.QMainWindow ):

    crnt_reading = 0
    prvs_reading = 0
    
    def __init__( self, parent=None ):

        # Initialize program and extract dial GUI
        QtGui.QWidget.__init__( self, parent )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        self.thread = Worker( self )

        # Close rfObject socket on exit
        self.ui.pushButtonQuit.clicked.connect( self.cleanUp )

        # Setup gauge-needle dimensions
        self.ui.Dial.setOrigin( 90.0 )
        self.ui.Dial.setScaleArc( 0.0, 340.0 )
        self.ui.Dial.update()
        self.ui.Dial.setNeedle( Qwt.QwtDialSimpleNeedle(
                                                        Qwt.QwtDialSimpleNeedle.Arrow,
                                                        True, Qt.QColor(Qt.Qt.red),
                                                        Qt.QColor(Qt.Qt.gray).light(130)
                                                        )
                                )

        self.ui.Dial.setScaleOptions( Qwt.QwtDial.ScaleTicks |
                                      Qwt.QwtDial.ScaleLabel | Qwt.QwtDial.ScaleBackbone )

        # Small ticks are length 5, medium are 15, large are 20
        self.ui.Dial.setScaleTicks( 5, 15, 25 )
        
        # Large ticks show every 20, put 10 small ticks between
        # each large tick and every 5 small ticks make a medium tick
        self.ui.Dial.setScale( 1.0, 2.0, 2.0 )
        self.ui.Dial.setRange( 0.0, 50.0 )
        self.ui.Dial.setValue( 0 )

        # Setup buttons
        self.ui.pushButtonPair.setEnabled( True )
        self.ui.pushButtonPair.setText( QtGui.QApplication.translate("MainWindow", "Start", None, QtGui.QApplication.UnicodeUTF8) )
        self.ui.pushButtonPair.clicked.connect( lambda: self.start() )

# ------------------------------------------------------------------------

    def start( self ):
        """
        Set things in motion
        """
        
        self.thread.not_ready = False                                               # Indicate we are ready
        self.ui.Dial.setEnabled( True )                                             # Enable dial
        self.ui.pushButtonPair.setEnabled( False )                                  # Disable pushbutton
        
        # set timeout function for updates
        self.ctimer = QtCore.QTimer()                                               # Define timer
        QtCore.QObject.connect( self.ctimer,                                        # Connect signals...
                                QtCore.SIGNAL( "timeout()" ),                       # to slots.
                                self.UpdateDisplay )                                # ...
        self.ctimer.start( 10 )                                                     # Start timed thread

# ------------------------------------------------------------------------

    def UpdateDisplay( self ):
        """
        Update DialGauge display with the most recent readings.
        """
        
        if( self.crnt_reading != self.prvs_reading ):

            self.ui.Dial.setValue( self.crnt_reading )                              # Update dial GUI
            self.prvs_reading = self.crnt_reading                                   # Update variables

# ------------------------------------------------------------------------

    def cleanUp( self ):
        """
        Clean up at program exit.
        Stops recording and closes communication with device
        """

        print( fullStamp() + " Cleaning up" ),
##        self.thread.finexus_method.close()                                          # Close pexpect spawn
        if( self.thread.t_readPort.isAlive() ):                                     # Terminate thread
            self.thread.t_readPort.join( 1.0 )                                      # ...
        print( "...DONE" )

        print( fullStamp() + " Goodbye!" )
        QtCore.QThread.sleep( 2 )                                                   # this delay may be essential

# ************************************************************************
# CLASS FOR OPTIONAL INDEPENDENT THREAD
# ************************************************************************

class Worker( QtCore.QThread ):
    
    not_ready = True
    
    def __init__( self, parent = None ):
        QtCore.QThread.__init__( self, parent )

        print( fullStamp() + " Initializing Worker Thread" ) ,

        # Error handling in case thread spawning fails (1/2)
        try:
            self.py_prog = "python /home/pi/Desktop/magneto/Tracking/Finexus_Method.py"
            self.q_py_output = Queue( maxsize=0 )                                   # Define queue (this will have the Finexus_Method output)
            self.t_readPort = Thread( target=self.readPort, args=() )               # Define thread
            self.t_readPort.daemon = True                                           # Set to daemon
            self.t_readPort.start()                                                 # Start thread

        # Error handling in case thread spawning fails (2/2)
        except Exception as e:
            print( "Could NOT create thread, check .cpp")
            print( "Error type {}".format(type(e))      )
            print( "Error Arguments {}".format(e.args)  )
            sleep( 2.5 )
            quit()                                                                  # Shutdown entire program
            
        self.crnt_rotation = 0                                                      # Current rotation stored
        self.prvs_rotation = 0                                                      # Previous rotation stored
        
        # Start
        self.owner = parent
        self.start()
        
# ------------------------------------------------------------------------

    def __del__( self ):
        print( fullStamp() + " Exiting Worker Thread" )

# ------------------------------------------------------------------------

    def readPort( self ):

        try:
            finexus_method = pexpect.spawn( self.py_prog, timeout=None )            # Spawn python program as 
            
            for line in finexus_method:
                out = line.strip('\n\r')                                            # Remove newlines & carriage return

                if( out == "GO!" ):
                    print( "...DONE" )

                if( out[0] == "<" ):
                    print( out )                                                    # Print to screen
                    
                    out = out.strip( "<" )                                          # Strip the SOH marker
                    out = out.strip( ">" )                                          # Strip the EOT marker
                    out = (out.rstrip()).split(",")                                 # Strip any white space and split at delimiter

                    dir_rev = str( out[0].strip("DIR:") )                           # Get direction
                    num_rev = int( out[1].strip("REV:") )                           # Get count
                    height  = float( out[2].strip( "H:" ) )                         # Get height

                    output = ( dir_rev, num_rev, height )                           # Pack data
                    
                    with self.q_py_output.mutex:                                    # Clear queue. This is done because we are placing items
                        self.q_py_output.queue.clear()                              # in the queue faster than we are using, causing a lag.
                        
                    self.q_py_output.put( output )                                  # Place items in queue

        except Exception as e:
            print( "Caught error in readPort()"         )
            print( "Error type {}".format(type(e))      )
            print( "Error arguments {}".format(e.args)  )

# ------------------------------------------------------------------------

    def run( self ):

        while( self.not_ready ):                                                    # Do nothing until we are ready
            sleep( 0.01 )                                                           # ...
            
        QtCore.QThread.sleep( 2 )                                                   # Delay for stability
        
        while( True ):                                                              # Loop 43va!

            (dir_rev, num_rev, height) = self.q_py_output.get()
            self.crnt_rotation = num_rev
            self.synthesize_pulse( self.prvs_rotation, self.crnt_rotation )
            self.prvs_rotation = self.crnt_rotation

# ------------------------------------------------------------------------

    def synthesize_pulse( self, prvs_val, crnt_val ):
        """
        Synthesize pulse

        INPUTS:-
            - val : Data point that will be used as a start and
                    end value for the synthesized pulse

        OUTPUT:-
            - NONE
        """

        if( crnt_val > prvs_val ):
            i = 0
            while( True ):
                self.owner.crnt_reading = prvs_val + i/50.
                i = i+1

                if( args["debug"] ):                                                # [INFO] Status
                    print( "[INFO] Dial @ {}".format(self.owner.crnt_reading) )     # ...
                else:
                    sleep(0.01)                                                     # Delay is required for pulses to be visible

                if( self.owner.crnt_reading >= crnt_val ):
                    self.owner.crnt_reading = crnt_val
                    break


        elif( crnt_val <= prvs_val ):
            i = 0
            while( True ):
                self.owner.crnt_reading = prvs_val - i/50.
                i = i+1

                if( args["debug"] ):                                                # [INFO] Status
                    print( "[INFO] Dial @ {}".format(self.owner.crnt_reading) )     # ...
                else:
                    sleep(0.01)                                                     # Delay is required for pulses to be visible

                if( self.owner.crnt_reading <= crnt_val ):
                    self.owner.crnt_reading = crnt_val
                    break

# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

if __name__ == "__main__":
    print( fullStamp() + " Booting DialGauge" )
    app = QtGui.QApplication( sys.argv )
    MyApp = MyWindow()
    MyApp.show()
    sys.exit(app.exec_())
