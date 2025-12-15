import { map1 } from "../maps/map1.js";
import { map2 } from "../maps/map2.js";
import { map3 } from "../maps/map3.js";

export const TILE_SIZE = 50;

export const gameState = {
    map: [],
    rows: 0,
    cols: 0,

    canvas: null,
    ctx: null,

    player: null,
    asteroids: []
};


export function initGameState() {
    const selectedMap = localStorage.getItem("selectedMap");

    let baseMap = map1;
    if (selectedMap === "map2") baseMap = map2;
    if (selectedMap === "map3") baseMap = map3;

    // generate pellet
    gameState.map = baseMap.map(row =>
        row.map(cell => (cell === 0 ? 2 : cell))
    );

    gameState.rows = gameState.map.length;
    gameState.cols = gameState.map[0].length;

    // canvas
    gameState.canvas = document.getElementById("gameCanvas");
    gameState.ctx = gameState.canvas.getContext("2d");

    gameState.canvas.width  = gameState.cols * TILE_SIZE;
    gameState.canvas.height = gameState.rows * TILE_SIZE;
}
