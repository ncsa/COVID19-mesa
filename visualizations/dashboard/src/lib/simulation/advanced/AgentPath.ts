import * as THREE from 'three';

export class AgentPath {

	public geometry: THREE.BufferGeometry;
	public positions: Float32Array;
	public alphas: Float32Array;
	public points;
	public drawCount: number;
	public lines: THREE.LineSegments;
	public material: THREE.LineBasicMaterial;

	constructor(config: any) {
		this.geometry = new THREE.BufferGeometry();
		this.positions = new Float32Array(config.points.length * 3);
		this.alphas = new Float32Array(config.points.length);
		this.drawCount = config.drawCount ?? 0;
		this.points = config.points;

		for (let i=0; i<config.points.length; i++) {
			this.positions[i*3] = config.scale(config.points[i].x) + config.offset;
			this.positions[i*3+1] = 0
			this.positions[i*3+2] = config.scale(config.points[i].y) + config.offset;
		}
		this.geometry.setAttribute("position", new THREE.BufferAttribute(this.positions, 3));

		this.material = new THREE.LineBasicMaterial( {
			color: 0xffffff,
		} );

		this.lines = new THREE.LineSegments(this.geometry, this.material);
		config.scene.add(this.lines);

		this.render();
	}

	render() {
		this.lines.geometry.setDrawRange(0, this.drawCount);
		this.lines.geometry.computeBoundingBox();
		this.lines.geometry.computeBoundingSphere();
		if (this.geometry.attributes.position !== undefined)
			this.geometry.attributes.position.needsUpdate = true;
	}

	dispose() {
		this.lines.geometry.dispose();
		this.material.dispose();
		this.lines.removeFromParent();
	}
}