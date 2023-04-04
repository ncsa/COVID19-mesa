<script lang="ts">
	import { fade } from 'svelte/transition';
	import EnsembleOverviewChart from './EnsembleOverviewChart.svelte';
	import EnsembleStageSelector from './EnsembleStageSelector.svelte';
	import { onMount } from 'svelte';
	import { maxFreq, maxStep, selectedStages } from '../../../stores';

	export let filename;
	export let onSelectRun;
	let data;

	function onReset() {
		selectedStages.set(
			["Stage.SYMPDETECTED", "Stage.SEVERE","Stage.EXPOSED","Stage.ASYMPTOMATIC"]
		);
		getEnsembleSummary();
	}

	async function getEnsembleSummary() {
		const response = await fetch(
			`http://localhost:5000/data/ensemble?filename=${filename}
			&${$selectedStages.map(d => "stage="+d).join('&')}`
		);
		if (response.ok) {
			data = await response.json();
			maxStep.set(data.maxStep);
			maxFreq.set(data.maxFreq);
		}
	}

	onMount(getEnsembleSummary);

</script>
<div id='ensemble-container' in:fade >
	<h1>Ensemble simulation overview</h1>
	<EnsembleStageSelector onChange={getEnsembleSummary} onReset={onReset}/>
	<EnsembleOverviewChart bind:filename onSelectRun={onSelectRun} data={data}/>
</div>


<style>
</style>