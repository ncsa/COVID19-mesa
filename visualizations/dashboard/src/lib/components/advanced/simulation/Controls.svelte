<script lang="ts">
	import { currentStep, maxStep, play } from '../../../stores';
	import { stepSize } from '../../../simulation/constants';

	let step;
	let max;
	let start;

	currentStep.subscribe(value => {step = value});
	maxStep.subscribe(value => max = value);
	play.subscribe(value => start = value);

	function playSimulation() {
		play.set(true);
	}
	function stopSimulation() {
		play.set(false);
	}
	function toggleStep() {
		currentStep.set(step);
		play.set(false);
	}

</script>
<p>Controls</p>

{#if start}
	<button on:click={stopSimulation}>Stop</button>
{:else}
	<button on:click={playSimulation}>Play</button>
{/if}
<div>
	<input type='range'
				 bind:value={step}
				 id='stepRange'
				 name='step'
				 min='0'
				 max={max}
				 step={stepSize}
				 on:input={toggleStep}
				 on:change={toggleStep} >
	<label for='stepRange'>Step {step}</label>
</div>

<!--<div>-->
<!--	<input type='range'-->
<!--				 value={framerate}-->
<!--				 id='framerate'-->
<!--				 name='framerate'-->
<!--				 min={1}-->
<!--				 max={20}-->
<!--				 step='1' >-->
<!--	<label for='stepRange'>{framerate} step(s) per frame</label>-->
<!--</div>-->

