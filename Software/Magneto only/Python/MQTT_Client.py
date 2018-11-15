'''
*
* MQTT Client for the smart gate valve project.
*
* VERSION: 0.1
*   - ADDED   : Initial release
*
* AUTHOR                    :   Mohammad Odeh
* DATE WRITTEN              :   Nov. 15th, 2018 Year of Our Lord
* LAST CONTRIBUTION DATE    :               -------
*
'''

from    time                        import  sleep                       # Add wait times
from    threading                   import  Thread                      # Use threads to free up main()
import  paho.mqtt.client            as      mqtt                        # Send stuff


# ************************************************************************
# ============================> DEFINE CLASS <============================
# ************************************************************************

class MQTT_Client( object ):

    def __init__( self, MQTT_broker_ip ):
        '''
        Initialize class
        '''
        
        self.topics =   { "dir"    : "gate_valve/dir"     ,             # For direction   communications
                          "rev"    : "gate_valve/rev"     ,             # For revolutions communications
                          "height" : "gate_valve/height"  ,             # For magneto (h) communications
                          "ToF_h"  : "gate_valve/ToF_h"   ,             # For ToF     (h) communications
                          "general": "gate_valve/general" }             # For things that are not in any previous category

        self.MQTT_client_setup( MQTT_broker_ip )                        # Setup MQTT client
        self.run()                                                      # Run program
        
# ------------------------------------------------------------------------

    def MQTT_client_setup( self, addr ):
        '''
        Setup MQTT client
        '''

        # Error handling in case MQTT communcation setup fails (1/2)
        try:
            self.client = mqtt.Client( client_id="Client",              # Initialize MQTT client object
                                       clean_session=True )             # ...
            
            self.client.max_inflight_messages_set( 60 )                 # Max number of messages that can be part of network flow at once
            self.client.max_queued_messages_set( 0 )                    # Size 0 == unlimited

            self.client.will_set( self.topics[ "general" ],             # "Last Will" message. Sent when connection is
                                  "CONERR_CLNT", qos=1, retain=False )  # ...lost (aka, disconnect was not called)

            self.client.reconnect_delay_set( min_delay=1,               # Min/max wait time in case of reconnection
                                             max_delay=2 )              # ...

            self.client.on_connect = self.on_connect                    # Assign callback functions
            self.client.on_message = self.on_message                    # ...
            
            self.client.connect( addr, port=1883, keepalive=60 )        # Connect to MQTT network
            self.t_client_loop=Thread(target=self.client_loop, args=()) # Start threaded MQTT data processing loop()
            self.t_client_loop.deamon = True                            # Allow program to shutdown even if thread is running
            self.t_client_loop.start()                                  # ...

            sleep( 0.5 )                                                # Allow some time for connection to be established
            
        # Error handling in case MQTT communcation setup fails (2/2)
        except Exception as e:
            print( "Could NOT setup MQTT communications" )              # Indicate error type and arguments
            print( "Error Type      : {}".format(type(e)))              # ...
            print( "Error Arguments : {}".format(e.args) )              # ...
            sleep( 1.0 )
            quit()                                                      # Shutdown entire program

# ------------------------------------------------------------------------

    def on_connect( self, client, userdata, flags, rc ):
        '''
        Callback function for when connection is established/attempted.
        
        Prints connection status and subscribes to ftp/# topic on
        successful connection.
        '''
        
        if  ( rc == 0 ):                                                # Upon successful connection
            print(  "MQTT Connection Successful"  )                     #   Subscribe to topic of choice
            self.client.subscribe( "gate_valve/#", qos=1 )              #   ...

        elif( rc == 1 ):                                                # Otherwise if connection failed
            print( "Connection Refused - Incorrect Protocol Version" )  #   Troubleshoot

        elif( rc == 2 ):                                                # Same ^
            print( "Connection Refused - Invalid Client Identifier"  )  #   ...

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
        if( msg.topic == self.topics["general"] ):                      # Decode payload
            inData = msg.payload.decode( "utf-8" )                      #   Decode payload
            print( "TOPIC: {}".format(msg.topic))                       #   [INFO] ...
            print( "RECV : {}\n".format(inData) )                       #   [INFO] ...

# ------------------------------------------------------------------------

    def client_loop( self ):
        '''
        A simple, basic workaround for the MQTT's library stupid 
        threaded implementation of loop() that doesn't really work.
        '''
        
        self.loop = True                                                # Boolean loop flag
        while( self.loop ):                                             # Loop 43va while loop flag is TRUE
            self.client.loop( timeout=1.0 )                             #   Pool messages queue for new data

# ------------------------------------------------------------------------

    def send( self, topic, payload ):
        '''
        Method to send messages over MQTT to windows broker.
        '''

        self.client.publish( topic, payload, qos=1, retain=True )       # Publish payload to topic
        
# ------------------------------------------------------------------------

    def disconnect( self ):
        '''
        Method to cleanly disconnect and shutdown MQTT client.
        '''

        self.client.disconnect()                                        # Disconnect client
        
# ------------------------------------------------------------------------

    def run( self ):
        '''
        Main thread
        '''
        
        sleep( 0.5 )                                                    # Sleep for stability
        print( "MQTT Client Initialized" )                              # [INFO] ...
        print( "Client Ready\n" )                                       # [INFO] ...
        
# ************************************************************************
# ===========================> SETUP  PROGRAM <===========================
# ************************************************************************      

### FOR TESTING
##MQTT_IP_ADDRESS = ""                                                    # IP address for MQTT broker
##MQTT = MQTT_Client( MQTT_IP_ADDRESS )                                   # Start program
