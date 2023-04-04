<script lang="ts">
	import NavBar from '../../lib/components/advanced/NavBar.svelte';
	import EnsembleOverview from '../../lib/components/advanced/ensemble/EnsembleOverview.svelte';
	import SimulationView from '../../lib/components/advanced/simulation/SimulationOverview.svelte';
	import { currentRun, currentStep } from '../../lib/stores';
	import AgentView from '../../lib/components/advanced/agent/AgentsView.svelte';
	import { onMount } from 'svelte';

	let currentView = 1;
	let files: File[];
	let file: File;
	let filename: string;
	let filenames: string[] = [];

	async function init() {
		currentRun.set(0);
	}

	function onSelectRun() {
		currentView = 2;
		currentStep.set(0);
	}

	async function getEnsembleSummary() {
		const response = await fetch(`http://localhost:5000/data/ensemble?filename=${filename}`);
		if (response.ok) return response.json();
	}

	async function getFilenames() {
		const response = await fetch(`http://localhost:5000/files`);
		if (response.ok) return response.json();
	}

	onMount(async () => {
		filenames = await getFilenames();
		if (filenames.length > 0) filename = filenames[0];
	});

</script>

<NavBar bind:currentView={currentView}/>
<div class='available-files'>
	Choose an ensemble:
	{#each filenames as name}
		<input type='radio' id={name} value={name} bind:group={filename}
					 on:change={init}/>
		<label for={name}>{name}</label>
	{/each}
</div>

{#key filename}
	{#if filename}
		{#if currentView == 1}
			<EnsembleOverview bind:filename onSelectRun={onSelectRun}/>
		{:else if currentView == 2}
			<SimulationView bind:filename/>
		{:else}
			<AgentView bind:filename />
		{/if}
	{/if}
{/key}


<style>
	:global(body) {
      background-color: #1A202C;
			color: white;
			font-family: monospace;
  }
</style>
