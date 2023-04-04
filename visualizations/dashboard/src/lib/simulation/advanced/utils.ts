import { STAGE } from '../constants';
import * as d3 from 'd3';

export function preprocessData(raw) {
	const all_stages = new Array(...new Set(raw.map(d => d.stage)));
	const infected_stages = [STAGE.exposed, STAGE.sympdetected, STAGE.severe];

	// create count summary from raw
	let df = d3.rollup(raw, v => d3.count(v, d => d.step), d => d.run, d => d.step, d => d.stage);
	const data = [];

	for (const [run, steps] of df.entries()) {
		for (const [step, stages] of steps.entries()) {
			for (const [stage, count] of stages.entries()) {
				data.push({ run: run, step: step, stage: stage, count: count });
			}
			for (let stage of all_stages) {
				if (!stages.has(stage)) data.push({ run: run, step: step, stage: stage, count: 0 });
			}
		}
	}

	// select only infected populations
	const infected = data.filter(d => infected_stages.includes(d.stage));

	// create step-wise summary across runs
	df = d3.rollup(infected, v => d3.sum(v, d => d.count), d => d.step, d => d.run);
	const agg = [];

	for (const [step, runs] of df.entries()) {
		const mean = d3.mean(runs.values());
		const min = d3.min(runs.values());
		const max = d3.max(runs.values());
		agg.push({step, mean, min, max});
	}

	agg.sort((a,b) => a.step > b.step ? 1 : -1);

	// create run-wise per step summary
	df = d3.rollup(infected, v => d3.sum(v, d => d.count), d => d.step, d => d.run);
	const agg_details = [];

	for (const [step, runs] of df.entries()) {
		for (const [run, count] of runs.entries()) {
			agg_details.push({run, step, count});
		}
	}

	agg_details.sort((a,b) => a.step > b.step ? 1 : -1)

	return [agg, agg_details];
}

export function getMinMax(details) {
	const data = d3.group(details, d => d.step);
	const steps = [];
	data.forEach(d => {
		let maxValue = 0;
		let minValue = Number.MAX_SAFE_INTEGER;
		let max = [];
		let min = [];

		for (let run of d) {
			if (run.count > maxValue) {
				maxValue = run.count;
				max = [];
			}
			if (run.count == maxValue) max.push(run.run);
			if (run.count < minValue) {
				minValue = run.count;
				min = [];
			}
			if (run.count == minValue) min.push(run.run);
		}
		steps.push({min: min, max:max});
	});

	return steps;
}
