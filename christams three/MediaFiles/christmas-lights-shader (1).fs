/*{
    "CREDIT": "by Assistant",
    "CATEGORIES": [
        "generator",
        "christmas",
        "lights",
        "animation"
    ],
    "DESCRIPTION": "Animated Christmas lights that morph and fade in space",
    "ISFVSN": "2",
    "INPUTS": [
        {
            "NAME": "intensity",
            "TYPE": "float",
            "DEFAULT": 1.0,
            "MIN": 0.0,
            "MAX": 2.0
        },
        {
            "NAME": "speed",
            "TYPE": "float",
            "DEFAULT": 0.5,
            "MIN": 0.0,
            "MAX": 2.0
        },
        {
            "NAME": "size",
            "TYPE": "float",
            "DEFAULT": 0.2,
            "MIN": 0.1,
            "MAX": 1.0
        },
        {
            "NAME": "colorMix",
            "TYPE": "float",
            "DEFAULT": 0.5,
            "MIN": 0.0,
            "MAX": 1.0
        },
        {
            "NAME": "spread",
            "TYPE": "float",
            "DEFAULT": 3.0,
            "MIN": 1.0,
            "MAX": 10.0
        }
    ]
}
*/

float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

float noise(vec2 st) {
    vec2 i = floor(st);
    vec2 f = fract(st);
    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x) + (c - a)* u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

void main() {
    vec2 uv = (2.0 * gl_FragCoord.xy - RENDERSIZE.xy) / RENDERSIZE.y;
    
    // Create multiple light positions that move over time
    float t = TIME * speed;
    vec3 finalColor = vec3(0.0);
    
    for(float i = 0.0; i < 5.0; i++) {
        float offset = i * 1.256;
        vec2 pos = vec2(
            sin(t + offset) * spread,
            cos(t * 0.7 + offset) * spread
        );
        
        float d = length(uv - pos * 0.3) * (1.0/size);
        float light = 1.0 / (1.0 + d * d * 4.0);
        
        // Create different colors for each light
        vec3 lightColor = vec3(
            sin(offset * 3.14) * 0.5 + 0.5,  // red component
            sin(offset * 3.14 + 2.09) * 0.5 + 0.5,  // green component
            sin(offset * 3.14 + 4.18) * 0.5 + 0.5   // blue component
        );
        
        // Add noise to make the lights flicker
        float flicker = noise(vec2(t + i, i)) * 0.3 + 0.7;
        
        finalColor += lightColor * light * flicker;
    }
    
    // Apply intensity and color mixing
    finalColor *= intensity;
    finalColor = mix(finalColor, vec3(length(finalColor)), colorMix * 0.5);
    
    gl_FragColor = vec4(finalColor, 1.0);
}
