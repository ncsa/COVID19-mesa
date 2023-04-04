<script lang="ts">
	import * as PIXI from 'pixi.js';
	import * as d3 from 'd3';
	import { onDestroy, onMount } from 'svelte';
	import { Agent } from '../../simulation/basic/Agent';
	import { Grid } from '../../simulation/basic/Grid';
	import InfoBar from './InfoBar.svelte';

	let socket: WebSocket;

	let simulation: PIXI.Application;
	let container: PIXI.Container;
	let elemCanvas: HTMLCanvasElement;
	let grid: Grid;

	let step = 0;
	let isStop = false;
	let showGridlines;

	const agents = new Map();

	const margin = 50;
	let width;
	let height;
	let x_pos;
	let y_pos;

	const backgroundColor = 0x0f1014;

	onMount(async () => {
		// Pixi.js Settings
		PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

		simulation = new PIXI.Application({
			view: elemCanvas,
			resizeTo: window,
			backgroundColor: backgroundColor,
		});

		if (simulation === null) return;
		container = new PIXI.Container();

		PIXI.Assets.add("bunny", "bunny.png");
		PIXI.Assets.add("circle", "circle.png");
		PIXI.Assets.add("trail", "trail.png");
		const textures = await PIXI.Assets.load(["bunny", "circle", "trail"]);
		x_pos = d3.scaleLinear()
			.domain([0, 49])
			.range([margin, width*0.8-margin]);
		y_pos = d3.scaleLinear()
			.domain([0, 49])
			.range([margin, height-margin]);

		socket = new WebSocket("ws://localhost:8521/ws");
		socket.addEventListener("open", () => {
			socket.send('{"type":"reset"}');
		});

		const gridConfig = {
			width: 50,
			height: 50,
			x_pos: x_pos,
			y_pos: y_pos,
			sizeX: (width*0.8 - 2*margin) / 50,
			sizeY: (height - 2*margin) / 50,
		}
		grid = new Grid(gridConfig);
		container.addChild(grid.container);
		simulation.stage.addChild(container);

		socket.onmessage = (event) => {
			let data = JSON.parse(event.data);
			const agentsData = data.data[0][0];
			for (let i=0; i<agentsData.length; i++) {
				if (agents.has(agentsData[i].id)) {
					const agent = agents.get(agentsData[i].id);
					agent.x = x_pos(agentsData[i].x);
					agent.y = y_pos(agentsData[i].y);
					agent.stage = agentsData[i].stage;
					agent.render();
				} else {
					const config = {
						id: agentsData[i].id,
						stage: agentsData[i].stage,
						x: x_pos(agentsData[i].x),
						y: y_pos(agentsData[i].y),
						texture: textures.circle,
						trailTexture: textures.trail,
						showPath: agentsData[i].id == 77,
						scale: 0.2,
					}
					const agent = new Agent(config);
					agents.set(agent.id, agent);
					container.addChild(agent.container);
				}
			}
			simulation.render();

			agents.forEach((agent) => {
				if (!agent.rendered) {
					container.removeChild(agent.container);
					agent.destroy();
					agents.delete(agent.id);
				}
			});
			agents.forEach((agent) => agent.rendered = false);

			if (!isStop) {
				step += 1;
				socket.send(`{"type":"get_step","step":${step}}`);
			}
		}

	});

	onDestroy(() => {
		// Helps memory leak issues
		if (simulation !== undefined) simulation.destroy();

		if (socket) {
			socket.close();
			console.log("Closed connection");
		}
	});

	function reset() {
		stop();
		agents.forEach((agent: Agent) => {
			agent.destroy();
		});
		agents.clear();
		container.destroy();
		container = new PIXI.Container();
		simulation.stage.addChild(container);
		container.addChild(grid.container);

		socket.send(`{"type":"reset"}`);
		simulation.render();
		step = 0;
		isStop = false;
	}

	function stop() {
		isStop = true;
	}

	function start() {
		isStop = false;
		step += 1;
		socket.send(`{"type":"get_step","step":${step}}`);
	}

	function resizeCanvas() {
		x_pos = d3.scaleLinear()
			.domain([0, 49])
			.range([margin, width*0.8-margin]);
		y_pos = d3.scaleLinear()
			.domain([0, 49])
			.range([margin, height-margin]);
		grid.resize(x_pos, y_pos,(width*0.8 - 2*margin) / 50, (height - 2*margin) / 50);
		simulation.render();
	}

	function displayGridlines() {
		if (!showGridlines) grid.color = 0xffffff;
		else grid.color = backgroundColor;
		grid.draw();
	}

	const controls = {
		start: start,
		stop: stop,
		reset: reset,
	}


</script>

<svelte:window bind:innerWidth={width} bind:innerHeight={height} />

<div class='container_div' style='position: relative;'>
	<div class='hover_div' style='position: absolute;right: 0;height: 100vh; width: 30vw; display: flex'>
		<InfoBar step={step} controls={controls} bind:showGridlines={showGridlines} on:submit={displayGridlines}/>
	</div>
	<canvas id="simulation" bind:this={elemCanvas} style='display:block'></canvas>
</div>
