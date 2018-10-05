'''
*
* Display number of complete revolutions of a valve's shaft on a dial gauge
*
* Adapted from: John Harrison's original work
* Link: http://cratel.wichita.edu/cratel/python/code/SimpleVoltMeter
*
* VERSION: 0.1
*   - MODIFIED: Initial release
*
* KNOWN ISSUES:
*   - Non atm
* 
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Oct.  2nd, 2018 Year of Our Lord
* LAST CONTRIBUTION DATE    :                   ---
*
'''

# ************************************************************************
# IMPORT MODULES
# ************************************************************************

# Python modules
import  sys, serial, argparse                                                       # 'nuff said
from    PyQt4                           import  QtCore, QtGui, Qt                   # PyQt4 libraries required to render display
from    PyQt4.Qwt5                      import  Qwt                                 # Same here, boo-boo!
from    threading                       import  Thread                              # Run functions in "parallel"
from    time                            import  sleep, time                         # Add delays for stability, time things
from    os                              import  getcwd, path, makedirs              # Pathname manipulation for saving data output

# PD3D modules
from    dial                            import  Ui_MainWindow                       # Imports pre-built dial guage from dial.py
from    timeStamp                       import  fullStamp                           # Show date/time on console output
from    usbProtocol                     import  createUSBPort

# ************************************************************************
# CONSTRUCT ARGUMENT PARSER 
# ************************************************************************
ap = argparse.ArgumentParser()

ap.add_argument( "-s", "--samplingFrequency", type=float, default=1.0,
                help="Set sampling frequency (in secs).\nDefault=1" )

ap.add_argument( "-d", "--debug", action='store_true',
                help="Invoke flag to enable debugging" )

ap.add_argument( "--directory", type=str, default='output',
                help="Set directory" )

args = vars( ap.parse_args() )

args["debug"] = True
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
        self.ui.pushButtonPair.clicked.connect( lambda: self.start(USB_PORT, USB_BAUD, USB_TIMEOUT) )

# ------------------------------------------------------------------------

    def start( self, USB_PORT, USB_BAUD, USB_TIMEOUT ):
        """
        Connect to MQTT server
        """
        
        self.thread.PORT    = str( USB_PORT )                                       # Set port number
        self.thread.BAUD    = USB_BAUD                                              # Set baudrate
        self.thread.TIMEOUT = USB_TIMEOUT                                           # Set timeout
        self.ui.Dial.setEnabled( True )                                             # Enable dial
        self.ui.pushButtonPair.setEnabled( False )                                  # Disable pushbutton

        # Create logfile
        self.setup_log()
        
        # set timeout function for updates
        self.ctimer = QtCore.QTimer()                                               # Define timer
        QtCore.QObject.connect( self.ctimer,                                        # Connect signals...
                                QtCore.SIGNAL( "timeout()" ),                       # to slots.
                                self.UpdateDisplay )                                # ...
        self.ctimer.start( 10 )                                                     # Start timed thread

        # Set timeout function for writing to log
        millis = int( args["samplingFrequency"]*1000 )                              # Cast into integer
        self.log_timer = QtCore.QTimer()                                            # Define timer
        QtCore.QObject.connect( self.log_timer,                                     # Connect signals...
                                QtCore.SIGNAL( "timeout()" ),                       # to slots.
                                self.thread.write_log )                             # ...
        self.log_timer.start( millis )                                              # Start timed thread
        
# ------------------------------------------------------------------------

    def UpdateDisplay( self ):
        """
        Update DialGauge display with the most recent readings.
        """
        
        if( self.crnt_reading != self.prvs_reading ):

            self.ui.Dial.setValue( self.crnt_reading )                              # Update dial GUI
            self.prvs_reading = self.crnt_reading                                   # Update variables

# ------------------------------------------------------------------------

    def setup_log( self ):
        """
        Setup directory and create logfile.
        """
        
        self.dataFileDir = getcwd() + "/dataOutput/" + args["directory"]            # Define directory
        self.dataFileName = self.dataFileDir + "/output.txt"                        # Define output file

        if( path.exists(self.dataFileDir) == False ):                               # Create directory ... 
            makedirs( self.dataFileDir )                                            # if it doesn't exist.
            print( fullStamp() + " Created data output folder" )                    # ...

        with open( self.dataFileName, "w" ) as f:                                   # Write down info as ...
            f.write( "Date/Time     :  {}\n".format(fullStamp())    )               # a header on the ...
            f.write( "seconds,    kPa , mmHg Actual, mmHg Simulated\n" )            # ...
            f.close()                                                               # ...

        print( fullStamp() + " Created data output .txt file\n" )                   # [INFO] Status

# ------------------------------------------------------------------------

    def cleanUp( self ):
        """
        Clean up at program exit.
        Stops recording and closes communication with device
        """
        
        print( fullStamp() + " Goodbye!" )
        QtCore.QThread.sleep( 2 )                                                   # this delay may be essential

# ************************************************************************
# CLASS FOR OPTIONAL INDEPENDENT THREAD
# ************************************************************************

class Worker( QtCore.QThread ):

    PORT    = 'none'
    BAUD    = 'none'
    TIMEOUT = 'none'
    
    # Define sampling frequency (units: sec) controls writing frequency
    wFreq = args["samplingFrequency"]                                               # Frequency at which to write data
    wFreqTrigger = time()                                                      # Trigger counter ^
    
    def __init__( self, parent = None ):
        QtCore.QThread.__init__( self, parent )

        print( fullStamp() + " Initializing Worker Thread" )

        # Start
        self.owner = parent
        self.start()
        
# ------------------------------------------------------------------------

    def __del__( self ):
        print( fullStamp() + " Exiting Worker Thread" )

# ------------------------------------------------------------------------

    def run( self ):

        while( self.PORT == 'none' ):                                               # Do nothing until
            sleep( 0.01 )                                                           # a device is paired
        

        ESP32 = createUSBPort( self.PORT, self.BAUD, self.TIMEOUT )
        QtCore.QThread.sleep( 2 )                                                   # Delay for stability
        
        self.startTime = time()                                                     # Store initial time (for timestamp)

        while( True ):                                                              # Loop 43va!
            j=0
            for i in range( 1, 11 ):
                self.synthesize_pulse( j, i )
                j=i

                sleep( 0.5 )

            sleep( 2.5 )
            
            j=10
            for i in range( 9, 0, -1 ):
                self.synthesize_pulse( j, i )
                j=i

                sleep( 0.5 )

            sleep( 2.5 )

# ------------------------------------------------------------------------

    def write_log( self ):
        """
        Write to log file.

        Inputs:-
            - NONE

        Output:-
            - NONE
        """

        try:
            self.wFreqTrigger = time()                                              # Reset wFreqTrigger
            stamp = time()-self.startTime                                           # Time stamp

            # Write to file
            dataStream = "%6.2f , %6.2f\n" %( stamp, self.owner.crnt_reading )      # Format readings into string

            with open( self.owner.dataFileName, "a" ) as f:
                f.write( dataStream )                                               # Write to file
                f.close()                                                           # Close file

        except:
            pass

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
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

USB_PORT    = 0                                                                     # USB port number
USB_BAUD    = 115200                                                                # Communication Baudrate
USB_TIMEOUT = 5                                                                     # Timout in seconds

# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

if __name__ == "__main__":
    print( fullStamp() + " Booting DialGauge" )
    app = QtGui.QApplication( sys.argv )
    MyApp = MyWindow()
    MyApp.show()
    sys.exit(app.exec_())
