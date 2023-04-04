<script lang="ts">
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import SimulationCanvas from './SimulationCanvas.svelte';
	import InfoBar from './InfoBar.svelte';
	import { currentRun, currentStep } from '../../../stores';

	export let filename;
	let run;
	let w, h;

	onMount(async () => {
		run = await getRun();
		console.log(run);
	});

	async function getRun() {
		const response = await fetch(`http://localhost:5000/data/simulation?filename=${filename}&id=${$currentRun}`);
		if (response.ok) return response.json();
	}

</script>

{#key filename}
<div id='simulation-container' transition:fade>
	<h1>Simulation run {$currentRun} overview at step {$currentStep.toFixed(0)}</h1>
	<div id='infobar-container'>
		<InfoBar/>
	</div>
	<div id='canvas-container' bind:clientWidth={w} bind:clientHeight={h}>
		{#if run}
			<SimulationCanvas
				bind:run={run}
				bind:step={$currentStep}
				bind:parentWidth={w}
				bind:parentHeight={h} />
		{/if}
	</div>
</div>
{/key}



<style>
	#simulation-container {
			display: flex;
			flex-direction: column;
			flex-grow: 1;
			overflow: hidden;
	}
	#infobar-container {
			z-index: 2;
	}
	#canvas-container {
			display: flex;
			flex-grow: 1;
			z-index: 1;
	}
</style>
