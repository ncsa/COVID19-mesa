<script lang="ts">
	import { fade } from 'svelte/transition';
	import * as THREE from 'three';
	import * as d3 from 'd3';
	import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
	import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
	import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
	import { AfterimagePass } from 'three/examples/jsm/postprocessing/AfterimagePass';
	import * as dat from 'lil-gui';
	import Stats from 'stats.js';

	import { onDestroy, onMount } from 'svelte';
	import { Grid } from '../../../simulation/advanced/Grid';
	import { Agents } from '../../../simulation/advanced/Agents';
	import { currentStep, maxStep, play } from '../../../stores';
	import { AgentPath } from '../../../simulation/advanced/AgentPath';
	import { stepSize } from '../../../simulation/constants';

	// three.js and canvas objects
	let elemCanvas: HTMLCanvasElement;
	let renderer: THREE.WebGLRenderer;
	let composer: EffectComposer;
	let camera;
	const scene = new THREE.Scene();
	const stats = new Stats();
	const sizes = {
		width: 800,
		height: 600,
	}
	export let parentWidth;
	export let parentHeight;
	const clock = new THREE.Clock();
	// three.js mouse click objects
	const raycaster = new THREE.Raycaster();
	const mouse = new THREE.Vector2();
	let intersection = null;

	// Debug
	const gui = new dat.GUI();
	const parameters = {
		grid: true,
		trail: false,
		agentNormalSize: 0.2,
		agentAbnormalSize: 0.3,
		framesPerStep: 3,
		raycasterThreshold: 0.1,
	};

	// Data
	export let run: any[];
	export let step;
	let perStepData;
	let perIdData;
	let maxStepValue: number;
	let playValue: boolean;
	let frameRateDelta: number;

	currentStep.subscribe(value => step = value);
	play.subscribe(value => playValue = value);
	maxStep.subscribe(value => maxStepValue = value);

	// Geometries
	let grid: Grid;
	let agents: Agents;
	const paths: Map<number, AgentPath> = new Map();
	const gridWidth = 5;
	const scale = d3.scaleLinear([0, 50], [-gridWidth, gridWidth]);
	const offset = gridWidth / 50;

	onMount(() => {
		init();
	});

	onDestroy(() => {
		if (renderer !== undefined) {
			renderer.dispose();
			renderer.forceContextLoss();
		}
		if (composer !== undefined) composer.dispose();
		gui.destroy();
	});

	function init() {
		initRun();

		// Stats
		stats.showPanel(0); // 0: fps, 1: ms, 2: mb, 3+: custom
		window.document.body.appendChild(stats.dom);
		sizes.width = parentWidth;
		sizes.height = parentHeight;

		// Geometries
		initGrid();
		initAgents();
		initPaths();
		initRayCaster();

		// Camera
		camera = new THREE.PerspectiveCamera(75, sizes.width/sizes.height);
		camera.position.y = 7;
		scene.add(camera);

		// Controls
		const controls = new OrbitControls(camera, elemCanvas);
		controls.enableDamping = true;
		controls.maxPolarAngle = (Math.PI- 0.1)/2; // radians

		initRenderer();

		// GUI debug
		addDebugParams();

		/**
		 * Animate
		 */
		frameRateDelta = parameters.framesPerStep;
		renderer.setAnimationLoop(tick);
	}

	function initRun() {
		[perIdData, perStepData] = findPositionsForRun(d3.group(run, d => d.id));
		perStepData.forEach((value, key) => {
			perStepData.set(key, value.sort((a, b) => d3.ascending(a.id,b.id)));
		});
	}

	function tick() {
		stats.begin();

		const elapsedTime = clock.getElapsedTime();

		if (frameRateDelta == 0) loadNextStep();
		frameRateDelta  = (frameRateDelta - 1) % parameters.framesPerStep;

		trackMouseMove();

		// Render
		if (parameters.trail) composer.render();
		else renderer.render(scene, camera);

		stats.end();
	}

	function initRayCaster() {
		elemCanvas.addEventListener('mousemove', (event) => {
			const rect = renderer.domElement.getBoundingClientRect();
			const x = event.clientX - rect.left;
			const y = event.clientY - rect.top;
			mouse.x = x / sizes.width * 2 - 1;
			mouse.y = - (y / sizes.height) * 2 + 1;
		});
		raycaster.params.Points.threshold = parameters.raycasterThreshold;
		elemCanvas.addEventListener('mousedown', updateAgentPaths);
	}

	function initAgents() {
		agents = new Agents({
			agents: perStepData.get(step),
			scene: scene,
			scale: scale,
			offset: offset,
			smallSize: parameters.agentNormalSize,
			largeSize:parameters.agentAbnormalSize,
			textureLoader: new THREE.TextureLoader(),
		});
	}

	function initGrid() {
		grid = new Grid({size: gridWidth*2, division: 50});
		grid.geometry.visible = parameters.grid;
		scene.add(grid.geometry);
	}

	function initPaths() {
		const initials = [];
		initials.forEach(id => paths.set(id, new AgentPath({
			points: perIdData.get(id),
			drawCount: step,
			scale: scale,
			offset: offset,
			scene: scene,
		})));
	}

	function initRenderer() {
		// Renderer
		renderer = new THREE.WebGL1Renderer({
			canvas: elemCanvas,
			alpha: true,
			antialias: true,
			// preserveDrawingBuffer: true,
		});
		// renderer.autoClearColor = false;
		renderer.setSize(sizes.width, sizes.height);
		renderer.render(scene, camera);

		// Effects
		const renderScene = new RenderPass(scene, camera);
		// const bloomPass = new UnrealBloomPass(new THREE.Vector2(sizes.width, sizes.height), 1.0, 0, 0);
		const afterImagePass = new AfterimagePass();
		afterImagePass.uniforms["damp"].value = 0.975;

		// Effect composer
		composer = new EffectComposer(renderer);
		composer.addPass(renderScene);
		// composer.addPass(bloomPass);
		composer.addPass(afterImagePass);
	}

	function loadNextStep() {
		if (step < maxStepValue) {
			if (playValue) {
				currentStep.update(n => +(n+stepSize).toFixed(2));
			}
		} else {
			play.set(false);
		}
		agents.render(perStepData.get(step));
		drawPaths();
	}

	function drawPaths() {
		paths.forEach(path => {
			path.drawCount = step*10;
			path.render();
		});
	}

	function trackMouseMove() {
		raycaster.setFromCamera(mouse, camera);

		const intersections = raycaster.intersectObject(agents.points, false );
		intersection = ( intersections.length ) > 0 ? intersections[0].index : null;
	}

	function updateAgentPaths() {
		if (intersection === null) return;
		if (paths.has(intersection)) {
			paths.get(intersection).dispose();
			paths.delete(intersection);
		} else {
			paths.set(intersection, new AgentPath({
				points: perIdData.get(intersection),
				drawCount: step,
				scale: scale,
				offset: offset,
				scene: scene,
			}))
		}
	}

	function addDebugParams() {
		gui.add(parameters, 'grid')
			.onFinishChange((value) => grid.geometry.visible = value );
		gui.add(parameters, 'trail');
		gui.add(parameters, 'agentNormalSize')
			.min(0.01).max(1).step(0.01)
			.onChange(() => agents.smallSize = parameters.agentNormalSize);
		gui.add(parameters, 'agentAbnormalSize')
			.min(0.01).max(1).step(0.01)
			.onChange(() => agents.largeSize = parameters.agentAbnormalSize);
		gui.add(parameters, 'framesPerStep')
			.min(1).max(20).step(1);
		gui.add(parameters, 'raycasterThreshold')
			.min(0.01).max(0.4).step(0.001)
			.onFinishChange(() => raycaster.params.Points.threshold = parameters.raycasterThreshold);
	}


	function findPositionsForRun(data) {
		const output = [];
		const frames = 1/stepSize;

		data.forEach(d => {
			for (let i=0; i<d.length-1; i++) {
				let delta_x = d[i+1].x-d[i].x;
				let delta_y = d[i+1].y-d[i].y;
				if (Math.abs(delta_x) > 1) delta_x = -1 * Math.sign(delta_x);
				if (Math.abs(delta_y) > 1) delta_y = -1 * Math.sign(delta_y);
				for (let t=0; t<frames; t++) {
					let x = delta_x*t/frames + d[i].x;
					let y = delta_y*t/frames + d[i].y;
					if (x < -0.5) x += 50;
					else if (x > 49.5) x -= 50;
					if (y < -0.5) y += 50;
					else if (y > 49.5) y -= 50;
					output.push({
						id: d[i].id,
						x: x,
						y: y,
						step: d[i].step + t/frames,
						stage: d[i].stage,
					});
				}
			}
			output.push({
				id: d[d.length-1].id,
				x: d[d.length-1].x,
				y: d[d.length-1].y,
				step: d[d.length-1].step,
				stage: d[d.length-1].stage,
			});
		})

		return [d3.group(output, d => d.id), d3.group(output, d => d.step)];
	}

</script>


<canvas class='simulation-canvas' bind:this={elemCanvas} transition:fade/>

