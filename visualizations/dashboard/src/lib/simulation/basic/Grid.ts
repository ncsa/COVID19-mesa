import * as PIXI from 'pixi.js';

export class Grid {

	public width: number;
	public height: number;
	public sizeX: number;
	public sizeY: number;
	public x_pos: any;
	public y_pos: any;
	public color: number;

	public gridLines: PIXI.Graphics;
	public container: PIXI.Container;

	constructor(config: any) {
		this.width = config.width;
		this.height = config.height;
		this.sizeX = config.sizeX;
		this.sizeY = config.sizeY;
		this.x_pos = config.x_pos;
		this.y_pos = config.y_pos;
		this.color = 0xffffff;

		this.container = new PIXI.Container();
		this.gridLines = new PIXI.Graphics();
		this.draw();
		this.container.addChild(this.gridLines);
	}

	draw() {
		this.gridLines.clear();
		this.gridLines.lineStyle(1,this.color, 0.1);
		for (let i=0; i<this.width; i++) {
			for (let j=0; j<this.height; j++) {
				const x = this.x_pos(i)-this.sizeX/2;
				const y = this.y_pos(j)-this.sizeY/2;
				this.gridLines.drawRect(x,y, this.sizeX, this.sizeY);
			}
		}
	}

	resize(x_pos: any, y_pos: any, sizeX: number, sizeY: number) {
		this.sizeX = sizeX;
		this.sizeY = sizeY;
		this.x_pos = x_pos;
		this.y_pos = y_pos;
		this.draw();
	}
}