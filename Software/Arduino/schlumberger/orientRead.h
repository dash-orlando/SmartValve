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

// ===================    ReOrient Readings       ===================
//This is an example for a setup whereby the sensor outputs are corrected to match the right hand rule.

//void orientRead(int pair) {
//  // The sensors need to output data along a consistent Coordinate System; all "x-components" point in the same direction.
//  // The XYZ coordinate system we're imposing is defined EXTERNALLY by the designer.
//  // Sensor orientations have, hence, been predefined; when they change this has to as well.
//
//  switch (pair) {
//    case 1:
//      //Sensor 1: mz -> X, -mx -> Y, my -> Z
//      sens[0][0] = double( imuHI.calcMag(imuHI.mz) );
//      sens[0][1] = -1 * double( imuHI.calcMag(imuHI.mx) );
//      sens[0][2] = double( imuHI.calcMag(imuHI.my) );
//
//      //Sensor 2: mz -> X, -mx -> Y, my -> Z
//      sens[1][0] = double( imuLO.calcMag(imuLO.mz) );
//      sens[1][1] = -1 * double( imuLO.calcMag(imuLO.mx) );
//      sens[1][2] = double( imuLO.calcMag(imuLO.my) );
//      break;
//
//    case 2:
//      //Sensor 3: mz -> X, my -> Y, mx -> Z
//      sens[2][0] = double( imuHI.calcMag(imuHI.mz) );
//      sens[2][1] = double( imuHI.calcMag(imuHI.my) );
//      sens[2][2] = double( imuHI.calcMag(imuHI.mx) );
//
//      //Sensor 4: mz -> X, -my -> Y, -mx -> Z
//      sens[3][0] = double( imuLO.calcMag(imuLO.mz) );
//      sens[3][1] = -1 * double( imuLO.calcMag(imuLO.my) );
//      sens[3][2] = -1 * double( imuLO.calcMag(imuLO.mx) );
//      break;
//
//    case 3:
//      //Sensor 5: mz -> X, mx -> Y, -my -> Z
//      sens[4][0] = double( imuHI.calcMag(imuHI.mz) );
//      sens[4][1] = double( imuHI.calcMag(imuHI.mx) );
//      sens[4][2] = -1 * double( imuHI.calcMag(imuHI.my) );
//
//      //Sensor 6: mz -> X, mx -> Y, -my -> Z
//      sens[5][0] = double( imuLO.calcMag(imuLO.mz) );
//      sens[5][1] = double( imuLO.calcMag(imuLO.mx) );
//      sens[5][2] = -1 * double( imuLO.calcMag(imuLO.my) );
//      break;
//
//    default:
//      Serial.print( F("Error. This sensor pair doesn't exist!") );
//      while (1);
//      break;
//  };
//}
