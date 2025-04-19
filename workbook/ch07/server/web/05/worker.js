let player = { x: 100, y: 100, angle: 0, speed: 3, turnSpeed: 0.05, fov: Math.PI / 3 }
let keys = { w: false, a: false, s: false, d: false, ArrowLeft: false, ArrowRight: false }
let canvasW = 800
let canvasH = 600
const cellSize = 64

const map = [
  [1,1,1,1,1,1,1,1,1,1],
  [1,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,1,1,1,0,1],
  [1,0,1,0,0,0,0,1,0,1],
  [1,0,1,0,0,0,0,1,0,1],
  [1,0,1,1,1,0,0,0,0,1],
  [1,0,0,0,1,0,0,0,0,1],
  [1,0,0,0,1,0,0,1,0,1],
  [1,0,0,0,0,0,0,1,0,1],
  [1,1,1,1,1,1,1,1,1,1]
]

function castRay(angle) {
  angle = angle % (2 * Math.PI)
  if (angle < 0) angle += 2 * Math.PI
  const rayDirX = Math.cos(angle)
  const rayDirY = Math.sin(angle)
  let mapX = Math.floor(player.x / cellSize)
  let mapY = Math.floor(player.y / cellSize)
  let deltaDistX = Math.abs(1 / rayDirX)
  let deltaDistY = Math.abs(1 / rayDirY)
  let stepX, stepY, sideDistX, sideDistY
  if (rayDirX < 0) {
    stepX = -1
    sideDistX = (player.x / cellSize - mapX) * deltaDistX
  } else {
    stepX = 1
    sideDistX = (mapX + 1.0 - player.x / cellSize) * deltaDistX
  }
  if (rayDirY < 0) {
    stepY = -1
    sideDistY = (player.y / cellSize - mapY) * deltaDistY
  } else {
    stepY = 1
    sideDistY = (mapY + 1.0 - player.y / cellSize) * deltaDistY
  }
  let hit = 0
  let side
  while (hit === 0) {
    if (sideDistX < sideDistY) {
      sideDistX += deltaDistX
      mapX += stepX
      side = 0
    } else {
      sideDistY += deltaDistY
      mapY += stepY
      side = 1
    }
    if (mapX < 0 || mapY < 0 || mapX >= map[0].length || mapY >= map.length) return { distance: Infinity, side: 0 }
    if (map[mapY][mapX] > 0) hit = 1
  }
  let perpWallDist
  if (side === 0) perpWallDist = (mapX - player.x / cellSize + (1 - stepX) / 2) / rayDirX
  else perpWallDist = (mapY - player.y / cellSize + (1 - stepY) / 2) / rayDirY
  perpWallDist *= Math.cos(player.angle - angle)
  return { distance: perpWallDist * cellSize, side }
}

function checkCollision(x, y) {
  const mx = Math.floor(x / cellSize)
  const my = Math.floor(y / cellSize)
  if (mx < 0 || my < 0 || mx >= map[0].length || my >= map.length) return true
  return map[my][mx] === 1
}

function updatePlayer() {
  if (keys.ArrowLeft) player.angle -= player.turnSpeed
  if (keys.ArrowRight) player.angle += player.turnSpeed
  let moveX = 0, moveY = 0
  if (keys.w) {
    moveX += Math.cos(player.angle) * player.speed
    moveY += Math.sin(player.angle) * player.speed
  }
  if (keys.s) {
    moveX -= Math.cos(player.angle) * player.speed
    moveY -= Math.sin(player.angle) * player.speed
  }
  if (keys.a) {
    moveX += Math.cos(player.angle - Math.PI / 2) * player.speed
    moveY += Math.sin(player.angle - Math.PI / 2) * player.speed
  }
  if (keys.d) {
    moveX += Math.cos(player.angle + Math.PI / 2) * player.speed
    moveY += Math.sin(player.angle + Math.PI / 2) * player.speed
  }
  const newX = player.x + moveX
  const newY = player.y + moveY
  const r = 10
  if (!checkCollision(newX + r, player.y + r) && !checkCollision(newX - r, player.y - r)) player.x = newX
  if (!checkCollision(player.x + r, newY + r) && !checkCollision(player.x - r, newY - r)) player.y = newY
}

function gameLoop() {
  updatePlayer()
  const numRays = Math.floor(canvasW / 2)
  const rays = []
  for (let i = 0; i < numRays; i++) {
    const angle = player.angle - player.fov / 2 + (i / numRays) * player.fov
    rays.push(castRay(angle))
  }
  postMessage({ rays, player, map, cellSize, canvasW, canvasH })
  setTimeout(gameLoop, 16)
}

onmessage = e => {
  const { type } = e.data
  if (type === 'keys') keys = e.data.keys
  else if (type === 'mouse') player.angle += e.data.dx * 0.003
  else if (type === 'resize') {
    canvasW = e.data.w
    canvasH = e.data.h
  }
}

gameLoop()