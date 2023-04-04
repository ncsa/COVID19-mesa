<script lang="ts">
	import { STAGE_MAP } from '../../../simulation/constants';
	import { selectedStages } from '../../../stores';

	export let onChange;
	export let onReset;
</script>

<style>

</style>

{#each Object.values(STAGE_MAP) as stage}
	<label>
		<input type='checkbox' bind:group={$selectedStages} name='stages' value={stage.alias} on:change={onChange}>
		{stage.name}
<!--		<Stage name={stage.name} color={stage.hexColor}/>-->
	</label>
{/each}
<button on:click={onReset}>reset</button>