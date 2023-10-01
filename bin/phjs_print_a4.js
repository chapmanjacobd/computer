var page = require('webpage').create(),
    system = require('system'),
    fs = require('fs');

page.paperSize = {
    format: 'A4',
    orientation: 'portrait',
    margin: {
        top: "1.5cm",
        bottom: "1cm"
    },
    footer: {
        height: "1cm",
    }
};

page.settings.dpi = "96";

var output = system.args[2];

page.open(system.args[1], function(status) {
  console.log('Status: ' + status);

	window.setTimeout(function () {
	    page.render(output, {format: 'pdf'});
	    phantom.exit(0);
	}, 2000);
});
