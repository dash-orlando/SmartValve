'''
*
* Display number of complete revolutions of a valve's shaft on a dial gauge
*
* Adapted from: John Harrison's original work
* Link: http://cratel.wichita.edu/cratel/python/code/SimpleVoltMeter
*
* VERSION: 0.2
*   - ADDED   : Completed the serial communication protocol
*
* KNOWN ISSUES:
*   - Non atm
* 
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Oct.  2nd, 2018 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Oct.  8th, 2018 Year of Our Lord
*
'''

# ************************************************************************
# IMPORT MODULES
# ************************************************************************

# Python modules
import  sys, serial, argparse                                                       # 'nuff said
import  numpy                           as      np                                  # Do Maffs!
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

        self.crnt_rotation = 0              # Current rotation stored
        self.prvs_rotation = 0              # Previous rotation stored
        
        # Start
        self.owner = parent
        self.start()
        
# ------------------------------------------------------------------------

    def __del__( self ):
        print( fullStamp() + " Exiting Worker Thread" )

# ------------------------------------------------------------------------

    def readPort( self ):

        # Flush buffer
        self.ESP32.reset_input_buffer()
        self.ESP32.reset_output_buffer()

        try:

            # Wait until we receive the SOH specifier '<'
            while( True ):
                if( self.ESP32.in_waiting > 0 ):
                    inData = self.ESP32.read()
                    if( inData == '<' ):
                        break

            # Read data until we hit the EOT specifier '>'
            line = ''
            while( True ):
                if( self.ESP32.in_waiting > 0 ):
                    inData = self.ESP32.read()
                    if( inData == '>' ):
                        break
                    line = line + inData

            # Split constructed string into its constituent components
            col     = (line.rstrip()).split(",")

            # Check if array is corrupted. We expect 3 readings per sensor + 2 for rotation.
            NSENS = 2
            if( len(col) == NSENS*3 + 2 ):
                # Construct magnetic field array
                # (in case we need to use ...
                #  ... it to determine position)

                # Magnetic field readings from Sensor 1
                Bx = float( col[0] )
                By = float( col[1] )
                Bz = float( col[2] )
                B1 = np.array( ([Bx],[By],[Bz]), dtype='float64' )      # Units { G }

                # Magnetic field readings from Sensor 2
                Bx = float( col[3] )
                By = float( col[4] )
                Bz = float( col[5] )
                B2 = np.array( ([Bx],[By],[Bz]), dtype='float64' )      # Units { G }

                # Number of rotations and direction
                num_rot = int( col[6] )
                dir_rot = str( col[7] )

                return( B1, B2, num_rot, dir_rot )

            # In case array is corrupted, do a recursive call to readPort() function
            else:
                self.readPort()
                
        
        except Exception as e:
            print( "Caught error in readPort()"         )
            print( "Error type {}".format(type(e))      )
            print( "Error arguments {}".format(e.args)  )

# ------------------------------------------------------------------------

    def run( self ):

        while( self.PORT == 'none' ):                                               # Do nothing until
            sleep( 0.01 )                                                           # a device is paired
        
        try:
            self.ESP32 = createUSBPort( self.PORT, self.BAUD, self.TIMEOUT )        # Start USB comms.
            if( self.ESP32.is_open == False ):                                      # Make sure port is open
                self.ESP32.open()                                                   #   ...
            print( "ESP32 Ready" )
            
        except:
            print( "FAILED TO CREATE PORT. ABORTING PROGRAM." )                     # DIE
            quit()                                                                  # ...
            
        QtCore.QThread.sleep( 2 )                                                   # Delay for stability
        
        self.startTime = time()                                                     # Store initial time (for timestamp)

        DEMO = False
        while( True ):                                                              # Loop 43va!

            # If demo-ing the dial turning
            if( DEMO ):
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

            # If actually using acquired data
            else:
                (H1, H2, rotation, direction) = self.readPort()
                self.crnt_rotation = rotation
                self.synthesize_pulse( self.prvs_rotation, self.crnt_rotation )
                self.prvs_rotation = self.crnt_rotation
                
                

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
