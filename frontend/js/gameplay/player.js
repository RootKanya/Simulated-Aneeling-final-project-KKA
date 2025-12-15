import { gameState, TILE_SIZE } from "./gameState.js";

let keys = {};

export function initPlayer() {
    const img = new Image();
    img.src = "../assets/rocket.png";

    gameState.player = {
        x: TILE_SIZE * 1 + TILE_SIZE / 2,
        y: TILE_SIZE * 1 + TILE_SIZE / 2,

        dirX: 1,   // mulai ke kanan
        dirY: 0,

        nextDirX: 1,
        nextDirY: 0,

        speed: 3,
        size: TILE_SIZE * 0.9,
        angle: 0,

        image: img
    };

    window.addEventListener("keydown", e => keys[e.key] = true);
    window.addEventListener("keyup",   e => keys[e.key] = false);
}

function canMove(tileX, tileY) {
    const map = gameState.map;
    if (tileY < 0 || tileY >= map.length) return false;
    if (tileX < 0 || tileX >= map[0].length) return false;
    return map[tileY][tileX] !== 1;
}


export function updatePlayer() {
    const p = gameState.player;

    // ambil input
    if (keys["ArrowUp"])    { p.nextDirX = 0; p.nextDirY = -1; }
    if (keys["ArrowDown"])  { p.nextDirX = 0; p.nextDirY = 1; }
    if (keys["ArrowLeft"])  { p.nextDirX = -1; p.nextDirY = 0; }
    if (keys["ArrowRight"]) { p.nextDirX = 1; p.nextDirY = 0; }

    // posisi tile
    const tileX = Math.floor(p.x / TILE_SIZE);
    const tileY = Math.floor(p.y / TILE_SIZE);

    // posisi center tile
    const centerX = tileX * TILE_SIZE + TILE_SIZE / 2;
    const centerY = tileY * TILE_SIZE + TILE_SIZE / 2;

    // cukup dekat dengan center → boleh belok
    const nearCenter =
        Math.abs(p.x - centerX) < p.speed &&
        Math.abs(p.y - centerY) < p.speed;

    if (nearCenter) {
        // snap ke center (ANTI NYANGKUT)
        p.x = centerX;
        p.y = centerY;

        // coba ganti arah
        if (canMove(tileX + p.nextDirX, tileY + p.nextDirY)) {
            p.dirX = p.nextDirX;
            p.dirY = p.nextDirY;
        }

        // stop kalau depan tembok
        if (!canMove(tileX + p.dirX, tileY + p.dirY)) {
            p.dirX = 0;
            p.dirY = 0;
        }
    }

    // gerak
    p.x += p.dirX * p.speed;
    p.y += p.dirY * p.speed;

    // makan pellet
    if (gameState.map[tileY][tileX] === 2) {
        gameState.map[tileY][tileX] = 0;
    }

    // update rotasi
    if (p.dirX === 1)  p.angle = 0;
    if (p.dirX === -1) p.angle = Math.PI;
    if (p.dirY === 1)  p.angle = Math.PI / 2;
    if (p.dirY === -1) p.angle = -Math.PI / 2;
}

export function renderPlayer() {
    const { ctx, player: p } = gameState;

    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(p.angle);

    ctx.drawImage(
        p.image,
        -p.size / 2,
        -p.size / 2,
        p.size,
        p.size
    );

    ctx.restore();
}
