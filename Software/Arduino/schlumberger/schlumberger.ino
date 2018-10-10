#include <SparkFunLSM9DS1.h>                                        // Call IMUs library
#define   BAUDRATE      115200                                      // Serial communication baudrate
#define   DEBUG         0                                           // Uncomment for debugging

LSM9DS1 imuHI;                                                      // Odd numbers
LSM9DS1 imuLO;                                                      // Even numbers

bool rotated_state = false;

#include "functions.h"                                              // Call auxiliary functions library


void setup() {

  bool not_ready[NSENS] = {0};                                      // Boolean to loop over failed sensor
  int  cnt              =  0;                                       // Counter for reset

  Serial.begin( BAUDRATE );                                         // Start serial monitor

  setupIMU();                                                       // Setup IMUs
  if ( !imuHI.begin() || !imuLO.begin() )                           // Initialize sensors, and print error code if failure.
  {
    Serial.print( F("[INFO] IMU Error\n\n") );                      // [INFO] ...

    for ( uint8_t i = 0; i < NSENS; i++ )                           // Iterate over sensors until initialized
    {
      char buff[27] = {'\0'};                                       // Array to hold INFO string
      sprintf( buff, "[INFO] Initializing IMU %i\n", i + 1 );       // [INFO] ...
      Serial.print( buff );                                         // [INFO] ...

      not_ready[i] = true;                                          // Set IMU as not ready
      while ( not_ready[i] )                                        // Loop until IMU is initialized/fixed
      {
        if ( !(i % 2) ) not_ready[i] = !imuHI.begin();              // If odd  index, it is the HI imus
        else            not_ready[i] = !imuLO.begin();              // If even index, it is the LO imus

        Serial.print( "." );                                        // Print "progress/status" dots
        if ( ++cnt % 20 == 0 ) Serial.println();                    // Print new-line every 10sec
        delay( 500 );                                               // Delay for sramatic purposes
      } Serial.print( F("DONE!\n") );                               // [INFO] ...
    }
  }
  calibrateIMU( 1 );                                                // Run calibration routine

}

void loop() {

  parseByte();

  // ============================== DO READINGS ==============================

  while ( !imuLO.magAvailable() && !imuHI.magAvailable() )
  {
    ;                                                               // Wait until the sensors are available.
  } imuHI.readMag(); imuLO.readMag();                               // Take readings

  orientRead( 1 );                                                  // Reorient readings and push to the array


  /* When all of the values have been collected, print them */
  /* all at once, adjusting for the calibration baseline!   */
  static double  norm_ngtv[NSENS]  = {0};                           // n-1  norm reading (Oldest)
  static double  norm_cntr[NSENS]  = {0};                           // n    norm reading (Older )
  static double  norm_pstv[NSENS]  = {0};                           // n+1  norm reading (Latest / current)

  long unsigned int startTime = millis();                           // timer for timed_out()

  char    buff[156]         = {'\0'};                               // String buffer

  strcat( buff, "<" );                                              // SOH indicator
  for (uint8_t i = 0; i < NSENS; i++)                               // Loop over sensors
  {
    norm_pstv[i] = 0;                                               // Reset (zero-out) current norm variable
    for (uint8_t j = 0; j < NAXES; j++)                             // Loop over axes
    {
      norm_pstv[i] += pow( sens[i][j] - cal[i][j], 2 );             // Compute norm of calibrated data
      dtostrf( sens[i][j] - cal[i][j], 9, 6, &buff[strlen(buff)]);  // Place calibrated data in string
      if (i == NSENS - 1 && j == NAXES - 1)
        continue;
      else
        strcat( buff, "," );
    }
    is_norm_max( norm_ngtv[i], norm_cntr[i], norm_pstv[i], i );     // Determine if we reached the maximum norm reading
    norm_ngtv[i] = norm_cntr[i]; norm_cntr[i] = norm_pstv[i];       // Propagate norm readings "upstream"

  }

  // ========================= PRINT STUFF TO SERIAL =========================

//  static int  rotation_num  = 0;
//  char        arr[ 10 ] = {'\0'};
//  if ( sqrt(norm_pstv[1]) >= 3 && !rotated_state )
//  { 
//    if ( norm_max[0] && norm_max[1] && timer[0] > 0 && timer[1] > 0 )
//    {
//      rotated_state = true;
//
//      if ( timer[0] < timer[1] )
//      {
//        sprintf( arr, ",%i,CW", ++rotation_num );                   // Number of rotations + direction
//        strcat( buff, arr );                                        // Concatenate strings
//      }
//      else if ( timer[0] > timer[1] )
//      {
//        sprintf( arr, ",%i,CCW", --rotation_num );                  // Number of rotations + direction
//        strcat( buff, arr );                                        // Concatenate strings
//      }
//      norm_max[0] = norm_max[1] = false;
//      timer[0] = timer[1] = 0;
//    }
//
//    else
//    {
//      sprintf( arr, ",%i,NULL", rotation_num );                     // Number of rotations + direction
//      strcat( buff, arr );                                          // Concatenate strings
//    }
//
//  }
//
//  else if ( sqrt(norm_pstv[1]) <= 4 && rotated_state )
//  {
//    rotated_state = false;
//    sprintf( arr, ",%i,NULL", rotation_num );                       // Number of rotations + direction
//    strcat( buff, arr );                                            // Concatenate strings
//  }
//
//  else
//  {
//    sprintf( arr, ",%i,NULL", rotation_num );                       // Number of rotations + direction
//    strcat( buff, arr );                                            // Concatenate strings
//  }
//
//  strcat( buff, ">" );                                              // EOT indicator
//  Serial.println( buff );
  norm_pstv[0] = ema_filter( norm_pstv[0], 0, -1, true );
  norm_pstv[1] = ema_filter( norm_pstv[1], 1, -1, true );
  Serial.print( 00 ); Serial.print( " " );                            // Set y-axis lower bound
  Serial.print( 40 ); Serial.print( " " );                            // Set y-axis upper bound
  Serial.print(   sqrt(norm_pstv[0]), 3 ); Serial.print( " " );
  Serial.println( sqrt(norm_pstv[1]), 3 );
  //delay( 75 );

}
