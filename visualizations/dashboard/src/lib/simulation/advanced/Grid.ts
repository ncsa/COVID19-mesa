import * as THREE from 'three';

export class Grid {
	public geometry;

	constructor(config: any) {
		this.geometry = new THREE.GridHelper(config.size, config.division, "#919294", "#616060");
	}
}