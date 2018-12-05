using UnityEngine;
using System.Collections;
using System.Text;
using System.Net;
using System.Threading;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;
using uPLibrary.Networking.M2Mqtt.Utility;
using uPLibrary.Networking.M2Mqtt.Exceptions;

using System;

public class mqttTest : MonoBehaviour
{
    public GameObject myGameObject;                                                         // Connect to valve assembly

    public static bool  CCW = false;                                                        // Booleans to indicate whether or
    public static bool  CW  = false;                                                        // ...not to animate rotation of valve
    public static int   i   = 0;                                                            // Counter

	private MqttClient client;
	// Use this for initialization
	void Start ()
    {
        /* Create client instance */
        const string    IP_address  = "10.190.102.138";                                     // IP address of MQTT broker (Window PC)
        const int       mqtt_port   = 1883;                                                 // Dedicated MQTT port
        const bool      secure_conn = false;                                                // Are we using a secure connection?
        //       new MqttClient( IPAddress brokerAddress, int port, bool secure, X509Certificate ca Cert );
        client = new MqttClient( IPAddress.Parse(IP_address), mqtt_port, secure_conn, null );

        /* Register a callback-function for when a message is received */
        client.MqttMsgPublishReceived += client_MqttMsgPublishReceived;                     // See function definition below

        /* Connect to client and enable "Last will & testament" */
        const string    username    = null;                                                 // Username
        const string    password    = null;                                                 // Password
        const bool      will_retain = true;                                                 // Retain "last will & testament message"
        const byte      will_qos    = MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE;                  // Send "last will..." with QoS 1
        const bool      will_ON     = true;                                                 // Enable "last will & testament" feature
        const string    will_topic  = "gate_valve/general";                                 // Topic to publish "last will" to
        const string    will_msg    = "CONNER_BRK";                                         // Message of "last will"
        const bool      clean_exit  = true;                                                 // Clean session flag
        const ushort    keep_alive  = 60;                                                   // Keep alive period

        client.Connect( Guid.NewGuid().ToString(),                                          // ...
                        username, password, will_retain,                                    // Finally connect
                        will_qos, will_ON, will_topic,                                      // to broker
                        will_msg, clean_exit, keep_alive );                                 // ...

        /* Subscribe to topics of interest with QoS 1 */
        // NOTE:-
        // QoS 0 = QOS_LEVEL_AT_MOST_ONCE
        // QoS 1 = QOS_LEVEL_AT_LEAST_ONCE
        // QoS 2 = QOS_LEVEL_EXACTLY_ONCE
        string[] topics = { "gate_valve/dir"    ,                                           // Direction of revolutions topic
                            "gate_valve/rev"    ,                                           // Number    of revolutions topic
                            "gate_valve/height" ,                                           // Height (obtained from IMU) topic
                            "gate_valve/ToF_h"  ,                                           // Height (obtained from ToF) topic
                            "gate_valve/general" };                                         // Everything else

        byte[] qos_level = {    MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE,                        // ...
                                MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE,                        // ...
                                MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE,                        // Define QoS for all topics individually
                                MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE,                        // ...
                                MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE };                      // ...
        
        for (int i = 0; i < topics.Length; i++)
            client.Publish( topics[i], Encoding.UTF8.GetBytes(""), qos_level[i], true );    // Sending zero-bytes clears up retained messages

        client.Subscribe( topics, qos_level );                                              // Finally subscribe

    }

    /* Callback-function for when a message is received */
	void client_MqttMsgPublishReceived( object sender, MqttMsgPublishEventArgs e ) 
	{ 
		Debug.Log( "TOPIC   : " + e.Topic  );                                               // Get topic data was sent to
        Debug.Log( "MESSAGE : " + Encoding.UTF8.GetString(e.Message) );                     // Decode payload into UTF8

        if( e.Topic == "gate_valve/dir" )
        {
            if( string.Equals(Encoding.UTF8.GetString(e.Message), "CW") )
            {
                Debug.Log( "Rotating CW" );
                CW = true;
            }

            else if( string.Equals(Encoding.UTF8.GetString(e.Message), "CCW") )
            {
                Debug.Log( "Rotating CCW" );
                CCW = true;
            } 
        }
    } 
	
	/* Create button on game screen */
	void OnGUI(){
		if ( GUI.Button (new Rect (20, 40, 320, 40), "Click here to send a test message"))
        {
            string test_msg = "Sending data from within Unity3D over MQTT!";

            Debug.Log( "Sending: " + test_msg );
			client.Publish( "gate_valve/general", Encoding.UTF8.GetBytes(test_msg),
                            MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, true );
			Debug.Log( "Sent" );
		}
	}

	// Update is called once per frame
    void Update ()
    {
        const int val = 5;																	// Scalar for how fast the valve should rotate
		
        if( CW ) 																			// In case CW is received
        {
            i++; 																			// Increment frame counter
            myGameObject.transform.Rotate( 0, val, 0 ); 									// Rotate CW a "val" degrees
            if( i == 360/val ) 																// If a complete revolution is done
            {
                CW = false;																	// Reset CW flag
                i = 0;																		// Reset frame counter
            }
        }

        if( CCW )
        {
            i++;
            myGameObject.transform.Rotate( 0, -1*val, 0 );
            if( i == 360/val )
            {
                CCW = false;
                i = 0;
            }
        }
        //myGameObject.transform.Rotate(0, Time.time, 0); // Do stuff here if you want
	}
}
