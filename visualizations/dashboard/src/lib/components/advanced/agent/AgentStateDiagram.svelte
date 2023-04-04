<script lang='ts'>
	import * as d3 from 'd3';
	import { afterUpdate } from 'svelte';
	import Stages from '../simulation/Stages.svelte';

	export let stateChangeData;
	export let transition;

	let el: HTMLDivElement;

	afterUpdate(() => {
		if (stateChangeData && stateChangeData.length > 0) draw();
	});

	function draw(): void {
		d3.select(el).html(null);

		const width = 700;
		const height = 250;
		const nodeSize = 30;

		const base = { x: 0, y: 100, dx: 150, dy: 50 };
		const arrowref = 5;
		const arrowConfig = { fill: "white", ref: 10, refX: 12, refY: 10, marker: 20 };

		const counts = d3.rollup(stateChangeData, v => v.length, d => d.edge);

		const svg = d3.select(el)
			.append('svg')
			.attr("width", width)
			.attr("height", height);
			// .attr("viewBox", [0, 0, width, height]);

		const g = svg.append("g")
		// .attr("transform-origin", "center")
		// .attr("transform", "rotate(-90) translate(100,0)");
		const ge = svg.append("g")
		const gs = svg.append("g")


		const edges = [
			{
				name: "SUSCEPTIBLE → EXPOSED", path: () => {
					const p = d3.path();
					p.moveTo(base.x, base.y + nodeSize/2);
					p.lineTo(base.x + base.dx - arrowref, base.y + nodeSize/2);
					return p;
				},
			},
			{
				name: "EXPOSED → SYMPDETECTED", path: () => {
					const p = d3.path();
					p.moveTo(base.x + base.dx + nodeSize/2, base.y + nodeSize/2);
					p.lineTo(base.x + 2*base.dx - arrowref, base.y + base.dy + nodeSize/2);
					return p;
				},
			},
			{
				name: "EXPOSED → ASYMPTOMATIC", path: () => {
					const p = d3.path();
					p.moveTo(base.x + base.dx, base.y + nodeSize/2);
					p.lineTo(base.x + 2*base.dx - arrowConfig.ref, base.y - base.dy + nodeSize/2);
					return p;
				},
			},
			// {name: "ASYMPTOMATIC → SEVERE", path:  () => {
			// 		const p = d3.path();
			// 		p.moveTo(base.x + 2*base.dx + nodeSize/2, base.y - base.dy + nodeSize/2)
			// 		p.lineTo(base.x + 3*base.dx - arrowConfig.ref, base.y + base.dy + nodeSize/4);
			// 		return p;
			// 	}},
			{
				name: "SYMPDETECTED → SEVERE", path: () => {
					const p = d3.path();
					p.moveTo(base.x + 2*base.dx + nodeSize/2, base.y + base.dy + nodeSize/2);
					p.lineTo(base.x + 3*base.dx - arrowConfig.ref, base.y + base.dy + nodeSize/2);
					return p;
				},
			},
			{
				name: "SEVERE → DECEASED", path: () => {
					const p = d3.path();
					p.moveTo(base.x + 3*base.dx, base.y + base.dy + nodeSize/2);
					p.lineTo(base.x + 4*base.dx - arrowConfig.ref, base.y + base.dy + nodeSize/2);
					return p;
				},
				id: "sevToDec",
			},
			{
				name: "ASYMPTOMATIC → RECOVERED", path: () => {
					const p = d3.path();
					p.moveTo(base.x + 2*base.dx + nodeSize/2, base.y - base.dy + nodeSize/2);
					p.lineTo(base.x + 3*base.dx - arrowConfig.ref, base.y - base.dy + nodeSize/2);
					return p;
				},
			},
			{
				name: "SYMPDETECTED → RECOVERED", path: () => {
					const p = d3.path();
					p.moveTo(base.x + 2*base.dx + nodeSize/2, base.y + base.dy + nodeSize/2);
					p.lineTo(base.x + 3*base.dx - arrowConfig.ref, base.y - base.dy + 3*nodeSize/4);
					return p;
				}
			},
			{
				name: "SEVERE → RECOVERED", path: () => {
					const p = d3.path();
					p.moveTo(base.x + 3*base.dx + nodeSize/2, base.y + base.dy + nodeSize/2);
					p.lineTo(base.x + 3*base.dx + nodeSize/2, base.y - base.dy + nodeSize + arrowConfig.ref);
					return p;
				}
			},
			// {
			// 	name: "RECOVERED → SUSCEPTIBLE", path: () => {
			// 		const p = d3.path();
			// 		p.moveTo(base.x + nodeSize / 2, base.y - base.dy);
			// 		p.lineTo(base.x + nodeSize / 2, base.y - arrowConfig.ref);
			// 		return p;
			// 	}
			// },

		];

		addEdges();
		addStates();


		function findEdgeStrokeStyle(edge) {
			return (counts.has(edge)) ? "0" : "6";
		}

		function findEdgeStrokeOpacity(edge) {
			return counts.has(edge) ? 0.8 : 0.3;
		}

		function findEdgeStrokeWidth(edge) {
			return transition == edge? 5:2;
		}

		function addEdges() {
			const arrowhead = g.append("defs")
				.append("marker")
				.attr("id", "arrowhead")
				.attr("markerWidth", arrowConfig.marker)
				.attr("markerHeight", arrowConfig.marker)
				.attr("refX", arrowConfig.refX)
				.attr("refY", arrowConfig.refY)
				.attr("orient", "auto-start-reverse")
				.attr("markerUnits", "userSpaceOnUse")
				.append("path")
				.attr("d", "M 0 0 L 20 10 L 0 20 z")
				.attr("fill", arrowConfig.fill);

			const arrows = ge.selectAll("path")
				.data(edges)
				.join("path")
				.attr("class", "edge")
				.attr("id", d => `edge-${d.name.replace(" → ","_")}`)
				.style("cursor", "pointer")
				.style("stroke", arrowConfig.fill)
				.style("stroke-width", (d) => findEdgeStrokeWidth(d.name))
				.style("stroke-dasharray", (d) => findEdgeStrokeStyle(d.name))
				.style("stroke-opacity", (d) => findEdgeStrokeOpacity(d.name))
				.style("fill", "none")
				.attr("marker-end", "url(#arrowhead)")
				.attr("d", d => {
					return d.path().toString();
				})
				.on('click', (event, d) => transition = d.name)
				.on('mouseover', (event) => d3.select(event.target).style("stroke-width", 5))
				.on('mouseleave', (event) =>
					d3.select(event.target).style("stroke-width", (d) => findEdgeStrokeWidth(d.name))
				);
		}
		function addStates() {
			const susceptible = gs.append("rect")
				.attr("x", base.x)
				.attr("y", base.y)
				.attr("fill", "#ffffff")
				.attr("stroke", "grey")
				.attr("width", nodeSize)
				.attr("height", nodeSize);

			const exposed = gs.append("rect")
				.attr("x", base.x + base.dx)
				.attr("y", base.y)
				.attr("fill", "#fa07bd")
				.attr("width", nodeSize)
				.attr("height", nodeSize);

			const severe = gs.append("rect")
				.attr("x", base.x + 3 * base.dx)
				.attr("y", base.y + base.dy)
				.attr("fill", "#5e0115")
				.attr("stroke", "#ffffff")
				.attr("width", nodeSize)
				.attr("height", nodeSize);

			const deceased = gs.append("rect")
				.attr("x", base.x + 4 * base.dx)
				.attr("y", base.y + base.dy)
				.attr("fill", "#000000")
				.attr("stroke", "#ffffff")
				.attr("width", nodeSize)
				.attr("height", nodeSize);

			const asymptoptic = gs.append("rect")
				.attr("x", base.x + 2 * base.dx)
				.attr("y", base.y - base.dy)
				.attr("fill", "#96bdff")
				.attr("width", nodeSize)
				.attr("height", nodeSize);

			const sympdetected = gs.append("rect")
				.attr("x", base.x + 2 * base.dx)
				.attr("y", base.y + base.dy)
				.attr("fill", "#de284f")
				.attr("width", nodeSize)
				.attr("height", nodeSize);

			const recovered = gs.append("rect")
				.attr("x", base.x + 3 * base.dx)
				.attr("y", base.y - base.dy)
				.attr("fill", "#03fcbe")
				.attr("width", nodeSize)
				.attr("height", nodeSize);
		}
	}

</script>

<style>
	#state-diagram {

	}

	#state-diagram-container {
			display: flex;
			align-items: center;
	}
</style>
<div id='state-diagram-container'>
	<div id='state-diagram' bind:this={el}/>
	<Stages />
</div>

