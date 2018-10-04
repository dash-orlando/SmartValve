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
import  paho.mqtt.client                as      mqtt                                # For general communications
from    PyQt4                           import  QtCore, QtGui, Qt                   # PyQt4 libraries required to render display
from    PyQt4.Qwt5                      import  Qwt                                 # Same here, boo-boo!
from    threading                       import  Thread                              # Run functions in "parallel"
from    time                            import  sleep, time                         # Add delays for stability, time things
from    os                              import  getcwd, path, makedirs              # Pathname manipulation for saving data output

# PD3D modules
from    dial                            import Ui_MainWindow                        # Imports pre-built dial guage from dial.py
from    timeStamp                       import fullStamp                            # Show date/time on console output

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
        self.ui.pushButtonPair.clicked.connect( lambda: self.start(addr) )

# ------------------------------------------------------------------------

    def start( self, address ):
        """
        Connect to MQTT server
        """
        
        self.thread.addr = str( address )                                           # Set MQTT address
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

    addr = 'none'
    
    # Define sampling frequency (units: sec) controls writing frequency
    wFreq = args["samplingFrequency"]                                               # Frequency at which to write data
    wFreqTrigger = time()                                                      # Trigger counter ^
    
    def __init__( self, parent = None ):
        QtCore.QThread.__init__( self, parent )

        print( fullStamp() + " Initializing Worker Thread" )

        # Define MQTT topics we are concerned with
        self.MQTT_topics = { "rotation" : "SmartValve/rotation" ,                   # For number    of rotations communications
                             "direction": "SmartValve/direction",                   # For direction of rotation  communications
                             "position" : "SmartValve/position" ,                   # For position               communications
                             "general"  : "SmartValve/general"  }                   # For things that are not in any previous category
        
        # Start
        self.owner = parent
        self.start()
        
# ------------------------------------------------------------------------

    def __del__( self ):
        print( fullStamp() + " Exiting Worker Thread" )

# ------------------------------------------------------------------------

    def run( self ):

        while( self.addr == 'none' ):                                               # Do nothing until
            sleep( 0.01 )                                                           # a device is paired
        

        self.MQTT_client_setup( self.addr )                                         # Setup MQTT Client
        QtCore.QThread.sleep( 2 )                                                   # Delay for stability
        
        self.startTime = time()                                                # Store initial time (for timestamp)

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

    def MQTT_client_setup( self, addr ):
        '''
        Setup MQTT client
        '''

        # Error handling in case MQTT communcation setup fails (1/2)
        try:
            self.client = mqtt.Client( client_id="Client",                          # Initialize MQTT client object
                                       clean_session=True )                         # ...
            
            self.client.max_inflight_messages_set( 60 )                             # Max number of messages that can be part of network flow at once
            self.client.max_queued_messages_set( 0 )                                # Size 0 == unlimited

            self.client.will_set( self.MQTT_topics[ "status" ],                     # "Last Will" message. Sent when connection is
                                  "CONERR_CLNT", qos=1, retain=False )              # ...lost (aka, disconnect was not called)

            self.client.reconnect_delay_set( min_delay=1,                           # Min/max wait time in case of reconnection
                                             max_delay=2 )                          # ...

            self.client.on_connect = self.on_connect                                # Assign callback functions
            self.client.on_message = self.on_message                                # ...
            
            self.client.connect( addr, port=1883, keepalive=60 )                    # Connect to MQTT network
            self.t_client_loop=Thread(target=self.client_loop, args=())             # Start threaded MQTT data processing loop()
            self.t_client_loop.deamon = True                                        # Allow program to shutdown even if thread is running
            self.t_client_loop.start()                                              # ...

            sleep( 0.5 )                                                            # Allow some time for connection to be established
            
        # Error handling in case MQTT communcation setup fails (2/2)
        except Exception as e:
            print( "Could NOT setup MQTT communications" )                          # Indicate error type and arguments
            print( "Error Type      : {}".format(type(e)))                          # ...
            print( "Error Arguments : {}".format(e.args) )                          # ...
            sleep( 1.0 )
            quit()                                                                  # Shutdown entire program

# ------------------------------------------------------------------------

    def on_connect( self, client, userdata, flags, rc ):
        '''
        Callback function for when connection is established/attempted.
        
        Prints connection status and subscribes to ftp/# topic on
        successful connection.
        '''
        
        if  ( rc == 0 ):                                                            # Upon successful connection
            print(  "MQTT Connection Successful"  )                                 #   Subscribe to topic of choice
            self.client.subscribe( "SmartValve/#", qos=1 )                          #   ...

        elif( rc == 1 ):                                                            # Otherwise if connection failed
            print( "Connection Refused - Incorrect Protocol Version" )              #   Troubleshoot

        elif( rc == 2 ):                                                            # Same ^
            print( "Connection Refused - Invalid Client Identifier"  )              #   ...

        elif( rc == 3 ):
            print( "Connection Refused - Server Unavailable"         )

        elif( rc == 4 ):
            print( "Connection Refused - Bad Username or Password"   )

        elif( rc == 5 ):
            print( "Connection Refused - Not Authorized"             )

        else:
            print( "Troubleshoot RPi   - Result Code {}".format(rc)  )
            print( "Terminating Program" )
            quit()

# ------------------------------------------------------------------------

    def on_message( self, client, userdata, msg ):
        '''
        Callback function for when a message is received.
        '''
        
        if( msg.topic == self.MQTT_topics[ "IP_addr" ] ):                           # If we receive something on the IP topic
            inData = msg.payload.decode( "utf-8" )                                  #   Decode payload
            if( len(inData) < 4 ): pass                                             #   Check it is a valid IP address
            else:                                                                   #   If IP address is valid
                self.FTP_server_ip = inData                                         #       Store IP address
                self.client.publish( self.MQTT_topics[ "status" ],                  #       Send SOH to indicate that we are ready
                                     "SOH", qos=1, retain=False  )                  #       ...
                    
                print( "Using IP: {}\n".format(self.FTP_server_ip) )                #       [INFO] ...

        elif( msg.topic == self.MQTT_topics[ "images" ] ):                          # If we receive something on the images topic
            img_name = msg.payload.decode( "utf-8" )                                #   Decode image name
            if( img_name == '' ): pass                                              #   If empty string (used to clear retained messages), pass
            else: self.get_file( img_name )                                         #   Else, retrieve it from FTP folder on server

        elif( msg.topic == self.MQTT_topics[ "status" ] ):                          # If we receive something on the status topic
            status = msg.payload.decode( "utf-8" )                                  #   Decode it and determine next action

            if( status == "EOT" ):                                                  #   If end of transmission is indicated
                print( "Disconnectiong MQTT" ) ,                                    #       [INFO] ...
                self.client.publish( self.MQTT_topics[ "status" ],                  #       Send EOT to inform server to
                                     "EOT", qos=1, retain=False  )                  #       ...shuwtdown MQTT client as
                self.loop = False                                                   #       Set loop flag to FALSE
                sleep( 0.10 )                                                       #       Allow time for state of flag to change
                self.client.disconnect()                                            #       Disconnect MQTT client
                print( "...DONE!" )                                                 #       [INFO] ...

            else                 : pass
        
        else: pass

# ------------------------------------------------------------------------

    def client_loop( self ):
        '''
        A simple, basic workaround for the MQTT's library stupid 
        threaded implementation of loop() that doesn't really work.
        '''
        
        self.loop = True                                                            # Boolean loop flag
        while( self.loop ):                                                         # Loop 43va while loop flag is TRUE
            self.client.loop( timeout=1.0 )                                         #   Pool messages queue for new data
    
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
                self.owner.crnt_reading = prvs_val + i/5.
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
                self.owner.crnt_reading = prvs_val - i/5.
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

port = 1883                                                                         # MQTT port number
addr = "192.168.42.1"                                                               # MQTT server address

# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

if __name__ == "__main__":
    print( fullStamp() + " Booting DialGauge" )
    app = QtGui.QApplication( sys.argv )
    MyApp = MyWindow()
    MyApp.show()
    sys.exit(app.exec_())
