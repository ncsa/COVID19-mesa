<script lang='ts' type='module'>
	import ObservablePlot from '../ObservablePlot.svelte';
	import * as Plot from '@observablehq/plot';
	import { maxStep } from '../../../stores';

	export let data;

</script>

{#if data && data.length > 0}
	<ObservablePlot options={{
		style:{
			background: "#1A202C",
			},
			facet: {
				data: data,
				y: "edge",
				marginLeft: 200,
			},
			r: {
				range: [0, 1]
			},
			x: {
				domain: [0, $maxStep]
			},
			marks: [
				Plot.dot(data,Plot.binX({r: "count", strokeWidth: "count"}, {x: {thresholds: 10, value:"days"}}))
			]
		}}
	/>
{:else}
	<p>Agent(s) has/have no state change.</p>
{/if}


