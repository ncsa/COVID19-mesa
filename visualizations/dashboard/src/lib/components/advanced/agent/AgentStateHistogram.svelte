<script lang='ts' type='module'>
	import ObservablePlot from '../ObservablePlot.svelte';
	import * as Plot from '@observablehq/plot';
	import * as d3 from 'd3';

	export let data;

</script>

{#if data && data.length > 0}
	<ObservablePlot options={{
		style:{
			background: "#1A202C",
		},
		height: 300,
		y: {
			grid: true,
		},
		x: {
			domain: [0, d3.max(data.map(d => d.days))],
			label: "Steps"
		},
		facet: {
			data: data,
			y: "edge",
			marginRight:200,
		},
		marks: [
			Plot.rectY(data, Plot.binX({y: "count"}, {x: {thresholds:30, value:"days"}})),
			Plot.ruleY([0])
		]
		}}
	/>
{:else}
	<p>Agent(s) has/have no state change.</p>
{/if}


