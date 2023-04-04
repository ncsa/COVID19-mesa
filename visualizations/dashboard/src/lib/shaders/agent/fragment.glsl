varying vec2 vUv;
varying vec3 vColor;

void main()
{
    // Disc
    float strength = distance(gl_PointCoord, vec2(0.5));
    strength *= 1.8;
    strength = 1.0 - strength;

    float a = 1.0;
    if (strength <= 0.5) a = 0.0;

    gl_FragColor = vec4(vColor*strength, a);
}