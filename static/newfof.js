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
        
            if (!(frontImage && backImage)) {
                frontImage = document.getElementById('frontImage');
                backImage = document.getElementById('backImage');
            }
        
            backImage.src = imgsArray[backImageIndex].src;
        
            frontImage.style.opacity = "0";
            backImage.style.opacity = "1";
        
            frontImage.src = imgsArray[frontImageIndex].src;
        
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
        
            timer = setInterval("homefadeTrans();", 10);
        } else {
            frontImage = document.getElementById('frontImage');
            frontImage.src = imgsArray[0].src;
        }
    }
}

function homefadeTrans() {
    if (newImageOpacity >= 100.0) {
        clearTimeout(timer);
        
        timer = 0;
        newImageOpacity = 0;
        threadRunning = false;
        setTimeout("homefade();", 1000);
        
    } else {

        frontImage.style.opacity = newImageOpacity/100.0;
        frontImage.style.filter = "alpha(opacity="+newImageOpacity+")";
        newImageOpacity = newImageOpacity + 1;
        
    }
}