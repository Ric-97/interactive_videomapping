/*{
    "DESCRIPTION": "3D rising light effect with dynamic movement",
    "CREDIT": "",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {
            "NAME": "speed",
            "TYPE": "float",
            "DEFAULT": 0.5,
            "MIN": 0.0,
            "MAX": 2.0,
            "LABEL": "Rise Speed"
        },
        {
            "NAME": "noiseScale",
            "TYPE": "float",
            "DEFAULT": 4.0,
            "MIN": 1.0,
            "MAX": 10.0,
            "LABEL": "Pattern Scale"
        },
        {
            "NAME": "height",
            "TYPE": "float",
            "DEFAULT": 0.5,
            "MIN": 0.0,
            "MAX": 1.0,
            "LABEL": "Height"
        },
        {
            "NAME": "baseColor",
            "TYPE": "color",
            "DEFAULT": [0.2, 0.4, 1.0, 1.0],
            "LABEL": "Base Color"
        },
        {
            "NAME": "highlightColor",
            "TYPE": "color",
            "DEFAULT": [1.0, 0.8, 0.4, 1.0],
            "LABEL": "Highlight Color"
        },
        {
            "NAME": "intensity",
            "TYPE": "float",
            "DEFAULT": 0.8,
            "MIN": 0.0,
            "MAX": 1.0,
            "LABEL": "Light Intensity"
        }
    ]
}*/

// Simplex 2D noise
vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }

float snoise(vec2 v) {
    const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                       -0.577350269189626, 0.024390243902439);
    vec2 i  = floor(v + dot(v, C.yy));
    vec2 x0 = v -   i + dot(i, C.xx);
    vec2 i1;
    i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec4 x12 = x0.xyxy + C.xxzz;
    x12.xy -= i1;
    i = mod(i, 289.0);
    vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0))
        + i.x + vec3(0.0, i1.x, 1.0));
    vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
        dot(x12.zw,x12.zw)), 0.0);
    m = m*m;
    m = m*m;
    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;
    m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
    vec3 g;
    g.x  = a0.x  * x0.x  + h.x  * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
}

void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE;
    
    // Create base noise pattern
    float baseNoise = snoise(uv * noiseScale);
    
    // Create moving wave effect
    float wave = sin(uv.x * 3.14159 * 2.0 + TIME * speed) * 0.5 + 0.5;
    
    // Combine noise and wave for 3D effect
    float heightMap = baseNoise * 0.5 + wave * 0.5;
    heightMap *= height;
    
    // Create rising effect
    float yOffset = mod(TIME * speed, 2.0);
    float risingMask = smoothstep(yOffset - 0.5, yOffset, uv.y);
    risingMask *= smoothstep(yOffset + 0.5, yOffset, uv.y);
    
    // Add depth shading
    float depthShading = heightMap * risingMask;
    depthShading = pow(depthShading, 1.5);
    
    // Combine colors
    vec4 color = mix(baseColor, highlightColor, depthShading);
    color.a *= intensity * risingMask;
    
    // Add highlights for 3D effect
    float highlight = pow(heightMap, 3.0) * risingMask;
    color.rgb += highlight * highlightColor.rgb * intensity;
    
    gl_FragColor = color;
}
