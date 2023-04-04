attribute float opacity;

varying vec4 vcolor;

void main() {
    vcolor = vec4(color, opacity);
    vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );
    gl_Position = projectionMatrix * mvPosition;
}