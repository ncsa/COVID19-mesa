<script>
	import { STAGE_MAP } from '../../../simulation/constants';
	import Stage from './Stage.svelte';
</script>

<style>
	.stages {
			display: flex;
			flex-direction: column;
      justify-content: space-between;
			gap: 10px;
			align-content: center;
			margin-bottom: 16px;
	}

</style>

<!--<p>Stages:</p>-->
<div class='stages'>
	{#each Object.values(STAGE_MAP) as stage}
		<Stage name={stage.name} color={stage.hexColor}/>
	{/each}
</div>
