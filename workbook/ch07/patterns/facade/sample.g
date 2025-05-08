// Simple Graphics VM Script - House Scene
// File: sample.g

// Create a 400x400 canvas
canvas 400 400

// Background
rectangle sky 0 0 400 400 128,128,255

// Sun
circle sun 100 100 50 yellow

// Ground
rectangle ground 0 300 400 100 20,128,20

// Green triangle (road)
triangle road 350 300 40 400 300 400 0,255,0

// Create a house group
group house

  // House base
  rectangle houseBase 150 250 100 80 150,75,0
  
  // House roof
  triangle houseRoof 150 250 250 250 200 200 red
  
  // House door
  rectangle houseDoor 180 290 30 40 70,40,0
  
// End house group
end

// Render the scene
render
