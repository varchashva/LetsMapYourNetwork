;(function(undefined) {
  'use strict';

  if (typeof sigma === 'undefined')
    throw 'sigma is not declared';

  // Initialize packages:
  sigma.utils.pkg('sigma.canvas.hovers');

  /**
   * This hover renderer will basically display the label with a background.
   *
   * @param  {object}                   node     The node object.
   * @param  {CanvasRenderingContext2D} context  The canvas context.
   * @param  {configurable}             settings The settings function.
   */
  sigma.canvas.hovers.def = function(node, context, settings) {
    var x,
        y,
        w,
        h,
        e,
        fontStyle = settings('hoverFontStyle') || settings('fontStyle'),
        prefix = settings('prefix') || '',
        size = node[prefix + 'size'],
        fontSize = (settings('labelSize') === 'fixed') ?
          settings('defaultLabelSize') :
          settings('labelSizeRatio') * size;

    // Label background:
    context.font = (fontStyle ? fontStyle + ' ' : '') +
      fontSize + 'px ' + (settings('hoverFont') || settings('font'));

    context.beginPath();
    context.fillStyle = settings('labelHoverBGColor') === 'node' ?
      (node.color || settings('defaultNodeColor')) :
      settings('defaultHoverLabelBGColor');

    if (node.neo4j_data.hostname && settings('labelHoverShadow')) {
      context.shadowOffsetX = 0;
      context.shadowOffsetY = 0;
      context.shadowBlur = 8;
      context.shadowColor = settings('labelHoverShadowColor');
    }

    if (node.neo4j_data.hostname && typeof node.neo4j_data.hostname === 'string') {
      x = Math.round(node[prefix + 'x'] - fontSize / 2 - 2);
      y = Math.round(node[prefix + 'y'] - fontSize / 2 - 22);
      w = Math.round(
        context.measureText(node.neo4j_data.hostname).width + fontSize / 2 + size + 87 //width
      );
      h = Math.round((fontSize + 4) * 3 + 5); // height
      e = Math.round(fontSize / 2 + 2);

      context.moveTo(x, y + e);
      context.arcTo(x, y, x + e, y, e);
      context.lineTo(x + w, y);
      context.lineTo(x + w, y + h);
      context.lineTo(x + e, y + h);
      context.arcTo(x, y + h, x, y + h - e, e);
      context.lineTo(x, y + e);

      context.closePath();
      context.fill();

      context.shadowOffsetX = 0;
      context.shadowOffsetY = 0;
      context.shadowBlur = 0;
    }

    // Node border:
    if (settings('borderSize') > 0) {
      context.beginPath();
      context.fillStyle = settings('nodeBorderColor') === 'node' ?
        (node.color || settings('defaultNodeColor')) :
        settings('defaultNodeBorderColor');
      context.arc(
        node[prefix + 'x'],
        node[prefix + 'y'],
        size + settings('borderSize'),
        0,
        Math.PI * 2,
        true
      );
      context.closePath();
      context.fill();
    }

    // Node:
    var nodeRenderer = sigma.canvas.nodes[node.type] || sigma.canvas.nodes.def;
    nodeRenderer(node, context, settings);

    // Display the label:
    if (node.neo4j_data.hostname && typeof node.neo4j_data.hostname === 'string') {
      context.fillStyle = (settings('labelHoverColor') === 'node') ?
        (node.color || settings('defaultNodeColor')) :
        settings('defaultLabelHoverColor');

      context.fillText(
      "Hostname: " + node.neo4j_data.hostname,
        Math.round(node[prefix + 'x'] + size + 6),
        Math.round(node[prefix + 'y'] + fontSize / 3 - 20)
      );
      context.fillText(
      "IP: " + node.neo4j_data.ip,
      Math.round(node[prefix + 'x'] + size + 6),
        Math.round(node[prefix + 'y'] + fontSize / 3)
        );
      context.fillText(
      "Enumeration: " + node.neo4j_data.enum.split("#")[0] ,
      Math.round(node[prefix + 'x'] + size + 6),
        Math.round(node[prefix + 'y'] + fontSize / 3 + 20)
        );
    }
  };
}).call(this);
