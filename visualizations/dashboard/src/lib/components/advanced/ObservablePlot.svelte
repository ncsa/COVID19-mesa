<script>
	import * as Plot from '@observablehq/plot';

	export let options;

	function myplot(node) {
		node.appendChild(
			Plot.plot(options)
		)
	}
</script>

{#key options}
	<div use:myplot {...$$restProps}></div>
{/key}