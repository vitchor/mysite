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
        
        var tempImg = [];

        for(var x=0;x<imgsArray.length;x++) {
            tempImg[x] = new Image()
            tempImg[x].src = imgsArray[x]
        }
        
        if (imgsArray.length > 1) {
        
            if (!(frontImage && backImage)) {
                frontImage = document.getElementById('frontImage');
                backImage = document.getElementById('backImage');
            }
        
            backImage.src = tempImg.src;
        
            frontImage.style.opacity = "0";
            frontImage.style.filter = "alpha(opacity="+0.0+")";            
            
            backImage.style.opacity = "1";
            backImage.style.filter = "alpha(opacity="+1.0+")"; 
                   
            
        
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
            frontImage.src = tempImg.src;            
        } else {
            frontImage = document.getElementById('frontImage');
            frontImage.src = imgsArray[0];
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
        frontImage.style.filter = "alpha(opacity="+newImageOpacity/100.0+")";
        newImageOpacity = newImageOpacity + 1;
        
    }
}
