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

function tooltips(){
	if(!window.jQuery)	{
		alert('jQuery not loaded');
	}
	else
	{
		$(document).ready(function(){
			$('#fofWidth').tooltip({'placement':'bottom', 'trigger' : 'hover'});
			$('#fofHeight').tooltip({'placement':'bottom', 'trigger' : 'hover'});
		});
	}		
}

function resize(embed_link, fofWidth, fofHeight, currentFof) {
	var height = document.getElementById(fofHeight).value;
	
	if (height == ""){// how to check if the attribute is null?
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
		"scrolling='no' marginwidth='0' marginheight='0' vspace='0' hspace='0'></iframe></textarea>";
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
