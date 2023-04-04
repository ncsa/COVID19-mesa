<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	import Controls from './Controls.svelte';
	import Stages from './Stages.svelte';

	const dispatch = createEventDispatcher();
	const submit = () => dispatch('submit');

	export let step;
	export let controls;
	export let showGridlines = true;
</script>

<style>
	* {
			display: flex;
			color: white;
			font-family: monospace;
	}
	.options {
			display: flex;
			flex-direction: column;

	}
</style>

<section style='padding:5vh;display: flex;flex-grow: 1;background-color: #332d3666;flex-direction: column'>
	<h1>Step: {step}</h1>

	<Controls controls={controls} />
	<Stages />
	<div class='options'>
		<p>Options:</p>
		<label>
			<input type='checkbox' bind:checked={showGridlines} on:click={submit}>
			<p>Show gridlines</p>
		</label>
	</div>

</section>

