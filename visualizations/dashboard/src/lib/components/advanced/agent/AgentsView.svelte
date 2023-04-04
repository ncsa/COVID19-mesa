<script lang="ts">
	import { fade } from 'svelte/transition';
	import { onMount } from 'svelte';
	import AgentStateDiagram from './AgentStateDiagram.svelte';
	import AgentStateAccChart from './AgentStateAccChart.svelte';
	import * as d3 from 'd3';
	import { policyAdoption, policyStep } from '../../../stores';

	export let filename;

	let id = 0;
	let data;
	let runs;
	let stateChangeData;
	let ids;
	let selectedIDs;
	let transition = "SUSCEPTIBLE → EXPOSED";
	let chartData = [];

	onMount(async () => {
		stateChangeData = await getStateChangeData();
		if ($policyStep < 0) {
			const overall = d3.map(stateChangeData, d => {
				if (d.edge == transition) {
					return {...d, steps: d.steps - $policyStep}
				} else return d;
			});
			chartData.push({data: overall, name: `Overall`});
		} else {
			const before = d3.filter(stateChangeData, d => d.step < $policyStep);
			const during = d3
				.filter(stateChangeData, d => d.step > $policyStep && d.step <= $policyStep + $policyAdoption)
				.map(d => {
					if (d.edge == transition) {
						return {...d, steps: d.steps - $policyStep}
					} else return d;
				});
			const after = d3
				.filter(stateChangeData, d => d.step > $policyStep + $policyAdoption)
				.map(d => {
					if (d.edge == transition) {
						return {...d, steps: d.steps - ($policyStep + $policyAdoption)}
					} else return d;
				});
			if (before.length > 0) chartData.push({data: before, name: `Before intervention at step ${$policyStep} [day ${Math.floor($policyStep/96)}]`});
			if (during.length > 0 ) chartData.push({data: during, name: `During intervention that lasts ${($policyAdoption / 96).toFixed(2)} days`});
			if (during.length > 0 )
				chartData.push({data: after, name: `After intervention at step ${$policyStep + $policyAdoption} [day ${Math.floor(($policyStep + $policyAdoption)/96)}]`});
		}

		console.log($policyAdoption, $policyStep)
	});

	function init() {
		runs = d3.group(data, d=>d.run);
		selectedIDs = [0];

		update();

		ids = [...new Set(data.map(item => +item.id))];
		ids.sort((a,b) => a-b);
	}

	function update() {
		stateChangeData = [];
		runs.forEach(run => {
			const agentData = d3.group(run.filter(d => selectedIDs.includes(d.id)), d => d.id);
			agentData.forEach(d => {
				for (let i=0; i<d.length-1; i++) {
					const cs = d[i].stage;
					const ns = d[i+1].stage;
					if (cs !== ns) {
						stateChangeData.push({
							step: i,
							edge: [cs, ns].join(' → ').replaceAll('Stage.', ''),
							id: d[i].id
						});
					}
				}
			});
		});
	}

	async function getStateChangeData() {
		const response = await fetch(`http://localhost:5000/data/states?filename=${filename}`);
		if (response.ok) return response.json();
	}

</script>
<div id='agent-container' in:fade >
	<h1>Agents overview</h1>
	<p>State change distribution at {transition}</p>
	{#if stateChangeData}
		<div id='agent-view-container'>
			<div id='agent-charts-container'>
				{#each chartData as { data,name }}
					<AgentStateAccChart stateChangeData={data} title={name} transition={transition} />
				{/each}
			</div>
			<AgentStateDiagram bind:stateChangeData bind:transition/>
		</div>
	{/if}
</div>

<style>
	#agent-view-container {
			display: flex;
      flex-direction: column;
      align-items: center;
	}
	#agent-charts-container {
			display: flex;
	}

</style>