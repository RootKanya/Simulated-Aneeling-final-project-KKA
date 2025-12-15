import { gameState, TILE_SIZE } from "./gameState.js";
import { initAsteroids, updateAsteroids, renderAsteroids } from "./gameplay/asteroid.js";

const ASTEROID_COUNT = 3;
const DNA_LENGTH = 20;
const SPEED = 2;

let asteroids = [];

//spawn
export function initAsteroids() {
    asteroids = [];

    for (let i = 0; i < ASTEROID_COUNT; i++) {
        const pos = simulatedAnnealingSpawn(asteroids);

        asteroids.push(createAsteroid(pos.x, pos.y));
    }

    gameState.asteroids = asteroids;
}

//SA
function simulatedAnnealingSpawn(existingAsteroids) {
    let current = randomEmptyTile();
    let best = current;

    let temp = 100;

    while (temp > 1) {
        const next = randomEmptyTile();

        const eCurr = energy(current, existingAsteroids);
        const eNext = energy(next, existingAsteroids);

        if (eNext > eCurr || Math.random() < Math.exp((eNext - eCurr) / temp)) {
            current = next;
        }

        if (energy(current, existingAsteroids) > energy(best, existingAsteroids)) {
            best = current;
        }

        temp *= 0.9;
    }

    return best;
}

function energy(tile, asteroids) {
    const player = gameState.player;

    let score = distance(tile, {
        x: Math.floor(player.x / TILE_SIZE),
        y: Math.floor(player.y / TILE_SIZE)
    });

    asteroids.forEach(a => {
        score += distance(tile, {
            x: a.tileX,
            y: a.tileY
        });
    });

    return score;
}

//GA
function generateDNA() {
    const genes = [];
    const dirs = [
        { x: 1, y: 0 },
        { x: -1, y: 0 },
        { x: 0, y: 1 },
        { x: 0, y: -1 }
    ];

    for (let i = 0; i < DNA_LENGTH; i++) {
        genes.push(dirs[Math.floor(Math.random() * 4)]);
    }

    return genes;
}

function createAsteroid(tileX, tileY) {
    return {
        x: tileX * TILE_SIZE + TILE_SIZE / 2,
        y: tileY * TILE_SIZE + TILE_SIZE / 2,

        tileX,
        tileY,

        dirX: 0,
        dirY: 0,

        dna: generateDNA(),
        geneIndex: 0,

        speed: SPEED,
        image: loadAsteroidImage()
    };
}

function fitness(a) {
    const player = gameState.player;
    return -Math.hypot(
        a.tileX - Math.floor(player.x / TILE_SIZE),
        a.tileY - Math.floor(player.y / TILE_SIZE)
    );
}

export function updateAsteroids() {
    asteroids.forEach(a => {
        const gene = a.dna[a.geneIndex];

        const nextX = a.x + gene.x * a.speed;
        const nextY = a.y + gene.y * a.speed;

        const nextTileX = Math.floor(nextX / TILE_SIZE);
        const nextTileY = Math.floor(nextY / TILE_SIZE);

        // collision dinding
        if (gameState.map[nextTileY]?.[nextTileX] !== 1) {
            a.x = nextX;
            a.y = nextY;
            a.dirX = gene.x;
            a.dirY = gene.y;
        }

        a.tileX = Math.floor(a.x / TILE_SIZE);
        a.tileY = Math.floor(a.y / TILE_SIZE);

        a.geneIndex++;

        // DNA habis → evolusi
        if (a.geneIndex >= a.dna.length) {
            evolve(a);
        }
    });
}

function evolve(a) {
    const bestGene = a.dna.reduce((best, g) =>
        Math.random() < 0.7 ? best : g
    );

    a.dna = a.dna.map(() =>
        Math.random() < 0.8 ? bestGene : randomGene()
    );

    a.geneIndex = 0;
}

function randomGene() {
    const dirs = [
        { x: 1, y: 0 },
        { x: -1, y: 0 },
        { x: 0, y: 1 },
        { x: 0, y: -1 }
    ];
    return dirs[Math.floor(Math.random() * 4)];
}

function loadAsteroidImage() {
    const img = new Image();
    img.src = "../assets/asteroid.png";
    return img;
}

export function renderAsteroids() {
    const ctx = gameState.ctx;

    asteroids.forEach(a => {
        ctx.drawImage(
            a.image,
            a.x - TILE_SIZE / 2,
            a.y - TILE_SIZE / 2,
            TILE_SIZE,
            TILE_SIZE
        );
    });
}
