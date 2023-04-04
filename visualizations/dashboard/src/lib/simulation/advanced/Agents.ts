import * as THREE from 'three';
import type * as d3 from 'd3';
import { STAGE, STAGE_MAP } from '../constants';

export class Agents {
	// geometry
	public pointsGeometry: THREE.BufferGeometry;
	public positions: Float32Array;
	public colors: Float32Array;
	public sizes: Float32Array;
	public texture: THREE.Texture;
	public material: THREE.ShaderMaterial;
	public points: THREE.Points;
	public offset: number;
	public smallSize;
	public largeSize;

	// utils
	public scale: d3.ScaleLinear<number, number>;
	public scene: THREE.Scene;

	constructor(config: any) {
		const n = config.agents.length;

		this.pointsGeometry = new THREE.BufferGeometry();
		this.positions = new Float32Array(n*3);
		this.colors = new Float32Array(n*3);
		this.sizes = new Float32Array(n);
		this.texture = config.textureLoader.load("advanced/textures/particles/5_32x32.png");
		this.material = new THREE.PointsMaterial();
		this.material.size = 0.2;
		this.material.sizeAttenuation = true;
		// this.material.color = new THREE.Color('#ff88cc');
		this.material.alphaMap = this.texture;
		this.material.transparent = true;
		this.material.alphaTest = 0.01;
		// this.material.depthTest = false;
		// this.material.depthWrite = false;
		this.material.blending = THREE.AdditiveBlending;
		this.material.vertexColors = true;
		this.material.onBeforeCompile = shader => {
			shader.vertexShader =
				shader.vertexShader.replace('uniform float size;', 'attribute float size;')
		}

		this.offset = config.offset;
		this.smallSize = config.smallSize;
		this.largeSize = config.largeSize;
		this.scale = config.scale;
		this.scene = config.scene;

		this.render(config.agents);

		this.pointsGeometry.setAttribute('position', new THREE.BufferAttribute(this.positions,3));
		this.pointsGeometry.setAttribute('color', new THREE.BufferAttribute(this.colors, 3));
		this.pointsGeometry.setAttribute('size', new THREE.BufferAttribute(this.sizes, 1));

		this.points = new THREE.Points(this.pointsGeometry, this.material);
		this.scene.add(this.points);
	}

	setColor(stage: STAGE, i: number) {
		this.colors[i*3] = STAGE_MAP[stage].color.r / 255.0;
		this.colors[i*3+1] = STAGE_MAP[stage].color.g / 255.0;
		this.colors[i*3+2] = STAGE_MAP[stage].color.b / 255.0;
		if (stage == STAGE.susceptible) this.sizes[i] = this.smallSize;
		else this.sizes[i] = this.largeSize;
	}

	render(agents: any[]) {
		for (let i=0; i<agents.length; i++) {
			const x = agents[i].x;
			const y = agents[i].y;
			this.positions[i*3] = this.scale(x) + this.offset;
			this.positions[i*3+1] = 0;
			this.positions[i*3+2] = this.scale(y) + this.offset;
			this.setColor(agents[i].stage, i);
		}
		if (this.pointsGeometry.attributes.position !== undefined)
			this.pointsGeometry.attributes.position.needsUpdate = true;
		if (this.pointsGeometry.attributes.color !== undefined)
			this.pointsGeometry.attributes.color.needsUpdate = true;
		if (this.pointsGeometry.attributes.size !== undefined)
			this.pointsGeometry.attributes.size.needsUpdate = true;
	}


}