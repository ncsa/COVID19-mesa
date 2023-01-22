<script lang="ts">
	import NavBar from '../../lib/components/advanced/NavBar.svelte';

	let currentView = 1;
</script>

<NavBar bind:currentView={currentView}/>
{#if currentView == 1}
	<h1>Ensemble simulation overview</h1>
	{:else if currentView == 2}
	<h1>Simulation view</h1>
	{:else}
	<h1>Agent view</h1>
{/if}

<style>
	:global(body) {
      background-color: #1A202C;
			color: white;
			font-family: monospace;
  }

	h1 {
			margin: 10px;
	}
</style>
