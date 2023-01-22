<script lang="ts">
import * as THREE from 'three';
import { onMount } from 'svelte';

let elemCanvas: HTMLCanvasElement;

onMount(() => {
	// Scene
	const scene = new THREE.Scene();

	// Red cube
	const geometry = new THREE.BoxGeometry(1,1,1);
	const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
	const mesh = new THREE.Mesh(geometry, material);
	scene.add(mesh);

	// Sizes
	const sizes = {
		width: 800,
		height: 600,
	}

	// Camera
	const camera = new THREE.PerspectiveCamera(75, sizes.width/sizes.height);
	camera.position.z = 3;
	scene.add(camera);

	// Renderer
	const renderer = new THREE.WebGL1Renderer({
		canvas: elemCanvas
	});
	renderer.setSize(sizes.width, sizes.height);
	renderer.render(scene, camera);
});

</script>

<canvas class='webgl' bind:this={elemCanvas}></canvas>