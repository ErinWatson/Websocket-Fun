
$(document).ready(function() {
	if (!window.console) window.console = {};
	if (!window.console.log) window.console.log = function() {};

	updater.start();
});

$(window).unload(function() {
	updater.stop()
});

function websocketAtUrl(socketPath) {
	var l = window.location;
	return ((l.protocol === "https:") ? "wss://" : "ws://") + l.hostname + (((l.port != 80) && (l.port != 443)) ? ":" + l.port : "") + l.pathname + socketPath;
}

function clientToWaiters() {
	//document.getElementById("message_in").value = document.getElementById("message_out").value;
	updater.socket.send(document.getElementById("message_out").value);
}


var updater = {
	socket: null,

	start: function() {

		if ("WebSocket" in window) {
			updater.socket = new WebSocket(websocketAtUrl("updatesocket"));
		} else {
			updater.socket = new MozWebSocket(websocketAtUrl("updatesocket"));
		}
		updater.socket.onmessage = function(event) {
			var d;
			console.log(event.data);
			json_message = JSON.parse(event.data);
			document.getElementById("message_in").value = json_message.msg;
			
			/*if (message.type == "camera"){
				//d = new Date();
				updater.updatePhoto(message);
				//$("#Loadcell1").text(String(message.cmd) + String(message.data));
			}*/
		}
	},

	stop: function() {
		updater.socket.close();
		updater.socket = null;
	},

	updatePhoto: function(message) {

		//d = new Date();
		//$("#fridgepic").attr("style", "background-image:url('/static/snap2.jpg?"+d.getTime()+"')");
		//message.image_url = "http://10.211.55.5:8888/static/image2.jpg"
		//$("#fridgepic").attr("src", "http://" + message.ip_address + ":8888" + message.url + "?" + d);

		//http://10.211.55.5:8888/static/image2.jpg
	}
};
