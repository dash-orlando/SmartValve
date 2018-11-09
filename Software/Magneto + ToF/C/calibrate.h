/*
 * Calibrate sensors to attenuate ambient magnetic field readings
 * 
 * Readings are done for CALIBRATION_INDEX number of times and
 * the averaged. The resultant offsets are then subtracted from
 * the RAW readings.
 */

#include <wiringPi.h>

#define CALIBRATION_INDEX         	150                     							// Accounting for ambient magnetic fields
#define DECLINATION                	6.29                    							// Accounting for the Earth's magnetic field

// Sensor Calibration variables: To store the averaged baseline values for each sensor.
double 		cal[NSENS][NAXES] = {0}; 													// Calibration array
const char 	OFFSETS_FILE[] = "OFFSETS.csv"; 											// Name of file containing offsets
FILE 		*offsets_fp; 																// File pointer to offsets file

// ========================  Calibrate  Sensors  =======================
void calibrateIMU( uint8_t whichPair, int val )
{
	// In case CALIBRATION flag is given, calibrate and write to offsets file
	if( val == 2 )
	{
		printf( "Calibrating and writing to %s, please wait.\n", OFFSETS_FILE );
		delay( 25 );
		
		if( whichPair == 1 ) 	offsets_fp = fopen( OFFSETS_FILE, "w" ); 				// Open file and truncate EVERYTHING
		else 					offsets_fp = fopen( OFFSETS_FILE, "a" ); 				// Open file and append to it
		
		double hold[6] = {0};
		for( uint8_t i = 0; i < CALIBRATION_INDEX; i++ )
		{
			//Declaring an index, to make it easier to assign values to/from the correct sensor.
			uint8_t n_HI = (whichPair - 1) * 2; 										// Define index for HI sensors
			uint8_t n_LO = (2 * whichPair) - 1; 										// Define index for LO sensors
			
			while( !imuLO.magAvailable() && !imuHI.magAvailable() );					// Wait until the sensors are available.
			imuHI.readMag(); imuLO.readMag(); 											// Take readings
			
			orientRead( whichPair );                                  					// Reorient readings and push to the array
			
			hold[0] += sens[n_HI][0];                                 					// Populate temporary hold array
			hold[1] += sens[n_HI][1];                                 					// for the HIGH sensors.
			hold[2] += sens[n_HI][2];                                 					// ...
			
			hold[3] += sens[n_LO][0];                                 					// Populate temporary hold array
			hold[4] += sens[n_LO][1];                                 					// for the LOW sensors.
			hold[5] += sens[n_LO][2];                                 					// ...
			
			if( i == CALIBRATION_INDEX - 1 ) 											// Average the readings
			{
				cal[n_HI][0] = hold[0] / CALIBRATION_INDEX;             				// Compute the calibration (BASE)
				cal[n_HI][1] = hold[1] / CALIBRATION_INDEX;             				// values for the High sensors
				cal[n_HI][2] = hold[2] / CALIBRATION_INDEX;             				// ...
				
				//Computing, finally, the actual calibration value for the Low sensor.
				cal[n_LO][0] = hold[3] / CALIBRATION_INDEX;             				// Compute the calibration (BASE)
				cal[n_LO][1] = hold[4] / CALIBRATION_INDEX;             				// values for the Low sensors
				cal[n_LO][2] = hold[5] / CALIBRATION_INDEX;             				// ...
				
				// Write OFFSETS to file then close file!
				fprintf( offsets_fp, "%f,%f,%f\n", cal[n_HI][0], cal[n_HI][1], cal[n_HI][2]);
				fprintf( offsets_fp, "%f,%f,%f\n", cal[n_LO][0], cal[n_LO][1], cal[n_LO][2]);
				fclose ( offsets_fp );
			}
		} printf( "Calibration success for pair: %i\n", whichPair );
	}
	
	// In case NO CALIBRATION flag is given, read OFFSETS file
	else
	{
		offsets_fp = fopen( OFFSETS_FILE, "r" ); 										// Open file for reading
		
		const char delimiter[2] = ","; 													// Specify comma delimiter
		char *token; 																	// For strtok() (used to break down string into "tokens")
		int i = 0, j = 0; 																// Counters to fill up cal[][]
		
		if( offsets_fp == NULL ) fprintf( stderr, "%s does NOT EXIST", OFFSETS_FILE ); 	// Check file exists
		else
		{
			char line[30*NSENS];
			while( fgets(line, sizeof(line), offsets_fp) != NULL )
			{
				token = strtok( line, delimiter );
				for( j=0; j < 3; j++ )
				{	
					cal[i][j] = strtof(token, NULL);
					//printf( "cal[%i][%i] = %.3lf\n", i, j, cal[i][j] );
					//printf( "token = %s\n", token );
					token = strtok( NULL, delimiter );
				} 	i += 1;
			}
		} fclose( offsets_fp );
	}
	
}
