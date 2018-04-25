 function callAjax(url, callback)
 {
 	var xmlhttp;
 	// compatible with IE7+, Firefox, Chrome, Opera, Safari
 	xmlhttp = new XMLHttpRequest();
 	xmlhttp.onreadystatechange = function()
 	{
 		if (xmlhttp.readyState == 4 && xmlhttp.status == 200)
 		{
 			callback(xmlhttp.responseText);
 		}
 	}
 	xmlhttp.open("GET", url, true);
 	xmlhttp.send();
 }


 function cb_myCallback(theStuff)
 {
     // process theStuff here. If it's JSON data, you can unpack it trivially in Javascript,
     // as I will describe later. For this example, it's just text. You're going to get
     // back "hello, Ben"
     console.log(theStuff);
 }

 pyRequest("Ben",cb_myCallback);