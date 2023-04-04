<script>
	export let controls;
	let isStop = false;


	function stop() {
		isStop = true;
		controls.stop();
	}

	function start() {
		isStop = false;
		controls.start();
	}

	function reset() {
		isStop = false;
		controls.reset();
	}

</script>

<div>
	{#if isStop}
		<button on:click={start}>Start</button>
		<button on:click={reset}>Reset</button>
	{:else}
		<button on:click={stop}>stop</button>
	{/if}

</div>