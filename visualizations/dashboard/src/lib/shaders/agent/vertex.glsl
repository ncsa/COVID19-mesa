attribute float aSize;

varying vec2 vUv;
varying vec3 vColor;

void main() {
    vec4 modelPosition = modelMatrix * vec4(position, 1.0);
    vec4 viewPosition = viewMatrix * modelPosition;
    vec4 projectedPosition = projectionMatrix * viewPosition;
    gl_Position = projectedPosition;

    gl_PointSize = aSize * 10.0;
    gl_PointSize *= (1.0 / - viewPosition.z);

    vUv = vUv;
    vColor = color;
}