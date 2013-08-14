#include "colors.inc"    // The include files contain
#include "stones.inc"    // pre-defined scene elements

#include "textures.inc"    // pre-defined scene elements
#include "shapes.inc"
#include "glass.inc"
#include "metals.inc"
#include "woods.inc"     

#include "jv4779_pov.inc"                   

global_settings {
    assumed_gamma 1.0
    max_trace_level 40

    photons {
        spacing 0.03
        autostop 0
        jitter 0    
    }
}

#declare wheel_r = 0.625 * 25.4;
#declare Wc = 2.5 * 25.4;
#declare Ht = 0.265 * 25.4;
#declare Hb = 1.405 * 25.4;

#declare Sw = 3.5 * 25.4;
#declare Sh = 2 * 25.4;

background { color <0.2,0.2,0.2> }

camera {
    location <Wc, 70, 0>
    look_at  <Wc, 0 ,  0>
    sky <0,0,-1>
    translate<-35,0,0>
}       

#declare MediaGlass=
    media {
        emission .5 absorption 0
        scattering {10,1}
        intervals 2 samples 1,3
        confidence 0.8 variance 1/100
        density {
            boxed color_map {
                [0    rgb .6]
                [1    rgb .6]
            }
        }
    }


/*      
// top display screen      
box {
    <Sw/2+Wc, wheel_r+Ht,  -Sh/2>,
    <Wc-Sw/2, wheel_r+Ht+.1, Sh/2>
    pigment { White filter .5}
    interior {
        ior 1.5
        media {
            MediaGlass
            scale <.4,25,25>
            translate x*22
        }
    }//end interior
    normal {bumps .1 scale <.01,.01,150> rotate x*-45 turbulence .5}
    finish {phong 0 specular 0}
    hollow
}
*/

/*    
// bottom reflecting mirror    
box {
    <Sw/2+Wc, -10.287,  -Sh/2>,
    <Wc-Sw/2, -10.387, Sh/2>
    //texture { pigment {White} }
    finish { reflection { 1.0 } }
    photons{
        target
        reflection on
    }
  }
*/
  
// bottom screen
box {
    <Wc+Sw/2, -(2*Hb+Ht)+wheel_r,  -Sh/2>,
    <Wc-Sw/2, -(2*Hb+Ht)-0.1+wheel_r, Sh/2>
    texture {pigment {White}   }
}

// sphere at 0,0,0 to show origin  
sphere {
    <0,0,0>, 2
    texture {
        pigment {color <1,0,0>}
    }
    translate <0,0,0>
}

// backdrop to mirrored spin disk      
cylinder {
    <0, 0, 0>,
    <-2, 0, 0>,
    wheel_r*1.1
    texture { 
        pigment {
            checker Red, White scale 10
        }
    }
    translate <-3,0,0>
    rotate <-clock-2,0>
}                              

// spin mirror
object {
    m_name
    finish { reflection { 1.0 } }
    photons{
        target
        reflection on
    }
    rotate <0,90,0>
    rotate <90,0,0>
    rotate <-clock-2,0>
}

light_source { <Wc/2, 10, 0> color White*0.5 photons { reflection off }  }

light_source {
    <20, wheel_r, 0>
    color White
    spotlight
    radius 1/4
    falloff 1/2
    tightness 100
    point_at <0, wheel_r, 0>
    photons {
        reflection on
    }    
}


