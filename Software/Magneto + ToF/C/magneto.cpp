#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include "LSM9DS1_Types.h"
#include "LSM9DS1.h"
#include <wiringPi.h>

// Time of flight (ToF) sensor
#include "vl6180_pi/vl6180_pi.h"

// System parameters
#define NSENS     					4                                       	// Number of sensors
#define NAXES     					3                                       	// Number of axes

#define LSM9DS1_M_HIGH             	0x1E                    					// SDO_M on these IMU's are HIGH
#define LSM9DS1_AG_HIGH            	0x6B                    					// SDO_AG on these IMU's are HIGH 
#define LSM9DS1_M_LOW             	0x1C                    					// SDO_M on these IMU's are LOW
#define LSM9DS1_AG_LOW            	0x6B                    					// SDO_AG on these IMU's are HIGH [PINS NOT GROUNDED]***

// Create two instances of the LSM object; one for each M_address.
LSM9DS1 imuHI( IMU_MODE_I2C, LSM9DS1_AG_HIGH, LSM9DS1_M_HIGH );					// Odd  sensors
LSM9DS1 imuLO( IMU_MODE_I2C, LSM9DS1_AG_LOW , LSM9DS1_M_LOW  );					// Even sensors

// Call auxiliary functions library
#include "functions.h"

// int 	argc	: number of arguments passed to program. argc >= 1 ALWAYS
// char *argv[]	: Contain the arguments passed. argv[0] is ALWAYS the program name
int main( int argc, char *argv[] )
{
	if( wiringPiSetupGpio() == -1 ) 											// Start the wiringPi library
    {
		fprintf( stderr, "Failed to start wiringPi" );
		return 0;
	} 
    
    vl6180 ToF = vl6180_initialise(1); 											// Start ToF Sensors
    if( ToF < 1 ) 																// Make sure ToF initialized
    {
		fprintf( stderr, "Failed to communicate with ToF" );
		return 0; 													
    }
    
    pinMode( S0, OUTPUT ); 														// Set select pins as output
	pinMode( S1, OUTPUT ); 														// ...
	pinMode( S2, OUTPUT ); 														// ...
    
    for( uint8_t i = 1; i <= NSENS/2; i++ )
    {
		pairSelect( i );
		setupIMU(); 															// Setup sampling rate, scale, etc...
		
		if ( !imuHI.begin() || !imuLO.begin() ) 								// Initialize sensors
		{
			fprintf( stderr, "Failed to communicate with LSM9DS1 pair %i.\n", i );
			printf( "!imuHI.begin() %i\n", !imuHI.begin() );
			printf( "!imuLO.begin() %i\n", !imuLO.begin() );
			exit( EXIT_FAILURE );
		} 	calibrateIMU( i, argc ); 													// Perform user-defined calibration routine
	}
    
	// Infinite loop after setup is complete
    for( ;; )
    {
		// Collect data
		for( uint8_t i = 1; i <= NSENS/2; i++ )
		{
			pairSelect( i ); 													// Switch between pairs
			
			while( !imuHI.magAvailable() && !imuLO.magAvailable() ) ; 			// Wait until the sensors are available.
			imuHI.readMag(); imuLO.readMag(); 									// Take readings
			
			orientRead( i );                                  					// Reorient readings and push to the array
		}
		
		// Print data
		char    buff[45*NSENS] = {'\0'};                                 		// String buffer
		strcat( buff, "<" );                                        			// SOH indicator
		for( uint8_t i = 0; i < NSENS; i++ ) 									// Loop over sensors
		{																		// ...
			for( uint8_t j = 0; j < NAXES; j++ ) 								//	Loop over axes
			{																	// 	...
				char temp[ 9 ] = {'\0'};										// 	Array to hold calibrated readings
				if( sens[i][j] - cal[i][j] >= 0 ) 								// 	Formatting in case of positive reading
				{
					snprintf( temp, 7+1, "%.5lf", sens[i][j] - cal[i][j] );
				}
				else 															// 	Formatting in case of negative reading
				{
					snprintf( temp, 8+1, "%.5lf", sens[i][j] - cal[i][j] );
				}
				strcat( buff, temp ); 											// 	Append calibrated array to output buffer
				
				if( i == NSENS - 1 && j == NAXES - 1 )
					continue;
				else
					strcat( buff, "," ); 										// 	Add delimiter
			}
		}
		char temp[ 5 ] = {'\0'};
		snprintf( temp, 3+1, ",%i", get_distance(ToF) );
		strcat( buff, temp );
		strcat( buff,  ">" );                                        			// SOH indicator
		printf( "%s\n", buff );                                        			// Print final OUTPUT string
    } exit(EXIT_SUCCESS);
}
