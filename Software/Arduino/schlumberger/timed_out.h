#define TIMEOUT 5000

bool timed_out( long unsigned int elapsed_time, long unsigned int timers[] )
{

  for ( uint8_t i = 0; i < sizeof( timers ) - 1; i++ )
  {
    if ( timers[i] > 0 )  continue;
    else                  return false;
  }

  if ( (millis() - elapsed_time > TIMEOUT) && !rotated_state )
  {
    for ( uint8_t i = 0; i < sizeof( timers ) - 1; i++ )
    {
      timers[i] = 0;
    }
  }

  return true;
}

