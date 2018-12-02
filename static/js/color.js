$.getJSON('/color', function(json) {
  r = json['data']['r'];
  g = json['data']['g'];
  b = json['data']['b'];
  if (r == null) {
    r = 0;
    g = 0;
    b = 0;
  }
  let colorPicker = new iro.ColorPicker(".colorPicker", {
    width: 400,
    height: 400,
    color: {r: r, g: g, b: b},
    anticlockwise: true,
    borderWidth: 1,
    borderColor: "#fff",
    css: {
      "#swatch": {
        "background-color": "$color"
      }
    }
  });
  picker(colorPicker)
});

function picker(colorPicker) {
  colorPicker.on("color:change", function(color, changes) {
    rgb.innerHTML = [color.rgbString];
    R = color.rgb['r'];
    G = color.rgb['g'];
    B = color.rgb['b'];
    $.ajax({
      type: "POST",
      url: "/color",
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify({'r': R, 'g': G, 'b': B}),
      dataType: "json",
    });
  });
}
