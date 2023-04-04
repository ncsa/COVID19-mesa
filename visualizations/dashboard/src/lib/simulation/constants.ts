export enum STAGE {
	susceptible = "Stage.SUSCEPTIBLE",
	sympdetected = "Stage.SYMPDETECTED",
	severe = "Stage.SEVERE",
	exposed = "Stage.EXPOSED",
	deceased = "Stage.DECEASED",
	asymptomatic = "Stage.ASYMPTOMATIC",
	recovered = "Stage.RECOVERED",
}

export enum STAGE_COLOR {
	susceptible = "#ffffff",
	sympdetected = "#de284f",
	severe = "#5e0115",
	exposed = "#fa07bd",
	deceased = "#000000",
	asymptomatic = "#96bdff",
	recovered = "#03fcbe",
}

export const STAGE_MAP = {
	"Stage.SUSCEPTIBLE": {
		name: "susceptible", color: hexToRGB("#ffffff"), hexColor: "#ffffff", alias: "Stage.SUSCEPTIBLE",
	},
	"Stage.EXPOSED": {
		name: "exposed", color: hexToRGB("#fa07bd"), hexColor: "#fa07bd",alias: "Stage.EXPOSED",
	},
	"Stage.SYMPDETECTED": {
		name: "symptoms detected", color: hexToRGB("#de284f"), hexColor: "#de284f",alias: "Stage.SYMPDETECTED",
	},
	"Stage.ASYMPTOMATIC": {
		name: "asymptomatic", color: hexToRGB("#96bdff"), hexColor: "#96bdff",alias: "Stage.ASYMPTOMATIC",
	},
	"Stage.SEVERE": {
		name: "severe", color: hexToRGB("#5e0115"), hexColor: "#5e0115",alias: "Stage.SEVERE",
	},
	"Stage.RECOVERED": {
		name: "recovered", color:hexToRGB("#03fcbe"), hexColor: "#03fcbe",alias: "Stage.RECOVERED",
	},
	"Stage.DECEASED": {
		name: "deceased", color: hexToRGB("#000000"), hexColor: "#000000",alias: "Stage.DECEASED",
	},
}

export const ropeSize = 500;
export const historySize = 500;
export const stepSize = 0.1;

function hexToDec(hex: string) {
	return parseInt(hex, 16);
}

export function hexToRGB(hexColor: string) {
	const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hexColor) ?? ["#000000", "00","00","00"];
	return {
		hex: hexColor,
		r: hexToDec(result[1]),
		g: hexToDec(result[2]),
		b: hexToDec(result[3]),
	};
}