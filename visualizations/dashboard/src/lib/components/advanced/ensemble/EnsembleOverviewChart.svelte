<script lang="ts">
	import { afterUpdate, beforeUpdate } from 'svelte';
	import * as d3 from 'd3';

	import { currentRun, maxStep, policyAdoption, policyStep } from '../../../stores';
	import { getMinMax } from '../../../simulation/advanced/utils';
	import { Canvg } from 'canvg';

	export let onSelectRun;
	export let filename;
	export let data;
	let el: HTMLDivElement;
	let canvas: HTMLCanvasElement;
	let aHref: HTMLAnchorElement;
	const margin = {top: 20, right: 100, bottom: 30, left: 40};

	function chart(data): void {
		if (data === undefined) return;

		d3.select(el).html(null);

		if (data.agg.length === 0) {
			d3.select(el).html("<h1>No available data.</h1>");
			return;
		}

		const width = d3.select(el).node().getBoundingClientRect().width;
		const height = 500;

		const svg = d3.select(el)
			.append('svg')
			.attr("class", "ensemble-svg")
			.attr("width", width)
			.attr("height", height)
			.attr("viewBox", [0, 0, width, height]);

		let step = 0;
		const groupedDetails = d3.group(data.details, d=>d.run)

		const curve = d3.curveLinear;
		const strokeColor = "steelblue";
		const strokeLinejoin = "round" // stroke line join of line
		const strokeLinecap = "round" // stroke line cap of line


		const xScale = d3.scaleLinear([0, data.maxStep], [margin.left, width - margin.right]);
		const yScale = d3.scaleLinear([0, data.maxFreq], [height-margin.bottom, margin.top]);
		const xLabel = "→ Step";
		const yLabel = "↑ No. of agents"
		const xAxis = g => g
			.attr("transform", `translate(0,${height - margin.bottom})`)
			.call(d3.axisBottom(xScale));
		const yAxis = g => g
			.attr("transform", `translate(${margin.left},0)`)
			.call(d3.axisLeft(yScale));

		svg.append("g")
			.call(xAxis)
			.call(g => g.append("text")
					.attr("x", width-margin.right)
					.attr("y", margin.bottom/2)
				.attr("fill", "currentColor")
				.attr("text-anchor", "start")
				.text(xLabel));

		svg.append("g")
			.attr("transform", `translate(${margin.left},0)`)
			.call(yAxis)
			.call(g => g.select(".domain").remove())
			.call(g => g.selectAll(".tick line").clone()
				.attr("x2", width - margin.left - margin.right)
				.attr("stroke-opacity", 0.1))
			.call(g => g.append("text")
				.attr("x", -margin.left)
				.attr("y", 10)
				.attr("fill", "currentColor")
				.attr("text-anchor", "start")
				.text(yLabel));

		const labels = svg.append("g")
			.attr("id", "line-labels");

		// min max interval
		const area = d3.area()
			.curve(curve)
			.x(d => xScale(d.step))
			.y0(d => yScale(d.min))
			.y1(d => yScale(d.max));

		svg.append("path")
			.attr("fill", "#4C8BB3")
			.attr("opacity", 0.4)
			.attr("d", area(data.agg));

		// mean
		const meanLine = svg.append("g")
			.attr("id", "mean-line")
			.style("pointer-events", "none");

		const line = d3.line()
			.curve(curve)
			.x(d => xScale(d.step))
			.y(d => {
				// console.log(d.mean);
				return yScale(d.mean)
			});

		meanLine.append("path")
			.attr("fill", "none")
			.attr("stroke", "white")
			.attr("stroke-width", 3)
			.attr("stroke-linejoin", strokeLinejoin)
			.attr("stroke-linecap", strokeLinecap)
			.attr("d", line(data.agg))
			.attr("id", "line-mean");

		// mean label
		labels.call(g => g.append("text")
			.attr("x", width - margin.right + 5)
			.attr("y", yScale(data.agg[data.agg.length-1].mean) + 4)
			.attr("text-anchor", "start")
			.attr("fill", "currentColor")
			.text("mean"));

		// detail line label
		const detailLineLabel =
			labels.append("text")
				.attr("x", width - margin.right + 5)
				.attr("y", 0)
				.attr("text-anchor", "start")
				.attr("fill", "currentColor")
				.text("");

		// per run lines and min max coloring
		const detailLine = d3.line()
			.curve(curve)
			.x(d => xScale(d.step))
			.y(d => yScale(d.count));

		const minMax = getMinMax(data.details);

		const detailColor = (i) => {
			if (step !== undefined) {
				if (minMax[step].max.includes(i)) return "#de9dd0";
				if (minMax[step].min.includes(i)) return "#26b4c0";
			}
			return strokeColor;
		}

		const detailStrokeWidth = (i) => {
			if (step === undefined) return 1;
			if (minMax[step].max.includes(i) || minMax[step].min.includes(i)) return 3;
			return 1;
		}

		const onMouseOverDetail = (e: Event) => {
			const id = +e.target.id.replace("detail-","");
			currentRun.set(id);
			d3.select(e.target).attr("stroke-width", 5);
			detailLineLabel
				.attr("y", yScale(groupedDetails.get(id)[data.maxStep-1].count))
				.text(`run ${id}`);
		}

		const onMouseOutDetail = (e: Event) => {
			const line = d3.select(e.target);
			if (line.attr("stroke") === strokeColor)
				line.attr("stroke-width", 1);
			else line.attr("stroke-width", 3);
			detailLineLabel.text("")
		}


		const detailLines = svg.append("g").attr("class", "detail-lines");
		detailLines.selectAll("path")
			.data(groupedDetails)
			.join("path")
			.attr("id", d => `detail-${d[0]}`)
			.attr("fill", "none")
			.attr("stroke", strokeColor)
			.attr("stroke-width", 1)
			.attr("stroke-linejoin", strokeLinejoin)
			.attr("stroke-linecap", strokeLinecap)
			.attr("d", d => detailLine(d[1]))
			.attr("style", "cursor: pointer")
			.on("mouseover", onMouseOverDetail)
			.on("mouseout", onMouseOutDetail)
			.on("pointerdown", onSelectRun);


		// Show the current step
		const tooltip = svg.append("g");
		const stepIndicator = tooltip.append("line")
			.attr("x1", 100)
			.attr("y1", margin.top)
			.attr("x2", 100)
			.attr("y2", height-margin.bottom)
			.attr("stroke", "#4C8BB3")
			.attr("stroke-width", 3)
			.attr("position", "relative");

		const stepLabel = tooltip.append("text")
			.attr("x", 0)
			.attr("y", margin.top-10)
			.attr("fill", "currentColor")
			.attr("font-size", 11)
			.text("");

		const policyRange = tooltip.append("rect")
			.attr("x", 0)
			.attr("y", margin.top)
			.attr("width", 0)
			.attr("height", height-margin.bottom-margin.top)
			.attr("fill", "currentColor")
			.attr("fill-opacity", 0.3);

		const handle = tooltip.append("rect")
			.attr("class", "handle")
			.attr("x", 200)
			.attr("y", (height-margin.top-margin.bottom)/2)
			.attr("width", 0)
			.attr("height", 40)
			.attr("fill", "white")
			.attr("cursor", "ew-resize")
			.attr("pointer-events", "all");

		let policyDuration = 7 * 96;
		let fixed = false;

		function onmousemove(event) {
			if (!fixed) {
				step = Math.round(xScale.invert(d3.pointer(event)[0]));
				const posX = xScale(step);
				const posY = d3.pointer(event)[1];
				if ((step < 0 || step > data.maxStep) || posY < margin.top || posY > height - margin.bottom) {
					stepIndicator.attr("stroke-width", 0);
					stepLabel.text("");
					policyRange.attr("width", 0);
					handle.attr("width", 0);
					detailLines.selectAll("path")
						.attr("stroke-width", 1)
						.attr("stroke", strokeColor);
				}
				else {
					stepIndicator.attr("x1", posX).attr("x2", posX).attr("stroke-width", 3);
					stepLabel.attr("x", posX-20)
						.text(`Intervention at step ${step}, adoption period for ${policyDuration} steps [${(policyDuration/96).toPrecision(2)} days]`);

					policyRange.attr("x", posX).attr("width", xScale(policyDuration)-margin.left);
					handle.attr("x", posX+xScale(policyDuration)-5-margin.left).attr("width", 10);
					for (let run of groupedDetails.keys()) {
						detailLines.select(`#detail-${run}`)
							.attr("stroke", () => detailColor(run))
							.attr("stroke-width", () => detailStrokeWidth(run));
					}
				}
			}
		}
		svg.on('mousemove', onmousemove);

		function onresize(event) {
			const posX = xScale(step);
			policyDuration = Math.min(
				Math.round(xScale.invert(event.x)) - step,
				$maxStep - step
			);
			policyAdoption.set(policyDuration);
			handle.attr("x", posX+xScale(policyDuration)-5-margin.left).attr("width", 10);
			policyRange.attr("x", posX).attr("width", xScale(policyDuration)-margin.left);
			stepLabel.attr("x", posX-20)
				.text(`Intervention at step ${step}, adoption period for ${policyDuration} steps [${(policyDuration/96).toFixed(2)} days]`);
		}
		handle.call(d3.drag().on("drag", onresize));

		function onclick(event) {
			if (fixed) {
				if (event.target.tagName === "svg") {
					fixed = false;
					onmousemove(event);
				}
			}
			else {
				fixed = true;
				policyStep.set(step);
			}
		}
		svg.on('pointerdown', onclick);
	}

	afterUpdate(() => {
		chart(data);
	});

	beforeUpdate(() => {
		d3.select(el).html("<h1>Loading...</h1>");
	});

</script>
<style>
    .chart  {
				margin: 5vw;
    }
		.ensemble-chart-container {
				position: relative;
		}
		.download-icon {
        position: absolute;
				top: 0;
				right: 12vw;
				cursor: pointer;
		}

</style>

{#key filename}
	<div class='ensemble-chart-container'>
		<img
			class='download-icon'
			src={'advanced/download.svg'}
			width='24' height='24'
			on:mousedown={async ()=> {
				const v = await Canvg.from(canvas.getContext('2d'), el.innerHTML);
				v.start();
				aHref.download = 'ensemble-chart.png';
				aHref.href = canvas.toDataURL();
				aHref.click();
			}}
		/>
		<div bind:this={el} class="chart" />
		<canvas bind:this={canvas} style='display: none'/>
		<a bind:this={aHref}></a>
	</div>
{/key}

