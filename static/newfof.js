var frontImage;
var backImage;

var frontImageIndex = 1;
var backImageIndex = 0;

var newImageOpacity = 0.00;

var timer = 0;
var threadRunning = false;

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
                var backImageDiv = document.getElementById('backImageEmbed');
                var frontImageDiv = document.getElementById('frontImageEmbed');        
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

            timer = setInterval("embeddedFadeTrans();", 10);

        } else {
            var backImageDiv = document.getElementById('backImageEmbed');
            imgsArray[0].id = "backImage";
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