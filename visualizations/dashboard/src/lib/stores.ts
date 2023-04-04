import { writable } from 'svelte/store';

/***
 * Data
 */
export const agg = writable();
export const aggDetails = writable();
export const groupedDetails = writable(); // per run data
export const minMax = writable(); // ensemble chart

export const maxStep = writable(-1);
export const maxFreq = writable(-1);
export const currentRun = writable(0);
export const selectedStages = writable(["Stage.SYMPDETECTED", "Stage.SEVERE","Stage.EXPOSED","Stage.ASYMPTOMATIC"]);

export const policyAdoption = writable(7 * 96);
export const policyStep = writable(-1);

/***
 * Simulation view
 */
export const currentStep = writable(1);
export const play = writable(false);
export const speed = writable(1);