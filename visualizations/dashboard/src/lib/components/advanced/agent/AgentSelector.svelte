<script lang="ts">
export let ids;
export let selectedIDs;
export let onChange;

</script>

<div id='agent-search-container'>
	<input type='search' id='search-field' placeholder='Enter agent id' autocomplete='off'>

	<div id='agent-checkboxes'>
		{#each ids as agent}
			<div>
				<input type='checkbox' bind:group={selectedIDs} on:change={onChange} value={agent}><label>{agent}</label>
			</div>
		{/each}
	</div>


</div>

<style>
	#agent-search-container {
			display: flex;
			flex-direction: column;
	}

	#agent-checkboxes {
			height: 10%;
			overflow-y: scroll;
	}
</style>