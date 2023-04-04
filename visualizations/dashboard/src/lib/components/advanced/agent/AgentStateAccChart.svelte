<script lang="ts">
	import * as d3 from 'd3';
	import { afterUpdate } from 'svelte';
	import { Legend } from '../Legend';

	export let stateChangeData;
	export let transition;
	export let title;

	let el: HTMLDivElement;
	let elLegend: HTMLDivElement;
	let elTooltip: HTMLDivElement;

	afterUpdate(() => {
		const data = preprocess(stateChangeData, transition);
		if (stateChangeData && stateChangeData.length > 0) draw(data);
	})

	function preprocess(data, edge) {
		let acc = 0;
		const ast = d3.sort(d3
			.flatRollup(data.filter(d => d.edge == edge).map(d => { return {...d, days: Math.floor(d.steps/96)}})
			, v => v.length, d => d.days), d => d[0]).map(d => {
			acc += d[1];
			return {
				days: d[0],
				count: d[1],
				acc: acc
			}
		});
		return ast;
	}

	function draw(data): void {
		d3.select(el).html(null);
		d3.select(elLegend).html(null);

		const width = 400;
		const height = 400;
		const margin = {top: 20, right: 30, bottom: 40, left: 40};
		const colorScale = createColorScale(data);

		const svg = d3.select(el)
			.append("svg")
			.attr("width", width)
			.attr("height", height);

		const xScale = d3.scaleLinear([0, d3.max(data, d => d.days)], [margin.left, width - margin.right]);
		const yScale = d3.scaleLinear([0, d3.sum(data, d => d.count)], [margin.top, height-margin.bottom]);
		const barHeightScale = d3.scaleLinear([0, d3.sum(data, d => d.count)], [0, height-margin.top-margin.bottom]);

		createAxes();

		const bars = svg.append("g")
			.selectAll("rect")
			.data(data)
			.join("rect")
			.attr("class", "ast-bars")
			.attr("x", xScale(0))
			.attr("y", d => yScale(d.acc-d.count))
			.attr("width", d => xScale(d.days)-margin.left)
			.attr("height", d => barHeightScale(d.count))
			.attr("stroke", "white")
			.attr("stroke-width", 0.1)
			.attr("fill", d => colorScale(d.count))
			.attr("fill-opacity", 0.7);

		initTooltip();

		function initTooltip() {
			const tooltip = d3.select(elTooltip)
				.style("position", "absolute")
				.style("visibility", "hidden");

			svg.selectAll(".ast-bars")
				.on("mouseover", function(){
					d3.select(this)
						.attr("stroke-width", 3)
						.attr("stroke", "blue");
					return tooltip.style("visibility", "visible");
				})
				.on("mousemove", function(event, d){
					return tooltip
						.style("top", (event.pageY-10)+"px")
						.style("left",(event.pageX+10)+"px")
						.text(`Days: ${d.days} Count: ${d.count}`);
				})
				.on("mouseout", function(){
					d3.select(this)
						.attr("stroke-width", 0.1)
						.attr("stroke", "white");
					return tooltip.style("visibility", "hidden");
				});
		}

		function createAxes() {
			const xLabel = "→ No. of days before transition";
			const yLabel = "↓ Acc. no. of agents"
			const xAxis = g => g
				.attr("transform", `translate(0,${height - margin.bottom})`)
				.call(d3.axisBottom(xScale));
			const yAxis = g => g
				.attr("transform", `translate(${margin.left},0)`)
				.call(d3.axisLeft(yScale));

			svg.append("g")
				.call(xAxis)
				.call(g => g.append("text")
					.attr("x", width - margin.right*5)
					.attr("y", margin.bottom/4*3)
					.attr("fill", "currentColor")
					.attr("text-anchor", "start")
					.text(xLabel));

			svg.append("g")
				.attr("transform", `translate(${margin.left},0)`)
				.call(yAxis)
				.call(g => g.select(".domain").remove())
				.call(g => g.selectAll(".tick line").clone()
					.attr("x2", width - margin.right)
					.attr("stroke-opacity", 0.1))
				.call(g => g.append("text")
					.attr("x", - margin.left)
					.attr("y", 10)
					.attr("fill", "currentColor")
					.attr("text-anchor", "start")
					.text(yLabel));
		}

		function createColorScale(data) {
			// const domain = [d3.min(data, d=>d.count)-10, d3.max(data, d=>d.count)];
			const domain = [0, d3.max(data, d=>d.count)];
			const range = [0,1];
			const color = d3.interpolateBlues;

			Legend(elLegend,
				d3.scaleSequential([0, d3.max(data, d=>d.count)], color), {
					title: "No. of agents",
				}
			);

			return d3.scaleLinear()
				.domain(domain)
				.range(range)
				.interpolate((i, j) => (t) => color(i + t * (j - i)))
		}
	}

</script>

<style>
	#svg-tooltip {
			font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple   Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
			background: rgba(69,77,93,.9);
			border-radius: .1rem;
			color: #fff;
			display: block;
			font-size: 11px;
			max-width: 320px;
			padding: .2rem .4rem;
			position: absolute;
			text-overflow: ellipsis;
			white-space: pre;
			z-index: 300;
			visibility: hidden;
	}

	.agent-acc-chart-container {
			display: flex;
			flex-direction: column;
			flex-grow: 1;
	}
</style>
<div class='agent-acc-chart-container'>
	<p>{title}</p>
	<div id='state-acc-legend' bind:this={elLegend}></div>
	<div id='state-acc-chart' bind:this={el}></div>
	<div id='svg-tooltip' bind:this={elTooltip}/>
</div>
