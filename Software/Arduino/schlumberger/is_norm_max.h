static long unsigned int  timer[NSENS]    = {0};
static bool               norm_max[NSENS] = {0};

void is_norm_max( double left, double center, double right, uint8_t NDX)
{
  
  if ( center > left + center*(0.1) && center > right + center*(0.1) )
  //if ( center > left*(1.25) && center > right*(1.25) )
  //if ( center > right*(1.25) )
  {
    norm_max[NDX] = true;
    timer[NDX]    = millis();
  }

  if ( CALIBRATION )
  {
    char  buff[65] = {'\0'};
    char  arr[150] = {'\0'};
    Serial.print( F("SENSOR [ ") ); Serial.print( NDX+1 ); Serial.print( F(" ] : ") );
    strcat( buff, "Norm[ n-1 ] = " ); dtostrf( sqrt(left)   , 5, 3, &buff[strlen(buff)] );
    strcat( buff, " || Norm[ n ] = " ); dtostrf( sqrt(center) , 5, 3, &buff[strlen(buff)] );
    strcat( buff, " || Norm[ n+1 ] = " ); dtostrf( sqrt(right)  , 5, 3, &buff[strlen(buff)] );
    Serial.println( buff );

//    strcat( arr, "center = " ); dtostrf( sqrt(center) , 5, 3, &arr[strlen(arr)] );
//    strcat( arr, " || left + center*(0.1) = " ); dtostrf( sqrt(left) + sqrt(center)*(0.1), 5, 3, &arr[strlen(arr)] );
//    strcat( arr, " || right + center*(0.1) = " ); dtostrf( sqrt(right) + sqrt(center)*(0.1), 5, 3, &arr[strlen(arr)] );
//    Serial.println( arr );
    
    if( norm_max[NDX] )
    {
      Serial.print( F("--------------------------------------------------------------\n") );
      Serial.print( F("SENSOR [ ") ); Serial.print( NDX+1); Serial.print( F(" ] timer: ") ); Serial.println( timer[NDX] );
      Serial.print( F("--------------------------------------------------------------\n") );
    }
    else
    {
      Serial.print( F("--------------------------------------------------------------\n") );
      Serial.println( F(" ") );
      Serial.print( F("--------------------------------------------------------------\n") );
    }

    if ( NDX == NSENS - 1 )
        Serial.println( "\n==============================\n" );
  }
}

