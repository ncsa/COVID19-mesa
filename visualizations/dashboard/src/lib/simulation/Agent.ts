import * as PIXI from 'pixi.js';
import {BloomFilter} from '@pixi/filter-bloom';
import { historySize, ropeSize, STAGE, STAGE_COLOR } from './constants';
import { cubicInterpolation } from './utils';

export class Agent {

	public id: number;
	public stage: string;
	public x: number;
	public y: number;
	public rendered: boolean;

	public showPath: boolean;
	public historyX: number[];
	public historyY: number[];
	public points: PIXI.Point[];
	public rope: PIXI.SimpleRope | null;

	public sprite: PIXI.Sprite;
	public container: PIXI.Container = new PIXI.Container();

	constructor(config: any) {
		this.id = config.id || -1;
		this.stage = config.stage || STAGE.susceptible;
		this.x = config.x;
		this.y = config.y;
		this.rendered = true;

		this.showPath = config.showPath ?? false;
		this.historyX = config.showPath ? new Array(historySize).fill(this.x) : [];
		this.historyY = config.showPath ? new Array(historySize).fill(this.y) : [];
		this.points = config.showPath ? new Array(ropeSize).fill(0).map(() => new PIXI.Point(this.x,this.y)): [];
		this.rope = config.showPath ? new PIXI.SimpleRope(config.trailTexture, this.points): null;

		if (this.rope) {
			this.rope.blendMode = PIXI.BLEND_MODES.ADD;
			this.container.addChild(this.rope);
		}

		const scale = config.scale ?? 0.5;
		this.sprite = PIXI.Sprite.from(config.texture);
		this.container.addChild(this.sprite);
		this.sprite.anchor.set(0.5);
		if (!config.showPath) this.sprite.scale.set(scale);
		if (config.showPath) this.container.filters = [new BloomFilter()];

		this.render();
	}

	render(): void {
		this.sprite.x = this.x;
		this.sprite.y = this.y;
		this.applyTint();
		this.rendered = true;

		if (this.showPath) this.drawPath();
	}

	drawPath(): void {
		this.historyX.pop();
		this.historyX.unshift(this.sprite.x);
		this.historyY.pop();
		this.historyY.unshift(this.sprite.y);

		// Update the points to correspond with history.
		for (let i = 0; i < ropeSize; i++) {
			const p = this.points[i];

			// Smooth the curve with cubic interpolation to prevent sharp edges.
			const ix = cubicInterpolation(this.historyX, i / ropeSize * historySize, null);
			const iy = cubicInterpolation(this.historyY, i / ropeSize * historySize, null);

			p.x = ix;
			p.y = iy;
		}
	}

	applyTint(): void {
		this.sprite.alpha = 1.0;
		if (this.stage == STAGE.exposed) this.sprite.tint = parseInt(STAGE_COLOR.exposed, 16);
		else if (this.stage == STAGE.sympdetected) this.sprite.tint = parseInt(STAGE_COLOR.sympdetected, 16);
		else if (this.stage == STAGE.severe) this.sprite.tint = parseInt(STAGE_COLOR.severe, 16);
		else if (this.stage == STAGE.deceased) this.sprite.tint = parseInt(STAGE_COLOR.deceased, 16);
		else if (this.stage == STAGE.asymptomatic) this.sprite.tint = parseInt(STAGE_COLOR.asymptomatic, 16);
		else {
			this.sprite.tint = parseInt(STAGE_COLOR.susceptible, 16);
			this.sprite.alpha = 0.5;
		}

	}

	destroy(): void {
		this.container.removeChild(this.sprite);
		this.sprite.destroy({children:true});

		if (this.rope) {
			this.container.removeChild(this.rope);
			this.rope.destroy({children:true});
		}
	}

	resetPath() {
		if (this.rope) {
			this.historyX.fill(this.x);
			this.historyY.fill(this.y);
			this.points.forEach((p) => {
				p.x = this.x;
				p.y = this.y;
			});
		}
	}

	handleCurrentPathing(): void {

	}

	nextPath(): void {

	}





}