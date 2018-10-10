/*
 * A generalized approach for the exponential moving average
 * data smoothing based on the microsmooth library.
 *
 * Allows for multiple registers (smoothing for multiple
 * readings instead of one. Good stuff!!)
 * 
 * Recall that the exponential moving average has the form of:
 * 
 * s_n = ALPHA*x_n + ( 1-ALPHA )*s_{n-1}
 * where 0 < ALPHA < 1 is the smoothing factor
 * High ALPHA: NO smoothing.
 * Low ALPHA : YES smoothing.
 * VERY Low ALPHA: GREAT smoothing but less responsive to recent changes.
 */

// System parameters
#define NSENS       2                                 // Number of sensors
#define NAXES       3                                 // Number of axes
#define ALPHA_READ  0.25                              // Smoothing factor
#define ALPHA_NORM  0.05                              // Smoothing factor

static double exp_avg_read[NSENS][NAXES]  =  { 0 };   //  {Bx, By, Bz}
static double exp_avg_norm[NSENS]         =  { 0 };   //  {Norm_1. Norm_2}

// ============================  EMA Filter  ===========================
double ema_filter( double current_value, byte sens, byte axis, bool filter_norm = false )
{
  if( filter_norm )
  {
    // Filter data
    exp_avg_norm[sens] = ALPHA_NORM*current_value + (1 - ALPHA_NORM)*exp_avg_norm[sens];
  
    // Return Filtered data
    return( exp_avg_norm[sens] );
  }

  else
  {
    // Filter data
    exp_avg_read[sens][axis] = ALPHA_READ*current_value + (1 - ALPHA_READ)*exp_avg_read[sens][axis];
  
    // Return Filtered data
    return( exp_avg_read[sens][axis] );
  }
}
