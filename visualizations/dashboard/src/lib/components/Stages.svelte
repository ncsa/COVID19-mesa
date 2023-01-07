<script>
	import { STAGE_COLOR } from '../simulation/constants';
	import Stage from './Stage.svelte';

	const stages = [
		{name: "susceptible", color: "#"+STAGE_COLOR.susceptible},
		{name: "exposed", color: "#"+STAGE_COLOR.exposed},
		{name: "symptoms detected", color: "#"+STAGE_COLOR.sympdetected},
		{name: "severe", color: "#"+STAGE_COLOR.severe},
		{name: "deceased", color: "#"+STAGE_COLOR.deceased},
		{name: "asymptomatic", color: "#"+STAGE_COLOR.asymptomatic},
	];
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

<p>Stages:</p>
<div class='stages'>
	{#each stages as stage}
		<Stage name={stage.name} color={stage.color}/>
	{/each}
</div>
