/*{
    "DESCRIPTION": "3D rotating light bulb with soft fade",
    "CREDIT": "",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {
            "NAME": "rotationSpeed",
            "TYPE": "float",
            "DEFAULT": 0.5,
            "MIN": 0.0,
            "MAX": 2.0,
            "LABEL": "Rotation Speed"
        },
        {
            "NAME": "pathRadius",
            "TYPE": "float",
            "DEFAULT": 0.3,
            "MIN": 0.0,
            "MAX": 1.0,
            "LABEL": "Motion Radius"
        },
        {
            "NAME": "bulbSize",
            "TYPE": "float",
            "DEFAULT": 0.2,
            "MIN": 0.05,
            "MAX": 0.5,
            "LABEL": "Bulb Size"
        },
        {
            "NAME": "glowIntensity",
            "TYPE": "float",
            "DEFAULT": 0.8,
            "MIN": 0.0,
            "MAX": 1.0,
            "LABEL": "Glow Intensity"
        },
        {
            "NAME": "bulbColor",
            "TYPE": "color",
            "DEFAULT": [1.0, 0.9, 0.7, 1.0],
            "LABEL": "Bulb Color"
        },
        {
            "NAME": "fadeSpeed",
            "TYPE": "float",
            "DEFAULT": 0.5,
            "MIN": 0.0,
            "MAX": 2.0,
            "LABEL": "Fade Speed"
        }
    ]
}*/

// Rotation matrix for 3D space
mat3 rotateY(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat3(
        c, 0, -s,
        0, 1, 0,
        s, 0, c
    );
}

mat3 rotateX(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat3(
        1, 0, 0,
        0, c, -s,
        0, s, c
    );
}

// Soft sphere function
float softSphere(vec3 p, float radius) {
    float d = length(p) - radius;
    return smoothstep(0.5, -0.1, d);
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * RENDERSIZE.xy) / min(RENDERSIZE.x, RENDERSIZE.y);
    
    // Calculate time-based movement
    float time = TIME * rotationSpeed;
    
    // Create 3D position for bulb
    vec3 bulbPos = vec3(
        cos(time) * pathRadius,
        sin(time * 0.7) * pathRadius * 0.5,
        sin(time) * pathRadius
    );
    
    // Apply rotations
    mat3 rot = rotateY(time) * rotateX(time * 0.5);
    bulbPos = rot * bulbPos;
    
    // Project 3D position to 2D space
    vec2 projected = bulbPos.xy / (bulbPos.z + 2.0);
    
    // Calculate distance for depth effect
    float depth = (bulbPos.z + 2.0) * 0.5;
    
    // Create the bulb with soft edges
    vec3 viewPos = vec3(uv - projected, 0.0);
    float sphere = softSphere(viewPos, bulbSize / depth);
    
    // Add glow effect
    float glow = sphere * glowIntensity;
    glow += pow(sphere, 3.0) * 2.0;
    
    // Add fade effect
    float fade = sin(TIME * fadeSpeed) * 0.5 + 0.5;
    glow *= fade;
    
    // Apply color and intensity
    vec3 finalColor = bulbColor.rgb * glow;
    
    // Add ambient glow
    finalColor += bulbColor.rgb * pow(glow, 2.0) * 0.5;
    
    gl_FragColor = vec4(finalColor, 1.0);
}
