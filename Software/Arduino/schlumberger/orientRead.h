/*
 * Supposedly reorients readings. For now, it only stores readings into an array.
 */

// Array that will house the smoothed sensor orientation adjusted readings, for printing.
// See the 'sensorOrientation()' definition.
double sens[NSENS][NAXES] = {0};

//This is for a setup
void orientRead( int pair ) {
  // No orientation attempt has been made. RHR is not enforced.
  // Single Exponential Smoothing has implemented.
  switch (pair) {
    case 1:
      //Sensor 1:
      sens[0][0] = ema_filter( double( imuHI.calcMag(imuHI.mx) ), 0, 0);
      sens[0][1] = ema_filter( double( imuHI.calcMag(imuHI.my) ), 0, 1);
      sens[0][2] = ema_filter( double( imuHI.calcMag(imuHI.mz) ), 0, 2);

      //Sensor 2:
      sens[1][0] = ema_filter( double( imuLO.calcMag(imuLO.mx) ), 1, 0);
      sens[1][1] = ema_filter( double( imuLO.calcMag(imuLO.my) ), 1, 1);
      sens[1][2] = ema_filter( double( imuLO.calcMag(imuLO.mz) ), 1, 2);
      break;

    case 2:
      //Sensor 3:
      sens[2][0] = ema_filter( double( imuHI.calcMag(imuHI.mx) ), 2, 0);
      sens[2][1] = ema_filter( double( imuHI.calcMag(imuHI.my) ), 2, 1);
      sens[2][2] = ema_filter( double( imuHI.calcMag(imuHI.mz) ), 2, 2);

      //Sensor 4:
      sens[3][0] = ema_filter( double( imuLO.calcMag(imuLO.mx) ), 3, 0);
      sens[3][1] = ema_filter( double( imuLO.calcMag(imuLO.my) ), 3, 1);
      sens[3][2] = ema_filter( double( imuLO.calcMag(imuLO.mz) ), 3, 2);
      break;

    default:
      Serial.print( F("Error. This sensor pair doesn't exist!") );
      while (1);
      break;
  };
}
