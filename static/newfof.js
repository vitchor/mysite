var frontImage;
var backImage;

var frontImageIndex = 1;
var backImageIndex = 0;

var newImageOpacity = 0.00;

var timer = 0;
var threadRunning = false;

// Iterates the imgsArray to cicle the frontImage(Div) and backImage(Div) correctly
function homefade() {
    
    if (!threadRunning) {
        threadRunning = true;
        
        if (imgsArray.length > 1) {
            
            if (frontImageIndex == (imgsArray.length - 1)) {
                frontImageIndex = 0;
                backImageIndex = imgsArray.length - 1;
        
            } else {    
                frontImageIndex++;
            
                if (backImageIndex == (imgsArray.length - 1)) {
                    backImageIndex = 0; 
                } else {
                    backImageIndex++;
                }
            
            }
            
            if (!backImageDiv || !frontImageDiv) {
                var backImageDiv = document.getElementById('backImageDiv');
                var frontImageDiv = document.getElementById('frontImageDiv');        
            }
            
            imgsArray[backImageIndex].id = "backImage";
            imgsArray[frontImageIndex].id = "frontImage";
            
            imgsArray[backImageIndex].style.opacity= "1";
            
            //Adds the back Image object:
            if (backImageDiv.hasChildNodes()) {
                 backImageDiv.removeChild(backImageDiv.lastChild);
             }      
            backImageDiv.appendChild(imgsArray[backImageIndex]);
            
            //Hides the front image:
            imgsArray[frontImageIndex].style.opacity= "0";
            
            //Adds front image object:
            if (frontImageDiv.hasChildNodes()) {
                frontImageDiv.removeChild(frontImageDiv.lastChild);
            }
            frontImageDiv.appendChild(imgsArray[frontImageIndex]);
            
            timer = setInterval("homefadeTrans();", 10);
            
        } else {
            var backImageDiv = document.getElementById('backImageDiv');
            imgsArray[0].id = "backImage";
            imgsArray[0].style.opacity = "1";
            backImageDiv.appendChild(imgsArray[0]);
        }
    }
}

function headScript(mobileAddress, current_fof, hide_arrows) {
/*  CHANGE THE PAGE IN CASE OF IPHONE	*/
	if ((navigator.userAgent.match(/iPhone/i)) || (navigator.userAgent.match(/iPod/i))) {
   		location.replace(mobileAddress);
	}
	window.onload = afterLoading(hide_arrows);
	$(window).bind("load", function() {
		resize('textAreaEmbedLink', 'fofWidth', 'fofHeight', current_fof);
	});
	
	/*  GOOGLE ANALYTICS:*/	
	var _gaq = _gaq || [];
	_gaq.push(['_setAccount', 'UA-35287341-1']);
	_gaq.push(['_trackPageview']);

	(function() {
		var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
		ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
		var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	})();
}

function bodyScript(){
	/*  FACEBOOK CONNECTION (USED FOR LIKE BUTTON?):  */
	window.fbAsyncInit = function() {
		FB.init({appId: '417476174956036', status: true, cookie: true, xfbml: true});
	};
	(function() {
		var e = document.createElement('script'); e.async = true;
		e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
		document.getElementById('fb-root').appendChild(e);
	}());

	/*  ATTRIBUTES OF THE SHARE BUTTON:	*/
	$(document).ready(function(){
		$('#share_button').click(function(e){
			e.preventDefault();	
			FB.ui(
			{
				method: 'feed',
				name: user_name + "'s FOF",
				link: "https://dyfoc.us/uploader/"+current_fof+"/share_fof/",
				picture: imgsArray[0].src,
				caption: window.location.href,
				description: 'This FOF was taken by ' + user_name,
				message: ''
			});		
		});
	});
}

// Fades the pictures frontImage and backImage so when one of the pics reaches 100%, it calls the homefade function
function homefadeTrans() {
    if (newImageOpacity >= 100.0) {
        clearTimeout(timer);
        
        timer = 0;
        newImageOpacity = 0;
        threadRunning = false;
        setTimeout("homefade();", 2000);
        
    } else {
        imgsArray[frontImageIndex].style.opacity = newImageOpacity/100.0;
        imgsArray[frontImageIndex].style.filter = "alpha(opacity="+newImageOpacity+")";
        newImageOpacity = newImageOpacity + 1;
    }

}

function afterLoading(hide_arrows){
	if(!window.jQuery)	{
		alert('jQuery not loaded');
	}
	else
	{
		$(document).ready(function(){
			$('#fofWidth').tooltip({'placement':'bottom', 'trigger' : 'hover'});
			$('#fofHeight').tooltip({'placement':'bottom', 'trigger' : 'hover'});
			
			if(hide_arrows == 1){
				hideArrows();
			}
			if(type == "featured_fof"){
				document.getElementById("left_arrow_link").href = "/uploader/"+prev_fof+"/featured_fof";
				document.getElementById("right_arrow_link").href = "/uploader/"+next_fof+"/featured_fof";
			}else if (type == "user_fof"){
				document.getElementById("left_arrow_link").href = "/uploader/"+device_id+"/user/"+prev_fof+"/fof_name/";
				document.getElementById("right_arrow_link").href = "/uploader/"+device_id+"/user/"+next_fof+"/fof_name/";
			} else if(type == "feed_fof"){
				document.getElementById("left_arrow_link").href = "/uploader/"+device_id+"/feed/"+prev_fof+"/";
				document.getElementById("right_arrow_link").href = "/uploader/"+device_id+"/feed/"+next_fof+"/"
			}
			
		});
	}		
}

function hideArrows(){
	document.getElementById("colwrap4").style.display = 'none';
	document.getElementById("colwrap2").style.display = 'none';
	document.getElementById("colwrap3").id = 'colwrap3_share';
}

function resize(embed_link, fofWidth, fofHeight, currentFof) {
	var height = document.getElementById(fofHeight).value;
	
	if (height == ""){
		height = "576";
		document.getElementById(fofHeight).value = "576";
	}
	var pic = imgsArray[backImageIndex];
	var widthFactor = (pic.offsetWidth)/(pic.offsetHeight);
	
	var width = height*widthFactor;	
	width = width.toFixed(0);
	
	document.getElementById(fofWidth).value = width
	
	var myvar = "<iframe src= 'http://dyfoc.us/uploader/"+currentFof+
		"/embedded_fof/"+height+"/height/' width="+width+" height="+height+" frameborder='no' "+
		"scrolling='no' marginwidth='0' marginheight='0' vspace='0' hspace='0'></iframe>";
	document.getElementById(embed_link).value = myvar;
}

function embeddedfade() {

    if (!threadRunning) {
        threadRunning = true;

        if (imgsArray.length > 1) {

            if (frontImageIndex == (imgsArray.length - 1)) {
                frontImageIndex = 0;
                backImageIndex = imgsArray.length - 1;

            } else {    
                frontImageIndex++;

                if (backImageIndex == (imgsArray.length - 1)) {
                    backImageIndex = 0; 
                } else {
                    backImageIndex++;
                }

            }

            if (!backImageDiv || !frontImageDiv) {
                var backImageDiv = document.getElementById('backImageEmbedDiv');
                var frontImageDiv = document.getElementById('frontImageEmbedDiv');        
            }

            imgsArray[backImageIndex].id = "embedBackImage";
            imgsArray[frontImageIndex].id = "embedFrontImage";
            /*
			imgsArray[backImageIndex].style.height = "200px";
			imgsArray[frontImageIndex].style.height = "200px";
			*/

            imgsArray[backImageIndex].style.opacity= "1";

            //Adds the back Image object:
            if (backImageDiv.hasChildNodes()) {
                 backImageDiv.removeChild(backImageDiv.lastChild);
             }      
            backImageDiv.appendChild(imgsArray[backImageIndex]);

            //Hides the front image:
            imgsArray[frontImageIndex].style.opacity= "0";

            //Adds front image object:
            if (frontImageDiv.hasChildNodes()) {
                frontImageDiv.removeChild(frontImageDiv.lastChild);
            }
            frontImageDiv.appendChild(imgsArray[frontImageIndex]);

            timer = setInterval("embeddedFadeTrans();", 10);

        } else {
            var backImageDiv = document.getElementById('backImageEmbedDiv');
            imgsArray[0].id = "embedBackImage";
            imgsArray[0].style.opacity = "1";
            backImageDiv.appendChild(imgsArray[0]);
        }
    }
}

function embeddedFadeTrans() {
    if (newImageOpacity >= 100.0) {
        clearTimeout(timer);

        timer = 0;
        newImageOpacity = 0;
        threadRunning = false;
        setTimeout("embeddedfade();", 2000);

    } else {
        imgsArray[frontImageIndex].style.opacity = newImageOpacity/100.0;
        imgsArray[frontImageIndex].style.filter = "alpha(opacity="+newImageOpacity+")";
        newImageOpacity = newImageOpacity + 1;

    }
}
