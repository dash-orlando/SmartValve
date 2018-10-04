bool    VERBOSE       = false;                // Verbose mode flag
bool    CALIBRATION   = false;                // Calibration mode flag
bool    ROTATION      = false;                // Rotation mode flag
char    inChar        = 0x00;                 // Incoming data

void parseByte()
{
  inChar = Serial.read();
  // Serial.println(inChar);

  switch ( inChar )
  {
    // 'V'erbose Mode
    case 'V':
    case 'v':
      VERBOSE = !VERBOSE;
      Serial.print( F("VERBOSE MODE: ") );
      Serial.println( VERBOSE );
      break;

    // 'C'alibration mode
    case 'C':
    case 'c':
      CALIBRATION = !CALIBRATION;
      Serial.print( F("CALIBRATION MODE: ") );
      Serial.println( CALIBRATION );
      break;

    // 'R'otation mode
    case 'R':
    case 'r':
      ROTATION = !ROTATION;
      Serial.print( F("ROTATION MODE: ") );
      Serial.println( ROTATION );
      break;

    default:
      break;
  }

}
